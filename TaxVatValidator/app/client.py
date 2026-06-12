import logging
import re

import httpx

from app.models import TaxAuthorityResponse

EU_VIES_URL = "https://europa.eu"
DE_BZST_URL = "https://bzst.de"

logger = logging.getLogger("VATClient")


class AsyncTaxClient:
    def __init__(self, timeout_seconds: float = 5.0):
        self.limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.timeout = httpx.Timeout(timeout_seconds)

    async def query_eu_vies(
        self, client: httpx.AsyncClient, country_code: str, vat_number: str
    ) -> TaxAuthorityResponse:
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
                    vies_consultation_id=data.get("requestIdentifier"),
                )
        except Exception as err:
            logger.error(f"VIES Request Failure on {country_code}{vat_number}: {str(err)}")

        return TaxAuthorityResponse(country_code=country_code, vat_number=vat_number, is_valid_active_vat=False)

    async def query_german_bzst(self, client: httpx.AsyncClient, vat_number: str) -> TaxAuthorityResponse:
        params = {
            "UstId_1": "DE123456789",  # Shopware ref id
            "UstId_2": vat_number,
            "Firmenname": "",
            "Ort": "",
            "PLZ": "",
            "Strasse": "",
        }
        try:
            response = await client.get(DE_BZST_URL, params=params, timeout=self.timeout)
            if response.status_code == 200:
                text_data = response.text
                valid_match = re.search(r"<ErrorCode>(\d+)</ErrorCode>", text_data)
                is_valid = bool(valid_match and valid_match.group(1) == "200")

                return TaxAuthorityResponse(
                    country_code="DE",
                    vat_number=vat_number,
                    is_valid_active_vat=is_valid,
                    vies_consultation_id=f"BZST-REF-{valid_match.group(1) if valid_match else 'ERR'}",
                )
        except Exception as err:
            logger.error(f"BZSt Remote Connection Error on DE{vat_number}: {str(err)}")

        return TaxAuthorityResponse(country_code="DE", vat_number=vat_number, is_valid_active_vat=False)

    async def dispatch_validation(self, client: httpx.AsyncClient, sanitized_id: str) -> TaxAuthorityResponse:
        country_code = sanitized_id[:2]
        vat_number = sanitized_id[2:]

        if country_code == "DE":
            return await self.query_german_bzst(client, vat_number)
        return await self.query_eu_vies(client, country_code, vat_number)
