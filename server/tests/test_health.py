"""
tests/test_health.py
────────────────────
Infrastructure & API surface tests.
Verifies every endpoint exists, returns correct shape, and handles bad input.

Run:  python tests/test_health.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
from tests.utils import (
    BASE_URL, section, subsection, ok, fail, warn, info,
    get, post, delete, require_server, TestResult, TIMEOUT_FAST,
)

def test_root():
    section("1 · Root & Health Endpoints")
    r = TestResult()

    for path, key in [("/health", "ok"), ("/", "message")]:
        data = get(path)
        if data and key in data:
            ok(f"GET {path} → {data}")
            r.record(True)
        else:
            fail(f"GET {path} missing key '{key}' in response")
            r.record(False)

    return r


def test_repos_endpoint():
    section("2 · /repos Endpoint")
    r = TestResult()

    data = get("/repos")
    if data is None:
        r.record(False)
        return r

    repos = data.get("repos")
    if isinstance(repos, list):
        ok(f"/repos returned list with {len(repos)} repo(s): {repos}")
        r.record(True)
    else:
        fail(f"/repos did not return a list — got: {data}")
        r.record(False)

    return r


def test_sessions_endpoint():
    section("3 · /sessions Endpoint")
    r = TestResult()

    data = get("/sessions")
    if data is None:
        r.record(False)
        return r

    sessions = data.get("sessions")
    if isinstance(sessions, list):
        ok(f"/sessions returned list — {len(sessions)} active session(s)")
        r.record(True)
    else:
        fail(f"Unexpected /sessions shape: {data}")
        r.record(False)

    return r


def test_bad_inputs():
    section("4 · Bad Input Handling")
    r = TestResult()
    subsection("4a — /init with empty body")

    # POST /init with completely empty body should fail validation (missing code_id)
    try:
        resp = requests.post(f"{BASE_URL}/init", json={}, timeout=TIMEOUT_FAST)
        if resp.status_code in (422, 400):
            ok(f"/init empty body → HTTP {resp.status_code} (expected validation failure)")
            r.record(True)
        else:
            fail(f"/init empty body → HTTP {resp.status_code}: {resp.text[:100]}")
            r.record(False)
    except Exception as e:
        fail(f"Request error: {e}")
        r.record(False)

    subsection("4b — /chat with missing session_id")
    try:
        code_items = get("/code-ids") or {}
        code_id = ((code_items.get("items") or [{}])[0]).get("code_id", "dummy-code-id")
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"code_id": code_id, "session_id": "nonexistent-id-abc123", "question": "hello"},
            timeout=TIMEOUT_FAST,
        )
        if resp.status_code == 404:
            ok(f"/chat unknown session → HTTP 404 (correct)")
            r.record(True)
        else:
            fail(f"/chat unknown session → HTTP {resp.status_code} (expected 404)")
            r.record(False)
    except Exception as e:
        fail(f"Request error: {e}")
        r.record(False)

    subsection("4c — /chat with empty question")
    # We need a real session for this — use init-from-cache if available
    code_items = get("/code-ids") or {}
    cache_code_id = ((code_items.get("items") or [{}])[0]).get("code_id")
    if not cache_code_id:
        warn("Skipping empty-question test — no code_id available")
        r.skipped += 1
        return r

    cache_data = post("/init-from-cache", {"llm_type": "groq", "code_id": cache_code_id}, timeout=30)
    if cache_data:
        sid = cache_data.get("session_id")
        try:
            resp = requests.post(
                f"{BASE_URL}/chat",
                json={"code_id": cache_code_id, "session_id": sid, "question": "   "},
                timeout=TIMEOUT_FAST,
            )
            if resp.status_code == 400:
                ok("/chat empty question → HTTP 400 (correct)")
                r.record(True)
            else:
                fail(f"/chat empty question → HTTP {resp.status_code} (expected 400)")
                r.record(False)
        except Exception as e:
            fail(f"Request error: {e}")
            r.record(False)
        delete(f"/session/{sid}")
    else:
        warn("Skipping empty-question test — no FAISS cache available (run /init first)")
        r.skipped += 1

    subsection("4d — DELETE unknown session")
    try:
        resp = requests.delete(f"{BASE_URL}/session/fake-id-xyz", timeout=TIMEOUT_FAST)
        if resp.status_code == 404:
            ok("DELETE unknown session → HTTP 404 (correct)")
            r.record(True)
        else:
            fail(f"DELETE unknown session → HTTP {resp.status_code} (expected 404)")
            r.record(False)
    except Exception as e:
        fail(f"Request error: {e}")
        r.record(False)

    return r


def test_docs_ui():
    section("5 · Swagger /docs UI Reachable")
    r = TestResult()
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT_FAST)
        if resp.status_code == 200 and "swagger" in resp.text.lower():
            ok("/docs Swagger UI is reachable")
            r.record(True)
        else:
            fail(f"/docs returned {resp.status_code}")
            r.record(False)
    except Exception as e:
        fail(f"/docs unreachable: {e}")
        r.record(False)
    return r


def test_cors_headers():
    section("6 · CORS Headers")
    r = TestResult()
    try:
        resp = requests.options(
            f"{BASE_URL}/chat",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
            timeout=TIMEOUT_FAST,
        )
        acao = resp.headers.get("access-control-allow-origin", "")
        if acao:
            ok(f"CORS header present: Access-Control-Allow-Origin: {acao}")
            r.record(True)
        else:
            warn("CORS header not detected on OPTIONS — may still work for simple requests")
            r.skipped += 1
    except Exception as e:
        fail(f"CORS check error: {e}")
        r.record(False)
    return r


if __name__ == "__main__":
    require_server()
    print(f"\n🐿️  Health & Infrastructure Tests  →  {BASE_URL}\n")

    results = [
        test_root(),
        test_repos_endpoint(),
        test_sessions_endpoint(),
        test_bad_inputs(),
        test_docs_ui(),
        test_cors_headers(),
    ]

    total_pass  = sum(r.passed  for r in results)
    total_fail  = sum(r.failed  for r in results)
    total_skip  = sum(r.skipped for r in results)
    total       = total_pass + total_fail

    print(f"\n{'═'*62}")
    print(f"  HEALTH TESTS COMPLETE")
    print(f"  Passed:  {total_pass}/{total}")
    if total_fail:  print(f"  Failed:  {total_fail}")
    if total_skip:  print(f"  Skipped: {total_skip}")
    print(f"{'═'*62}\n")

    sys.exit(0 if total_fail == 0 else 1)
