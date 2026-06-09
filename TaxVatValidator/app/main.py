import sys
import json
from typing import List, Dict, Any
from app.transformer import transform_and_analyze


def execute_local_sprint_pipeline(batch_inputs: List[str]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for record in batch_inputs:
        analyzed_payload = transform_and_analyze(record)
        results.append(analyzed_payload)
    return results


def main() -> None:
    #samples
    mock_ingested_batch: List[str] = [
        "de 123456789",
        "DE-987-654-321",
        "  de.111_222_333  ",
        "INVALID-DE-99",
        "FR88123456789",
        "DE12345678"
    ]
    
    print("--- Local Sanitization & Transformation ---")
    
    pipeline_outputs = execute_local_sprint_pipeline(mock_ingested_batch)
    
    print(json.dumps(pipeline_outputs, indent=4))
    
    print("\n--- Finished successfully ---")
    sys.exit(0)


if __name__ == "__main__":
    main()
