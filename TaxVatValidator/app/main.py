import asyncio
import sys
from typing import Any, Dict

import httpx

from app.client import AsyncTaxClient
from app.crypto import generate_tamper_proof_receipt
from app.file_io import parse_batch_input_file, write_audit_ledger_output
from app.models import VATIngestStream


async def process_record(
    client: httpx.AsyncClient, tax_client: AsyncTaxClient, raw_record: Dict[str, Any]
) -> Dict[str, Any]:
    model = VATIngestStream(**raw_record)

    audit_log = {
        "raw_input": model.raw_vat_id,
        "company_hint": model.company_name,
        "sanitized_id": model.sanitized_id,
        "status": "REJECTED_LOCAL_FORMAT_FAIL",
        "api_response": None,
    }

    if model.is_structurally_valid_de or (len(model.sanitized_id) >= 4 and not model.sanitized_id.startswith("DE")):
        # pass the local rules
        audit_log["status"] = "PENDING_NETWORK_VERIFICATION"

        response_data = await tax_client.dispatch_validation(client, model.sanitized_id)

        audit_log["api_response"] = response_data.model_dump()
        audit_log["status"] = "SUCCESS_VERIFIED" if response_data.is_valid_active_vat else "SUCCESS_INVALID_ACCOUNT"

    return audit_log


async def run_pipeline_worker(
    client: httpx.AsyncClient, tax_client: AsyncTaxClient, raw_row: Dict[str, Any]
) -> Dict[str, Any]:
    model = VATIngestStream(**raw_row)

    input_payload_snapshot = {"raw_vat_id": model.raw_vat_id, "company_name": model.company_name}
    response_payload_snapshot = None

    if model.is_structurally_valid_de or (len(model.sanitized_id) >= 4 and not model.sanitized_id.startswith("DE")):
        remote_tax_data = await tax_client.dispatch_validation(client, model.sanitized_id)
        response_payload_snapshot = remote_tax_data.model_dump()

    sealed_compliance_receipt = generate_tamper_proof_receipt(input_payload_snapshot, response_payload_snapshot)
    return sealed_compliance_receipt.model_dump()


async def main_async(input_file: str, output_file: str) -> None:
    tax_client = AsyncTaxClient()

    print(f"Start loading data from: {input_file}")
    untrusted_batch_rows = await parse_batch_input_file(input_file)
    print(f"Successfully loaded {len(untrusted_batch_rows)} rows")

    async with httpx.AsyncClient(limits=tax_client.limits) as client:
        task_workers = [run_pipeline_worker(client, tax_client, row) for row in untrusted_batch_rows]
        finalized_receipt_ledger = await asyncio.gather(*task_workers)

    print(f"Exporting signed receipts to: {output_file}")
    await write_audit_ledger_output(output_file, finalized_receipt_ledger)
    print("Completed")


def main() -> None:
    input_target = "data/input_sample.csv"
    output_target = "data/audit_res.json"

    if len(sys.argv) >= 3:
        input_target = sys.argv[1]
        output_target = sys.argv[2]

    from pathlib import Path

    if not Path(input_target).exists():
        Path("data").mkdir(exist_ok=True)
        with open(input_target, "w", encoding="utf-8") as f:
            f.write("raw_vat_id,company_name\n")
            f.write("de 123456789,Berlin X\n")
            f.write("DE-987-654-321,Hamburg Y\n")
            f.write("FR88123456789,Paris Z\n")
            f.write("INVALID-DE-99,Data Y\n")


    try:
        asyncio.run(main_async(input_target, output_target))
    except Exception as fatal_error:
        print(f"pipeline terminated via fault: {str(fatal_error)}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
