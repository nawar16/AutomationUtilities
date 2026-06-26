# Automation Utilities 

A main repository containing AI microservices, automation pipelines, and compliance tools.


![CI](https://github.com/nawar16/automationUtilities/actions/workflows/ci.yml/badge.svg)

### 1. Local Product Optimizer (`LocalProductOpt`)
Request-driven, self-hosted, GDPR-compliant AI microservice that generates SEO-optimized Shopware product content on demand. Designed for request-response workflows where Shopware submits product data and receives optimized content.

* **Tech Stack:** Python, FastAPI, Pydantic v2, Ollama (Local LLM)
* **Local Run Command:** 
  docker compose up --build


### 2. Tax VAT Validator (`TaxVatValidator`)
Command Script, asynchronous, decoupled corporate compliance utility aim to handle high-speed, parallel validation of European B2B VAT IDs against official EU VIES and BZSt government APIs.


* **Tech Stack:** Python, Asyncio, HTTPX, Pydantic v2, Pytest
* **Execution Command:** 
  python -m app.main --input data/input_batch.csv --output verification_receipts.json

### 3. Local Product Reviews Analyzer (`LocalProductAnalyzer`)
Batch-processing, self-hosted AI microservice that analyzes customer reviews and automatically identifies and escalates urgent support issues.

* **Tech Stack:** Python, Pydantic v2, Ollama, Pytest, requests, python-dotenv
* **Local Run Command:** 
python -m app.main --input reviews.json --output outputs/analysis.json
* **Run Command with Shopware:** 
python -m app.main --output outputs/analysis.json






