from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.transformer import sanitize_vat_id, validate_german_format


class VATIngestStream(BaseModel):
    raw_vat_id: str = Field(...)
    company_name: Optional[str] = Field(None)

    @property
    def sanitized_id(self) -> str:
        return sanitize_vat_id(self.raw_vat_id)

    @property
    def is_structurally_valid_de(self) -> bool:
        return validate_german_format(self.sanitized_id)


class TaxAuthorityResponse(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    vat_number: str = Field(..., min_length=2, max_length=12)
    request_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_valid_active_vat: bool = Field(...)
    trader_name: Optional[str] = Field("UNKNOWN", description="Legal name in registry records.")
    trader_address: Optional[str] = Field("UNKNOWN", description="Registered physical operational address.")
    vies_consultation_id: Optional[str] = Field("LOCAL_FALLBACK_ERR", description="Unique legal audit trail token.")
