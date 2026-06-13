import csv
import json
from pathlib import Path
from typing import Any, Dict, List


async def parse_batch_input_file(file_path_str: str) -> List[Dict[str, Any]]:
    target_path = Path(file_path_str)
    if not target_path.exists():
        raise FileNotFoundError(f"Target dataset tracking asset missing at: {file_path_str}")

    records: List[Dict[str, Any]] = []

    if target_path.suffix.lower() == ".json":
        with open(target_path, mode="r", encoding="utf-8") as raw_json:
            parsed_data = json.load(raw_json)
            return parsed_data if isinstance(parsed_data, list) else [parsed_data]

    elif target_path.suffix.lower() == ".csv":
        with open(target_path, mode="r", encoding="utf-8-sig") as raw_csv:
            csv_reader = csv.DictReader(raw_csv)
            for row in csv_reader:
                records.append(
                    {
                        "raw_vat_id": row.get("raw_vat_id", "").strip(),
                        "company_name": row.get("company_name", "").strip() or None,
                    }
                )
        return records

    else:
        raise ValueError(f"Unsupported storage container classification profile format: {target_path.suffix}")


async def write_audit_ledger_output(file_path_str: str, complete_receipts: List[Dict[str, Any]]) -> None:
    destination_path = Path(file_path_str)

    destination_path.parent.mkdir(parents=True, exist_ok=True)

    with open(destination_path, mode="w", encoding="utf-8") as target_file:
        json.dump(complete_receipts, target_file, indent=4, ensure_ascii=False)
