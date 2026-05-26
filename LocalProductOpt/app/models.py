from typing import Optional, List
from pydantic import BaseModel, Field

class RawProductInput(BaseModel):
    sku: str = Field(..., description="Unique Shopware product number/SKU")
    name: str = Field(..., description="Original raw product title")
    description: str = Field(..., description="Unoptimized raw text description")
    keywords: Optional[List[str]] = Field(default=[], description="Target SEO keywords to inject")

class ShopwareProductOutput(BaseModel):
    name: str = Field(..., max_length=255, description="SEO-optimized product title")
    description: str = Field(..., description="GDPR-compliant, SEO-optimized HTML/Text description")
    meta_title: Optional[str] = Field(None, max_length=255, alias="metaTitle", description="Shopware meta title tag")
    meta_description: Optional[str] = Field(None, max_length=255, alias="metaDescription", description="Shopware meta description tag")

    class Config:
        populate_by_name = True