import json
from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_optimize_product_success():
    content_data = {
        "name": "name for test",
        "description": "<p>Winter boots.</p>",
        "metaTitle": "title for meta",
        "metaDescription": "Description text for meta",
    }
    mock_ollama_response = {
        "message": {
            "content": json.dumps(content_data)
        }
    }

    with patch("ollama.chat", return_model=mock_ollama_response) as mock_chat:
        payload = {
            "sku": "SW-12345",
            "name": "leather boots waterproof basic black",
            "description": "good boots for winter weather. made of leather. keep feet dry.",
            "keywords": ["Hiking shoes", "name"],
        }

        response = client.post("/optimize", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "name for test"
        assert "<p>" in data["description"]
        assert "metaTitle" in data
        mock_chat.assert_called_once()
