import hashlib
import hmac
import json
import uuid
from typing import Any, Dict, Optional

from app.models import AuditReceipt

SECRET_COMPLIANCE_SALT = b"FINANZAMT_REGULATORY_COMPLIANCE_PEPPER_2026"

def compute_record_signature(raw_input_data: Dict[str, Any], api_response_data: Optional[Dict[str, Any]]) -> str:
    payload_aggregation = {
        "source": raw_input_data,
        "verification": api_response_data or {"status": "LOCAL_FORMAT_REJECTION_NO_NET_DISPATCH"}
    }

    canonical_json_bytes = json.dumps(payload_aggregation, sort_keys=True).encode("utf-8")

    hashed_signature = hmac.new(SECRET_COMPLIANCE_SALT, canonical_json_bytes, hashlib.sha256).hexdigest()
    return hashed_signature


def generate_tamper_proof_receipt(ingest: Dict[str, Any], response: Optional[Dict[str, Any]]) -> AuditReceipt:
    integrity_checksum = compute_record_signature(ingest, response)

    return AuditReceipt(
        receipt_id=str(uuid.uuid4()),
        input_records=ingest,
        verification_metrics=response,
        sha256_integrity_hash=integrity_checksum
    )
