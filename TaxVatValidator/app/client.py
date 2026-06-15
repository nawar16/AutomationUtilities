import asyncio
import logging
import re

import httpx

from app.exceptions import TaxAuthorityNetworkError
from app.models import TaxAuthorityResponse

EU_VIES_URL = "https://europa.eu"
DE_BZST_URL = "https://bzst.de"

logger = logging.getLogger("VATClient")


class AsyncTaxClient:
    def __init__(self, timeout_seconds: float = 6.0, max_retries: int = 3):
        self.limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_retries = max_retries

    async def execute_with_backoff(self, func, *args, **kwargs):
        attempt = 0
        backoff_delay = 1.0

        while attempt < self.max_retries:
            try:
                return await func(*args, **kwargs)
            except (httpx.NetworkError, httpx.TimeoutException) as exc:
                attempt += 1
                logger.warning(
                    f"Network error detected (Attempt {attempt}/{self.max_retries})."
                    f"Retrying in {backoff_delay}s... Error: {str(exc)}"
                )
                if attempt >= self.max_retries:
                    raise TaxAuthorityNetworkError(f"Connection permanently lost after {attempt} attempts") from exc
                await asyncio.sleep(backoff_delay)
                backoff_delay *= 2.0

    async def query_eu_vies(
        self, client: httpx.AsyncClient, country_code: str, vat_number: str
    ) -> TaxAuthorityResponse:
        payload = {"countryCode": country_code, "vatNumber": vat_number}
        response = await client.post(EU_VIES_URL, json=payload, timeout=self.timeout)
        if response.status_code != 200:
            raise TaxAuthorityNetworkError(f"EU VIES API returned bad status code: {response.status_code}")

        data = response.json()
        return TaxAuthorityResponse(
            country_code=country_code,
            vat_number=vat_number,
            is_valid_active_vat=data.get("isValid", False),
            trader_name=data.get("name"),
            trader_address=data.get("address"),
            vies_consultation_id=data.get("requestIdentifier"),
        )

    async def query_german_bzst(self, client: httpx.AsyncClient, vat_number: str) -> TaxAuthorityResponse:
        params = {
            "UstId_1": "DE123456789",  # Shopware ref id
            "UstId_2": vat_number,
            "Firmenname": "",
            "Ort": "",
            "PLZ": "",
            "Strasse": "",
        }
        response = await client.get(DE_BZST_URL, params=params, timeout=self.timeout)
        if response.status_code != 200:
            raise TaxAuthorityNetworkError(f"German BZSt API returned bad status code: {response.status_code}")

        text_data = response.text
        valid_match = re.search(r"<ErrorCode>(\d+)</ErrorCode>", text_data)
        is_valid = bool(valid_match and valid_match.group(1) == "200")
        return TaxAuthorityResponse(
            country_code="DE",
            vat_number=vat_number,
            is_valid_active_vat=is_valid,
            vies_consultation_id=f"BZST-REF-{valid_match.group(1) if valid_match else 'ERR'}",
        )

    async def dispatch_validation(self, client: httpx.AsyncClient, sanitized_id: str) -> TaxAuthorityResponse:
        country_code = sanitized_id[:2]
        vat_number = sanitized_id[2:]
        try:
            if country_code == "DE":
                return await self.execute_with_backoff(self.query_german_bzst, client, vat_number)
            return await self.execute_with_backoff(self.query_eu_vies, client, country_code, vat_number)
        except TaxAuthorityNetworkError as network_exc:
            logger.error(f"Failing network tracking loop on item {sanitized_id}: {str(network_exc)}")
            # negative response with normal structure so the pipeline donot crash
            return TaxAuthorityResponse(
                country_code=country_code,
                vat_number=vat_number,
                is_valid_active_vat=False,
                vies_consultation_id="NETWORK_TIMEOUT_FAILURE_RETRY_EXHAUSTED",
            )
