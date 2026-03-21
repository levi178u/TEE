import requests
import sys
import time
import json

# from server.test_api import print_answer


BASE_URL = "http://127.0.0.1:8000"
def ask(code_id: str, session_id: str, question: str, label: str = "") -> dict | None:
    tag = f"  ❓ {label + ': ' if label else ''}{question}"
    print(tag)
    try:
        res = requests.post(
            f"{BASE_URL}/chat",
            json={"code_id": code_id, "session_id": session_id, "question": question},
            timeout=60,
        )
        res.raise_for_status()
        data = res.json()
        print(f"  ✅ Answer received: {data['answer']}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Chat request failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"     Server: {e.response.text}")
        return None

print(
    ask(
        "replace-with-code-id",
        "04af6c59-e14f-4339-b2e6-5b9abb3d770c",
        "What is the meaning of life?",
        label="Test Question",
    )
)