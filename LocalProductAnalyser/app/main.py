import json
import ollama
from models import ReviewAnalysis
from transformer import create_analysis_prompt


MODEL = "llama3"


mock_reviews = [
    "Ich liebe dieses Produkt! Die Qualität ist hoch und der Versand war schnell.",
    "Der Artikel kam leider komplett kaputt an. Absolut enttäuschend."
]


def analyze_review(review_text: str):
    messages = create_analysis_prompt(review_text)
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format="json"
    )
    data = json.loads(response["message"]["content"])
    return ReviewAnalysis(**data)


def main():

    print(f"Processing {len(mock_reviews)} reviews...\n")
    for idx, review in enumerate(mock_reviews, 1):
        print(f"--- Review #{idx} ---")
        result = analyze_review(review)
        print(f"score: {result.score}/5")
        print(f"Topics: {result.topics}")
        print(f"Severe: {result.is_urgent}")

        if result.is_urgent and result.issue_reason:

            filename = f"ticket_reply_{idx}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(
                    "Sehr geehrter Kunde,\n\n"
                    "wir entschuldigen uns für das Problem.\n\n"
                    f"Issue: {result.issue_reason}\n"
                )

            print(f"Ticket saved: {filename}")



if __name__ == "__main__":
    main()