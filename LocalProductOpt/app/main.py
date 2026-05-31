from fastapi import FastAPI

from app.models import RawProductInput, ShopwareProductOutput

app = FastAPI(
    title="Local Product Optimizer API",
    description="Local Python microservice for GDPR-compliant Shopware SEO optimization",
    version="1.0.0",
)


@app.post("/optimize", response_model=ShopwareProductOutput)
def optimize_product(payload: RawProductInput):
    return ShopwareProductOutput(
        metaTitle=f"Kaufen Sie {payload.name} online | Ihr Shop",
        name=payload.name.strip().title(),
        description=f"<p>{payload.description.strip()}</p>",
        metaDescription=payload.description[:150].strip(),
    )
