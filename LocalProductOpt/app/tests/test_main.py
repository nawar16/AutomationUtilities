import json
from unittest.mock import patch

from app.main import app
from app.transformer import sanitize_html, serialize_for_shopware
from fastapi.testclient import TestClient

client = TestClient(app)


def test_optimize_product_success():
    content_data = {
        "name": "Wasserdichte Leder-Winterstiefel - Klassisch Schwarz",
        "description": (
            "<p>Machen Sie sich bereit für die kalte Jahreszeit. Unsere "
            "hochwertigen Winterstiefel aus echtem Leder bieten optimalen Schutz "
            "vor Nässe und Kälte. Dank der robusten Profilsohle haben Sie "
            "jederzeit sicheren Halt auf Schnee und Eis.</p>"
        ),
        "metaTitle": "Wasserdichte Leder-Winterstiefel in Schwarz kaufen",
        "metaDescription": "Entdecken Sie robuste Herren- und Damen-Winterstiefel aus echtem Leder.",
    }

    mock_ollama_response = {"message": {"content": json.dumps(content_data)}}

    with patch("ollama.chat", return_value=mock_ollama_response) as mock_chat:
        payload = {
            "sku": "SW-12345",
            "name": "leather boots waterproof basic black",
            "description": "good boots for winter weather. made of leather. keep feet dry.",
            "keywords": ["Hiking shoes", "name"],
        }

        response = client.post("/optimize", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Wasserdichte Leder-Winterstiefel - Klassisch Schwarz"
        assert "<p>" in data["description"]
        assert "metaTitle" in data
        mock_chat.assert_called_once()


def test_html_sanitization_strips_markdown():
    dirty_html = "```html <p>Hier ist ein <strong>Gurt</strong></p> <script>alert(1)</script>```"
    clean_html = sanitize_html(dirty_html)
    assert "```" not in clean_html
    assert "<script>" not in clean_html
    assert "<p>Hier ist ein <strong>Gurt</strong></p>" in clean_html


def test_serialize_for_shopware_pricing_math():
    mock_data = {"name": "Test", "description": "<p>Test</p>"}
    payload = serialize_for_shopware(sku="SW1", optimized_data=mock_data, tax_id="tax-uuid", price=119.00)

    assert payload["price"][0]["net"] == 100.00
    assert payload["productNumber"] == "SW1"
    assert payload["taxId"] == "tax-uuid"


def test_shopware_payload_endpoint():

    content_data = {
        "name": "Schuhe",
        "description": "```html <p>Schöne Schuhe.</p> ```",
        "metaTitle": "Schuhe",
        "metaDescription": "Schuhe",
    }

    mock_ollama_response = {"message": {"content": json.dumps(content_data)}}

    with patch("ollama.chat", return_model=mock_ollama_response):
        payload = {"sku": "SW-100", "name": "shoes", "description": "old shoes", "price": 59.50, "taxId": "my-tax-id"}
        response = client.post("/optimize/shopware-payload", json=payload)
        assert response.status_code == 200

        outer_data = response.json()
        shopware_data = outer_data["shopware_api_payload"]

        assert shopware_data["productNumber"] == "SW-100"
        assert "```" not in shopware_data["description"]  # automated transformation ran
        assert shopware_data["price"][0]["gross"] == 59.50
