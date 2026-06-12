import re
import logging
import httpx
from app.models import TaxAuthorityResponse

EU_VIES_URL = "https://europa.eu"

logger = logging.getLogger("VATClient")

class AsyncTaxClient:
    def __init__(self, timeout_seconds: float = 5.0):
        self.limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.timeout = httpx.Timeout(timeout_seconds)

    async def query_eu_vies(self, client: httpx.AsyncClient, country_code: str, vat_number: str) -> TaxAuthorityResponse:
        payload = {"countryCode": country_code, "vatNumber": vat_number}
        try:
            response = await client.post(EU_VIES_URL, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return TaxAuthorityResponse(
                    country_code=country_code,
                    vat_number=vat_number,
                    is_valid_active_vat=data.get("isValid", False),
                    trader_name=data.get("name"),
                    trader_address=data.get("address"),
                    vies_consultation_id=data.get("requestIdentifier")
                )
        except Exception as err:
            logger.error(f"VIES Request Failure on {country_code}{vat_number}: {str(err)}")
            
        return TaxAuthorityResponse(country_code=country_code, vat_number=vat_number, is_valid_active_vat=False)
