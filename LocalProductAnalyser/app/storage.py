import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REVIEWS_PATH = BASE_DIR / "reviews" / "reviews.json"

OUTPUT_DIR = BASE_DIR / "outputs"
ANALYSIS_PATH = OUTPUT_DIR / "analysis.json"
TICKET_PATH = OUTPUT_DIR / "ticket_reply.txt"


def init_storage():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_reviews():
    if not REVIEWS_PATH.exists():
        raise FileNotFoundError(f"Missing file: {REVIEWS_PATH}")

    with open(REVIEWS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_analysis(results):
    with open(ANALYSIS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def save_ticket(text: str):
    with open(TICKET_PATH, "w", encoding="utf-8") as f:
        f.write(text)
