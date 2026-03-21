import { PrismaClient } from "../lib/generated/prisma";
import { hash } from "bcryptjs";

const prisma = new PrismaClient();

// ─── Helpers ──────────────────────────────────────────────────────────────────

const future = (days: number) => new Date(Date.now() + days * 86_400_000);

async function main() {
  console.log("🌱 Seeding database...\n");

  // ─── Clean (FK order matters) ───────────────────────────────────────────────
  await prisma.chatMessage.deleteMany();
  await prisma.codeBase.deleteMany();
  await prisma.code.deleteMany();
  await prisma.repository.deleteMany();
  await prisma.session.deleteMany();
  await prisma.account.deleteMany();
  await prisma.verificationToken.deleteMany();
  await prisma.user.deleteMany();
  console.log("🧹 Cleared all tables\n");

  // ─── Users ──────────────────────────────────────────────────────────────────
  const pw = await hash("password123", 12);

  const alice = await prisma.user.create({
    data: { name: "Alice Johnson", email: "alice@example.com", emailVerified: new Date(), image: "https://avatars.githubusercontent.com/u/1?v=4", password: pw },
  });
  const bob = await prisma.user.create({
    data: { name: "Bob Smith",     email: "bob@example.com",   emailVerified: new Date(), image: "https://avatars.githubusercontent.com/u/2?v=4", password: pw },
  });
  const carol = await prisma.user.create({
    data: { name: "Carol White",   email: "carol@example.com", emailVerified: new Date(), image: "https://avatars.githubusercontent.com/u/3?v=4", password: pw },
  });
  const david = await prisma.user.create({
    data: { name: "David Kumar",   email: "david@example.com", emailVerified: new Date(), image: "https://avatars.githubusercontent.com/u/4?v=4", password: pw },
  });
  const eve = await prisma.user.create({
    data: { name: "Eve Martinez",  email: "eve@example.com",   emailVerified: new Date(), image: "https://avatars.githubusercontent.com/u/5?v=4", password: pw },
  });
  console.log("✅ Created 5 users");

  // ─── Accounts (OAuth) ───────────────────────────────────────────────────────
  await prisma.account.createMany({
    data: [
      { userId: alice.id, type: "oauth",       provider: "github",   providerAccountId: "gh_alice_001",    access_token: "gho_alice_fake",  token_type: "bearer", scope: "read:user,repo" },
      { userId: bob.id,   type: "oauth",       provider: "google",   providerAccountId: "google_bob_001",  access_token: "ya29_bob_fake",   token_type: "Bearer", scope: "openid email profile", expires_at: Math.floor(Date.now() / 1000) + 3600 },
      { userId: carol.id, type: "oauth",       provider: "github",   providerAccountId: "gh_carol_001",   access_token: "gho_carol_fake",  token_type: "bearer", scope: "read:user,repo" },
      { userId: david.id, type: "credentials", provider: "password", providerAccountId: "david_cred_001" },
      { userId: eve.id,   type: "oauth",       provider: "google",   providerAccountId: "google_eve_001",  access_token: "ya29_eve_fake",   token_type: "Bearer", scope: "openid email profile" },
    ],
  });
  console.log("✅ Created 5 OAuth / credential accounts");

  // ─── Sessions ───────────────────────────────────────────────────────────────
  await prisma.session.createMany({
    data: [
      { sessionToken: `sess_alice_${Date.now()}`,   userId: alice.id, expires: future(30) },
      { sessionToken: `sess_bob_${Date.now() + 1}`, userId: bob.id,   expires: future(7)  },
      { sessionToken: `sess_carol_${Date.now() + 2}`,userId: carol.id,expires: future(14) },
      { sessionToken: `sess_david_${Date.now() + 3}`,userId: david.id,expires: future(30) },
      { sessionToken: `sess_eve_${Date.now() + 4}`,  userId: eve.id,  expires: future(7)  },
    ],
  });
  console.log("✅ Created 5 sessions");

  // ─── Verification Tokens ────────────────────────────────────────────────────
  await prisma.verificationToken.createMany({
    data: [
      { identifier: carol.email!, token: `verify_carol_${Date.now()}`,  expires: future(1) },
      { identifier: david.email!, token: `verify_david_${Date.now() + 1}`, expires: future(1) },
    ],
  });
  console.log("✅ Created 2 verification tokens");

  // ─── Repositories ───────────────────────────────────────────────────────────
  const repoTcpUdp = await prisma.repository.create({ data: {
    name: "tcp-udp-server",       ownerId: alice.id, language: "Python",     license: "MIT",
    description: "Raw TCP and UDP socket servers in Python with asyncio.",
    url: "https://github.com/alice/tcp-udp-server",
    stars: 820, forks: 94, issues: 8, updated: new Date("2025-03-12T09:00:00Z"),
  }});

  const repoHttpRest = await prisma.repository.create({ data: {
    name: "http-rest-api",        ownerId: bob.id,   language: "Python",     license: "MIT",
    description: "FastAPI REST service with JWT auth, rate limiting, and OpenAPI docs.",
    url: "https://github.com/bob/http-rest-api",
    stars: 1540, forks: 210, issues: 22, updated: new Date("2025-03-14T11:30:00Z"),
  }});

  const repoWsChat = await prisma.repository.create({ data: {
    name: "websocket-chat",       ownerId: carol.id, language: "Python",     license: "Apache-2.0",
    description: "Real-time WebSocket chat server using asyncio and aiohttp.",
    url: "https://github.com/carol/websocket-chat",
    stars: 430, forks: 55, issues: 6, updated: new Date("2025-02-28T08:00:00Z"),
  }});

  const repoGrpc = await prisma.repository.create({ data: {
    name: "grpc-microservice",    ownerId: david.id, language: "Python",     license: "MIT",
    description: "Python gRPC service with Protobuf, health checks, and TLS.",
    url: "https://github.com/david/grpc-microservice",
    stars: 660, forks: 78, issues: 11, updated: new Date("2025-03-05T14:00:00Z"),
  }});

  const repoRedis = await prisma.repository.create({ data: {
    name: "redis-queue-worker",   ownerId: eve.id,   language: "Python",     license: "MIT",
    description: "Background job queue using Redis Streams and asyncio workers.",
    url: "https://github.com/eve/redis-queue-worker",
    stars: 310, forks: 42, issues: 4, updated: new Date("2025-03-08T10:00:00Z"),
  }});

  const repoSaas = await prisma.repository.create({ data: {
    name: "next-saas-starter",    ownerId: alice.id, language: "TypeScript", license: "MIT",
    description: "Next.js 14 SaaS starter with Prisma, NextAuth, and Tailwind CSS.",
    url: "https://github.com/alice/next-saas-starter",
    stars: 1240, forks: 198, issues: 14, updated: new Date("2025-03-10T10:00:00Z"),
  }});

  const repoGraphql = await prisma.repository.create({ data: {
    name: "graphql-api-server",   ownerId: bob.id,   language: "TypeScript", license: "MIT",
    description: "GraphQL API with Apollo Server, Prisma, and subscription support.",
    url: "https://github.com/bob/graphql-api-server",
    stars: 890, forks: 112, issues: 9, updated: new Date("2025-03-09T12:00:00Z"),
  }});

  const repoRustHttp = await prisma.repository.create({ data: {
    name: "rust-http-server",     ownerId: carol.id, language: "Rust",       license: "MIT",
    description: "Minimal async HTTP server with Hyper and Tokio.",
    url: "https://github.com/carol/rust-http-server",
    stars: 3870, forks: 412, issues: 27, updated: new Date("2025-03-15T14:45:00Z"),
  }});

  const repoRustTcp = await prisma.repository.create({ data: {
    name: "rust-tcp-echo",        ownerId: david.id, language: "Rust",       license: "MIT",
    description: "High-performance TCP echo server in Rust using Tokio.",
    url: "https://github.com/david/rust-tcp-echo",
    stars: 540, forks: 67, issues: 5, updated: new Date("2025-03-11T09:30:00Z"),
  }});

  const repoGoMicro = await prisma.repository.create({ data: {
    name: "go-microservices",     ownerId: eve.id,   language: "Go",         license: "MIT",
    description: "Go microservices with gRPC, Docker, and Postgres.",
    url: "https://github.com/eve/go-microservices",
    stars: 670, forks: 88, issues: 11, updated: new Date("2025-03-01T11:20:00Z"),
  }});

  const repoGoUdp = await prisma.repository.create({ data: {
    name: "go-udp-broadcast",     ownerId: alice.id, language: "Go",         license: "MIT",
    description: "UDP multicast and broadcast server in Go.",
    url: "https://github.com/alice/go-udp-broadcast",
    stars: 220, forks: 30, issues: 3, updated: new Date("2025-02-20T07:00:00Z"),
  }});

  const repoCpp = await prisma.repository.create({ data: {
    name: "cpp-socket-server",    ownerId: bob.id,   language: "C++",        license: "GPL-3.0",
    description: "Multi-threaded TCP server in C++ using POSIX sockets and epoll.",
    url: "https://github.com/bob/cpp-socket-server",
    stars: 1100, forks: 145, issues: 18, updated: new Date("2025-03-07T16:00:00Z"),
  }});

  const repoJava = await prisma.repository.create({ data: {
    name: "java-spring-rest",     ownerId: carol.id, language: "Java",       license: "Apache-2.0",
    description: "Spring Boot REST API with JPA, JWT security, and Swagger UI.",
    url: "https://github.com/carol/java-spring-rest",
    stars: 760, forks: 98, issues: 13, updated: new Date("2025-03-06T13:00:00Z"),
  }});

  const repoDevops = await prisma.repository.create({ data: {
    name: "devops-scripts",       ownerId: david.id, language: "Shell",      license: "MIT",
    description: "Shell scripts for CI/CD, log rotation, and server provisioning.",
    url: "https://github.com/david/devops-scripts",
    stars: 380, forks: 50, issues: 7, updated: new Date("2025-03-04T10:00:00Z"),
  }});

  const repoMl = await prisma.repository.create({ data: {
    name: "ml-pipeline-toolkit",  ownerId: eve.id,   language: "Python",     license: "GPL-3.0",
    description: "Reproducible ML pipelines with DVC, MLflow, and Docker.",
    url: "https://github.com/eve/ml-pipeline-toolkit",
    stars: 920, forks: 134, issues: 19, updated: new Date("2025-01-05T09:00:00Z"),
  }});

  console.log("✅ Created 15 repositories");

  // ─── Chat Messages ───────────────────────────────────────────────────────────
  await prisma.chatMessage.createMany({
    data: [
      // tcp-udp-server
      { content: "How does the TCP echo server handle concurrent connections?",                        userId: bob.id,   repositoryId: repoTcpUdp.id  },
      { content: "Each connection spawns a coroutine via asyncio.start_server — fully non-blocking.", userId: alice.id, repositoryId: repoTcpUdp.id  },
      { content: "What's the buffer size for the UDP server?",                                        userId: carol.id, repositoryId: repoTcpUdp.id  },
      { content: "1024 bytes per datagram by default, configurable via BUFFER_SIZE constant.",        userId: alice.id, repositoryId: repoTcpUdp.id  },
      // http-rest-api
      { content: "How does the JWT authentication work here?",                                        userId: carol.id, repositoryId: repoHttpRest.id },
      { content: "Tokens are HS256-signed with a 30-minute expiry. Login at /auth/login.",            userId: bob.id,   repositoryId: repoHttpRest.id },
      { content: "Does this have rate limiting?",                                                     userId: david.id, repositoryId: repoHttpRest.id },
      { content: "Yes — sliding window per IP, 100 req/min, enforced in middleware.",                 userId: bob.id,   repositoryId: repoHttpRest.id },
      // websocket-chat
      { content: "How do messages get broadcast to all connected clients?",                           userId: alice.id, repositoryId: repoWsChat.id   },
      { content: "All WebSocketResponse objects live in a set; asyncio.gather fans out to each.",     userId: carol.id, repositoryId: repoWsChat.id   },
      // grpc-microservice
      { content: "What does StreamSum demonstrate?",                                                  userId: eve.id,   repositoryId: repoGrpc.id     },
      { content: "Client-side streaming — the client sends a stream of numbers, server returns sum.", userId: david.id, repositoryId: repoGrpc.id     },
      // redis-queue-worker
      { content: "How does the worker avoid processing the same job twice after a crash?",            userId: alice.id, repositoryId: repoRedis.id    },
      { content: "XREADGROUP + XACK — the message stays pending until explicitly acked.",             userId: eve.id,   repositoryId: repoRedis.id    },
      // next-saas-starter
      { content: "How is authentication set up in this repo?",                                        userId: bob.id,   repositoryId: repoSaas.id     },
      { content: "NextAuth with GitHub, Google, and Credentials. PrismaAdapter stores sessions.",     userId: alice.id, repositoryId: repoSaas.id     },
      { content: "What happens if the user is not logged in on the dashboard?",                       userId: carol.id, repositoryId: repoSaas.id     },
      { content: "The page calls auth() and redirects to /login if no session exists.",               userId: alice.id, repositoryId: repoSaas.id     },
      // graphql-api-server
      { content: "How do GraphQL subscriptions work?",                                                userId: carol.id, repositoryId: repoGraphql.id  },
      { content: "PubSub from graphql-subscriptions publishes POST_PUBLISHED on every publishPost.", userId: bob.id,   repositoryId: repoGraphql.id  },
      // rust-http-server
      { content: "This Rust server is incredibly fast. What benchmarks did you run?",                userId: alice.id, repositoryId: repoRustHttp.id },
      { content: "~180k req/s with wrk, 12 threads, 400 connections on an M2 Mac.",                  userId: carol.id, repositoryId: repoRustHttp.id },
      { content: "Does this support async handlers?",                                                 userId: david.id, repositoryId: repoRustHttp.id },
      { content: "Full async via Tokio. See /examples for handler patterns.",                         userId: carol.id, repositoryId: repoRustHttp.id },
      // rust-tcp-echo
      { content: "Why does the server use tokio::spawn per connection?",                              userId: eve.id,   repositoryId: repoRustTcp.id  },
      { content: "tokio::spawn creates a lightweight async task so the accept loop never blocks.",    userId: david.id, repositoryId: repoRustTcp.id  },
      // go-microservices
      { content: "Love the gRPC setup. Planning to add service mesh support?",                        userId: alice.id, repositoryId: repoGoMicro.id  },
      { content: "Yes, Istio integration is on the Q2 roadmap. Watch the issue tracker.",             userId: eve.id,   repositoryId: repoGoMicro.id  },
      // go-udp-broadcast
      { content: "How does the broadcast reach all LAN hosts?",                                       userId: bob.id,   repositoryId: repoGoUdp.id    },
      { content: "It dials 255.255.255.255:9999 — the OS delivers to every host on the subnet.",      userId: alice.id, repositoryId: repoGoUdp.id    },
      // cpp-socket-server
      { content: "How does the C++ server handle many clients without blocking?",                     userId: carol.id, repositoryId: repoCpp.id      },
      { content: "std::thread::detach() per accepted fd — main loop never waits on a client.",        userId: bob.id,   repositoryId: repoCpp.id      },
      // java-spring-rest
      { content: "How is JWT validation handled on each request?",                                    userId: david.id, repositoryId: repoJava.id     },
      { content: "JwtFilter extends OncePerRequestFilter and validates the Bearer token before auth.",userId: carol.id, repositoryId: repoJava.id     },
      // devops-scripts
      { content: "What happens if the kubectl rollout fails?",                                        userId: eve.id,   repositoryId: repoDevops.id   },
      { content: "set -euo pipefail aborts the script immediately on any non-zero exit.",             userId: david.id, repositoryId: repoDevops.id   },
      // ml-pipeline-toolkit
      { content: "How does DVC track training data without committing it to git?",                    userId: alice.id, repositoryId: repoMl.id       },
      { content: "DVC hashes files and stores them in a cache; only the .dvc pointer files go to git.",userId: eve.id,  repositoryId: repoMl.id       },
    ],
  });
  console.log("✅ Created 38 chat messages");

  // ─── Code entries ────────────────────────────────────────────────────────────

  // ── tcp-udp-server ──────────────────────────────────────────────────────────
  const codeTcp = await prisma.code.create({ data: { repoName: "tcp-udp-server", amount: 5, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Python",   filename: "tcp_server.py",  route: "/src/tcp_server.py",  codeId: codeTcp.id, text: `import asyncio

HOST = "0.0.0.0"
PORT = 9000
BUFFER_SIZE = 4096

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"[TCP] New connection from {addr}")
    try:
        while True:
            data = await reader.read(BUFFER_SIZE)
            if not data:
                break
            message = data.decode().strip()
            writer.write(f"ECHO: {message}\\n".encode())
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        print(f"[TCP] Listening on {HOST}:{PORT}")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())` },
    { language: "Python",   filename: "udp_server.py",  route: "/src/udp_server.py",  codeId: codeTcp.id, text: `import asyncio

HOST = "0.0.0.0"
PORT = 9001

class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple):
        message = data.decode().strip()
        self.transport.sendto(f"UDP_ECHO: {message}".encode(), addr)

    def error_received(self, exc):
        print(f"[UDP] Error: {exc}")

async def main():
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(), local_addr=(HOST, PORT)
    )
    try:
        await asyncio.sleep(float("inf"))
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())` },
    { language: "Python",   filename: "tcp_client.py",  route: "/src/tcp_client.py",  codeId: codeTcp.id, text: `import asyncio

async def tcp_client(messages: list[str]):
    reader, writer = await asyncio.open_connection("127.0.0.1", 9000)
    for msg in messages:
        writer.write(f"{msg}\\n".encode())
        await writer.drain()
        resp = await reader.readline()
        print(f"[CLIENT] {resp.decode().strip()}")
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(tcp_client(["Hello", "Ping", "World"]))` },
    { language: "Python",   filename: "udp_client.py",  route: "/src/udp_client.py",  codeId: codeTcp.id, text: `import socket

def udp_client(messages: list[str]):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(2.0)
        for msg in messages:
            sock.sendto(msg.encode(), ("127.0.0.1", 9001))
            try:
                data, _ = sock.recvfrom(1024)
                print(f"[UDP CLIENT] {data.decode()}")
            except socket.timeout:
                print(f"[UDP CLIENT] Timeout: {msg}")

if __name__ == "__main__":
    udp_client(["Ping", "Hello UDP", "Test packet"])` },
    { language: "Markdown", filename: "README.md",       route: "/README.md",           codeId: codeTcp.id, text: `# TCP / UDP Server

Async TCP echo server and UDP datagram server in Python asyncio.

## Run
\`\`\`bash
python src/tcp_server.py   # port 9000
python src/udp_server.py   # port 9001
python src/tcp_client.py
python src/udp_client.py
\`\`\`` },
  ]});

  // ── http-rest-api ───────────────────────────────────────────────────────────
  const codeHttp = await prisma.code.create({ data: { repoName: "http-rest-api", amount: 5, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Python", filename: "main.py",         route: "/app/main.py",                      codeId: codeHttp.id, text: `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, items
from app.database import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI(title="REST API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router,  prefix="/auth",  tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/health")
def health(): return {"status": "ok"}` },
    { language: "Python", filename: "auth.py",          route: "/app/routers/auth.py",              codeId: codeHttp.id, text: `from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "super-secret-key"
ALGORITHM  = "HS256"

def create_token(data: dict) -> str:
    return jwt.encode({**data, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    # validate user then issue token
    return {"access_token": create_token({"sub": form.username}), "token_type": "bearer"}` },
    { language: "Python", filename: "models.py",        route: "/app/models.py",                    codeId: codeHttp.id, text: `from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id              = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email           = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    items           = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name        = Column(String, nullable=False)
    price       = Column(Float, default=0.0)
    owner_id    = Column(String, ForeignKey("users.id"))
    owner       = relationship("User", back_populates="items")` },
    { language: "Python", filename: "rate_limiter.py",  route: "/app/middleware/rate_limiter.py",   codeId: codeHttp.id, text: `import time
from collections import defaultdict
from fastapi import Request, HTTPException

_log: dict[str, list[float]] = defaultdict(list)
WINDOW = 60
LIMIT  = 100

def rate_limit(request: Request):
    ip  = request.client.host
    now = time.time()
    _log[ip] = [t for t in _log[ip] if now - t < WINDOW]
    _log[ip].append(now)
    if len(_log[ip]) > LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")` },
    { language: "YAML",   filename: "docker-compose.yml", route: "/docker-compose.yml",             codeId: codeHttp.id, text: `version: "3.9"
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://api:api_pass@db:5432/apidb
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: api
      POSTGRES_PASSWORD: api_pass
      POSTGRES_DB: apidb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U api"]
      interval: 5s
      retries: 10` },
  ]});

  // ── websocket-chat ──────────────────────────────────────────────────────────
  const codeWs = await prisma.code.create({ data: { repoName: "websocket-chat", amount: 3, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Python",   filename: "server.py",  route: "/server.py", codeId: codeWs.id, text: `import asyncio, json
from aiohttp import web

clients: set[web.WebSocketResponse] = set()

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            payload = json.loads(msg.data)
            broadcast = json.dumps({"user": payload.get("user"), "message": payload.get("message")})
            await asyncio.gather(*[c.send_str(broadcast) for c in clients if not c.closed], return_exceptions=True)
    clients.discard(ws)
    return ws

app = web.Application()
app.router.add_get("/ws", ws_handler)
app.router.add_get("/health", lambda r: web.json_response({"ok": True}))

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8765)` },
    { language: "Python",   filename: "client.py",  route: "/client.py", codeId: codeWs.id, text: `import asyncio, json, aiohttp

async def chat_client(username: str, messages: list[str]):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("ws://localhost:8765/ws") as ws:
            for msg in messages:
                await ws.send_str(json.dumps({"user": username, "message": msg}))
                resp = await ws.receive_str()
                print(f"[{username}] {resp}")
                await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(chat_client("Alice", ["Hello!", "How are you?", "Bye!"]))` },
    { language: "Markdown", filename: "README.md",   route: "/README.md", codeId: codeWs.id, text: `# WebSocket Chat Server

Real-time broadcast chat using Python aiohttp WebSockets.

## Run
\`\`\`bash
pip install aiohttp
python server.py     # ws://localhost:8765/ws
python client.py
\`\`\`` },
  ]});

  // ── grpc-microservice ───────────────────────────────────────────────────────
  const codeGrpc = await prisma.code.create({ data: { repoName: "grpc-microservice", amount: 4, subscription: true } });
  await prisma.codeBase.createMany({ data: [
    { language: "Protobuf", filename: "service.proto", route: "/proto/service.proto", codeId: codeGrpc.id, text: `syntax = "proto3";
package calculator;

service Calculator {
  rpc Add      (BinaryRequest)        returns (NumberReply);
  rpc Subtract (BinaryRequest)        returns (NumberReply);
  rpc Multiply (BinaryRequest)        returns (NumberReply);
  rpc Divide   (BinaryRequest)        returns (NumberReply);
  rpc StreamSum(stream NumberRequest) returns (NumberReply);
}

message BinaryRequest  { double a = 1; double b = 2; }
message NumberRequest  { double value = 1; }
message NumberReply    { double result = 1; string error = 2; }` },
    { language: "Python", filename: "server.py", route: "/server.py", codeId: codeGrpc.id, text: `import grpc
from concurrent import futures
import calculator_pb2, calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, req, ctx):      return calculator_pb2.NumberReply(result=req.a + req.b)
    def Subtract(self, req, ctx): return calculator_pb2.NumberReply(result=req.a - req.b)
    def Multiply(self, req, ctx): return calculator_pb2.NumberReply(result=req.a * req.b)
    def Divide(self, req, ctx):
        if req.b == 0:
            ctx.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return calculator_pb2.NumberReply(error="Division by zero")
        return calculator_pb2.NumberReply(result=req.a / req.b)
    def StreamSum(self, req_iter, ctx):
        return calculator_pb2.NumberReply(result=sum(r.value for r in req_iter))

def serve():
    s = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), s)
    s.add_insecure_port("[::]:50051")
    s.start()
    print("[gRPC] Listening on :50051")
    s.wait_for_termination()

if __name__ == "__main__": serve()` },
    { language: "Python", filename: "client.py", route: "/client.py", codeId: codeGrpc.id, text: `import grpc, calculator_pb2, calculator_pb2_grpc

with grpc.insecure_channel("localhost:50051") as ch:
    stub = calculator_pb2_grpc.CalculatorStub(ch)
    print("Add(10,5)     =", stub.Add(calculator_pb2.BinaryRequest(a=10, b=5)).result)
    print("Divide(10,0)  =", stub.Divide(calculator_pb2.BinaryRequest(a=10, b=0)).error)
    nums = [calculator_pb2.NumberRequest(value=i) for i in range(1, 6)]
    print("StreamSum(1..5)=", stub.StreamSum(iter(nums)).result)` },
    { language: "YAML", filename: "docker-compose.yml", route: "/docker-compose.yml", codeId: codeGrpc.id, text: `version: "3.9"
services:
  grpc-server:
    build: .
    ports: ["50051:50051"]` },
  ]});

  // ── redis-queue-worker ──────────────────────────────────────────────────────
  const codeRedis = await prisma.code.create({ data: { repoName: "redis-queue-worker", amount: 3, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Python", filename: "producer.py", route: "/producer.py", codeId: codeRedis.id, text: `import asyncio, json
import redis.asyncio as aioredis

STREAM_KEY = "job_stream"

async def produce(jobs: list[dict]):
    r = await aioredis.from_url("redis://localhost:6379", decode_responses=True)
    for job in jobs:
        msg_id = await r.xadd(STREAM_KEY, {"payload": json.dumps(job)}, maxlen=1000)
        print(f"[PRODUCER] {msg_id}: {job}")
    await r.aclose()

if __name__ == "__main__":
    asyncio.run(produce([
        {"type": "email",  "to": "user@example.com"},
        {"type": "resize", "image_id": "img_001", "width": 800},
        {"type": "report", "report_id": "rep_042", "format": "pdf"},
    ]))` },
    { language: "Python", filename: "worker.py", route: "/worker.py", codeId: codeRedis.id, text: `import asyncio, json
import redis.asyncio as aioredis

STREAM_KEY = "job_stream"
GROUP      = "workers"
CONSUMER   = "worker-1"

async def process(job: dict):
    print(f"[WORKER] Processing {job['type']}: {job}")
    await asyncio.sleep(0.1)

async def consume():
    r = await aioredis.from_url("redis://localhost:6379", decode_responses=True)
    try:
        await r.xgroup_create(STREAM_KEY, GROUP, id="0", mkstream=True)
    except Exception: pass
    while True:
        messages = await r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=5, block=2000)
        for _, entries in (messages or []):
            for msg_id, fields in entries:
                await process(json.loads(fields["payload"]))
                await r.xack(STREAM_KEY, GROUP, msg_id)

if __name__ == "__main__": asyncio.run(consume())` },
    { language: "YAML", filename: "docker-compose.yml", route: "/docker-compose.yml", codeId: codeRedis.id, text: `version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server --appendonly yes
  worker:
    build: .
    command: python worker.py
    environment:
      REDIS_URL: redis://redis:6379
    depends_on: [redis]
    deploy:
      replicas: 3` },
  ]});

  // ── next-saas-starter ───────────────────────────────────────────────────────
  const codeSaas = await prisma.code.create({ data: { repoName: "next-saas-starter", amount: 5, subscription: true } });
  await prisma.codeBase.createMany({ data: [
    { language: "TypeScript", filename: "auth.ts",      route: "/lib/auth.ts",              codeId: codeSaas.id, text: `import NextAuth from "next-auth";
import GithubProvider from "next-auth/providers/github";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "./prisma";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GithubProvider({ clientId: process.env.GITHUB_ID!, clientSecret: process.env.GITHUB_SECRET! }),
    GoogleProvider({ clientId: process.env.GOOGLE_ID!, clientSecret: process.env.GOOGLE_SECRET! }),
    CredentialsProvider({
      name: "credentials",
      credentials: { email: {}, password: { type: "password" } },
      async authorize(credentials) {
        const user = await prisma.user.findUnique({ where: { email: credentials.email as string } });
        if (!user?.password) return null;
        return await bcrypt.compare(credentials.password as string, user.password) ? user : null;
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
});` },
    { language: "TypeScript", filename: "prisma.ts",    route: "/lib/prisma.ts",            codeId: codeSaas.id, text: `import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient | undefined };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({ log: process.env.NODE_ENV === "development" ? ["query", "warn", "error"] : ["error"] });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;` },
    { language: "TypeScript", filename: "page.tsx",     route: "/app/dashboard/page.tsx",   codeId: codeSaas.id, text: `import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user?.email) redirect("/login");

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
    include: { repositories: { orderBy: { updatedAt: "desc" }, take: 5 } },
  });

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Welcome, {user?.name}</h1>
      {user?.repositories.map(repo => (
        <div key={repo.id} className="border rounded-lg p-4 mb-3">
          <h3 className="font-medium">{repo.name}</h3>
          <p className="text-sm text-gray-500">{repo.description}</p>
        </div>
      ))}
    </main>
  );
}` },
    { language: "CSS",        filename: "globals.css", route: "/app/globals.css",           codeId: codeSaas.id, text: `@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
}

@layer base {
  body { @apply bg-background text-foreground; }
}` },
    { language: "JSON",       filename: ".env.example", route: "/.env.example",             codeId: codeSaas.id, text: `DATABASE_URL=postgresql://user:pass@localhost:5432/saasdb
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
GITHUB_ID=your-github-client-id
GITHUB_SECRET=your-github-client-secret
GOOGLE_ID=your-google-client-id
GOOGLE_SECRET=your-google-client-secret` },
  ]});

  // ── graphql-api-server ──────────────────────────────────────────────────────
  const codeGql = await prisma.code.create({ data: { repoName: "graphql-api-server", amount: 3, subscription: true } });
  await prisma.codeBase.createMany({ data: [
    { language: "TypeScript", filename: "schema.ts",    route: "/src/schema.ts",   codeId: codeGql.id, text: `import { gql } from "apollo-server-express";

export const typeDefs = gql\`
  type User  { id: ID!  email: String!  name: String  posts: [Post!]! }
  type Post  { id: ID!  title: String!  content: String  published: Boolean!  author: User! }
  type Query {
    users: [User!]!         user(id: ID!): User
    posts(published: Boolean): [Post!]!   post(id: ID!): Post
  }
  type Mutation {
    createUser(email: String!, name: String): User!
    createPost(title: String!, content: String, authorId: ID!): Post!
    publishPost(id: ID!): Post!
    deletePost(id: ID!): Boolean!
  }
  type Subscription { postPublished: Post! }
\`;` },
    { language: "TypeScript", filename: "resolvers.ts", route: "/src/resolvers.ts", codeId: codeGql.id, text: `import { PubSub } from "graphql-subscriptions";
import { prisma } from "./prisma";

const pubsub = new PubSub();
const POST_PUBLISHED = "POST_PUBLISHED";

export const resolvers = {
  Query: {
    users: () => prisma.user.findMany({ include: { posts: true } }),
    posts: (_: any, { published }: { published?: boolean }) =>
      prisma.post.findMany({ where: published !== undefined ? { published } : {}, include: { author: true } }),
  },
  Mutation: {
    createPost: (_: any, args: any) =>
      prisma.post.create({ data: { ...args, published: false }, include: { author: true } }),
    publishPost: async (_: any, { id }: { id: string }) => {
      const post = await prisma.post.update({ where: { id }, data: { published: true }, include: { author: true } });
      pubsub.publish(POST_PUBLISHED, { postPublished: post });
      return post;
    },
  },
  Subscription: {
    postPublished: { subscribe: () => pubsub.asyncIterator([POST_PUBLISHED]) },
  },
};` },
    { language: "TypeScript", filename: "server.ts",    route: "/src/server.ts",   codeId: codeGql.id, text: `import express from "express";
import { ApolloServer } from "apollo-server-express";
import { makeExecutableSchema } from "@graphql-tools/schema";
import { typeDefs } from "./schema";
import { resolvers } from "./resolvers";

async function bootstrap() {
  const app    = express();
  const schema = makeExecutableSchema({ typeDefs, resolvers });
  const apollo = new ApolloServer({ schema });
  await apollo.start();
  apollo.applyMiddleware({ app });
  app.listen(4000, () => console.log("GraphQL ready at http://localhost:4000/graphql"));
}

bootstrap();` },
  ]});

  // ── rust-http-server ────────────────────────────────────────────────────────
  const codeRustHttp = await prisma.code.create({ data: { repoName: "rust-http-server", amount: 3, subscription: true } });
  await prisma.codeBase.createMany({ data: [
    { language: "Rust",     filename: "main.rs",     route: "/src/main.rs", codeId: codeRustHttp.id, text: `use tokio::net::TcpListener;
use std::convert::Infallible;
use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Request, Response, Server};

async fn handle(_req: Request<Body>) -> Result<Response<Body>, Infallible> {
    Ok(Response::new(Body::from("Hello, World!")))
}

#[tokio::main]
async fn main() {
    let addr = ([0, 0, 0, 0], 3000).into();
    let make_svc = make_service_fn(|_conn| async { Ok::<_, Infallible>(service_fn(handle)) });
    let server = Server::bind(&addr).serve(make_svc);
    println!("Listening on http://{}", addr);
    server.await.unwrap();
}` },
    { language: "TOML",     filename: "Cargo.toml",  route: "/Cargo.toml",  codeId: codeRustHttp.id, text: `[package]
name    = "rust-http-server"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
hyper = { version = "0.14", features = ["full"] }` },
    { language: "Markdown", filename: "README.md",   route: "/README.md",   codeId: codeRustHttp.id, text: `# Rust HTTP Server

Minimal async HTTP server built with Hyper and Tokio.

## Run
\`\`\`bash
cargo run
\`\`\`

Server starts on http://localhost:3000` },
  ]});

  // ── rust-tcp-echo ───────────────────────────────────────────────────────────
  const codeRustTcp = await prisma.code.create({ data: { repoName: "rust-tcp-echo", amount: 3, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Rust", filename: "main.rs",     route: "/src/main.rs",     codeId: codeRustTcp.id, text: `use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:7000").await?;
    println!("[TCP ECHO] Listening on :7000");
    loop {
        let (stream, addr) = listener.accept().await?;
        println!("[TCP ECHO] Connection from {}", addr);
        tokio::spawn(handle(stream));
    }
}

async fn handle(mut s: TcpStream) {
    let mut buf = vec![0u8; 4096];
    loop {
        match s.read(&mut buf).await {
            Ok(0) | Err(_) => break,
            Ok(n) => { let _ = s.write_all(&buf[..n]).await; }
        }
    }
}` },
    { language: "Rust", filename: "udp_echo.rs", route: "/src/udp_echo.rs", codeId: codeRustTcp.id, text: `use tokio::net::UdpSocket;

pub async fn run_udp_echo() -> anyhow::Result<()> {
    let socket = UdpSocket::bind("0.0.0.0:7001").await?;
    println!("[UDP ECHO] Listening on :7001");
    let mut buf = vec![0u8; 1024];
    loop {
        let (len, addr) = socket.recv_from(&mut buf).await?;
        socket.send_to(&buf[..len], addr).await?;
    }
}` },
    { language: "TOML", filename: "Cargo.toml",  route: "/Cargo.toml",      codeId: codeRustTcp.id, text: `[package]
name    = "rust-tcp-echo"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio  = { version = "1", features = ["full"] }
anyhow = "1"` },
  ]});

  // ── go-microservices ────────────────────────────────────────────────────────
  const codeGoMicro = await prisma.code.create({ data: { repoName: "go-microservices", amount: 4, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Go",       filename: "main.go",           route: "/cmd/api/main.go",      codeId: codeGoMicro.id, text: `package main

import (
    "log"; "net/http"; "os"
    "github.com/gorilla/mux"
)

func main() {
    r := mux.NewRouter()
    r.HandleFunc("/health",          healthHandler).Methods("GET")
    r.HandleFunc("/api/users",       listUsersHandler).Methods("GET")
    r.HandleFunc("/api/users/{id}",  getUserHandler).Methods("GET")
    r.HandleFunc("/api/users",       createUserHandler).Methods("POST")
    port := os.Getenv("PORT"); if port == "" { port = "8080" }
    log.Printf("API on :%s", port)
    log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(\`{"status":"ok"}\`))
}` },
    { language: "Go",       filename: "udp_broadcast.go",  route: "/cmd/broadcast/main.go",codeId: codeGoMicro.id, text: `package main

import ("fmt"; "net"; "time")

func main() {
    addr, _ := net.ResolveUDPAddr("udp", "255.255.255.255:9999")
    conn, _ := net.DialUDP("udp", nil, addr)
    defer conn.Close()
    for i := 0; ; i++ {
        msg := fmt.Sprintf("BROADCAST #%d @ %s", i, time.Now().Format(time.RFC3339))
        conn.Write([]byte(msg))
        fmt.Println("[SENT]", msg)
        time.Sleep(2 * time.Second)
    }
}` },
    { language: "YAML",     filename: "docker-compose.yml",route: "/docker-compose.yml",   codeId: codeGoMicro.id, text: `version: "3.9"
services:
  api:
    build: .
    ports: ["8080:8080"]
    environment:
      PORT: "8080"
      DATABASE_URL: postgres://admin:secret@postgres:5432/appdb
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      retries: 10` },
    { language: "Go",       filename: "go.mod",            route: "/go.mod",               codeId: codeGoMicro.id, text: `module github.com/carol/go-microservices

go 1.22

require (
    github.com/gorilla/mux v1.8.1
    github.com/lib/pq      v1.10.9
)` },
  ]});

  // ── go-udp-broadcast ────────────────────────────────────────────────────────
  const codeGoUdp = await prisma.code.create({ data: { repoName: "go-udp-broadcast", amount: 2, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Go",       filename: "main.go",    route: "/main.go",    codeId: codeGoUdp.id, text: `package main

import ("fmt"; "net"; "os"; "time")

func main() {
    addr, err := net.ResolveUDPAddr("udp", "255.255.255.255:9999")
    if err != nil { fmt.Println(err); os.Exit(1) }
    conn, err := net.DialUDP("udp", nil, addr)
    if err != nil { fmt.Println(err); os.Exit(1) }
    defer conn.Close()
    for i := 0; ; i++ {
        msg := fmt.Sprintf("HELLO from broadcaster #%d", i)
        conn.Write([]byte(msg))
        fmt.Println("[BROADCAST]", msg)
        time.Sleep(2 * time.Second)
    }
}` },
    { language: "Markdown", filename: "README.md",  route: "/README.md",  codeId: codeGoUdp.id, text: `# Go UDP Broadcast

Sends UDP broadcast datagrams to 255.255.255.255:9999 every 2 seconds.

## Run
\`\`\`bash
go run main.go
\`\`\`` },
  ]});

  // ── cpp-socket-server ───────────────────────────────────────────────────────
  const codeCpp = await prisma.code.create({ data: { repoName: "cpp-socket-server", amount: 3, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "C++",      filename: "server.cpp",     route: "/src/server.cpp",     codeId: codeCpp.id, text: `#include <iostream>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

const int PORT = 8888;

void handle_client(int fd) {
    char buf[4096];
    while (true) {
        ssize_t n = recv(fd, buf, sizeof(buf)-1, 0);
        if (n <= 0) break;
        buf[n] = '\\0';
        std::string resp = "ECHO: " + std::string(buf, n);
        send(fd, resp.c_str(), resp.size(), 0);
    }
    close(fd);
}

int main() {
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = INADDR_ANY; addr.sin_port = htons(PORT);
    bind(srv, (sockaddr*)&addr, sizeof(addr));
    listen(srv, 128);
    std::cout << "[C++ TCP] Listening on " << PORT << "\\n";
    while (true) {
        sockaddr_in cli{}; socklen_t len = sizeof(cli);
        int fd = accept(srv, (sockaddr*)&cli, &len);
        std::thread(handle_client, fd).detach();
    }
    close(srv);
}` },
    { language: "C++",      filename: "udp_server.cpp", route: "/src/udp_server.cpp", codeId: codeCpp.id, text: `#include <iostream>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

int main() {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = INADDR_ANY; addr.sin_port = htons(8889);
    bind(fd, (sockaddr*)&addr, sizeof(addr));
    std::cout << "[C++ UDP] Listening on 8889\\n";
    char buf[1024]; sockaddr_in cli{}; socklen_t cli_len = sizeof(cli);
    while (true) {
        ssize_t n = recvfrom(fd, buf, sizeof(buf)-1, 0, (sockaddr*)&cli, &cli_len);
        if (n < 0) break;
        buf[n] = '\\0';
        sendto(fd, buf, n, 0, (sockaddr*)&cli, cli_len);
    }
    close(fd);
}` },
    { language: "Makefile", filename: "Makefile",       route: "/Makefile",           codeId: codeCpp.id, text: `CXX      = g++
CXXFLAGS = -std=c++17 -Wall -O2 -pthread

all: tcp_server udp_server

tcp_server: src/server.cpp
\t$(CXX) $(CXXFLAGS) $< -o $@

udp_server: src/udp_server.cpp
\t$(CXX) $(CXXFLAGS) $< -o $@

clean:
\trm -f tcp_server udp_server` },
  ]});

  // ── java-spring-rest ────────────────────────────────────────────────────────
  const codeJava = await prisma.code.create({ data: { repoName: "java-spring-rest", amount: 3, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Java", filename: "UserController.java", route: "/src/main/java/com/api/UserController.java", codeId: codeJava.id, text: `package com.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService svc;
    public UserController(UserService svc) { this.svc = svc; }

    @GetMapping           public List<UserDTO>          getAll()                      { return svc.findAll(); }
    @GetMapping("/{id}")  public ResponseEntity<UserDTO> get(@PathVariable Long id)   { return svc.findById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build()); }
    @PostMapping          public ResponseEntity<UserDTO> create(@RequestBody CreateUserRequest r) { return ResponseEntity.ok(svc.create(r)); }
    @DeleteMapping("/{id}") public ResponseEntity<Void> delete(@PathVariable Long id){ svc.delete(id); return ResponseEntity.noContent().build(); }
}` },
    { language: "Java", filename: "SecurityConfig.java", route: "/src/main/java/com/api/SecurityConfig.java", codeId: codeJava.id, text: `package com.api;

import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class SecurityConfig {
    private final JwtFilter jwtFilter;
    public SecurityConfig(JwtFilter jwtFilter) { this.jwtFilter = jwtFilter; }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(c -> c.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a.requestMatchers("/api/auth/**","/actuator/health").permitAll().anyRequest().authenticated())
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}` },
    { language: "YAML", filename: "application.yml",    route: "/src/main/resources/application.yml",         codeId: codeJava.id, text: `spring:
  datasource:
    url: \${DATABASE_URL}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
  security:
    jwt:
      secret: \${JWT_SECRET}
      expiration: 86400000

server:
  port: 8080

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics` },
  ]});

  // ── devops-scripts ──────────────────────────────────────────────────────────
  const codeDevops = await prisma.code.create({ data: { repoName: "devops-scripts", amount: 4, subscription: false } });
  await prisma.codeBase.createMany({ data: [
    { language: "Shell",    filename: "deploy.sh",              route: "/scripts/deploy.sh",              codeId: codeDevops.id, text: `#!/usr/bin/env bash
set -euo pipefail
APP_NAME=\${1:?Usage: deploy.sh <app> <tag>}
IMAGE_TAG=\${2:?Usage: deploy.sh <app> <tag>}
REGISTRY="registry.example.com"
NAMESPACE="production"

echo "Deploying $APP_NAME:$IMAGE_TAG to $NAMESPACE"
docker pull "$REGISTRY/$APP_NAME:$IMAGE_TAG"
kubectl set image deployment/"$APP_NAME" "$APP_NAME=$REGISTRY/$APP_NAME:$IMAGE_TAG" -n "$NAMESPACE"
kubectl rollout status deployment/"$APP_NAME" -n "$NAMESPACE" --timeout=120s
echo "Done: $APP_NAME:$IMAGE_TAG"` },
    { language: "Shell",    filename: "log_rotate.sh",          route: "/scripts/log_rotate.sh",          codeId: codeDevops.id, text: `#!/usr/bin/env bash
set -euo pipefail
LOG_DIR=\${LOG_DIR:-/var/log/app}
RETAIN_DAYS=\${RETAIN_DAYS:-7}
ARCHIVE_DIR="$LOG_DIR/archive"
mkdir -p "$ARCHIVE_DIR"

find "$LOG_DIR" -maxdepth 1 -name "*.log" -mtime +"$RETAIN_DAYS" | while read -r f; do
    ts=$(date +%Y%m%d_%H%M%S)
    gzip -c "$f" > "$ARCHIVE_DIR/$(basename "$f" .log)_.log.gz"
    rm "$f"
    echo "Archived $f"
done
find "$ARCHIVE_DIR" -name "*.gz" -mtime +30 -delete
echo "Log rotation done."` },
    { language: "Shell",    filename: "health_check.sh",        route: "/scripts/health_check.sh",        codeId: codeDevops.id, text: `#!/usr/bin/env bash
set -euo pipefail
ENDPOINTS=("http://api-service:8000/health" "http://grpc-service:8080/health")
SLACK_WEBHOOK=\${SLACK_WEBHOOK:-""}
all_ok=true

for url in "\${ENDPOINTS[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" || echo "000")
    if [[ "$status" != "200" ]]; then
        echo "DOWN: $url ($status)"; all_ok=false
        [[ -n "$SLACK_WEBHOOK" ]] && curl -s -X POST "$SLACK_WEBHOOK" -H "Content-Type: application/json" -d "{\\"text\\":\\"Health check failed: $url ($status)\\"}" > /dev/null
    else echo "OK: $url"; fi
done
$all_ok || exit 1` },
    { language: "YAML",     filename: "github-actions-ci.yml",  route: "/.github/workflows/ci.yml",       codeId: codeDevops.id, text: `name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: testdb }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
        env: { DATABASE_URL: postgresql://test:test@localhost:5432/testdb }` },
  ]});

  // ── ml-pipeline-toolkit ─────────────────────────────────────────────────────
  const codeMl = await prisma.code.create({ data: { repoName: "ml-pipeline-toolkit", amount: 3, subscription: true } });
  await prisma.codeBase.createMany({ data: [
    { language: "Python", filename: "pipeline.py", route: "/pipeline/pipeline.py", codeId: codeMl.id, text: `import mlflow, mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def run_pipeline(data_path: str, target_col: str, n_estimators: int = 100):
    mlflow.set_experiment("classification-pipeline")
    with mlflow.start_run():
        df = pd.read_csv(data_path)
        X, y = df.drop(columns=[target_col]), df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier(n_estimators=n_estimators, n_jobs=-1))])
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc, f1 = accuracy_score(y_test, preds), f1_score(y_test, preds, average="weighted")
        mlflow.log_params({"n_estimators": n_estimators}); mlflow.log_metrics({"accuracy": acc, "f1": f1})
        mlflow.sklearn.log_model(model, "model")
        print(f"Accuracy: {acc:.4f}  F1: {f1:.4f}")
        return model, acc, f1` },
    { language: "YAML",   filename: "dvc.yaml",     route: "/dvc.yaml",             codeId: codeMl.id, text: `stages:
  preprocess:
    cmd: python pipeline/preprocess.py
    deps: [data/raw/train.csv]
    outs: [data/processed/train.csv]
  train:
    cmd: python pipeline/pipeline.py
    deps: [data/processed/train.csv, pipeline/pipeline.py]
    outs: [models/model.pkl]
    metrics: [metrics/scores.json]
  evaluate:
    cmd: python pipeline/evaluate.py
    deps: [models/model.pkl, data/processed/test.csv]
    metrics: [metrics/eval.json]` },
    { language: "Markdown", filename: "README.md",  route: "/README.md",            codeId: codeMl.id, text: `# ML Pipeline Toolkit

Reproducible ML pipelines using DVC, MLflow, and scikit-learn.

## Run
\`\`\`bash
dvc repro       # run full pipeline
mlflow ui       # http://localhost:5000
\`\`\`` },
  ]});

  console.log("✅ Created 15 Code entries with 48 CodeBase files");

  // ─── Summary ─────────────────────────────────────────────────────────────────
  const counts = await Promise.all([
    prisma.user.count(),
    prisma.repository.count(),
    prisma.code.count(),
    prisma.codeBase.count(),
    prisma.chatMessage.count(),
    prisma.account.count(),
    prisma.session.count(),
  ]);

  console.log("\n📊 Database summary:");
  console.log(`   Users:        ${counts[0]}`);
  console.log(`   Repositories: ${counts[1]}`);
  console.log(`   Code:         ${counts[2]}`);
  console.log(`   CodeBase:     ${counts[3]}`);
  console.log(`   ChatMessages: ${counts[4]}`);
  console.log(`   Accounts:     ${counts[5]}`);
  console.log(`   Sessions:     ${counts[6]}`);
  console.log("\n🎉 Seeding complete!");
}

main()
  .catch((e) => { console.error("❌ Seeding failed:", e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });