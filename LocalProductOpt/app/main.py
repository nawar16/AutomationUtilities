import json
from fastapi import FastAPI, HTTPException
import ollama
from app.models import RawProductInput, ShopwareProductOutput

app = FastAPI(
    title="Local Product Optimizer API",
    description="Local Python microservice for GDPR-compliant Shopware SEO optimization",
    version="1.0.0",
)
MODEL_NAME = "llama3"
SYSTEM_PROMPT = """
You are an expert e-commerce SEO copywriter specializing in the German market and Shopware 6 platforms.
Your task is to optimize the provided raw product information into clean, high-converting German content.

Strict Output Rules:
1. You must respond exclusively in valid JSON. Do not include markdown formatting like ```json or any conversational greetings.
2. All string values must be purely in high-quality German.
3. Your output JSON must precisely follow this schema keys:
   - name: A catchy, SEO-optimized product title max 255 chars.
   - description: A detailed, persuasive product description wrapped in clean HTML paragraphs (<p>).
   - metaTitle: A professional search engine title tag max 255 chars.
   - metaDescription: A compact search summary capturing search intent max 255 chars.
"""
@app.post("/optimize", response_model=ShopwareProductOutput)
async def optimize_product(payload: RawProductInput):
    user_content = f"SKU: {payload.sku}\nName: {payload.name}\nDescription: {payload.description}\nKeywords: {', '.join(payload.keywords or [])}"
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            options={"temperature": 0.3},
            format="json"
        )
        
        ai_data = json.loads(response['message']['content'])
        return ShopwareProductOutput(**ai_data)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"LLM generated invalid JSON structures: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local AI inference node pipeline error: {str(e)}")
