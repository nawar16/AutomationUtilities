import json
import sys
from typing import Any, Dict, List

from app.models import VATIngestStream


def execute_sprint_pipeline(raw_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    audit_trail: List[Dict[str, Any]] = []

    for record in raw_batch:
        stream_model = VATIngestStream(**record)

        audit_trail.append(
            {
                "provided_input": stream_model.raw_vat_id,
                "sanitized_output": stream_model.sanitized_id,
                "is_german_format": stream_model.is_structurally_valid_de,
                "metadata": {
                    "company_hint": stream_model.company_name,
                    "action_required": (
                        "queue_for_api_dispatch" if stream_model.is_structurally_valid_de else "reject_bad_format"
                    ),
                },
            }
        )

    return audit_trail


def main() -> None:
    mock_incoming_b2b_stream: List[Dict[str, Any]] = [
        {"raw_vat_id": "de 123456789", "company_name": "Tech X"},
        {"raw_vat_id": "DE-987-654-321", "company_name": "Tech Y"},
        {"raw_vat_id": "  de.111_222_333  ", "company_name": "Munich Z"},
        {"raw_vat_id": "INVALID-DE-99", "company_name": "Data Y"},
        {"raw_vat_id": "FR88123456789", "company_name": "Paris E"},
    ]

    print("--- Pydantic Context Validation ---")

    pipeline_outputs = execute_sprint_pipeline(mock_incoming_b2b_stream)

    print(json.dumps(pipeline_outputs, indent=4))

    print("\n--- Finished successfully ---")
    sys.exit(0)


if __name__ == "__main__":
    main()
