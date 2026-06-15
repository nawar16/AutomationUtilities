import argparse
import asyncio
import sys

import httpx

from app.client import AsyncTaxClient
from app.crypto import generate_tamper_proof_receipt
from app.exceptions import VATValidatorException
from app.file_io import parse_batch_input_file, write_audit_ledger_output
from app.logger import configure_production_logging
from app.models import VATIngestStream

logger = configure_production_logging("CLI-Orchestrator")


async def run_pipeline_worker(client: httpx.AsyncClient, tax_client: AsyncTaxClient, raw_row: dict) -> dict:

    try:
        model = VATIngestStream(**raw_row)
    except Exception as validation_err:
        logger.warning(f"Skipping incorrect input structure row item: {str(validation_err)}")
        return {"error": "BAD_ROW_CONTRACT_LAYOUT", "raw_data_dump": raw_row}

    input_payload_snapshot = {"raw_vat_id": model.raw_vat_id, "company_name": model.company_name}
    response_payload_snapshot = None

    if model.is_structurally_valid_de or (len(model.sanitized_id) >= 4 and not model.sanitized_id.startswith("DE")):
        remote_tax_data = await tax_client.dispatch_validation(client, model.sanitized_id)
        response_payload_snapshot = remote_tax_data.model_dump()
    else:
        logger.info(f"Local reject on format: '{model.raw_vat_id}'")

    sealed_compliance_receipt = generate_tamper_proof_receipt(input_payload_snapshot, response_payload_snapshot)
    return sealed_compliance_receipt.model_dump()


async def main_async(input_file: str, output_file: str) -> None:
    tax_client = AsyncTaxClient()
    try:
        logger.info(f"Opening data stream source from: {input_file}")
        batch_rows = await parse_batch_input_file(input_file)
        logger.info(f"{len(batch_rows)} rows matching requirements...")
    except Exception as file_read_err:
        logger.critical(f"Aborting, data pipeline source broken: {str(file_read_err)}")
        raise

    async with httpx.AsyncClient(limits=tax_client.limits) as client:
        task_workers = [run_pipeline_worker(client, tax_client, row) for row in batch_rows]
        finalized_receipt_ledger = await asyncio.gather(*task_workers)

    try:
        logger.info(f"Writing crypto signed verification receipts to: {output_file}")
        await write_audit_ledger_output(output_file, finalized_receipt_ledger)
        logger.info("Completed")
    except Exception as file_write_err:
        logger.critical(f"Fatal storage error occurred: {str(file_write_err)}")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Compliance Automation: German & European Tax VAT ID Validator Engine")
    parser.add_argument(
        "--input", "-i", default="data/input_batch.csv", help="Source file location path (.csv or .json)"
    )
    parser.add_argument(
        "--output", "-o", default="data/audit_compliance_receipt.json", help="Output verification destination path"
    )
    args = parser.parse_args()
    from pathlib import Path

    if args.input == "data/input_batch.csv" and not Path(args.input).exists():
        Path("data").mkdir(exist_ok=True)
        with open(args.input, "w", encoding="utf-8") as file_buffer:
            file_buffer.write("raw_vat_id,company_name\n")
            file_buffer.write("de 123456789,Berlin X\n")
            file_buffer.write("FR88123456789,Paris Z\n")
            file_buffer.write("INVALID-DE-99,Data Y\n")

    try:
        asyncio.run(main_async(args.input, args.output))
    except VATValidatorException as custom_fault:
        logger.error(f"Job failed under controlled exception code: {str(custom_fault)}")
        sys.exit(1)
    except Exception as unhandled_panic:
        logger.critical(f"System abort, failure : {str(unhandled_panic)}", exc_info=True)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
