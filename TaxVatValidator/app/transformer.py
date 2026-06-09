import re
from typing import Dict, Any, Final

#Prefix 'DE' + exactly 9 digits
REGEX_GERMAN_VAT: Final[re.Pattern] = re.compile(r"^DE\d{9}$")

#tabs, dashes, dots, spaces
REGEX_SANITY_STRIP: Final[re.Pattern] = re.compile(r"[\s\-\._]+")


def sanitize_vat_id(raw_id: Any) -> str:
    if not isinstance(raw_id, str):
        return ""
    
    purged_string = REGEX_SANITY_STRIP.sub("", raw_id)
    return purged_string.strip().upper()


def validate_german_format(sanitized_id: str) -> bool:
    return bool(REGEX_GERMAN_VAT.match(sanitized_id))


def transform_and_analyze(raw_id: str) -> Dict[str, Any]:
    cleaned = sanitize_vat_id(raw_id)
    is_valid_de = validate_german_format(cleaned)
    
    country_prefix = cleaned[:2] if len(cleaned) >= 2 and cleaned[:2].isalpha() else "UNKNOWN"
    
    return {
        "input_raw": raw_id,
        "input_sanitized": cleaned,
        "country_prefix": country_prefix,
        "is_structurally_valid_de": is_valid_de,
        "requires_network_dispatch": is_valid_de
    }
