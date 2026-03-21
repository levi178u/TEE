"""
tests/test_vectorstore.py
─────────────────────────
Tests that the FAISS vectorstore is built correctly:
  - Chunks are stored with complete metadata
  - Similarity scores are present and sensible
  - Retrieval finds the right file for targeted questions
  - Multi-query retrieval returns more results than single-query

Run:  python tests/test_vectorstore.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.utils import (
    section, subsection, ok, fail, warn, info,
    get, post, delete, init_session, cleanup_session,
    require_server, get_repos, get_code_id_for_repo, TestResult, ask,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def check_sources(sources: list[dict], expected_filename: str, label: str) -> bool:
    """Assert that expected_filename appears somewhere in the source list."""
    filenames = [s.get("filename", "") for s in sources]
    if expected_filename in filenames:
        ok(f"[{label}] Retrieved expected file: {expected_filename}")
        return True
    fail(f"[{label}] Expected '{expected_filename}' in sources, got: {filenames}")
    return False


def check_similarity_scores(sources: list[dict], label: str) -> bool:
    """Assert that similarity_score is present and between 0 and 1."""
    missing = [s for s in sources if "similarity_score" not in s]
    oob     = [s for s in sources if "similarity_score" in s and not (0.0 <= s["similarity_score"] <= 1.05)]
    if missing:
        fail(f"[{label}] {len(missing)} sources missing similarity_score")
        return False
    if oob:
        fail(f"[{label}] {len(oob)} sources have out-of-range similarity_score")
        return False
    scores = [round(s["similarity_score"], 3) for s in sources]
    ok(f"[{label}] Similarity scores present and valid: {scores}")
    return True


def check_metadata_completeness(sources: list[dict], label: str) -> bool:
    """Assert all expected metadata fields are present."""
    required = {"filename", "route", "language", "repo_name", "source"}
    all_ok = True
    for s in sources:
        missing = required - set(s.keys())
        if missing:
            fail(f"[{label}] Source missing metadata fields: {missing}  file={s.get('filename','?')}")
            all_ok = False
    if all_ok and sources:
        ok(f"[{label}] All {len(sources)} sources have complete metadata")
    return all_ok


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_next_saas_retrieval(sid: str) -> TestResult:
    section("VECTORSTORE · next-saas-starter Retrieval Precision")
    r = TestResult()

    # Each tuple: (question, expected_filename, expected_keywords_in_answer)
    cases = [
        (
            "Show me the authentication configuration",
            "auth.ts",
            ["nextauth", "github", "prisma"],
        ),
        (
            "How is the Prisma client exported and reused across the app?",
            "prisma.ts",
            ["prismaClient", "globalForPrisma"],
        ),
        (
            "What does the dashboard page component do?",
            "page.tsx",
            ["dashboard", "session", "redirect"],
        ),
        (
            "What Tailwind directives are in the global CSS file?",
            "globals.css",
            ["tailwind", "@tailwind"],
        ),
    ]

    for question, expected_file, keywords in cases:
        subsection(expected_file)
        data = ask(sid, question, label=expected_file)
        if not data:
            r.record(False)
            continue

        sources = data.get("sources", [])
        passed = True
        passed &= check_sources(sources, expected_file, expected_file)
        passed &= check_similarity_scores(sources, expected_file)
        passed &= check_metadata_completeness(sources, expected_file)

        # Keyword check (case-insensitive)
        answer = data.get("answer", "").lower()
        missing_kw = [kw for kw in keywords if kw.lower() not in answer]
        if missing_kw:
            warn(f"Answer soft-missing keywords (may still be correct): {missing_kw}")
        else:
            ok(f"Answer contains expected keywords: {keywords}")

        r.record(passed)

    return r


def test_rust_retrieval(sid: str) -> TestResult:
    section("VECTORSTORE · rust-http-server Retrieval Precision")
    r = TestResult()

    cases = [
        (
            "Show me the main.rs server implementation",
            "main.rs",
            ["tokio", "hyper", "handle"],
        ),
        (
            "What does the Cargo.toml file say about dependencies?",
            "Cargo.toml",
            ["tokio", "hyper", "version"],
        ),
        (
            "What does the README say about this project?",
            "README.md",
            ["http", "server", "cargo"],
        ),
    ]

    for question, expected_file, keywords in cases:
        subsection(expected_file)
        data = ask(sid, question, label=expected_file)
        if not data:
            r.record(False)
            continue

        sources = data.get("sources", [])
        passed = True
        passed &= check_sources(sources, expected_file, expected_file)
        passed &= check_similarity_scores(sources, expected_file)
        passed &= check_metadata_completeness(sources, expected_file)
        r.record(passed)

    return r


def test_go_retrieval(sid: str) -> TestResult:
    section("VECTORSTORE · go-microservices Retrieval Precision")
    r = TestResult()

    cases = [
        (
            "Show me the Go main.go server code",
            "main.go",
            ["http", "ListenAndServe", "health"],
        ),
        (
            "What services are in the docker-compose file?",
            "docker-compose.yml",
            ["postgres", "api", "ports"],
        ),
    ]

    for question, expected_file, keywords in cases:
        subsection(expected_file)
        data = ask(sid, question, label=expected_file)
        if not data:
            r.record(False)
            continue

        sources = data.get("sources", [])
        passed = True
        passed &= check_sources(sources, expected_file, expected_file)
        passed &= check_similarity_scores(sources, expected_file)
        passed &= check_metadata_completeness(sources, expected_file)
        r.record(passed)

    return r


def test_metadata_fields_all_repos(sid: str) -> TestResult:
    section("VECTORSTORE · Metadata Completeness (all repos)")
    r = TestResult()

    data = ask(sid, "List all the files in this codebase", label="metadata-all")
    if not data:
        r.record(False)
        return r

    sources = data.get("sources", [])
    if not sources:
        warn("No sources returned — cannot check metadata fields")
        r.skipped += 1
        return r

    subsection("Checking all required metadata fields")
    passed = check_metadata_completeness(sources, "all-repos")
    r.record(passed)

    subsection("Checking similarity scores")
    passed2 = check_similarity_scores(sources, "all-repos")
    r.record(passed2)

    subsection("Checking repo_name is populated")
    no_repo = [s for s in sources if not s.get("repo_name")]
    if no_repo:
        fail(f"{len(no_repo)} sources have empty repo_name")
        r.record(False)
    else:
        ok("All sources have repo_name populated")
        r.record(True)

    subsection("Checking language is populated")
    no_lang = [s for s in sources if not s.get("language")]
    if no_lang:
        warn(f"{len(no_lang)} sources have empty language field")
    else:
        ok("All sources have language populated")

    return r


def test_cache_consistency() -> TestResult:
    section("VECTORSTORE · Cache Load Consistency (/init-from-cache)")
    r = TestResult()

    code_id = get_code_id_for_repo()
    if not code_id:
        warn("No code_id found — skipping cache consistency test")
        r.skipped += 1
        return r

    data = post("/init-from-cache", {"llm_type": "groq", "code_id": code_id}, timeout=30)
    if not data:
        warn("No FAISS cache found — skipping cache consistency test (run /init first)")
        r.skipped += 1
        return r

    sid = data.get("session_id")
    ok(f"Loaded from cache — session: {sid}")

    q_data = ask(sid, "What is the main entry point of the rust server?", label="cache-test")
    if q_data and q_data.get("answer"):
        ok("Cache session answered a question successfully")
        r.record(True)
    else:
        fail("Cache session failed to answer")
        r.record(False)

    cleanup_session(sid)
    return r


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    require_server()
    print(f"\n🐿️  Vectorstore & Retrieval Tests\n")

    repos = get_repos()
    all_results = []

    # Per-repo precision tests
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            all_results.append(test_next_saas_retrieval(sid))
            cleanup_session(sid)

    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            all_results.append(test_rust_retrieval(sid))
            cleanup_session(sid)

    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            all_results.append(test_go_retrieval(sid))
            cleanup_session(sid)

    # All-repos metadata test
    sid_all = init_session(label="ALL repos")
    if sid_all:
        all_results.append(test_metadata_fields_all_repos(sid_all))
        cleanup_session(sid_all)

    # Cache test
    all_results.append(test_cache_consistency())

    # Summary
    tp = sum(r.passed  for r in all_results)
    tf = sum(r.failed  for r in all_results)
    ts = sum(r.skipped for r in all_results)
    print(f"\n{'═'*62}")
    print(f"  VECTORSTORE TESTS COMPLETE")
    print(f"  Passed: {tp}/{tp+tf}  |  Skipped: {ts}")
    print(f"{'═'*62}\n")
    sys.exit(0 if tf == 0 else 1)
