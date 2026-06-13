import asyncio
import json
import sys
from typing import Any, Dict, List

import httpx

from app.client import AsyncTaxClient
from app.crypto import generate_tamper_proof_receipt
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


async def main_async() -> None:
    mock_input_queue: List[Dict[str, Any]] = [
        {"raw_vat_id": "de 123456789", "company_name": "Berlin Tech"},
        {"raw_vat_id": "DE-987-654-321", "company_name": "Hamburg Logistics"},
        {"raw_vat_id": "FR88123456789", "company_name": "Paris Fashion"},  # none-DE
        {"raw_vat_id": "INVALID-DE-99", "company_name": "Data Collect"},
        {"raw_vat_id": "DE12345678", "company_name": "Too Short"},
    ]

    tax_client = AsyncTaxClient()

    print("--- Async Connection ---")

    async with httpx.AsyncClient(limits=tax_client.limits) as client:
        tasks = [process_record(client, tax_client, record) for record in mock_input_queue]

        completed_audit_trails = await asyncio.gather(*tasks)

    print(json.dumps(completed_audit_trails, indent=4))
    print("--- finish ---")


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\ncanceled manually by operational signal.")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
