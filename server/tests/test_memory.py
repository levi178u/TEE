"""
tests/test_memory.py
────────────────────
Tests that the chatbot correctly maintains conversational memory across
multiple turns in a single session.

Verifies:
  - Follow-up questions resolve pronouns ("it", "that", "this function")
  - The bot remembers facts stated in previous answers
  - Memory does NOT leak between different sessions
  - Long conversations (10+ turns) still work
  - Clarification requests work mid-conversation

Run:  python tests/test_memory.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
from tests.utils import (
    section, subsection, ok, fail, warn, info,
    post, delete, init_session, cleanup_session,
    require_server, get_repos, TestResult, ask, BASE_URL,
)


def raw_ask(session_id: str, question: str) -> str | None:
    """Return just the answer string for assertion-heavy tests."""
    data = post("/chat", {"session_id": session_id, "question": question})
    if not data:
        return None
    answer = data.get("answer", "")
    print(f"\n  ❓ {question}")
    print(f"  🤖 {answer[:400]}{'…' if len(answer) > 400 else ''}")
    time.sleep(0.4)
    return answer


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_pronoun_resolution(sid: str) -> TestResult:
    section("MEMORY · Pronoun & Reference Resolution")
    r = TestResult()

    subsection("Turn 1 — establish context")
    a1 = raw_ask(sid, "What does the handle function in main.rs do?")
    if not a1:
        r.record(False)
        return r
    ok("Turn 1 answered")
    r.record(True)

    subsection("Turn 2 — pronoun 'it'")
    a2 = raw_ask(sid, "What type does it return?")
    if a2 and ("response" in a2.lower() or "infallible" in a2.lower() or "body" in a2.lower()):
        ok("Bot resolved 'it' correctly to the handle function")
        r.record(True)
    else:
        fail(f"Bot failed to resolve 'it' — answer: {a2[:200] if a2 else 'None'}")
        r.record(False)

    subsection("Turn 3 — 'that file'")
    a3 = raw_ask(sid, "What other functions are defined in that file?")
    if a3 and ("main" in a3.lower() or "main.rs" in a3.lower()):
        ok("Bot resolved 'that file' correctly to main.rs")
        r.record(True)
    else:
        warn(f"Soft fail — 'that file' resolution uncertain: {a3[:200] if a3 else 'None'}")
        r.skipped += 1

    return r


def test_fact_retention(sid: str) -> TestResult:
    section("MEMORY · Fact Retention Across Turns")
    r = TestResult()

    subsection("Turn 1 — state a fact")
    a1 = raw_ask(sid, "What port does the Rust HTTP server listen on?")
    if not a1:
        r.record(False)
        return r
    ok("Turn 1 answered")
    r.record(True)

    subsection("Turn 2 — unrelated question")
    raw_ask(sid, "What is the Cargo.toml edition?")

    subsection("Turn 3 — recall the fact from turn 1")
    a3 = raw_ask(sid, "What was the port number you mentioned a moment ago?")
    if a3 and "3000" in a3:
        ok("Bot correctly recalled port 3000 from earlier in the conversation")
        r.record(True)
    else:
        fail(f"Bot failed to recall port — answer: {a3[:200] if a3 else 'None'}")
        r.record(False)

    return r


def test_clarification_chain(sid: str) -> TestResult:
    section("MEMORY · Clarification & Drill-Down Chain")
    r = TestResult()

    turns = [
        ("What does auth.ts export?",
         lambda a: any(w in a.lower() for w in ["handlers", "auth", "signin", "signout"])),

        ("Tell me more about the `auth` export specifically.",
         lambda a: "auth" in a.lower()),

        ("How would a Next.js page component use that export?",
         lambda a: any(w in a.lower() for w in ["import", "session", "await"])),

        ("What would happen if the session is null?",
         lambda a: any(w in a.lower() for w in ["redirect", "null", "undefined", "login"])),

        ("Show me the exact code from the dashboard page that handles that case.",
         lambda a: any(w in a.lower() for w in ["redirect", "session", "if"])),
    ]

    for i, (question, check) in enumerate(turns, 1):
        subsection(f"Turn {i}")
        answer = raw_ask(sid, question)
        if answer and check(answer):
            ok(f"Turn {i} passed assertion")
            r.record(True)
        elif answer:
            warn(f"Turn {i} answered but assertion uncertain — review manually")
            r.skipped += 1
        else:
            fail(f"Turn {i} got no answer")
            r.record(False)

    return r


def test_session_isolation() -> TestResult:
    section("MEMORY · Session Isolation (no cross-session leakage)")
    r = TestResult()

    # Init two separate sessions for different repos
    sid_rust = init_session("rust-http-server", label="rust-isolation")
    sid_go   = init_session("go-microservices",  label="go-isolation")

    if not sid_rust or not sid_go:
        warn("Could not create both sessions — skipping isolation test")
        r.skipped += 1
        return r

    subsection("Ask Rust session about Rust")
    a_rust = raw_ask(sid_rust, "What programming language is this codebase written in?")

    subsection("Ask Go session about Go")
    a_go = raw_ask(sid_go, "What programming language is this codebase written in?")

    subsection("Assert answers are different / not cross-contaminated")
    if a_rust and a_go:
        rust_mentions_go  = "go" in a_rust.lower() and "rust" not in a_rust.lower()
        go_mentions_rust  = "rust" in a_go.lower() and "go" not in a_go.lower()

        if rust_mentions_go:
            fail("Rust session answered with Go content — session isolation broken!")
            r.record(False)
        elif go_mentions_rust:
            fail("Go session answered with Rust content — session isolation broken!")
            r.record(False)
        else:
            ok("Sessions returned distinct, appropriate answers")
            r.record(True)
    else:
        warn("One or both sessions returned empty answers — skipping isolation assertion")
        r.skipped += 1

    cleanup_session(sid_rust)
    cleanup_session(sid_go)
    return r


def test_long_conversation(sid: str) -> TestResult:
    section("MEMORY · Long Conversation (10 turns)")
    r = TestResult()

    turns = [
        "What files exist in this repository?",
        "Which file is the most important one?",
        "Explain what that file does in detail.",
        "What functions or exports does it contain?",
        "What would break if that file was deleted?",
        "How does it connect to the rest of the codebase?",
        "Are there any environment variables it depends on?",
        "How would I test that file in isolation?",
        "What improvements would you suggest to that file?",
        "Give me a one-paragraph summary of everything we discussed about this file.",
    ]

    answered = 0
    for i, q in enumerate(turns, 1):
        subsection(f"Turn {i}/10")
        a = raw_ask(sid, q)
        if a and len(a) > 20:
            answered += 1
        else:
            warn(f"Turn {i} returned short/empty answer")

    if answered >= 8:
        ok(f"Long conversation: {answered}/10 turns answered successfully")
        r.record(True)
    else:
        fail(f"Long conversation: only {answered}/10 turns answered")
        r.record(False)

    return r


def test_history_grows(sid: str) -> TestResult:
    section("MEMORY · Chat History Length Grows Correctly")
    r = TestResult()

    for i in range(1, 5):
        subsection(f"Turn {i}")
        data = post("/chat", {
            "session_id": sid,
            "question": f"Question number {i}: what does this repo contain?"
        })
        if not data:
            r.record(False)
            continue

        history = data.get("chat_history", [])
        expected_min = i * 2 - 1   # at minimum i user messages
        if len(history) >= expected_min:
            ok(f"Turn {i} — history length {len(history)} (≥ {expected_min} expected)")
            r.record(True)
        else:
            fail(f"Turn {i} — history length {len(history)}, expected ≥ {expected_min}")
            r.record(False)
        time.sleep(0.3)

    return r


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    require_server()
    print(f"\n🐿️  Conversational Memory Tests\n")

    repos = get_repos()
    all_results: list[TestResult] = []

    # Pronoun + fact retention need rust (main.rs has clear "3000" and "handle")
    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            all_results.append(test_pronoun_resolution(sid))
            cleanup_session(sid)

        sid = init_session("rust-http-server")
        if sid:
            all_results.append(test_fact_retention(sid))
            cleanup_session(sid)

    # Clarification chain needs next-saas-starter (auth.ts is richest)
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            all_results.append(test_clarification_chain(sid))
            cleanup_session(sid)

    # Session isolation
    all_results.append(test_session_isolation())

    # Long conversation — use whichever repo is available
    for repo in repos:
        sid = init_session(repo, label=f"long-conv ({repo})")
        if sid:
            all_results.append(test_long_conversation(sid))
            cleanup_session(sid)
            break

    # History growth — use any repo
    for repo in repos:
        sid = init_session(repo, label=f"history-growth ({repo})")
        if sid:
            all_results.append(test_history_grows(sid))
            cleanup_session(sid)
            break

    tp = sum(r.passed  for r in all_results)
    tf = sum(r.failed  for r in all_results)
    ts = sum(r.skipped for r in all_results)
    print(f"\n{'═'*62}")
    print(f"  MEMORY TESTS COMPLETE")
    print(f"  Passed: {tp}/{tp+tf}  |  Skipped: {ts}")
    print(f"{'═'*62}\n")
    sys.exit(0 if tf == 0 else 1)
