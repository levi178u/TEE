import requests
import sys
import time
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION_CODE_IDS: dict[str, str] = {}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def print_section(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")

def print_answer(chat_data: dict):
    answer = chat_data.get("answer", "No answer.")
    print(f"\n  🤖 Answer:\n  {answer}")

    sources = chat_data.get("sources", [])
    if sources:
        print(f"\n  📎 Sources ({len(sources)}):")
        for s in sources:
            lang = s.get("language", "?")
            filename = s.get("filename", "?")
            route = s.get("route", "?")
            repo = s.get("repo_name", "?")
            print(f"     • [{lang}] {filename}  →  {route}  (repo: {repo})")
    else:
        print("  📎 Sources: none returned")

    history = chat_data.get("chat_history", [])
    print(f"\n  🧠 Chat history length: {len(history)} message(s)")

def get_code_id(repo_name: str | None = None) -> str | None:
    try:
        suffix = f"?repo_name={repo_name}" if repo_name else ""
        res = requests.get(f"{BASE_URL}/code-ids{suffix}", timeout=10)
        res.raise_for_status()
        items = res.json().get("items", [])
        if not items:
            return None
        return items[0].get("code_id")
    except requests.exceptions.RequestException:
        return None


def ask(session_id: str, question: str, label: str = "") -> dict | None:
    tag = f"  ❓ {label + ': ' if label else ''}{question}"
    print(tag)
    code_id = SESSION_CODE_IDS.get(session_id)
    if not code_id:
        print(f"  ❌ Missing code_id for session {session_id}")
        return None
    try:
        res = requests.post(
            f"{BASE_URL}/chat",
            json={"code_id": code_id, "session_id": session_id, "question": question},
            timeout=60,
        )
        res.raise_for_status()
        data = res.json()
        print_answer(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Chat request failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"     Server: {e.response.text}")
        return None

def init_session(repo_name: str | None = None, llm_type: str = "groq") -> str | None:
    code_id = get_code_id(repo_name)
    if not code_id:
        print(f"  ❌ No code_id found for repo '{repo_name}'")
        return None

    payload: dict = {"llm_type": llm_type, "code_id": code_id}
    if repo_name:
        payload["repo_name"] = repo_name
    label = repo_name or "ALL repos"
    print(f"\n  ⏳ Initialising session for [{label}] with {llm_type.upper()} ...")
    try:
        res = requests.post(f"{BASE_URL}/init", json=payload, timeout=120)
        res.raise_for_status()
        data = res.json()
        sid = data["session_id"]
        SESSION_CODE_IDS[sid] = code_id
        print(f"  ✅ Session ready — ID: {sid}  |  docs indexed: {data.get('doc_count', '?')}")
        return sid
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Init failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"     Server: {e.response.text}")
        return None

def delete_session(session_id: str):
    try:
        res = requests.delete(f"{BASE_URL}/session/{session_id}", timeout=10)
        res.raise_for_status()
        SESSION_CODE_IDS.pop(session_id, None)
        print(f"  🗑  Session {session_id} deleted.")
    except Exception:
        pass

# ─── Test Suites ──────────────────────────────────────────────────────────────

def test_health():
    print_section("TEST 0 — Health & Root")
    for path in ["/health", "/"]:
        try:
            res = requests.get(f"{BASE_URL}{path}", timeout=5)
            res.raise_for_status()
            print(f"  ✅ GET {path} → {res.json()}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ GET {path} failed: {e}")
            sys.exit(1)


def test_repos():
    print_section("TEST 1 — Available Repositories")
    try:
        res = requests.get(f"{BASE_URL}/repos", timeout=10)
        res.raise_for_status()
        repos = res.json().get("repos", [])
        if repos:
            print(f"  ✅ {len(repos)} repo(s) found:")
            for r in repos:
                print(f"     • {r}")
        else:
            print("  ⚠️  No repos found — did you run the seed?")
        return repos
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed: {e}")
        return []


def test_general_questions(session_id: str):
    """Questions that should work regardless of which repo is loaded."""
    print_section("TEST 2 — General Repository Questions")

    questions = [
        ("overview",       "Give me a high-level overview of this codebase."),
        ("purpose",        "What is the main purpose of this project?"),
        ("structure",      "Describe the overall project structure and folder layout."),
        ("entry_point",    "What is the entry point of this application?"),
        ("languages",      "What programming languages are used in this repository?"),
        ("dependencies",   "What are the key external libraries or dependencies used?"),
        ("config_files",   "Are there any configuration files? What do they configure?"),
        ("run_project",    "How do I set up and run this project locally?"),
        ("env_vars",       "What environment variables does this project require?"),
        ("architecture",   "Explain the high-level architecture of this project."),
    ]

    passed = 0
    for label, q in questions:
        result = ask(session_id, q, label)
        if result and result.get("answer"):
            passed += 1
        time.sleep(0.5)

    print(f"\n  📊 General questions: {passed}/{len(questions)} answered")


def test_next_saas_starter(session_id: str):
    """Deep-dive questions specific to the next-saas-starter repo."""
    print_section("TEST 3 — next-saas-starter: Architecture & Code Questions")

    questions = [
        ("auth_setup",       "How is authentication implemented in this repo?"),
        ("auth_providers",   "Which OAuth providers are configured?"),
        ("prisma_client",    "How is the Prisma client initialised and exported?"),
        ("dashboard_page",   "What does the dashboard page do and how does it protect routes?"),
        ("session_check",    "How does the app check if a user is logged in?"),
        ("redirect_logic",   "What happens when an unauthenticated user visits the dashboard?"),
        ("css_framework",    "What CSS framework is used and how is it configured?"),
        ("db_adapter",       "How is the database adapter connected to NextAuth?"),
        ("global_styles",    "What global styles or CSS variables are defined?"),
        ("env_required",     "What environment variables are required for this project to work?"),
        ("file_roles",       "What is the role of auth.ts vs prisma.ts in this project?"),
        ("memory_follow_up", "Based on what you just told me about auth.ts, how would I add a Google OAuth provider?"),
    ]

    passed = 0
    for label, q in questions:
        result = ask(session_id, q, label)
        if result and result.get("answer"):
            passed += 1
        time.sleep(0.5)

    print(f"\n  📊 next-saas-starter questions: {passed}/{len(questions)} answered")


def test_rust_http_server(session_id: str):
    """Deep-dive questions specific to the rust-http-server repo."""
    print_section("TEST 4 — rust-http-server: Architecture & Code Questions")

    questions = [
        ("overview",         "What does this Rust HTTP server do?"),
        ("async_runtime",    "What async runtime does this project use and why?"),
        ("request_handler",  "Explain the handle() function — what does it do?"),
        ("server_startup",   "How is the server started and what address does it bind to?"),
        ("dependencies",     "What crates are listed in Cargo.toml and what are they for?"),
        ("run_command",      "How do I build and run this project?"),
        ("response_format",  "What does the server return for every request right now?"),
        ("extend_routes",    "How would I add a new route to this server based on the current code?"),
        ("tokio_main",       "What is the purpose of the #[tokio::main] macro?"),
        ("readme_summary",   "Summarise what the README says about this project."),
        ("memory_follow_up", "You mentioned Tokio earlier — what version of Tokio is specified in Cargo.toml?"),
    ]

    passed = 0
    for label, q in questions:
        result = ask(session_id, q, label)
        if result and result.get("answer"):
            passed += 1
        time.sleep(0.5)

    print(f"\n  📊 rust-http-server questions: {passed}/{len(questions)} answered")


def test_go_microservices(session_id: str):
    """Deep-dive questions specific to the go-microservices repo."""
    print_section("TEST 5 — go-microservices: Architecture & Code Questions")

    questions = [
        ("overview",         "What is the purpose of the go-microservices project?"),
        ("health_endpoint",  "What does the /health endpoint return and how is it implemented?"),
        ("http_router",      "What HTTP router or mux is used in this project?"),
        ("server_port",      "What port does the server listen on?"),
        ("docker_services",  "What services are defined in docker-compose.yml?"),
        ("postgres_config",  "How is the Postgres database configured in Docker?"),
        ("env_vars",         "What environment variables are set for the API service in Docker?"),
        ("run_locally",      "How would I start this application locally using Docker?"),
        ("extend_api",       "Based on the current code, how would I add a new /users endpoint?"),
        ("architecture",     "Describe the overall architecture — how do the services interact?"),
        ("memory_follow_up", "You mentioned the API service earlier — what image does it build from?"),
    ]

    passed = 0
    for label, q in questions:
        result = ask(session_id, q, label)
        if result and result.get("answer"):
            passed += 1
        time.sleep(0.5)

    print(f"\n  📊 go-microservices questions: {passed}/{len(questions)} answered")


def test_cross_repo(session_id: str):
    """Questions that compare or span across all repos (all-repos session only)."""
    print_section("TEST 6 — Cross-Repo Comparison Questions (all repos loaded)")

    questions = [
        ("lang_compare",    "Which repos use TypeScript and which use other languages?"),
        ("web_servers",     "Which repos implement an HTTP server? How do they differ?"),
        ("docker_usage",    "Which repos use Docker? What do their Docker configs do?"),
        ("db_usage",        "Which repos interact with a database?"),
        ("auth_repos",      "Which repo handles user authentication?"),
        ("simplest_repo",   "Which repository has the simplest codebase and why?"),
        ("readme_presence", "Which repos have a README file?"),
        ("async_patterns",  "Which repos use async programming patterns?"),
    ]

    passed = 0
    for label, q in questions:
        result = ask(session_id, q, label)
        if result and result.get("answer"):
            passed += 1
        time.sleep(0.5)

    print(f"\n  📊 Cross-repo questions: {passed}/{len(questions)} answered")


def test_conversational_memory(session_id: str):
    """Multi-turn conversation to verify memory is working."""
    print_section("TEST 7 — Conversational Memory (follow-up chain)")

    turns = [
        "What files are in this codebase?",
        "Which of those files is the most important one?",
        "Can you show me a summary of what that file contains?",
        "What would happen if that file was removed?",
        "Based on everything we discussed, give me a one-paragraph summary of this project.",
    ]

    print("  Testing 5-turn conversation chain...\n")
    for i, q in enumerate(turns, 1):
        print(f"  Turn {i}/5:")
        result = ask(session_id, q)
        if not result:
            print(f"  ⚠️  Turn {i} failed — memory test may be incomplete")
        time.sleep(0.5)


def test_edge_cases(session_id: str):
    """Edge cases: out-of-scope, vague, and adversarial questions."""
    print_section("TEST 8 — Edge Cases & Hallucination Guardrails")

    cases = [
        ("out_of_scope",   "How do I configure a TCP Reno network simulation?"),
        ("vague",          "Tell me everything."),
        ("nonexistent",    "What does the calculate_quantum_flux() function do?"),
        ("unrelated",      "What is the capital of France?"),
        ("empty_followup", "What about the other thing?"),
    ]

    for label, q in cases:
        print(f"\n  [{label}]")
        ask(session_id, q)
        time.sleep(0.5)


def test_cache_init():
    """Test /init-from-cache reuses the saved FAISS index."""
    print_section("TEST 9 — Init From Cache")
    code_id = get_code_id()
    if not code_id:
        print("  ❌ Could not resolve a code_id for cache init test")
        return

    try:
        res = requests.post(
            f"{BASE_URL}/init-from-cache",
            json={"llm_type": "groq", "code_id": code_id},
            timeout=30,
        )
        res.raise_for_status()
        data = res.json()
        sid = data.get("session_id")
        if sid:
            SESSION_CODE_IDS[sid] = code_id
        print(f"  ✅ Cache init successful — session: {sid}")

        # Quick smoke test on the cached session
        ask(sid, "What is this codebase about?", "cache_smoke_test")
        delete_session(sid)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Cache init failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"     Server: {e.response.text}")


def test_sessions_and_cleanup(session_ids: list[str]):
    """Verify /sessions lists all active sessions, then clean up."""
    print_section("TEST 10 — Sessions List & Cleanup")
    try:
        res = requests.get(f"{BASE_URL}/sessions", timeout=10)
        res.raise_for_status()
        sessions = res.json().get("sessions", [])
        print(f"  ✅ Active sessions: {len(sessions)}")
        for s in sessions:
            print(f"     • {s.get('session_id')} | repo: {s.get('repo_name')} | llm: {s.get('llm_type')} | docs: {s.get('doc_count')}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed: {e}")

    print("\n  🧹 Cleaning up sessions...")
    for sid in session_ids:
        if sid:
            delete_session(sid)


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_tests():
    print("\n🐿️  Squirrel ChatBot — Full API Test Suite")
    print(f"    Target: {BASE_URL}\n")

    # 0. Basic connectivity
    test_health()

    # 1. What repos exist
    repos = test_repos()

    active_sessions: list[str] = []

    # ── Per-repo deep-dive sessions ──────────────────────────────────────────

    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            active_sessions.append(sid)
            test_general_questions(sid)
            test_next_saas_starter(sid)
            test_conversational_memory(sid)
            test_edge_cases(sid)

    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            active_sessions.append(sid)
            test_rust_http_server(sid)

    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            active_sessions.append(sid)
            test_go_microservices(sid)

    # ── All-repos session for cross-repo questions ───────────────────────────
    sid_all = init_session(repo_name=None)   # loads everything
    if sid_all:
        active_sessions.append(sid_all)
        test_cross_repo(sid_all)

    # ── Cache test ───────────────────────────────────────────────────────────
    test_cache_init()

    # ── Sessions list + cleanup ──────────────────────────────────────────────
    test_sessions_and_cleanup(active_sessions)

    print("\n\n🎉 Full test suite complete!\n")


if __name__ == "__main__":
    run_tests()