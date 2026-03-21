# import os
# import uuid
# import psycopg2
# from datetime import datetime

# DATABASE_URL = "postgresql://myuser:mypassword@localhost:51214/chatbotdb"


# def seed_db():
#     conn = psycopg2.connect(DATABASE_URL)
#     conn.autocommit = True
#     cursor = conn.cursor()

#     print("Creating tables if they don't exist...")
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS "Code" (
#             "id" TEXT PRIMARY KEY,
#             "repoName" TEXT NOT NULL,
#             "amount" DOUBLE PRECISION NOT NULL,
#             "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
#         );
#         CREATE TABLE IF NOT EXISTS "CodeBase" (
#             "id" TEXT PRIMARY KEY,
#             "language" TEXT NOT NULL,
#             "filename" TEXT NOT NULL,
#             "route" TEXT NOT NULL,
#             "text" TEXT NOT NULL,
#             "codeId" TEXT NOT NULL REFERENCES "Code"("id") ON DELETE CASCADE,
#             "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
#         );
#     """)

#     print("Seeding dummy data...")
#     code_id = str(uuid.uuid4())
#     cursor.execute(
#         'INSERT INTO "Code" ("id", "repoName", "amount", "createdAt") VALUES (%s, %s, %s, %s)',
#         (code_id, "MyTestRepo", 1.0, datetime.now()),
#     )

#     dummy_python_code = """
# def calculate_sum(a, b):
#     # This function adds two numbers
#     return a + b
# """
#     cursor.execute(
#         'INSERT INTO "CodeBase" ("id", "language", "filename", "route", "text", "codeId", "createdAt") VALUES (%s, %s, %s, %s, %s, %s, %s)',
#         (
#             str(uuid.uuid4()),
#             "python",
#             "math_utils.py",
#             "/src/utils",
#             dummy_python_code,
#             code_id,
#             datetime.now(),
#         ),
#     )

#     print("Database successfully seeded!")
#     cursor.close()
#     conn.close()


# if __name__ == "__main__":
#     seed_db()

"""
seed.py — Comprehensive PostgreSQL seeder for the Squirrel ChatBot schema.

Populates: User, Account, Session, VerificationToken, Repository,
           ChatMessage, Code, CodeBase

Covers repos in: Python, TypeScript/Next.js, Rust, Go, C++,
                 Java, Bash/DevOps, TCP/UDP networking, HTTP/REST,
                 WebSocket, gRPC, GraphQL, Redis, Message Queues

Usage:
    pip install psycopg2-binary python-dotenv bcrypt
    python seed.py
    python seed.py --clean      # wipe all tables first
    python seed.py --repo tcp-udp-server   # seed only one repo
"""

import os
import sys
import uuid
import argparse
import hashlib
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://squirrel:squirrel_pass@localhost:5432/squirrel_db",
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def now() -> datetime:
    return datetime.now(timezone.utc)

def future(days: int = 30) -> datetime:
    return now() + timedelta(days=days)

def past(days: int = 10) -> datetime:
    return now() - timedelta(days=days)

def fake_hash(password: str) -> str:
    """SHA-256 stand-in (use bcrypt in production)."""
    return "$fake$" + hashlib.sha256(password.encode()).hexdigest()

def uid() -> str:
    return str(uuid.uuid4())

def cuid() -> str:
    """Simple cuid-like id."""
    import random, string
    return "c" + "".join(random.choices(string.ascii_lowercase + string.digits, k=24))


# ── Connection ────────────────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ── Clean ─────────────────────────────────────────────────────────────────────

def clean_all(cur):
    print("🧹 Cleaning all tables...")
    tables = [
        '"ChatMessage"', '"CodeBase"', '"Code"',
        '"Repository"', '"Session"', '"Account"',
        '"VerificationToken"', '"User"',
    ]
    for t in tables:
        cur.execute(f"DELETE FROM {t}")
    print("   ✅ All tables cleared.\n")


# ══════════════════════════════════════════════════════════════════════════════
#  SEED DATA
# ══════════════════════════════════════════════════════════════════════════════

# ── Users ─────────────────────────────────────────────────────────────────────

USERS = [
    {"id": cuid(), "name": "Alice Johnson",   "email": "alice@example.com",   "password": fake_hash("password123")},
    {"id": cuid(), "name": "Bob Smith",       "email": "bob@example.com",     "password": fake_hash("password123")},
    {"id": cuid(), "name": "Carol White",     "email": "carol@example.com",   "password": fake_hash("password123")},
    {"id": cuid(), "name": "David Kumar",     "email": "david@example.com",   "password": fake_hash("password123")},
    {"id": cuid(), "name": "Eve Martinez",    "email": "eve@example.com",     "password": fake_hash("password123")},
]


# ── Repos ─────────────────────────────────────────────────────────────────────

def make_repos(users):
    alice, bob, carol, david, eve = users
    return [
        # Python
        {"id": uid(), "name": "tcp-udp-server",        "description": "Raw TCP and UDP socket servers in Python with asyncio.",               "url": "https://github.com/alice/tcp-udp-server",        "ownerId": alice["id"], "license": "MIT",        "language": "Python",     "stars": 820,  "forks": 94,  "issues": 8},
        {"id": uid(), "name": "http-rest-api",          "description": "FastAPI REST service with JWT auth, rate limiting, and OpenAPI docs.", "url": "https://github.com/bob/http-rest-api",           "ownerId": bob["id"],   "license": "MIT",        "language": "Python",     "stars": 1540, "forks": 210, "issues": 22},
        {"id": uid(), "name": "websocket-chat",         "description": "Real-time WebSocket chat server using asyncio and aiohttp.",          "url": "https://github.com/carol/websocket-chat",        "ownerId": carol["id"], "license": "Apache-2.0", "language": "Python",     "stars": 430,  "forks": 55,  "issues": 6},
        {"id": uid(), "name": "grpc-microservice",      "description": "Python gRPC service with Protobuf, health checks, and TLS.",         "url": "https://github.com/david/grpc-microservice",     "ownerId": david["id"], "license": "MIT",        "language": "Python",     "stars": 660,  "forks": 78,  "issues": 11},
        {"id": uid(), "name": "redis-queue-worker",     "description": "Background job queue using Redis Streams and asyncio workers.",       "url": "https://github.com/eve/redis-queue-worker",      "ownerId": eve["id"],   "license": "MIT",        "language": "Python",     "stars": 310,  "forks": 42,  "issues": 4},
        # TypeScript / Next.js
        {"id": uid(), "name": "next-saas-starter",      "description": "Next.js 14 SaaS starter with Prisma, NextAuth, and Tailwind.",       "url": "https://github.com/alice/next-saas-starter",     "ownerId": alice["id"], "license": "MIT",        "language": "TypeScript", "stars": 1240, "forks": 198, "issues": 14},
        {"id": uid(), "name": "graphql-api-server",     "description": "GraphQL API with Apollo Server, Prisma, and subscription support.",  "url": "https://github.com/bob/graphql-api-server",      "ownerId": bob["id"],   "license": "MIT",        "language": "TypeScript", "stars": 890,  "forks": 112, "issues": 9},
        # Rust
        {"id": uid(), "name": "rust-http-server",       "description": "Minimal async HTTP server with Hyper and Tokio.",                    "url": "https://github.com/carol/rust-http-server",      "ownerId": carol["id"], "license": "MIT",        "language": "Rust",       "stars": 3870, "forks": 412, "issues": 27},
        {"id": uid(), "name": "rust-tcp-echo",          "description": "High-performance TCP echo server in Rust using Tokio.",               "url": "https://github.com/david/rust-tcp-echo",         "ownerId": david["id"], "license": "MIT",        "language": "Rust",       "stars": 540,  "forks": 67,  "issues": 5},
        # Go
        {"id": uid(), "name": "go-microservices",       "description": "Go microservices with gRPC, Docker, and Postgres.",                  "url": "https://github.com/eve/go-microservices",        "ownerId": eve["id"],   "license": "MIT",        "language": "Go",         "stars": 670,  "forks": 88,  "issues": 11},
        {"id": uid(), "name": "go-udp-broadcast",       "description": "UDP multicast and broadcast server in Go.",                          "url": "https://github.com/alice/go-udp-broadcast",      "ownerId": alice["id"], "license": "MIT",        "language": "Go",         "stars": 220,  "forks": 30,  "issues": 3},
        # C++
        {"id": uid(), "name": "cpp-socket-server",      "description": "Multi-threaded TCP server in C++ using POSIX sockets and epoll.",    "url": "https://github.com/bob/cpp-socket-server",       "ownerId": bob["id"],   "license": "GPL-3.0",    "language": "C++",        "stars": 1100, "forks": 145, "issues": 18},
        # Java
        {"id": uid(), "name": "java-spring-rest",       "description": "Spring Boot REST API with JPA, JWT security, and Swagger UI.",       "url": "https://github.com/carol/java-spring-rest",      "ownerId": carol["id"], "license": "Apache-2.0", "language": "Java",       "stars": 760,  "forks": 98,  "issues": 13},
        # Bash / DevOps
        {"id": uid(), "name": "devops-scripts",         "description": "Shell scripts for CI/CD, log rotation, and server provisioning.",    "url": "https://github.com/david/devops-scripts",        "ownerId": david["id"], "license": "MIT",        "language": "Shell",      "stars": 380,  "forks": 50,  "issues": 7},
        # ML / Data
        {"id": uid(), "name": "ml-pipeline-toolkit",    "description": "Reproducible ML pipelines with DVC, MLflow, and Docker.",           "url": "https://github.com/eve/ml-pipeline-toolkit",     "ownerId": eve["id"],   "license": "GPL-3.0",    "language": "Python",     "stars": 920,  "forks": 134, "issues": 19},
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  CODE FILES  (Code + CodeBase rows)
# ══════════════════════════════════════════════════════════════════════════════

CODE_ENTRIES = []   # filled below — list of (repo_name, files[])

# ─────────────────────────────────────────────────────────────────────────────
# 1. tcp-udp-server  (Python)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("tcp-udp-server", [
    ("Python", "tcp_server.py", "/src/tcp_server.py", """\
import asyncio

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
            print(f"[TCP] Received from {addr}: {message}")
            response = f"ECHO: {message}\\n"
            writer.write(response.encode())
            await writer.drain()
    except asyncio.IncompleteReadError:
        pass
    finally:
        print(f"[TCP] Connection closed: {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        print(f"[TCP] Server listening on {HOST}:{PORT}")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
"""),
    ("Python", "udp_server.py", "/src/udp_server.py", """\
import asyncio

HOST = "0.0.0.0"
PORT = 9001
BUFFER_SIZE = 1024

class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print(f"[UDP] Server started on {HOST}:{PORT}")

    def datagram_received(self, data: bytes, addr: tuple):
        message = data.decode().strip()
        print(f"[UDP] Received from {addr}: {message}")
        response = f"UDP_ECHO: {message}".encode()
        self.transport.sendto(response, addr)

    def error_received(self, exc):
        print(f"[UDP] Error: {exc}")

    def connection_lost(self, exc):
        print("[UDP] Server closed")

async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=(HOST, PORT),
    )
    try:
        print(f"[UDP] Listening on {HOST}:{PORT}")
        await asyncio.sleep(float("inf"))
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
"""),
    ("Python", "tcp_client.py", "/src/tcp_client.py", """\
import asyncio

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

async def tcp_client(messages: list[str]):
    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    print(f"[CLIENT] Connected to {SERVER_HOST}:{SERVER_PORT}")
    for msg in messages:
        writer.write(f"{msg}\\n".encode())
        await writer.drain()
        response = await reader.readline()
        print(f"[CLIENT] Server response: {response.decode().strip()}")
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(tcp_client(["Hello", "Ping", "World"]))
"""),
    ("Python", "udp_client.py", "/src/udp_client.py", """\
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9001
TIMEOUT     = 2.0

def udp_client(messages: list[str]):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIMEOUT)
        for msg in messages:
            sock.sendto(msg.encode(), (SERVER_HOST, SERVER_PORT))
            try:
                data, addr = sock.recvfrom(1024)
                print(f"[UDP CLIENT] Response from {addr}: {data.decode()}")
            except socket.timeout:
                print(f"[UDP CLIENT] Timeout waiting for response to: {msg}")

if __name__ == "__main__":
    udp_client(["Ping", "Hello UDP", "Test packet"])
"""),
    ("TOML", "requirements.txt", "/requirements.txt", """\
asyncio>=3.4.3
pytest>=7.4.0
pytest-asyncio>=0.21.0
"""),
    ("Markdown", "README.md", "/README.md", """\
# TCP / UDP Server

Async TCP echo server and UDP datagram server built with Python asyncio.

## Architecture

```
src/
  tcp_server.py   — asyncio StreamReader/StreamWriter echo server (port 9000)
  udp_server.py   — asyncio DatagramProtocol echo server (port 9001)
  tcp_client.py   — asyncio TCP test client
  udp_client.py   — raw socket UDP test client
```

## Run

```bash
python src/tcp_server.py   # terminal 1
python src/udp_server.py   # terminal 2
python src/tcp_client.py   # terminal 3
python src/udp_client.py   # terminal 4
```

## Protocol
- TCP: newline-delimited messages, response prefixed with `ECHO:`
- UDP: raw datagrams, response prefixed with `UDP_ECHO:`
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 2. http-rest-api  (Python / FastAPI)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("http-rest-api", [
    ("Python", "main.py", "/app/main.py", """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, items
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="REST API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(auth.router,  prefix="/auth",  tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/health")
def health():
    return {"status": "ok"}
"""),
    ("Python", "auth.py", "/app/routers/auth.py", """\
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super-secret-key"
ALGORITHM  = "HS256"
TOKEN_TTL  = 30  # minutes

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_TTL)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
def register(email: str, password: str, db=Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, hashed_password=pwd_context.hash(password))
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "email": user.email}
"""),
    ("Python", "models.py", "/app/models.py", """\
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email          = Column(String, unique=True, nullable=False)
    hashed_password= Column(String, nullable=False)
    created_at     = Column(DateTime, server_default=func.now())
    items          = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name        = Column(String, nullable=False)
    description = Column(String)
    price       = Column(Float, default=0.0)
    owner_id    = Column(String, ForeignKey("users.id"))
    created_at  = Column(DateTime, server_default=func.now())
    owner       = relationship("User", back_populates="items")
"""),
    ("Python", "rate_limiter.py", "/app/middleware/rate_limiter.py", """\
import time
from collections import defaultdict
from fastapi import Request, HTTPException

# Simple in-memory sliding window rate limiter
_request_log: dict[str, list[float]] = defaultdict(list)

WINDOW_SECONDS = 60
MAX_REQUESTS   = 100

def rate_limit(request: Request):
    ip  = request.client.host
    now = time.time()
    log = _request_log[ip]

    # Remove entries outside the window
    _request_log[ip] = [t for t in log if now - t < WINDOW_SECONDS]
    _request_log[ip].append(now)

    if len(_request_log[ip]) > MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
"""),
    ("YAML", "docker-compose.yml", "/docker-compose.yml", """\
version: "3.9"
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://api:api_pass@db:5432/apidb
      SECRET_KEY: super-secret-key
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: api
      POSTGRES_PASSWORD: api_pass
      POSTGRES_DB: apidb
    ports: ["5433:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U api"]
      interval: 5s
      retries: 10
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 3. websocket-chat  (Python / aiohttp)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("websocket-chat", [
    ("Python", "server.py", "/server.py", """\
import asyncio
import json
from aiohttp import web

clients: set[web.WebSocketResponse] = set()

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    print(f"[WS] Client connected. Total: {len(clients)}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                payload = json.loads(msg.data)
                broadcast = json.dumps({
                    "user":    payload.get("user", "anonymous"),
                    "message": payload.get("message", ""),
                    "ts":      asyncio.get_event_loop().time(),
                })
                # Broadcast to all connected clients
                await asyncio.gather(
                    *[c.send_str(broadcast) for c in clients if not c.closed],
                    return_exceptions=True,
                )
            elif msg.type == web.WSMsgType.ERROR:
                print(f"[WS] Error: {ws.exception()}")
    finally:
        clients.discard(ws)
        print(f"[WS] Client disconnected. Total: {len(clients)}")
    return ws

app = web.Application()
app.router.add_get("/ws", ws_handler)
app.router.add_get("/health", lambda r: web.json_response({"ok": True}))

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8765)
"""),
    ("Python", "client.py", "/client.py", """\
import asyncio
import json
import aiohttp

SERVER_URL = "ws://localhost:8765/ws"

async def chat_client(username: str, messages: list[str]):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(SERVER_URL) as ws:
            print(f"[{username}] Connected to {SERVER_URL}")
            for msg in messages:
                payload = json.dumps({"user": username, "message": msg})
                await ws.send_str(payload)
                response = await ws.receive_str()
                print(f"[{username}] Received: {response}")
                await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(chat_client("Alice", ["Hello!", "How are you?", "Bye!"]))
"""),
    ("Markdown", "README.md", "/README.md", """\
# WebSocket Chat Server

Real-time broadcast chat server using Python aiohttp WebSockets.

## Features
- Multi-client broadcast (every message sent to all connected clients)
- JSON message protocol: `{"user": "name", "message": "text"}`
- `/health` HTTP endpoint for liveness checks

## Run
```bash
pip install aiohttp
python server.py        # starts on ws://localhost:8765/ws
python client.py        # test client
```
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 4. grpc-microservice  (Python)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("grpc-microservice", [
    ("Protobuf", "service.proto", "/proto/service.proto", """\
syntax = "proto3";

package calculator;

service Calculator {
  rpc Add       (BinaryRequest)  returns (NumberReply);
  rpc Subtract  (BinaryRequest)  returns (NumberReply);
  rpc Multiply  (BinaryRequest)  returns (NumberReply);
  rpc Divide    (BinaryRequest)  returns (NumberReply);
  rpc StreamSum (stream NumberRequest) returns (NumberReply);
}

message BinaryRequest {
  double a = 1;
  double b = 2;
}

message NumberRequest {
  double value = 1;
}

message NumberReply {
  double result = 1;
  string error  = 2;
}
"""),
    ("Python", "server.py", "/server.py", """\
import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):

    def Add(self, request, context):
        return calculator_pb2.NumberReply(result=request.a + request.b)

    def Subtract(self, request, context):
        return calculator_pb2.NumberReply(result=request.a - request.b)

    def Multiply(self, request, context):
        return calculator_pb2.NumberReply(result=request.a * request.b)

    def Divide(self, request, context):
        if request.b == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Division by zero")
            return calculator_pb2.NumberReply(error="Division by zero")
        return calculator_pb2.NumberReply(result=request.a / request.b)

    def StreamSum(self, request_iterator, context):
        total = sum(req.value for req in request_iterator)
        return calculator_pb2.NumberReply(result=total)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("[gRPC] Listening on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
"""),
    ("Python", "client.py", "/client.py", """\
import grpc
import calculator_pb2
import calculator_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)

        r = stub.Add(calculator_pb2.BinaryRequest(a=10, b=5))
        print(f"Add(10, 5)      = {r.result}")

        r = stub.Divide(calculator_pb2.BinaryRequest(a=10, b=0))
        print(f"Divide(10, 0)   = error: {r.error}")

        numbers = [calculator_pb2.NumberRequest(value=i) for i in range(1, 6)]
        r = stub.StreamSum(iter(numbers))
        print(f"StreamSum(1..5) = {r.result}")

if __name__ == "__main__":
    run()
"""),
    ("YAML", "docker-compose.yml", "/docker-compose.yml", """\
version: "3.9"
services:
  grpc-server:
    build: .
    ports: ["50051:50051"]
    environment:
      ENV: production
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 5. redis-queue-worker  (Python)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("redis-queue-worker", [
    ("Python", "producer.py", "/producer.py", """\
import asyncio
import json
import redis.asyncio as aioredis

REDIS_URL  = "redis://localhost:6379"
STREAM_KEY = "job_stream"
MAX_LEN    = 1000   # cap stream length

async def produce(jobs: list[dict]):
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    for job in jobs:
        msg_id = await r.xadd(
            STREAM_KEY,
            {"payload": json.dumps(job)},
            maxlen=MAX_LEN,
        )
        print(f"[PRODUCER] Sent job {msg_id}: {job}")
    await r.aclose()

if __name__ == "__main__":
    sample_jobs = [
        {"type": "email",  "to": "user@example.com", "subject": "Welcome!"},
        {"type": "resize", "image_id": "img_001",    "width": 800},
        {"type": "report", "report_id": "rep_042",   "format": "pdf"},
    ]
    asyncio.run(produce(sample_jobs))
"""),
    ("Python", "worker.py", "/worker.py", """\
import asyncio
import json
import redis.asyncio as aioredis

REDIS_URL    = "redis://localhost:6379"
STREAM_KEY   = "job_stream"
CONSUMER_GRP = "workers"
CONSUMER_ID  = "worker-1"
BLOCK_MS     = 2000   # block up to 2 s waiting for messages

async def process_job(job: dict):
    job_type = job.get("type")
    if job_type == "email":
        print(f"[WORKER] Sending email to {job['to']}: {job['subject']}")
        await asyncio.sleep(0.1)   # simulate work
    elif job_type == "resize":
        print(f"[WORKER] Resizing image {job['image_id']} to {job['width']}px")
        await asyncio.sleep(0.2)
    elif job_type == "report":
        print(f"[WORKER] Generating {job['format']} report {job['report_id']}")
        await asyncio.sleep(0.3)
    else:
        print(f"[WORKER] Unknown job type: {job_type}")

async def consume():
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    # Create consumer group if not exists
    try:
        await r.xgroup_create(STREAM_KEY, CONSUMER_GRP, id="0", mkstream=True)
    except Exception:
        pass   # group already exists

    print(f"[WORKER] Listening on stream '{STREAM_KEY}' as '{CONSUMER_ID}'")
    while True:
        messages = await r.xreadgroup(
            CONSUMER_GRP, CONSUMER_ID,
            {STREAM_KEY: ">"}, count=5, block=BLOCK_MS,
        )
        for stream, entries in (messages or []):
            for msg_id, fields in entries:
                job = json.loads(fields["payload"])
                await process_job(job)
                await r.xack(STREAM_KEY, CONSUMER_GRP, msg_id)
                print(f"[WORKER] Acked {msg_id}")

if __name__ == "__main__":
    asyncio.run(consume())
"""),
    ("YAML", "docker-compose.yml", "/docker-compose.yml", """\
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
  worker:
    build: .
    command: python worker.py
    environment:
      REDIS_URL: redis://redis:6379
    depends_on: [redis]
    deploy:
      replicas: 3    # run 3 parallel workers
volumes:
  redis_data:
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 6. next-saas-starter  (TypeScript)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("next-saas-starter", [
    ("TypeScript", "auth.ts", "/lib/auth.ts", """\
import NextAuth from "next-auth";
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
      credentials: { email: { label: "Email" }, password: { label: "Password", type: "password" } },
      async authorize(credentials) {
        const user = await prisma.user.findUnique({ where: { email: credentials.email as string } });
        if (!user?.password) return null;
        const valid = await bcrypt.compare(credentials.password as string, user.password);
        return valid ? user : null;
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: { signIn: "/login", error: "/auth/error" },
});
"""),
    ("TypeScript", "prisma.ts", "/lib/prisma.ts", """\
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient | undefined };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({ log: process.env.NODE_ENV === "development" ? ["query", "warn", "error"] : ["error"] });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
"""),
    ("TypeScript", "page.tsx", "/app/dashboard/page.tsx", """\
import { auth } from "@/lib/auth";
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
      <section>
        <h2 className="text-xl font-semibold mb-4">Recent Repositories</h2>
        {user?.repositories.map(repo => (
          <div key={repo.id} className="border rounded-lg p-4 mb-3">
            <h3 className="font-medium">{repo.name}</h3>
            <p className="text-sm text-gray-500">{repo.description}</p>
            <span className="text-xs text-blue-500">{repo.language}</span>
          </div>
        ))}
      </section>
    </main>
  );
}
"""),
    ("CSS", "globals.css", "/app/globals.css", """\
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
}

@layer base {
  body { @apply bg-background text-foreground; }
  h1   { @apply text-4xl font-bold tracking-tight; }
  h2   { @apply text-2xl font-semibold; }
}
"""),
    ("JSON", ".env.example", "/.env.example", """\
DATABASE_URL=postgresql://user:pass@localhost:5432/saasdb
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

GITHUB_ID=your-github-client-id
GITHUB_SECRET=your-github-client-secret
GOOGLE_ID=your-google-client-id
GOOGLE_SECRET=your-google-client-secret
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 7. graphql-api-server  (TypeScript / Apollo)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("graphql-api-server", [
    ("TypeScript", "schema.ts", "/src/schema.ts", """\
import { gql } from "apollo-server-express";

export const typeDefs = gql`
  type User {
    id: ID!
    email: String!
    name: String
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    content: String
    published: Boolean!
    author: User!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    posts(published: Boolean): [Post!]!
    post(id: ID!): Post
  }

  type Mutation {
    createUser(email: String!, name: String): User!
    createPost(title: String!, content: String, authorId: ID!): Post!
    publishPost(id: ID!): Post!
    deletePost(id: ID!): Boolean!
  }

  type Subscription {
    postPublished: Post!
  }
`;
"""),
    ("TypeScript", "resolvers.ts", "/src/resolvers.ts", """\
import { PubSub } from "graphql-subscriptions";
import { prisma } from "./prisma";

const pubsub = new PubSub();
const POST_PUBLISHED = "POST_PUBLISHED";

export const resolvers = {
  Query: {
    users: () => prisma.user.findMany({ include: { posts: true } }),
    user: (_: any, { id }: { id: string }) =>
      prisma.user.findUnique({ where: { id }, include: { posts: true } }),
    posts: (_: any, { published }: { published?: boolean }) =>
      prisma.post.findMany({
        where: published !== undefined ? { published } : {},
        include: { author: true },
      }),
    post: (_: any, { id }: { id: string }) =>
      prisma.post.findUnique({ where: { id }, include: { author: true } }),
  },
  Mutation: {
    createUser: (_: any, args: { email: string; name?: string }) =>
      prisma.user.create({ data: args }),
    createPost: (_: any, args: { title: string; content?: string; authorId: string }) =>
      prisma.post.create({ data: { ...args, published: false }, include: { author: true } }),
    publishPost: async (_: any, { id }: { id: string }) => {
      const post = await prisma.post.update({ where: { id }, data: { published: true }, include: { author: true } });
      pubsub.publish(POST_PUBLISHED, { postPublished: post });
      return post;
    },
    deletePost: async (_: any, { id }: { id: string }) => {
      await prisma.post.delete({ where: { id } });
      return true;
    },
  },
  Subscription: {
    postPublished: { subscribe: () => pubsub.asyncIterator([POST_PUBLISHED]) },
  },
};
"""),
    ("TypeScript", "server.ts", "/src/server.ts", """\
import express from "express";
import { ApolloServer } from "apollo-server-express";
import { createServer } from "http";
import { SubscriptionServer } from "subscriptions-transport-ws";
import { execute, subscribe } from "graphql";
import { makeExecutableSchema } from "@graphql-tools/schema";
import { typeDefs } from "./schema";
import { resolvers } from "./resolvers";

async function bootstrap() {
  const app = express();
  const httpServer = createServer(app);
  const schema = makeExecutableSchema({ typeDefs, resolvers });

  const apolloServer = new ApolloServer({
    schema,
    context: ({ req }) => ({ req }),
  });

  await apolloServer.start();
  apolloServer.applyMiddleware({ app });

  SubscriptionServer.create(
    { schema, execute, subscribe },
    { server: httpServer, path: "/graphql" },
  );

  const PORT = process.env.PORT || 4000;
  httpServer.listen(PORT, () => {
    console.log(`🚀 GraphQL ready at http://localhost:${PORT}/graphql`);
    console.log(`🔌 Subscriptions ready at ws://localhost:${PORT}/graphql`);
  });
}

bootstrap();
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 8. rust-tcp-echo  (Rust)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("rust-tcp-echo", [
    ("Rust", "main.rs", "/src/main.rs", """\
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};

const ADDR: &str = "0.0.0.0:7000";
const BUF_SIZE: usize = 4096;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let listener = TcpListener::bind(ADDR).await?;
    println!("[TCP ECHO] Listening on {}", ADDR);

    loop {
        let (stream, addr) = listener.accept().await?;
        println!("[TCP ECHO] Connection from {}", addr);
        tokio::spawn(handle_client(stream));
    }
}

async fn handle_client(mut stream: TcpStream) {
    let mut buf = vec![0u8; BUF_SIZE];
    loop {
        match stream.read(&mut buf).await {
            Ok(0) => break,   // EOF
            Ok(n) => {
                if stream.write_all(&buf[..n]).await.is_err() {
                    break;
                }
            }
            Err(e) => {
                eprintln!("[TCP ECHO] Read error: {}", e);
                break;
            }
        }
    }
}
"""),
    ("Rust", "udp_echo.rs", "/src/udp_echo.rs", """\
use tokio::net::UdpSocket;

const UDP_ADDR: &str = "0.0.0.0:7001";

pub async fn run_udp_echo() -> anyhow::Result<()> {
    let socket = UdpSocket::bind(UDP_ADDR).await?;
    println!("[UDP ECHO] Listening on {}", UDP_ADDR);
    let mut buf = vec![0u8; 1024];
    loop {
        let (len, addr) = socket.recv_from(&mut buf).await?;
        socket.send_to(&buf[..len], addr).await?;
    }
}
"""),
    ("TOML", "Cargo.toml", "/Cargo.toml", """\
[package]
name    = "rust-tcp-echo"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio  = { version = "1",    features = ["full"] }
anyhow = "1"
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 9. cpp-socket-server  (C++)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("cpp-socket-server", [
    ("C++", "server.cpp", "/src/server.cpp", """\
#include <iostream>
#include <thread>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/epoll.h>

const int PORT       = 8888;
const int BACKLOG    = 128;
const int MAX_EVENTS = 64;
const int BUF_SIZE   = 4096;

void handle_client(int client_fd) {
    char buf[BUF_SIZE];
    while (true) {
        ssize_t n = recv(client_fd, buf, BUF_SIZE - 1, 0);
        if (n <= 0) break;
        buf[n] = '\\0';
        std::string response = "ECHO: " + std::string(buf, n);
        send(client_fd, response.c_str(), response.size(), 0);
    }
    close(client_fd);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port        = htons(PORT);

    bind(server_fd, (sockaddr*)&addr, sizeof(addr));
    listen(server_fd, BACKLOG);
    std::cout << "[C++ TCP] Server on port " << PORT << "\\n";

    while (true) {
        sockaddr_in client_addr{};
        socklen_t len = sizeof(client_addr);
        int client_fd = accept(server_fd, (sockaddr*)&client_addr, &len);
        std::cout << "[C++ TCP] Client: " << inet_ntoa(client_addr.sin_addr) << "\\n";
        std::thread(handle_client, client_fd).detach();
    }
    close(server_fd);
    return 0;
}
"""),
    ("C++", "udp_server.cpp", "/src/udp_server.cpp", """\
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

const int UDP_PORT  = 8889;
const int BUF_SIZE  = 1024;

int main() {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port        = htons(UDP_PORT);
    bind(sockfd, (sockaddr*)&addr, sizeof(addr));

    std::cout << "[C++ UDP] Listening on port " << UDP_PORT << "\\n";
    char buf[BUF_SIZE];
    sockaddr_in client{};
    socklen_t client_len = sizeof(client);

    while (true) {
        ssize_t n = recvfrom(sockfd, buf, BUF_SIZE - 1, 0, (sockaddr*)&client, &client_len);
        if (n < 0) break;
        buf[n] = '\\0';
        std::cout << "[UDP] " << buf << "\\n";
        sendto(sockfd, buf, n, 0, (sockaddr*)&client, client_len);
    }
    close(sockfd);
    return 0;
}
"""),
    ("Makefile", "Makefile", "/Makefile", """\
CXX      = g++
CXXFLAGS = -std=c++17 -Wall -O2 -pthread

all: tcp_server udp_server

tcp_server: src/server.cpp
\t$(CXX) $(CXXFLAGS) $< -o $@

udp_server: src/udp_server.cpp
\t$(CXX) $(CXXFLAGS) $< -o $@

clean:
\trm -f tcp_server udp_server
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 10. java-spring-rest  (Java)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("java-spring-rest", [
    ("Java", "UserController.java", "/src/main/java/com/api/UserController.java", """\
package com.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;
    public UserController(UserService userService) { this.userService = userService; }

    @GetMapping
    public List<UserDTO> getAll() { return userService.findAll(); }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<UserDTO> create(@RequestBody CreateUserRequest req) {
        return ResponseEntity.ok(userService.create(req));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
"""),
    ("Java", "SecurityConfig.java", "/src/main/java/com/api/SecurityConfig.java", """\
package com.api;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
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
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/actuator/health").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
"""),
    ("YAML", "application.yml", "/src/main/resources/application.yml", """\
spring:
  datasource:
    url: ${DATABASE_URL}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
  security:
    jwt:
      secret: ${JWT_SECRET}
      expiration: 86400000   # 24 hours in ms

server:
  port: 8080

management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 11. devops-scripts  (Shell)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("devops-scripts", [
    ("Shell", "deploy.sh", "/scripts/deploy.sh", """\
#!/usr/bin/env bash
set -euo pipefail

APP_NAME=${1:?Usage: deploy.sh <app_name> <image_tag>}
IMAGE_TAG=${2:?Usage: deploy.sh <app_name> <image_tag>}
REGISTRY="registry.example.com"
NAMESPACE="production"

echo "🚀 Deploying $APP_NAME:$IMAGE_TAG to $NAMESPACE"

# Pull latest image
docker pull "$REGISTRY/$APP_NAME:$IMAGE_TAG"

# Rolling update via kubectl
kubectl set image deployment/"$APP_NAME" \\
    "$APP_NAME=$REGISTRY/$APP_NAME:$IMAGE_TAG" \\
    -n "$NAMESPACE"

# Wait for rollout
kubectl rollout status deployment/"$APP_NAME" -n "$NAMESPACE" --timeout=120s

echo "✅ Deployment complete: $APP_NAME:$IMAGE_TAG"
"""),
    ("Shell", "log_rotate.sh", "/scripts/log_rotate.sh", """\
#!/usr/bin/env bash
# Rotate logs older than N days and compress them
set -euo pipefail

LOG_DIR=${LOG_DIR:-/var/log/app}
RETAIN_DAYS=${RETAIN_DAYS:-7}
ARCHIVE_DIR="$LOG_DIR/archive"

mkdir -p "$ARCHIVE_DIR"

find "$LOG_DIR" -maxdepth 1 -name "*.log" -mtime +"$RETAIN_DAYS" | while read -r logfile; do
    basename=$(basename "$logfile")
    ts=$(date +%Y%m%d_%H%M%S)
    gzip -c "$logfile" > "$ARCHIVE_DIR/${basename%.log}_${ts}.log.gz"
    rm "$logfile"
    echo "[LOG ROTATE] Archived $logfile"
done

# Remove archives older than 30 days
find "$ARCHIVE_DIR" -name "*.gz" -mtime +30 -delete
echo "[LOG ROTATE] Done. Retained last $RETAIN_DAYS days."
"""),
    ("Shell", "health_check.sh", "/scripts/health_check.sh", """\
#!/usr/bin/env bash
# Ping a list of HTTP health endpoints and alert if any are down
set -euo pipefail

ENDPOINTS=(
    "http://api-service:8000/health"
    "http://grpc-service:8080/health"
    "http://worker-service:9000/health"
)
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}
TIMEOUT=5

all_ok=true

for url in "${ENDPOINTS[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" || echo "000")
    if [[ "$status" != "200" ]]; then
        echo "❌ DOWN: $url (HTTP $status)"
        all_ok=false
        if [[ -n "$SLACK_WEBHOOK" ]]; then
            curl -s -X POST "$SLACK_WEBHOOK" \\
                -H "Content-Type: application/json" \\
                -d "{\"text\": \"🚨 Health check failed: $url (status $status)\"}" > /dev/null
        fi
    else
        echo "✅ OK:   $url"
    fi
done

$all_ok && echo "All services healthy." || exit 1
"""),
    ("YAML", "github-actions-ci.yml", "/.github/workflows/ci.yml", """\
name: CI Pipeline

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
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

  docker-build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: false
          tags: myapp:${{ github.sha }}
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 12. go-microservices  (Go)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("go-microservices", [
    ("Go", "main.go", "/cmd/api/main.go", """\
package main

import (
    "log"
    "net/http"
    "os"

    "github.com/gorilla/mux"
)

func main() {
    r := mux.NewRouter()
    r.HandleFunc("/health",       healthHandler).Methods("GET")
    r.HandleFunc("/api/users",    listUsersHandler).Methods("GET")
    r.HandleFunc("/api/users/{id}", getUserHandler).Methods("GET")
    r.HandleFunc("/api/users",    createUserHandler).Methods("POST")

    port := os.Getenv("PORT")
    if port == "" { port = "8080" }
    log.Printf("API server on :%s", port)
    log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"status":"ok"}`))
}
"""),
    ("Go", "udp_broadcast.go", "/cmd/broadcast/main.go", """\
package main

import (
    "fmt"
    "net"
    "time"
)

const BROADCAST_ADDR = "255.255.255.255:9999"
const INTERVAL       = 2 * time.Second

func main() {
    addr, err := net.ResolveUDPAddr("udp", BROADCAST_ADDR)
    if err != nil { panic(err) }

    conn, err := net.DialUDP("udp", nil, addr)
    if err != nil { panic(err) }
    defer conn.Close()

    fmt.Printf("[UDP BROADCAST] Sending to %s every %s\\n", BROADCAST_ADDR, INTERVAL)
    i := 0
    for {
        msg := fmt.Sprintf("BROADCAST #%d @ %s", i, time.Now().Format(time.RFC3339))
        conn.Write([]byte(msg))
        fmt.Println("[SENT]", msg)
        i++
        time.Sleep(INTERVAL)
    }
}
"""),
    ("YAML", "docker-compose.yml", "/docker-compose.yml", """\
version: "3.9"
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
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      retries: 10
"""),
    ("Go", "go.mod", "/go.mod", """\
module github.com/carol/go-microservices

go 1.22

require (
    github.com/gorilla/mux v1.8.1
    github.com/lib/pq      v1.10.9
)
"""),
]))

# ─────────────────────────────────────────────────────────────────────────────
# 13. ml-pipeline-toolkit  (Python)
# ─────────────────────────────────────────────────────────────────────────────
CODE_ENTRIES.append(("ml-pipeline-toolkit", [
    ("Python", "pipeline.py", "/pipeline/pipeline.py", """\
import mlflow
import mlflow.sklearn
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
        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)),
        ])

        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        f1  = f1_score(y_test, preds, average="weighted")

        mlflow.log_params({"n_estimators": n_estimators, "target": target_col})
        mlflow.log_metrics({"accuracy": acc, "f1": f1})
        mlflow.sklearn.log_model(model, "model")

        print(f"✅ Accuracy: {acc:.4f}  F1: {f1:.4f}")
        return model, acc, f1

if __name__ == "__main__":
    run_pipeline("data/train.csv", target_col="label")
"""),
    ("YAML", "dvc.yaml", "/dvc.yaml", """\
stages:
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
    metrics: [metrics/eval.json]
"""),
    ("Markdown", "README.md", "/README.md", """\
# ML Pipeline Toolkit

Reproducible ML pipelines using DVC, MLflow, and scikit-learn.

## Stack
- **DVC** — data versioning and pipeline orchestration
- **MLflow** — experiment tracking and model registry
- **scikit-learn** — model training and evaluation

## Run
```bash
dvc repro          # run full pipeline
mlflow ui          # view experiment dashboard at http://localhost:5000
```
"""),
]))


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT MESSAGES
# ══════════════════════════════════════════════════════════════════════════════

def make_chat_messages(users, repos_by_name):
    alice, bob, carol, david, eve = users
    msgs = []

    def m(content, user, repo_name):
        r = repos_by_name.get(repo_name)
        if r:
            msgs.append({"id": uid(), "content": content, "userId": user["id"], "repositoryId": r["id"]})

    m("How does the TCP echo server handle concurrent connections?",       bob,   "tcp-udp-server")
    m("Each connection spawns a coroutine via asyncio.start_server.",      alice, "tcp-udp-server")
    m("What's the difference between the TCP and UDP implementations?",    carol, "tcp-udp-server")
    m("TCP uses StreamReader/Writer for reliable ordered delivery; UDP uses DatagramProtocol for fire-and-forget datagrams.", alice, "tcp-udp-server")

    m("How does JWT authentication work in this API?",                     carol, "http-rest-api")
    m("JWTs are signed with HS256 and expire after 30 minutes. The token is issued at /auth/login.", bob, "http-rest-api")
    m("How does the rate limiter work?",                                   david, "http-rest-api")
    m("It's a sliding window counter per IP stored in memory. 100 req/min limit.", bob, "http-rest-api")

    m("How do WebSocket messages get broadcast to all clients?",           alice, "websocket-chat")
    m("All connected WebSocketResponse objects are stored in a set. On each message, asyncio.gather fans out to all.", carol, "websocket-chat")

    m("What's the purpose of StreamSum in the gRPC service?",              eve,   "grpc-microservice")
    m("It demonstrates client-side streaming — the client sends a stream of numbers and the server returns their sum.", david, "grpc-microservice")

    m("How does the Redis worker avoid processing the same job twice?",    alice, "redis-queue-worker")
    m("It uses XREADGROUP with XACK. Only after processing does the worker ack the message id, so crashes don't lose jobs.", eve, "redis-queue-worker")

    m("How is authentication set up in next-saas-starter?",                bob,   "next-saas-starter")
    m("NextAuth with GitHub, Google, and Credentials providers. PrismaAdapter stores sessions in Postgres.", alice, "next-saas-starter")

    m("How do GraphQL subscriptions work in this server?",                 carol, "graphql-api-server")
    m("PubSub from graphql-subscriptions triggers the postPublished event whenever publishPost mutation runs.", bob, "graphql-api-server")

    m("Why does the Rust TCP server use tokio::spawn per connection?",     david, "rust-tcp-echo")
    m("tokio::spawn creates a lightweight async task per client, allowing thousands of concurrent connections without OS threads.", carol, "rust-tcp-echo")

    m("How does the C++ server handle multiple connections without blocking?", eve, "cpp-socket-server")
    m("Each accepted connection is handed to std::thread::detach(), so the main loop never blocks on a client.", bob, "cpp-socket-server")

    m("What does the deploy script do if the rollout fails?",              alice, "devops-scripts")
    m("kubectl rollout status exits non-zero on timeout, and set -euo pipefail causes the script to abort immediately.", david, "devops-scripts")

    m("How does the Go UDP broadcast work?",                               carol, "go-udp-broadcast")
    m("It dials the broadcast address 255.255.255.255:9999 and sends a timestamped datagram every 2 seconds.", alice, "go-udp-broadcast")

    m("How does DVC track the training data?",                             bob,   "ml-pipeline-toolkit")
    m("DVC stages declare deps and outs. Data files are hashed and stored in the DVC cache; only hashes go into git.", eve, "ml-pipeline-toolkit")

    return msgs


# ══════════════════════════════════════════════════════════════════════════════
#  INSERT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def insert_users(cur, users):
    """
    Upsert users by email and return list of dicts with the ACTUAL db ids.
    Using ON CONFLICT (email) DO UPDATE ensures we always get back the real id
    regardless of whether the row already existed.
    """
    confirmed = []
    for u in users:
        cur.execute(
            '''
            INSERT INTO "User" (id, name, email, password, "emailVerified", "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE
                SET name      = EXCLUDED.name,
                    password  = EXCLUDED.password,
                    "updatedAt" = EXCLUDED."updatedAt"
            RETURNING id, name, email
            ''',
            (u["id"], u["name"], u["email"], u["password"], now(), now(), now()),
        )
        row = cur.fetchone()
        confirmed.append({**u, "id": row["id"]})   # use the DB-confirmed id
    print(f"  ✅ {len(confirmed)} users (upserted by email)")
    return confirmed


def insert_accounts(cur, users):
    alice, bob, carol, david, eve = users
    accounts = [
        (cuid(), alice["id"], "oauth",       "github",  "gh_alice_001",   "gho_alice_fake",   "bearer", "read:user,repo"),
        (cuid(), bob["id"],   "oauth",       "google",  "google_bob_001", "ya29_bob_fake",    "Bearer", "openid email profile"),
        (cuid(), carol["id"], "oauth",       "github",  "gh_carol_001",   "gho_carol_fake",   "bearer", "read:user,repo"),
        (cuid(), david["id"], "credentials", "password","david_cred_001", None,               None,     None),
        (cuid(), eve["id"],   "oauth",       "google",  "google_eve_001", "ya29_eve_fake",    "Bearer", "openid email profile"),
    ]
    for a in accounts:
        cur.execute(
            '''
            INSERT INTO "Account" (id,"userId",type,provider,"providerAccountId","access_token","token_type",scope)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (provider,"providerAccountId") DO UPDATE
                SET "access_token" = EXCLUDED."access_token"
            ''',
            a,
        )
    print(f"  ✅ {len(accounts)} accounts")


def insert_sessions(cur, users):
    for u in users:
        # Delete any existing session for this user so we can insert fresh
        cur.execute('DELETE FROM "Session" WHERE "userId" = %s', (u["id"],))
        cur.execute(
            'INSERT INTO "Session" (id,"sessionToken","userId",expires) VALUES (%s,%s,%s,%s)',
            (cuid(), f"sess_{u['email']}_{uid()}", u["id"], future(30)),
        )
    print(f"  ✅ {len(users)} sessions")


def insert_verification_tokens(cur, users):
    for u in users[2:]:   # unverified users
        cur.execute(
            'INSERT INTO "VerificationToken" (identifier,token,expires) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',
            (u["email"], f"verify_{uid()}", future(1)),
        )
    print(f"  ✅ {len(users[2:])} verification tokens")


def insert_repos(cur, repos):
    confirmed = []
    for r in repos:
        cur.execute(
            '''
            INSERT INTO "Repository" (id,name,description,url,"ownerId",license,language,stars,forks,issues,updated,"createdAt","updatedAt")
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE
                SET name        = EXCLUDED.name,
                    description = EXCLUDED.description,
                    stars       = EXCLUDED.stars,
                    forks       = EXCLUDED.forks,
                    "updatedAt" = EXCLUDED."updatedAt"
            RETURNING id, name
            ''',
            (r["id"], r["name"], r["description"], r["url"], r["ownerId"],
             r["license"], r["language"], r["stars"], r["forks"], r["issues"],
             now(), now(), now()),
        )
        row = cur.fetchone()
        confirmed.append({**r, "id": row["id"]})
    print(f"  ✅ {len(confirmed)} repositories (upserted)")
    return confirmed


def insert_code_entries(cur, code_entries, repos_by_name, filter_repo=None):
    total_code = 0
    total_cb   = 0
    for repo_name, files in code_entries:
        if filter_repo and repo_name != filter_repo:
            continue
        repo = repos_by_name.get(repo_name)
        if not repo:
            print(f"  ⚠️  Repo '{repo_name}' not found — skipping code entries")
            continue

        code_id = uid()
        cur.execute(
            'INSERT INTO "Code" (id,"repoName",amount,"createdAt") VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING',
            (code_id, repo_name, float(len(files)), now()),
        )
        total_code += 1

        for lang, filename, route, text in files:
            cur.execute(
                'INSERT INTO "CodeBase" (id,language,filename,route,text,"codeId","createdAt") '
                'VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                (uid(), lang, filename, route, text, code_id, now()),
            )
            total_cb += 1

    print(f"  ✅ {total_code} Code entries, {total_cb} CodeBase files")


def insert_chat_messages(cur, messages):
    for m in messages:
        cur.execute(
            'INSERT INTO "ChatMessage" (id,content,"userId","repositoryId","createdAt") '
            'VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
            (m["id"], m["content"], m["userId"], m["repositoryId"], now()),
        )
    print(f"  ✅ {len(messages)} chat messages")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Squirrel DB Seeder")
    parser.add_argument("--clean", action="store_true", help="Delete all rows before seeding")
    parser.add_argument("--repo",  default=None,        help="Seed code only for this repo name")
    args = parser.parse_args()

    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        print("\n🌱 Squirrel DB Seeder starting...\n")

        if args.clean:
            clean_all(cur)

        # ── Step 1: upsert users and get back DB-confirmed ids ────────────────
        print("👤 Users")
        confirmed_users = insert_users(cur, USERS)

        # ── Step 2: all downstream data uses confirmed_users ids ──────────────
        print("🔑 Accounts")
        insert_accounts(cur, confirmed_users)

        print("🪪  Sessions")
        insert_sessions(cur, confirmed_users)

        print("📧 Verification tokens")
        insert_verification_tokens(cur, confirmed_users)

        # ── Step 3: build repos using confirmed user ids ──────────────────────
        repos = make_repos(confirmed_users)

        print("📦 Repositories")
        confirmed_repos = insert_repos(cur, repos)
        repos_by_name   = {r["name"]: r for r in confirmed_repos}

        print("💾 Code + CodeBase")
        insert_code_entries(cur, CODE_ENTRIES, repos_by_name, filter_repo=args.repo)

        print("💬 Chat messages")
        chat_msgs = make_chat_messages(confirmed_users, repos_by_name)
        insert_chat_messages(cur, chat_msgs)

        conn.commit()
        print(f"\n🎉 Seeding complete!\n")

        # Summary
        for table in ['"User"', '"Repository"', '"Code"', '"CodeBase"', '"ChatMessage"']:
            cur.execute(f"SELECT COUNT(*) AS n FROM {table}")
            row = cur.fetchone()
            print(f"   {table:20s}: {row['n']} rows")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Seeding failed: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()