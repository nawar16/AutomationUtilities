import json

import ollama
from models import ReviewAnalysis
from storage import load_reviews
from transformer import create_analysis_prompt

MODEL = "llama3"


reviews = load_reviews()


def analyze_review(review_text: str):
    messages = create_analysis_prompt(review_text)
    response = ollama.chat(model=MODEL, messages=messages, format="json")
    data = json.loads(response["message"]["content"])
    return ReviewAnalysis(**data)


def main():

    print(f"Processing {len(reviews)} reviews\n")
    for idx, review in enumerate(reviews, 1):
        print(f"--- Review #{idx} ---")
        result = analyze_review(review)
        print(f"score: {result.score}/5")
        print(f"Topics: {result.topics}")
        print(f"Severe: {result.is_urgent}")

        if result.is_urgent and result.issue_reason:
            filename = f"ticket_reply_{idx}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(
                    f"Sehr geehrter Kunde,\n\nwir entschuldigen uns für das Problem.\n\nIssue: {result.issue_reason}\n"
                )

            print(f"Ticket saved: {filename}")


if __name__ == "__main__":
    main()
