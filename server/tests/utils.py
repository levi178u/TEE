"""
tests/utils.py
Shared helpers used by every test file.
"""
import sys
import time
import json
import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_INIT = 120   # /init can take a while (embeddings)
TIMEOUT_CHAT = 60
TIMEOUT_FAST = 10
SESSION_CODE_IDS: dict[str, str] = {}

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg): print(f"  {RED}❌ {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}⚠️  {msg}{RESET}")
def info(msg): print(f"  {CYAN}ℹ️  {msg}{RESET}")

def section(title: str):
    bar = "═" * 62
    print(f"\n{BOLD}{BLUE}{bar}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{bar}{RESET}")

def subsection(title: str):
    print(f"\n  {BOLD}── {title} ──{RESET}")

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def get(path: str, timeout: int = TIMEOUT_FAST) -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        fail(f"GET {path} → {e}")
        return None

def post(path: str, payload: dict, timeout: int = TIMEOUT_CHAT) -> dict | None:
    # Keep tests backward compatible by auto-attaching code_id for /chat calls.
    if path == "/chat" and "code_id" not in payload and payload.get("session_id"):
        session_id = payload["session_id"]
        code_id = SESSION_CODE_IDS.get(session_id)
        if code_id:
            payload = {**payload, "code_id": code_id}

    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        fail(f"POST {path} HTTP {e.response.status_code} → {e.response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        fail(f"POST {path} → {e}")
        return None

def delete(path: str, timeout: int = TIMEOUT_FAST) -> dict | None:
    try:
        r = requests.delete(f"{BASE_URL}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        fail(f"DELETE {path} → {e}")
        return None

# ── Session helpers ───────────────────────────────────────────────────────────

def init_session(
    repo_name: str | None = None,
    code_id: str | None = None,
    llm_type: str = "groq",
    label: str | None = None,
) -> str | None:
    chosen_code_id = code_id or get_code_id_for_repo(repo_name)
    if not chosen_code_id:
        fail(f"No code_id available for repo '{repo_name}'")
        return None

    payload: dict = {"llm_type": llm_type, "code_id": chosen_code_id}
    if repo_name:
        payload["repo_name"] = repo_name
    display = label or repo_name or "ALL repos"
    info(f"Initialising [{display}] with {llm_type.upper()} (code_id={chosen_code_id}) ...")
    data = post("/init", payload, timeout=TIMEOUT_INIT)
    if not data:
        return None
    sid = data.get("session_id")
    if sid:
        SESSION_CODE_IDS[sid] = chosen_code_id
    ok(f"Session ready — {sid}  |  docs: {data.get('doc_count', '?')}")
    return sid

def cleanup_session(session_id: str):
    if session_id:
        SESSION_CODE_IDS.pop(session_id, None)
        delete(f"/session/{session_id}")

# ── Chat helper ───────────────────────────────────────────────────────────────

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def record(self, passed: bool):
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> str:
        total = self.passed + self.failed + self.skipped
        colour = GREEN if self.failed == 0 else RED
        return (f"{colour}{BOLD}{self.passed}/{total} passed"
                f"{' ⚠ ' + str(self.failed) + ' failed' if self.failed else ''}{RESET}")


def ask(
    session_id: str,
    question: str,
    label: str = "",
    expect_sources: bool = False,
    expect_keywords: list[str] | None = None,
    result_tracker: TestResult | None = None,
) -> dict | None:
    """
    Post a question and pretty-print the response.
    Optionally assert sources exist and/or keywords appear in the answer.
    Returns the raw response dict.
    """
    tag = f"[{label}] " if label else ""
    print(f"\n  {BOLD}❓ {tag}{question}{RESET}")

    data = post("/chat", {"session_id": session_id, "question": question})
    if not data:
        if result_tracker:
            result_tracker.record(False)
        return None

    answer = data.get("answer", "")
    sources = data.get("sources", [])
    history_len = len(data.get("chat_history", []))

    # Print answer (truncate very long ones in test output)
    display_answer = answer if len(answer) <= 600 else answer[:600] + " …[truncated]"
    print(f"\n  🤖 {display_answer}")

    # Print sources
    if sources:
        print(f"\n  📎 Sources ({len(sources)}):")
        seen = set()
        for s in sources:
            src = s.get("source", s.get("filename", "?"))
            if src not in seen:
                lang = s.get("language", "?")
                repo = s.get("repo_name", "?")
                score = s.get("similarity_score")
                score_str = f"  score={score:.3f}" if score is not None else ""
                print(f"     • [{lang}] {src}  repo:{repo}{score_str}")
                seen.add(src)
    else:
        warn("No sources returned.")

    print(f"  🧠 History length: {history_len}")

    # Assertions
    passed = True
    if expect_sources and not sources:
        fail(f"Expected sources but got none for: {question}")
        passed = False
    if expect_keywords:
        missing = [kw for kw in expect_keywords if kw.lower() not in answer.lower()]
        if missing:
            fail(f"Answer missing expected keywords: {missing}")
            passed = False
        else:
            ok(f"All expected keywords found: {expect_keywords}")

    if result_tracker:
        result_tracker.record(passed)
    elif passed:
        ok("Answer received")

    time.sleep(0.4)   # be polite to the API
    return data


def require_server():
    """Exit immediately if the server is not reachable."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        r.raise_for_status()
    except Exception as e:
        fail(f"Server unreachable at {BASE_URL}: {e}")
        print("  Run:  docker compose up -d")
        sys.exit(1)


def get_repos() -> list[str]:
    data = get("/repos")
    if not data:
        return []
    repos = data.get("repos", [])
    if not repos:
        warn("No repos in DB — did you run the seed?")
    return repos


def get_code_id_items(repo_name: str | None = None) -> list[dict]:
    query = ""
    if repo_name:
        query = f"?repo_name={repo_name}"
    data = get(f"/code-ids{query}")
    if not data:
        return []
    return data.get("items", [])


def get_code_id_for_repo(repo_name: str | None = None) -> str | None:
    items = get_code_id_items(repo_name=repo_name)
    if items:
        return items[0].get("code_id")
    return None
