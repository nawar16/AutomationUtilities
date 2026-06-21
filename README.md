# Automation Utilities 

A main repository containing AI microservices, automation pipelines, and compliance tools.


### 1. Local Product Optimizer (`LocalProductOpt`)
A self-hosted, **GDPR-compliant** e-commerce microservice designed to automate SEO text optimization using local AI for **Shopware** frameworks locally.

* **Tech Stack:** Python, FastAPI, Pydantic v2, Ollama (Local LLM)
* **Local Run Command:** 
  docker compose up --build


### 2. Tax VAT Validator (`TaxVatValidator`)
An asynchronous, decoupled corporate compliance utility aim to handle high-speed, parallel validation of European B2B VAT IDs against official EU VIES and BZSt government APIs.


* **Tech Stack:** Python, Asyncio, HTTPX, Pydantic v2, Pytest
* **Execution Command:** 
  python -m app.main --input data/input_batch.csv --output verification_receipts.json

### 3. Local Product Reviews Analyzer (`LocalProductAnalyzer`)
A self-hosted, e-commerce microservice designed to extract insights from product reviews and automatically flag urgent issues for customer support.


* **Tech Stack:** Python, Pydantic v2, Ollama, Pytest


