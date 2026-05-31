import json
from unittest.mock import patch

from app.main import app
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
        "metaDescription": "Entdecken Sie robuste Herren- und Damen-Winterstiefel aus echtem Leder. Wasserdicht, warm gefüttert und ideal für winterliche Bedingungen.",
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
