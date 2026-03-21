# import uuid
# import logging
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware

# from ingest import load_codebase
# from vector_db import create_vectorstore, load_vectorstore
# from llm import build_conversational_chain

# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# app = FastAPI(
#     title="Squirrel ChatBot",
#     description="A chatbot that helps users understand GitHub repositories by ingesting their content and answering questions.",
#     version="1.0.0",
# )

# # In-memory session store: session_id -> {chain, vectorstore, ...}
# session_storage: dict = {}

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ─── Pydantic models ──────────────────────────────────────────────────────────

# class InitRequest(BaseModel):
#     repo_name: str | None = None
#     code_id: str | None = None
#     llm_type: str = "groq"          # default to groq (free)

# class ChatRequest(BaseModel):
#     session_id: str
#     question: str



# # ─── Routes ───────────────────────────────────────────────────────────────────

# @app.get("/")
# def read_root():
#     return {"message": "Squirrel ChatBot API is running. Use /docs for Swagger UI."}

# @app.get("/health")
# def health():
#     return {"ok": True}


# @app.get("/repos")
# def list_repos():
#     """Return distinct repo names available in the CodeBase table."""
#     from ingest import list_available_repos
#     return {"repos": list_available_repos()}


# @app.post("/init")
# def initialize(request: InitRequest):
#     """
#     Load codebase from Postgres, build FAISS vectorstore, start a session.
#     Pass repo_name OR code_id to filter; omit both to load everything.
#     """
#     docs = load_codebase(repo_name=request.repo_name, code_id=request.code_id)
#     if not docs:
#         raise HTTPException(
#             status_code=400,
#             detail="No codebase documents found. Check repo_name / code_id or run the seed first.",
#         )

#     vectorstore = create_vectorstore(docs)
#     chain = build_conversational_chain(vectorstore, llm_type=request.llm_type)
#     session_id = str(uuid.uuid4())
#     session_storage[session_id] = {
#         "chain": chain,
#         "vectorstore": vectorstore,
#         "repo_name": request.repo_name,
#         "code_id": request.code_id,
#         "llm_type": request.llm_type,
#         "doc_count": len(docs),
#     }
#     return {
#         "session_id": session_id,
#         "repo_name": request.repo_name,
#         "code_id": request.code_id,
#         "llm_type": request.llm_type,
#         "doc_count": len(docs),
#     }


# @app.post("/init-from-cache")
# def init_from_cache(request: InitRequest):
#     """Re-use a previously saved FAISS index (skip DB + embedding step)."""
#     vectorstore = load_vectorstore()
#     if not vectorstore:
#         raise HTTPException(
#             status_code=400,
#             detail="No local FAISS index found. Call /init first.",
#         )
#     chain = build_conversational_chain(vectorstore, llm_type=request.llm_type)
#     session_id = str(uuid.uuid4())
#     session_storage[session_id] = {
#         "chain": chain,
#         "vectorstore": vectorstore,
#         "llm_type": request.llm_type,
#     }
#     return {"session_id": session_id, "llm_type": request.llm_type}


# @app.post("/chat")
# def chat(request: ChatRequest):
#     """Send a question and get an answer with sources."""
#     question = request.question.strip()
#     if not question:
#         raise HTTPException(status_code=400, detail="Question cannot be empty.")

#     if request.session_id not in session_storage:
#         raise HTTPException(status_code=404, detail="Session not found. Call /init first.")

#     chain = session_storage[request.session_id]["chain"]

#     try:
#         res = chain.invoke({"question": question})
#     except Exception as e:
#         import logging
#         logging.exception("LLM error")
#         raise HTTPException(status_code=500, detail="LLM processing failed. Please try again.")

#     answer = res.get("answer") or res.get("output_text", "No answer returned.")
#     chat_history = res.get("chat_history", [])

#     sources = []
#     for doc in res.get("source_documents", []):
#         sources.append(doc.metadata)

#     return {
#         "answer": answer,
#         "sources": sources,
#         "chat_history": [
#             {"type": role, "content": content}
#             for role, content in chat_history
#         ],
#     }


# @app.delete("/session/{session_id}")
# def delete_session(session_id: str):
#     """Clean up a session from memory."""
#     if session_id not in session_storage:
#         raise HTTPException(status_code=404, detail="Session not found.")
#     del session_storage[session_id]
#     return {"status": "deleted", "session_id": session_id}


# @app.get("/sessions")
# def list_sessions():
#     """Dev helper – list active session IDs."""
#     return {
#         "sessions": [
#             {"session_id": sid, "repo_name": v.get("repo_name"), "llm_type": v.get("llm_type")}
#             for sid, v in session_storage.items()
#         ]
#     }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

import uuid
import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ingest import (
    load_codebase,
    list_available_repos,
    list_available_code_ids,
    get_code_subscription,
)
from vector_db import create_vectorstore, load_vectorstore
from llm import build_conversational_chain

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Squirrel ChatBot",
    description="A chatbot that helps users understand GitHub repositories by ingesting their content and answering questions.",
    version="1.0.0",
)

# In-memory session store: session_id -> {chain, vectorstore, ...}
session_storage: dict = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic models ──────────────────────────────────────────────────────────

class InitRequest(BaseModel):
    repo_name: str | None = None
    code_id: str
    llm_type: str = "groq"

class ChatRequest(BaseModel):
    code_id: str
    session_id: str
    question: str


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Squirrel ChatBot API is running. Use /docs for Swagger UI."}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/repos")
def list_repos():
    """Return distinct repo names available in the CodeBase table."""
    return {"repos": list_available_repos()}


@app.get("/code-ids")
def list_code_ids(repo_name: str | None = None):
    """Return Code.id values available for testing /init and /chat sessions."""
    return {"items": list_available_code_ids(repo_name=repo_name)}


@app.post("/init")
def initialize(request: InitRequest):
    """
    Load codebase from Postgres, build FAISS vectorstore, start a session.
    Pass repo_name OR code_id to filter; omit both to load everything.
    """
    # if not request.code_id.strip():
    #     raise HTTPException(status_code=400, detail="code_id cannot be empty.")

    if request.session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found. Call /init first.")

    session = session_storage[request.session_id]
    chain = session["chain"]

    # Use the provided code_id, or fall back to the one saved in the session
    active_code_id = request.code_id if request.code_id else session.get("code_id")
    
    if not active_code_id:
        raise HTTPException(status_code=400, detail="No code_id provided and none found in session.")

    # ... later in the function, pass active_code_id to the chain ...
    try:
        res = chain.invoke({"question": question, "code_id": active_code_id})
    except Exception as e:
        logger.exception("LLM error")
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {e}")

    docs = load_codebase(repo_name=request.repo_name, code_id=request.code_id)
    subscription = get_code_subscription(request.code_id)

    if not docs:
        raise HTTPException(
            status_code=400,
            detail="No codebase documents found. Check repo_name / code_id or run the seed first.",
        )

    vectorstore = create_vectorstore(docs)
    chain = build_conversational_chain(
        vectorstore,
        llm_type=request.llm_type,
        code_id=request.code_id,
        subscription=subscription,
    )
    session_id = str(uuid.uuid4())
    session_storage[session_id] = {
        "chain": chain,
        "vectorstore": vectorstore,
        "repo_name": request.repo_name,
        "code_id": request.code_id,
        "llm_type": request.llm_type,
        "subscription": subscription,
        "doc_count": len(docs),
    }
    return {
        "session_id": session_id,
        "repo_name": request.repo_name,
        "code_id": request.code_id,
        "llm_type": request.llm_type,
        "subscription": subscription,
        "doc_count": len(docs),
    }


@app.post("/init-from-cache")
def init_from_cache(request: InitRequest):
    """Re-use a previously saved FAISS index (skip DB + embedding step)."""
    if not request.code_id.strip():
        raise HTTPException(status_code=400, detail="code_id cannot be empty.")

    vectorstore = load_vectorstore()
    if not vectorstore:
        raise HTTPException(
            status_code=400,
            detail="No local FAISS index found. Call /init first.",
        )
    subscription = get_code_subscription(request.code_id)
    chain = build_conversational_chain(
        vectorstore,
        llm_type=request.llm_type,
        code_id=request.code_id,
        subscription=subscription,
    )

    if hasattr(vectorstore, "stats"):
        stats = vectorstore.stats()
        available_code_ids = set(stats.get("code_ids", []))
        if request.code_id not in available_code_ids:
            logger.warning(
                "init-from-cache: requested code_id %s not present in cached index (available=%s)",
                request.code_id,
                sorted(available_code_ids),
            )
    session_id = str(uuid.uuid4())
    session_storage[session_id] = {
        "chain": chain,
        "vectorstore": vectorstore,
        "code_id": request.code_id,
        "llm_type": request.llm_type,
        "subscription": subscription,
    }
    return {
        "session_id": session_id,
        "code_id": request.code_id,
        "llm_type": request.llm_type,
        "subscription": subscription,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    """Send a question and get an answer with sources."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.code_id.strip():
        raise HTTPException(status_code=400, detail="code_id cannot be empty.")

    if request.session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found. Call /init first.")

    session = session_storage[request.session_id]
    chain = session["chain"]

    # Ensure chat requests use the same Code.id context selected at session init.
    session_code_id = session.get("code_id")
    if session_code_id and request.code_id != session_code_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"code_id mismatch for this session. Expected '{session_code_id}', "
                f"received '{request.code_id}'."
            ),
        )

    try:
        res = chain.invoke(
            {
                "question": question,
                "code_id": request.code_id,
                "subscription": bool(session.get("subscription", False)),
            }
        )
    except Exception as e:
        logger.exception("LLM error")
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {e}")

    answer = res.get("answer") or res.get("output_text", "No answer returned.")

    # chat_history is a list of LangChain message objects (HumanMessage, AIMessage).
    # Each has .type ("human"/"ai") and .content (str) — NOT tuples.
    chat_history = []
    for msg in res.get("chat_history", []):
        if hasattr(msg, "type") and hasattr(msg, "content"):
            chat_history.append({"type": msg.type, "content": msg.content})

    sources = []
    seen_sources = set()
    for doc in res.get("source_documents", []):
        src = doc.metadata.get("source", doc.metadata.get("filename", "unknown"))
        if src not in seen_sources:
            sources.append(doc.metadata)
            seen_sources.add(src)

    return {
        "answer": answer,
        "sources": sources,
        "chat_history": chat_history,
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Clean up a session from memory."""
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found.")
    del session_storage[session_id]
    return {"status": "deleted", "session_id": session_id}


@app.get("/sessions")
def list_sessions():
    """Dev helper – list active session IDs."""
    return {
        "sessions": [
            {
                "session_id": sid,
                "repo_name": v.get("repo_name"),
                "code_id": v.get("code_id"),
                "llm_type": v.get("llm_type"),
                "subscription": v.get("subscription"),
                "doc_count": v.get("doc_count"),
            }
            for sid, v in session_storage.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)