import re


def sanitize_html(raw_html: str) -> str:

    if not raw_html:
        return ""

    clean_text = re.sub(r"```[a-zA-Z]*", "", raw_html)
    clean_text = clean_text.replace("```", "").strip()

    safe_tags = ["p", "br", "strong", "b", "u", "em", "ul", "ol", "li"]
    tag_pattern = re.compile(r"</?([a-zA-Z0-9]+)\b[^>]*>")

    def replace_tag(match):
        tag_name = match.group(1).lower()
        if tag_name in safe_tags:
            return f"<{tag_name}>" if not match.group(0).startswith("</") else f"</{tag_name}>"
        return ""

    return tag_pattern.sub(replace_tag, clean_text)


def serialize_for_shopware(sku: str, optimized_data: dict, tax_id: str, price: float = 0.0) -> dict:

    clean_description = sanitize_html(optimized_data.get("description", ""))

    return {
        "productNumber": sku,
        "stock": 0,  # default to 0 on initial sync
        "name": optimized_data.get("name", "").strip()[:255],
        "description": clean_description,
        "metaTitle": optimized_data.get("metaTitle", "").strip()[:255],
        "metaDescription": optimized_data.get("metaDescription", "").strip()[:255],
        # Shopware 6 strictly requires a valid UUID mapping for Tax objects
        "taxId": tax_id,
        "price": [
            {
                "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",  # for Euro
                "gross": price,
                "net": price / 1.19,  # 19% MwSt.
                "linked": True,
            }
        ],
    }
