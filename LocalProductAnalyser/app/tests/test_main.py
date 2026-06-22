import main


class FakeOllama:
    def chat(self, model, messages, format=None):
        return {
            "message": {
                "content": """
                {
                    "score": 2,
                    "topics": ["shipping"],
                    "review_extracted": ["kaputt"],
                    "is_urgent": true,
                    "issue_reason": "Product arrived damaged"
                }
                """
            }
        }


def test_main_runs(monkeypatch):
    monkeypatch.setattr(main, "ollama", FakeOllama())
    main.main()
