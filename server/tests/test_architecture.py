"""
tests/test_architecture.py
──────────────────────────
Tests that require understanding of project architecture, cross-file
relationships, and cross-repository comparisons.

Covers:
  - High-level architecture description
  - Data flow tracing
  - Dependency mapping
  - Cross-repo technology comparisons
  - Setup/deployment understanding

Run:  python tests/test_architecture.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
from tests.utils import (
    section, subsection, ok, fail, warn,
    init_session, cleanup_session,
    require_server, get_repos, TestResult, ask,
)


# ── Per-repo architecture ─────────────────────────────────────────────────────

def test_next_saas_architecture(sid: str) -> TestResult:
    section("ARCH · next-saas-starter — Full Architecture")
    r = TestResult()

    questions = [
        ("overview",
         "Give a high-level architectural overview of this Next.js SaaS project.",
         ["auth", "prisma", "dashboard"]),

        ("auth-flow",
         "Trace the complete authentication flow: from a user clicking 'Sign in with GitHub' to landing on the dashboard.",
         ["GithubProvider", "PrismaAdapter", "session", "redirect"]),

        ("data-flow",
         "How does user data flow from GitHub OAuth back into the Prisma database?",
         ["adapter", "prisma", "user"]),

        ("file-relationships",
         "How do auth.ts, prisma.ts, and page.tsx depend on each other?",
         ["auth", "prisma", "import"]),

        ("env-required",
         "List every environment variable this project needs to function and explain each one.",
         ["GITHUB_ID", "GITHUB_SECRET"]),

        ("layer-separation",
         "How is this project layered — what are the presentation, logic, and data layers?",
         []),

        ("deployment-checklist",
         "What would a production deployment checklist look like for this project?",
         ["environment", "database"]),

        ("security-analysis",
         "What security mechanisms are in place in this codebase?",
         ["auth", "session"]),
    ]

    for label, q, keywords in questions:
        subsection(label)
        ask(sid, q, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_rust_architecture(sid: str) -> TestResult:
    section("ARCH · rust-http-server — Architecture & Design")
    r = TestResult()

    questions = [
        ("async-arch",
         "Explain the async architecture of this Rust HTTP server — how does Tokio fit in?",
         ["tokio", "async", "await"]),

        ("request-lifecycle",
         "Trace the lifecycle of an HTTP request from TCP connection to response.",
         ["TcpListener", "handle", "Response"]),

        ("crate-roles",
         "What role does each crate (tokio, hyper) play in this project?",
         ["tokio", "hyper"]),

        ("scale-this",
         "How would you add routing to support multiple endpoints in this architecture?",
         ["uri", "path", "match"]),

        ("compare-to-express",
         "How does this Rust server compare architecturally to a Node.js Express server?",
         []),

        ("production-gaps",
         "What is missing from this server to make it production-ready?",
         []),
    ]

    for label, q, keywords in questions:
        subsection(label)
        ask(sid, q, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_go_architecture(sid: str) -> TestResult:
    section("ARCH · go-microservices — Architecture & Docker")
    r = TestResult()

    questions = [
        ("service-overview",
         "Describe the overall microservices architecture of this Go project.",
         ["api", "postgres"]),

        ("docker-network",
         "How do the Docker services communicate with each other in this compose setup?",
         ["postgres", "api", "service"]),

        ("health-design",
         "Why is a /health endpoint important in a microservices architecture and how is it implemented here?",
         ["health", "status"]),

        ("db-connection",
         "How would the Go API service connect to the Postgres database defined in docker-compose?",
         ["postgres", "DATABASE_URL", "connection"]),

        ("add-service",
         "How would you add a Redis caching service to this docker-compose setup?",
         ["redis", "service"]),

        ("12-factor",
         "How does this project follow or violate 12-factor app principles?",
         []),
    ]

    for label, q, keywords in questions:
        subsection(label)
        ask(sid, q, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


# ── Cross-repo comparisons ────────────────────────────────────────────────────

def test_cross_repo_comparisons(sid: str) -> TestResult:
    section("ARCH · Cross-Repository Comparisons (all repos loaded)")
    r = TestResult()

    questions = [
        ("lang-matrix",
         "Create a table mapping each repository to its primary programming language and framework.",
         ["TypeScript", "Rust", "Go"]),

        ("web-server-compare",
         "Compare how the Rust and Go projects implement HTTP servers. What are the key differences?",
         ["hyper", "tokio", "http.NewServeMux"]),

        ("docker-usage",
         "Which repositories use Docker? What are the differences in how they use it?",
         ["go-microservices", "docker-compose"]),

        ("db-usage",
         "Which repositories interact with a database, and how?",
         ["prisma", "postgres"]),

        ("auth-presence",
         "Which repository has authentication? Describe its auth mechanism.",
         ["next-saas-starter", "NextAuth", "GitHub"]),

        ("async-compare",
         "Compare the async programming patterns used across these repositories.",
         ["tokio", "async"]),

        ("entry-points",
         "What is the entry point of each repository?",
         ["main.rs", "main.go", "auth.ts"]),

        ("readme-repos",
         "Which repositories have a README file and what do they contain?",
         ["README.md", "rust"]),

        ("config-files",
         "List all configuration files across all repositories and what they configure.",
         ["Cargo.toml", "docker-compose", "globals.css"]),

        ("complexity-rank",
         "Rank the three repositories from simplest to most complex codebase and justify your ranking.",
         []),

        ("monorepo-suggest",
         "If you were to combine all three repositories into a monorepo, how would you structure it?",
         []),

        ("tech-stack-summary",
         "Give a complete technology stack summary for all three repositories combined.",
         ["TypeScript", "Rust", "Go", "PostgreSQL"]),
    ]

    for label, q, keywords in questions:
        subsection(label)
        ask(sid, q, label=label,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)
        time.sleep(0.5)

    return r


def test_setup_and_devex(sid: str) -> TestResult:
    section("ARCH · Developer Experience & Setup Questions")
    r = TestResult()

    questions = [
        ("onboard",
         "I'm a new developer joining this project. What are the first 5 steps I should take to get up and running?",
         []),

        ("debug-auth",
         "A developer reports that GitHub OAuth login is failing with a callback URL error. Where in the codebase would you look first?",
         ["NEXTAUTH_URL", "auth.ts", "GITHUB"]),

        ("local-db",
         "How would a developer run the Postgres database locally for the Go microservices project?",
         ["docker", "postgres"]),

        ("first-pr",
         "What would a first pull request look like to add a new REST endpoint to the Go microservices project?",
         ["main.go", "HandleFunc"]),
    ]

    for label, q, keywords in questions:
        subsection(label)
        ask(sid, q, label=label,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    require_server()
    print(f"\n🐿️  Architecture & Cross-Repo Tests\n")

    repos = get_repos()
    all_results: list[TestResult] = []

    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            all_results.append(test_next_saas_architecture(sid))
            cleanup_session(sid)

    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            all_results.append(test_rust_architecture(sid))
            cleanup_session(sid)

    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            all_results.append(test_go_architecture(sid))
            cleanup_session(sid)

    # Cross-repo: load everything
    sid_all = init_session(label="ALL repos — cross-repo")
    if sid_all:
        all_results.append(test_cross_repo_comparisons(sid_all))
        all_results.append(test_setup_and_devex(sid_all))
        cleanup_session(sid_all)

    tp = sum(r.passed  for r in all_results)
    tf = sum(r.failed  for r in all_results)
    ts = sum(r.skipped for r in all_results)
    print(f"\n{'═'*62}")
    print(f"  ARCHITECTURE TESTS COMPLETE")
    print(f"  Passed: {tp}/{tp+tf}  |  Skipped: {ts}")
    print(f"{'═'*62}\n")
    sys.exit(0 if tf == 0 else 1)
