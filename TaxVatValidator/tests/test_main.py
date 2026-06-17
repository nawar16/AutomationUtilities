from app.crypto import compute_record_signature, generate_tamper_proof_receipt
from app.models import VATIngestStream


def test_sanitization_and_regex():
    # format
    model_valid = VATIngestStream(raw_vat_id="  de-123.456_789  ", company_name="Berlin Tech")
    assert model_valid.sanitized_id == "DE123456789"
    assert model_valid.is_structurally_valid_de is True
    # invalid one
    model_short = VATIngestStream(raw_vat_id="DE12345")
    assert model_short.is_structurally_valid_de is False


def test_cryptographic_signatures():
    ingest = {"raw_vat_id": "DE123456789", "company_name": "Berlin Tech"}
    response = {"is_valid_active_vat": True, "trader_name": "Berlin Tech"}
    # hash match
    hash_one = compute_record_signature(ingest, response)
    hash_two = compute_record_signature(ingest, response)
    assert hash_one == hash_two
    # filed modified => checksum break
    original_receipt = generate_tamper_proof_receipt(ingest, response)
    tampered_ingest = {"raw_vat_id": "DE123456789", "company_name": "FRAUD CORP"}
    new_checksum = compute_record_signature(tampered_ingest, response)
    assert original_receipt.sha256_integrity_hash != new_checksum
