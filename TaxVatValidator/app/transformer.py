import re
from typing import Any, Final

REGEX_GERMAN_VAT: Final[re.Pattern] = re.compile(r"^DE\d{9}$")

# spaces, dashes, periods, underscores
REGEX_SANITY_STRIP: Final[re.Pattern] = re.compile(r"[\s\-\._]+")


def sanitize_vat_id(raw_id: Any) -> str:
    if not isinstance(raw_id, str):
        return ""

    purged_string = REGEX_SANITY_STRIP.sub("", raw_id)
    return purged_string.strip().upper()


def validate_german_format(sanitized_id: str) -> bool:
    return bool(REGEX_GERMAN_VAT.match(sanitized_id))
