import os

import requests
from dotenv import load_dotenv

load_dotenv()

SHOPWARE_URL = os.getenv("SHOPWARE_URL")
CLIENT_ID = os.getenv("SHOPWARE_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPWARE_CLIENT_SECRET")


def get_access_token():
    url = f"{SHOPWARE_URL}/api/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]


def load_reviews():
    token = get_access_token()

    url = f"{SHOPWARE_URL}/api/product-review"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()

    reviews = []

    for item in data.get("data", []):
        reviews.append({"id": item["id"], "text": item["attributes"]["content"]})

    return reviews


# def update_review_metadata():

# def create_support_note():
