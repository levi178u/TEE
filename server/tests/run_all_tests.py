"""
run_all_py
────────────────
Master test runner. Runs all five test suites in sequence and prints
a consolidated summary at the end.

Usage:
    python run_all_tests.py              # run everything
    python run_all_tests.py --fast       # skip architecture + memory (slow)
    python run_all_tests.py --suite health
    python run_all_tests.py --suite vectorstore
    python run_all_tests.py --suite comprehension
    python run_all_tests.py --suite memory
    python run_all_tests.py --suite edge
    python run_all_tests.py --suite architecture
"""
import sys
import os
import time
import argparse

# So we can import from tests/
sys.path.insert(0, os.path.dirname(__file__))

from utils import require_server, get_repos, section, ok, fail, warn, info, BOLD, RESET, GREEN, RED, YELLOW

# Import all suites
import test_health          as suite_health
import test_vectorstore     as suite_vec
import test_code_comprehension as suite_comp
import test_memory          as suite_mem
import test_edge_cases      as suite_edge
import test_architecture    as suite_arch


def run_suite(name: str, fn, repos: list[str]) -> tuple[int, int, int]:
    """Run a suite function and return (passed, failed, skipped)."""
    start = time.time()
    print(f"\n{'▶' * 3}  Running suite: {BOLD}{name}{RESET}")
    try:
        fn(repos)
    except SystemExit:
        pass   # suites call sys.exit — we catch it here
    elapsed = time.time() - start
    print(f"  ⏱  Suite '{name}' completed in {elapsed:.1f}s")
    return 0, 0, 0   # per-suite counts tracked inside each module


def run_health(repos):
    from test_health import (
        test_root, test_repos_endpoint, test_sessions_endpoint,
        test_bad_inputs, test_docs_ui, test_cors_headers,
    )
    results = [
        test_root(), test_repos_endpoint(), test_sessions_endpoint(),
        test_bad_inputs(), test_docs_ui(), test_cors_headers(),
    ]
    return results


def run_vectorstore(repos):
    from test_vectorstore import (
        test_next_saas_retrieval, test_rust_retrieval, test_go_retrieval,
        test_metadata_fields_all_repos, test_cache_consistency,
    )
    from utils import init_session, cleanup_session
    results = []
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            results.append(test_next_saas_retrieval(sid))
            cleanup_session(sid)
    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            results.append(test_rust_retrieval(sid))
            cleanup_session(sid)
    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            results.append(test_go_retrieval(sid))
            cleanup_session(sid)
    sid_all = init_session(label="ALL")
    if sid_all:
        results.append(test_metadata_fields_all_repos(sid_all))
        cleanup_session(sid_all)
    results.append(test_cache_consistency())
    return results


def run_comprehension(repos):
    from test_code_comprehension import (
        test_auth_ts, test_prisma_ts, test_dashboard_page, test_globals_css,
        test_main_rs, test_cargo_toml, test_main_go, test_docker_compose_yml,
    )
    from utils import init_session, cleanup_session
    results = []
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            results += [test_auth_ts(sid), test_prisma_ts(sid),
                        test_dashboard_page(sid), test_globals_css(sid)]
            cleanup_session(sid)
    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            results += [test_main_rs(sid), test_cargo_toml(sid)]
            cleanup_session(sid)
    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            results += [test_main_go(sid), test_docker_compose_yml(sid)]
            cleanup_session(sid)
    return results


def run_memory(repos):
    from test_memory import (
        test_pronoun_resolution, test_fact_retention, test_clarification_chain,
        test_session_isolation, test_long_conversation, test_history_grows,
    )
    from utils import init_session, cleanup_session
    results = []
    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            results.append(test_pronoun_resolution(sid))
            cleanup_session(sid)
        sid = init_session("rust-http-server")
        if sid:
            results.append(test_fact_retention(sid))
            cleanup_session(sid)
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            results.append(test_clarification_chain(sid))
            cleanup_session(sid)
    results.append(test_session_isolation())
    for repo in repos:
        sid = init_session(repo)
        if sid:
            results.append(test_long_conversation(sid))
            cleanup_session(sid)
            break
    for repo in repos:
        sid = init_session(repo)
        if sid:
            results.append(test_history_grows(sid))
            cleanup_session(sid)
            break
    return results


def run_edge(repos):
    from test_edge_cases import (
        test_out_of_scope, test_nonexistent_identifiers, test_vague_questions,
        test_injection_attempts, test_special_characters,
        test_repeated_question, test_very_long_question,
    )
    from utils import init_session, cleanup_session
    primary = next(
        (r for r in ["next-saas-starter", "rust-http-server", "go-microservices"] if r in repos),
        repos[0] if repos else None,
    )
    if not primary:
        return []
    sid = init_session(primary)
    if not sid:
        return []
    results = [
        test_out_of_scope(sid),
        test_nonexistent_identifiers(sid),
        test_vague_questions(sid),
        test_injection_attempts(sid),
        test_special_characters(sid),
        test_repeated_question(sid),
        test_very_long_question(sid),
    ]
    cleanup_session(sid)
    return results


def run_architecture(repos):
    from test_architecture import (
        test_next_saas_architecture, test_rust_architecture, test_go_architecture,
        test_cross_repo_comparisons, test_setup_and_devex,
    )
    from utils import init_session, cleanup_session
    results = []
    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            results.append(test_next_saas_architecture(sid))
            cleanup_session(sid)
    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            results.append(test_rust_architecture(sid))
            cleanup_session(sid)
    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            results.append(test_go_architecture(sid))
            cleanup_session(sid)
    sid_all = init_session(label="ALL — architecture")
    if sid_all:
        results.append(test_cross_repo_comparisons(sid_all))
        results.append(test_setup_and_devex(sid_all))
        cleanup_session(sid_all)
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

SUITES = {
    "health":        run_health,
    "vectorstore":   run_vectorstore,
    "comprehension": run_comprehension,
    "memory":        run_memory,
    "edge":          run_edge,
    "architecture":  run_architecture,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Squirrel ChatBot — Master Test Runner")
    parser.add_argument("--suite", choices=list(SUITES.keys()), default=None,
                        help="Run a single test suite")
    parser.add_argument("--fast", action="store_true",
                        help="Skip slow suites (memory, architecture)")
    args = parser.parse_args()

    require_server()
    repos = get_repos()
    if not repos:
        fail("No repos in database. Run: docker compose up seed")
        sys.exit(1)

    info(f"Repos available: {repos}")

    grand_pass = grand_fail = grand_skip = 0
    suite_summary: list[tuple[str, int, int, int]] = []

    if args.suite:
        to_run = {args.suite: SUITES[args.suite]}
    elif args.fast:
        to_run = {k: v for k, v in SUITES.items() if k not in ("memory", "architecture")}
    else:
        to_run = SUITES

    wall_start = time.time()

    for suite_name, suite_fn in to_run.items():
        t0 = time.time()
        print(f"\n\n{'━'*62}")
        print(f"  🧪  SUITE: {BOLD}{suite_name.upper()}{RESET}")
        print(f"{'━'*62}")

        try:
            results = suite_fn(repos)
        except Exception as e:
            fail(f"Suite '{suite_name}' crashed: {e}")
            suite_summary.append((suite_name, 0, 1, 0))
            grand_fail += 1
            continue

        sp = sum(r.passed  for r in results)
        sf = sum(r.failed  for r in results)
        ss = sum(r.skipped for r in results)
        elapsed = time.time() - t0

        grand_pass += sp
        grand_fail += sf
        grand_skip += ss
        suite_summary.append((suite_name, sp, sf, ss))

        colour = GREEN if sf == 0 else RED
        print(f"\n  {colour}{BOLD}{suite_name}: {sp}/{sp+sf} passed  ({elapsed:.1f}s){RESET}")

    wall_elapsed = time.time() - wall_start

    # ── Grand Summary ─────────────────────────────────────────────────────────
    print(f"\n\n{'═'*62}")
    print(f"  {BOLD}🐿️  SQUIRREL CHATBOT — FULL TEST SUMMARY{RESET}")
    print(f"{'═'*62}")
    for name, sp, sf, ss in suite_summary:
        status = f"{GREEN}✅{RESET}" if sf == 0 else f"{RED}❌{RESET}"
        skip_str = f"  skipped:{ss}" if ss else ""
        print(f"  {status}  {name:<18}  passed:{sp}  failed:{sf}{skip_str}")

    print(f"{'─'*62}")
    colour = GREEN if grand_fail == 0 else RED
    print(f"  {colour}{BOLD}TOTAL: {grand_pass}/{grand_pass+grand_fail} passed  |  "
          f"skipped: {grand_skip}  |  {wall_elapsed:.1f}s{RESET}")
    print(f"{'═'*62}\n")

    sys.exit(0 if grand_fail == 0 else 1)
