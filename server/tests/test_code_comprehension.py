"""
tests/test_code_comprehension.py
─────────────────────────────────
Tests the chatbot's ability to understand and explain actual code
from each seeded repository in depth.

Covers:
  - Function-level explanation
  - Import/dependency reasoning
  - Variable and type explanation
  - Logic flow tracing
  - Code modification suggestions

Run:  python tests/test_code_comprehension.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.utils import (
    section, subsection, ok, fail, warn, info,
    init_session, cleanup_session,
    require_server, get_repos, TestResult, ask,
)


# ── next-saas-starter ─────────────────────────────────────────────────────────

def test_auth_ts(sid: str) -> TestResult:
    section("CODE · next-saas-starter · auth.ts")
    r = TestResult()

    cases = [
        ("what-imports",
         "What are all the imports in auth.ts and what is each one for?",
         ["next-auth", "GithubProvider", "PrismaAdapter"]),

        ("nextauth-export",
         "What does the NextAuth() call in auth.ts export and how are those exports used?",
         ["handlers", "auth", "signIn", "signOut"]),

        ("prisma-adapter",
         "Why is PrismaAdapter used in the NextAuth configuration?",
         ["adapter", "database", "session"]),

        ("github-provider",
         "What environment variables does the GithubProvider require?",
         ["GITHUB_ID", "GITHUB_SECRET"]),

        ("add-google",
         "Based on the existing auth.ts code, how would I add Google OAuth as a second provider?",
         ["GoogleProvider", "clientId", "clientSecret"]),

        ("session-type",
         "What session strategy does this NextAuth setup use — JWT or database?",
         []),   # open-ended — just check answer exists
    ]

    for label, question, keywords in cases:
        subsection(label)
        data = ask(sid, question, label=label,
                   expect_sources=True,
                   expect_keywords=keywords if keywords else None,
                   result_tracker=r)

    return r


def test_prisma_ts(sid: str) -> TestResult:
    section("CODE · next-saas-starter · prisma.ts")
    r = TestResult()

    cases = [
        ("global-singleton",
         "Why does prisma.ts use `globalThis` to store the PrismaClient instance?",
         ["hot reload", "singleton", "production"]),

        ("log-option",
         "What does `log: ['query']` do in the PrismaClient constructor?",
         ["log", "query"]),

        ("prevent-multiple",
         "How does this file prevent multiple PrismaClient instances in development?",
         ["globalForPrisma", "NODE_ENV"]),

        ("import-usage",
         "How would another file in this project import and use the Prisma client?",
         ["import", "prisma"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_dashboard_page(sid: str) -> TestResult:
    section("CODE · next-saas-starter · page.tsx (Dashboard)")
    r = TestResult()

    cases = [
        ("auth-call",
         "What does `const session = await auth()` do in the dashboard page?",
         ["auth", "session"]),

        ("redirect-logic",
         "Under what condition does the dashboard page redirect the user, and where?",
         ["redirect", "login", "session"]),

        ("server-component",
         "Is DashboardPage a client component or a server component? How can you tell?",
         ["server", "async"]),

        ("ui-output",
         "What HTML/JSX does the dashboard page actually render when a user is logged in?",
         ["Welcome", "name"]),

        ("protect-api",
         "How would you protect an API route using the same auth() pattern shown in this file?",
         []),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_globals_css(sid: str) -> TestResult:
    section("CODE · next-saas-starter · globals.css")
    r = TestResult()

    cases = [
        ("tailwind-directives",
         "What are the three Tailwind directives in globals.css and what do they do?",
         ["@tailwind base", "@tailwind components", "@tailwind utilities"]),

        ("css-variables",
         "What CSS custom properties (variables) are defined in globals.css?",
         ["--background", "--foreground"]),

        ("body-styles",
         "What styles are applied to the body element?",
         ["bg-background", "text-foreground"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


# ── rust-http-server ──────────────────────────────────────────────────────────

def test_main_rs(sid: str) -> TestResult:
    section("CODE · rust-http-server · main.rs")
    r = TestResult()

    cases = [
        ("handle-fn",
         "Explain the `handle` function in main.rs — what are its parameters and return type?",
         ["Request", "Response", "Body", "Infallible"]),

        ("tokio-main",
         "What does the `#[tokio::main]` attribute macro do and why is it needed?",
         ["async", "tokio", "runtime"]),

        ("server-bind",
         "What IP address and port does the server bind to in main.rs?",
         ["127.0.0.1", "3000"]),

        ("make-service",
         "What is `make_service_fn` and why is it used here?",
         ["service", "connection"]),

        ("add-route",
         "How would you modify main.rs to return different responses based on the request path?",
         ["uri", "path", "match"]),

        ("error-handling",
         "How does this server handle errors — what type is used for the error?",
         ["Infallible"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_cargo_toml(sid: str) -> TestResult:
    section("CODE · rust-http-server · Cargo.toml")
    r = TestResult()

    cases = [
        ("package-info",
         "What is the package name, version, and edition in Cargo.toml?",
         ["rust-http-server", "0.1.0", "2021"]),

        ("tokio-features",
         "What Tokio features are enabled in Cargo.toml?",
         ["full"]),

        ("hyper-features",
         "What Hyper features are enabled and why might 'full' be specified?",
         ["hyper", "full"]),

        ("add-serde",
         "How would you add serde with JSON support to this Cargo.toml?",
         ["serde", "features"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


# ── go-microservices ──────────────────────────────────────────────────────────

def test_main_go(sid: str) -> TestResult:
    section("CODE · go-microservices · main.go")
    r = TestResult()

    cases = [
        ("imports",
         "What packages does main.go import and what is each used for?",
         ["log", "net/http"]),

        ("mux-setup",
         "How is the HTTP router set up in main.go?",
         ["NewServeMux", "HandleFunc"]),

        ("health-handler",
         "What does the /health handler return — what is the exact response body?",
         ["status", "ok"]),

        ("server-start",
         "How does main.go start the server and what happens if it fails?",
         ["ListenAndServe", "log.Fatal", "8080"]),

        ("add-endpoint",
         "Based on the pattern in main.go, write the code to add a /version endpoint that returns a JSON version string.",
         ["HandleFunc", "version", "w.Write"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


def test_docker_compose_yml(sid: str) -> TestResult:
    section("CODE · go-microservices · docker-compose.yml")
    r = TestResult()

    cases = [
        ("services",
         "What two services are defined in docker-compose.yml?",
         ["api", "postgres"]),

        ("postgres-env",
         "What environment variables configure the Postgres service?",
         ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]),

        ("api-ports",
         "What port mapping is used for the API service?",
         ["8080"]),

        ("network",
         "How can the api service communicate with the postgres service in this compose file?",
         ["postgres", "service"]),

        ("override-env",
         "How would you add an environment variable to the API service to pass a database connection string?",
         ["environment", "DATABASE_URL"]),
    ]

    for label, question, keywords in cases:
        subsection(label)
        ask(sid, question, label=label,
            expect_sources=True,
            expect_keywords=keywords if keywords else None,
            result_tracker=r)

    return r


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    require_server()
    print(f"\n🐿️  Code Comprehension Tests\n")

    repos = get_repos()
    all_results: list[TestResult] = []

    if "next-saas-starter" in repos:
        sid = init_session("next-saas-starter")
        if sid:
            all_results.append(test_auth_ts(sid))
            all_results.append(test_prisma_ts(sid))
            all_results.append(test_dashboard_page(sid))
            all_results.append(test_globals_css(sid))
            cleanup_session(sid)

    if "rust-http-server" in repos:
        sid = init_session("rust-http-server")
        if sid:
            all_results.append(test_main_rs(sid))
            all_results.append(test_cargo_toml(sid))
            cleanup_session(sid)

    if "go-microservices" in repos:
        sid = init_session("go-microservices")
        if sid:
            all_results.append(test_main_go(sid))
            all_results.append(test_docker_compose_yml(sid))
            cleanup_session(sid)

    tp = sum(r.passed  for r in all_results)
    tf = sum(r.failed  for r in all_results)
    ts = sum(r.skipped for r in all_results)
    print(f"\n{'═'*62}")
    print(f"  CODE COMPREHENSION TESTS COMPLETE")
    print(f"  Passed: {tp}/{tp+tf}  |  Skipped: {ts}")
    print(f"{'═'*62}\n")
    sys.exit(0 if tf == 0 else 1)
