# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory


# def build_conversational_chain(vectorstore, llm_type="openai"):

#     if llm_type == "openai":
#         llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
#     elif llm_type == "groq":
#         llm = ChatGroq(model="llama3-70b-8192", temperature=0.2)
#     else:
#         raise ValueError("Unsupported LLM type. Choose 'openai' or 'groq'.")

#     retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         output_key="answer",
#         input_key="question",
#     )

#     chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=memory,
#         return_source_documents=True,
#         verbose=False,
#     )

#     return chain

# import os
# from openai import OpenAI
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()


# class MockMessage:
#     """Mimics a LangChain HumanMessage / AIMessage so app.py serialisation works."""
#     def __init__(self, msg_type: str, content: str):
#         self.type = msg_type
#         self.content = content


# # ── System prompt ─────────────────────────────────────────────────────────────

# SYSTEM_TEMPLATE = """\
# You are **Squirrel**, a senior software engineer and code-intelligence assistant. \
# Your only knowledge source is the repository context injected below — \
# do NOT invent code, functions, files, or behaviours that are not present in that context.

# ━━━━━━━━━━━━━━━━━━━━━━━  REPOSITORY CONTEXT  ━━━━━━━━━━━━━━━━━━━━━━━
# {context}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ## Your capabilities
# You can answer questions about:
# - **Architecture** — how components are structured, layered, and connected
# - **Code logic** — what specific functions, classes, or modules do
# - **Data flow** — how data moves between files, functions, and services
# - **Configuration** — env vars, Docker, build files, config schemas
# - **Dependencies** — libraries used, why they exist, how they are wired
# - **Setup & usage** — how to install, run, test, or extend the project
# - **Cross-file relationships** — imports, adapters, shared utilities
# - **Security patterns** — auth, session management, secrets handling
# - **Multi-turn follow-ups** — you remember everything said earlier in the chat

# ## Rules
# 1. **Stay grounded** — base every claim on the context above. If a file or function \
# is not in the context, say so explicitly rather than guessing.
# 2. **Be precise** — quote exact filenames, function names, variable names, and line \
# snippets when they are available in the context.
# 3. **Explain deeply** — for architecture / design questions give layered explanations \
# (what → why → how → trade-offs).
# 4. **Use markdown** — use code blocks (```language), bullet lists, and bold headings \
# to structure longer answers.
# 5. **Acknowledge gaps** — if the context does not contain enough information to fully \
# answer the question, say what you *can* determine and what would need to be checked \
# elsewhere (e.g. a file not included in the index).
# 6. **Never hallucinate** — do not invent API endpoints, package versions, function \
# signatures, or file paths that are not visible in the context.
# """

# # ── Query expansion ───────────────────────────────────────────────────────────

# def _expand_query(question: str) -> list[str]:
#     """
#     Return 2-3 semantically related search strings for the same question.
#     This dramatically improves recall for vague or high-level questions.
#     """
#     q = question.lower()
#     variants: list[str] = [question]

#     # Architecture / structure questions
#     if any(w in q for w in ["architecture", "structure", "overview", "layout", "project"]):
#         variants += ["folder structure files modules", "main entry point application"]

#     # Auth / security
#     if any(w in q for w in ["auth", "login", "session", "oauth", "jwt", "password", "secure"]):
#         variants += ["authentication provider session token", "NextAuth OAuth adapter"]

#     # Database / ORM
#     if any(w in q for w in ["database", "db", "prisma", "postgres", "sql", "orm", "schema"]):
#         variants += ["PrismaClient database connection schema model"]

#     # Config / env
#     if any(w in q for w in ["config", "env", "environment", "variable", "secret", "setup"]):
#         variants += ["environment variables configuration dotenv"]

#     # Docker / deployment
#     if any(w in q for w in ["docker", "deploy", "container", "compose", "run", "start"]):
#         variants += ["docker-compose services ports volumes", "how to run start server"]

#     # Dependencies
#     if any(w in q for w in ["depend", "librar", "package", "import", "install", "crate", "cargo", "npm"]):
#         variants += ["dependencies imports packages libraries"]

#     # Functions / code logic
#     if any(w in q for w in ["function", "method", "class", "how does", "what does", "explain"]):
#         variants += ["function implementation logic code"]

#     # Deduplicate while preserving order
#     seen: set[str] = set()
#     result: list[str] = []
#     for v in variants:
#         if v not in seen:
#             seen.add(v)
#             result.append(v)
#     return result[:4]   # cap at 4 queries


# # ── Chain ─────────────────────────────────────────────────────────────────────

# class CustomConversationalChain:
#     def __init__(self, vectorstore, llm_type: str = "groq"):
#         self.vectorstore = vectorstore
#         self.llm_type = llm_type
#         self.chat_history: list[dict] = []

#         if llm_type == "openai":
#             self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             self.model = "gpt-4o-mini"          # smarter than gpt-3.5-turbo, still cheap
#         elif llm_type == "groq":
#             self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#             self.model = "llama-3.3-70b-versatile"
#         else:
#             raise ValueError(f"Unsupported llm_type '{llm_type}'. Choose 'openai' or 'groq'.")

#     # ── Retrieval ─────────────────────────────────────────────────────────────

#     def _retrieve(self, question: str, k: int = 8) -> tuple[list, str]:
#         """
#         Multi-query retrieval:
#         1. Expand the question into several search variants.
#         2. Run similarity_search for each variant.
#         3. Deduplicate by document id / content hash.
#         4. Format into a rich context block with file metadata headers.
#         """
#         queries = _expand_query(question)
#         seen_ids: set[str] = set()
#         unique_docs: list = []

#         for query in queries:
#             hits = self.vectorstore.similarity_search(query, k=k)
#             for doc in hits:
#                 # Use content hash as dedup key (FAISS has no stable id)
#                 doc_key = hash(doc.page_content[:200])
#                 if doc_key not in seen_ids:
#                     seen_ids.add(doc_key)
#                     unique_docs.append(doc)

#         # Keep the most relevant docs — cap total context to avoid token limits
#         MAX_DOCS = 12
#         selected = unique_docs[:MAX_DOCS]

#         # Build rich context with per-file headers
#         context_parts: list[str] = []
#         for doc in selected:
#             meta = doc.metadata
#             header = (
#                 f"### File: {meta.get('source', meta.get('filename', 'unknown'))}\n"
#                 f"Language: {meta.get('language', 'unknown')}  |  "
#                 f"Repo: {meta.get('repo_name', 'unknown')}"
#             )
#             context_parts.append(f"{header}\n\n```\n{doc.page_content}\n```")

#         context_text = "\n\n---\n\n".join(context_parts)
#         return selected, context_text

#     # ── Invoke ────────────────────────────────────────────────────────────────

#     def invoke(self, inputs: dict) -> dict:
#         question: str = inputs.get("question", "").strip()
#         if not question:
#             return {
#                 "answer": "Please ask a question.",
#                 "source_documents": [],
#                 "chat_history": [],
#             }

#         # 1. Retrieve relevant code context
#         source_docs, context_text = self._retrieve(question)

#         # 2. Build the system prompt with injected context
#         system_prompt = SYSTEM_TEMPLATE.format(context=context_text)

#         # 3. Assemble the full message list
#         messages: list[dict] = [{"role": "system", "content": system_prompt}]

#         # Include recent history (last 10 turns = 5 exchanges) to stay within limits
#         recent_history = self.chat_history[-10:]
#         messages.extend(recent_history)
#         messages.append({"role": "user", "content": question})

#         # 4. Call the LLM
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.2,        # low temp = precise, factual answers
#                 max_tokens=2048,        # enough for detailed architectural answers
#             )
#             answer: str = response.choices[0].message.content

#         except Exception as e:
#             print(f"\n❌ LLM API ERROR ({self.llm_type}): {e}\n")
#             answer = (
#                 f"I couldn't reach the LLM ({self.llm_type}). "
#                 f"Error: {e}\n\n"
#                 "Please check your API key and network connection."
#             )

#         # 5. Persist history
#         self.chat_history.append({"role": "user", "content": question})
#         self.chat_history.append({"role": "assistant", "content": answer})

#         # 6. Format history as MockMessage objects (matches app.py serialiser)
#         formatted_history = [
#             MockMessage("human" if m["role"] == "user" else "ai", m["content"])
#             for m in self.chat_history
#         ]

#         return {
#             "answer": answer,
#             "source_documents": source_docs,
#             "chat_history": formatted_history,
#         }


# # ── Public factory ────────────────────────────────────────────────────────────

# def build_conversational_chain(vectorstore, llm_type: str = "groq") -> CustomConversationalChain:
#     return CustomConversationalChain(vectorstore, llm_type)

import os
import re
from groq import Groq
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class MockMessage:
    """Mimics a LangChain HumanMessage / AIMessage so app.py serialisation works."""
    def __init__(self, msg_type: str, content: str):
        self.type = msg_type
        self.content = content


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_TEMPLATE = """\
You are **Squirrel**, a senior software engineer and code-intelligence assistant. \
Your only knowledge source is the repository context injected below — \
do NOT invent code, functions, files, or behaviours that are not present in that context.

━━━━━━━━━━━━━━━━━━━━━━━  REPOSITORY CONTEXT  ━━━━━━━━━━━━━━━━━━━━━━━
{context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Your capabilities
You can answer questions about:
- **Architecture** — how components are structured, layered, and connected
- **Code logic** — what specific functions, classes, or modules do
- **Data flow** — how data moves between files, functions, and services
- **Configuration** — env vars, Docker, build files, config schemas
- **Dependencies** — libraries used, why they exist, how they are wired
- **Setup & usage** — how to install, run, test, or extend the project
- **Cross-file relationships** — imports, adapters, shared utilities
- **Security patterns** — auth, session management, secrets handling
- **Multi-turn follow-ups** — you remember everything said earlier in the chat

## Rules
1. **Stay grounded** — base every claim on the context above. If a file or function \
is not in the context, say so explicitly rather than guessing.
2. **Be precise** — quote exact filenames, function names, variable names, and key \
snippets when they are available in the context.
3. **Explain deeply** — for architecture / design questions give layered explanations \
(what → why → how → trade-offs).
4. **Use markdown** — use code blocks (```language), bullet lists, and bold headings \
to structure longer answers.
5. **Acknowledge gaps** — if the context does not contain enough information to fully \
answer the question, say what you *can* determine and what would need to be checked \
elsewhere (e.g. a file not included in the index).
6. **Never hallucinate** — do not invent API endpoints, package versions, function \
signatures, or file paths that are not visible in the context.
"""

NON_SUBSCRIPTION_RESPONSE = "Feature can only be enabled post Subsciption"


# ── Subscription gate ─────────────────────────────────────────────────────────

# Hard keyword patterns — matched against the lowercased question
_GATED_EXACT: list[str] = [
    "show me the code", "show the code", "show code",
    "display the code", "print the code",
    "give me the code", "give the code",
    "full code", "entire code", "whole code",
    "show me the file", "show the file", "display the file",
    "give me the file", "print the file",
    "show codebase", "show me the codebase", "give me the codebase",
    "entire codebase", "full codebase", "source code",
    "paste the code", "paste the file", "dump the code",
    "print out the file", "output the file", "output the code",
    "raw file", "raw content", "file content", "file contents",
    "what is in the file", "what's in the file",
    "contents of the file", "content of the file",
]

# Regex patterns — catch rephrasing and combinations
_GATED_REGEX: list[re.Pattern] = [
    # "show/display/give/paste/print/dump/output" + optional filler + "code/file/codebase"
    re.compile(
        r"\b(show|display|give|paste|print|dump|output|reproduce|copy)\b"
        r".{0,25}\b(code|file|codebase|implementation|source)\b",
        re.IGNORECASE,
    ),
    # "full/entire/whole/complete/raw" + optional filler + "code/file/codebase/content"
    re.compile(
        r"\b(full|entire|whole|complete|raw)\b"
        r".{0,20}\b(code|file|codebase|content|source|implementation)\b",
        re.IGNORECASE,
    ),
    # "what is/what's in <filename>" — e.g. "what is in auth.ts"
    re.compile(
        r"\bwhat(\'s| is) in\b.{0,40}\.(ts|tsx|js|jsx|py|go|rs|toml|yaml|yml|json|css|md)\b",
        re.IGNORECASE,
    ),
    # "read/open/load the file"
    re.compile(
        r"\b(read|open|load)\b.{0,20}\b(the\s+)?(file|code|source)\b",
        re.IGNORECASE,
    ),
]


def _is_gated(question: str) -> bool:
    """
    Return True if the question is asking to dump/display raw file contents.
    Checks both exact phrase list and regex patterns to catch rephrasing.
    """
    q_lower = question.lower().strip()

    # 1. Exact phrase match
    if any(pattern in q_lower for pattern in _GATED_EXACT):
        return True

    # 2. Regex match
    if any(rx.search(question) for rx in _GATED_REGEX):
        return True

    return False


# ── Query expansion ───────────────────────────────────────────────────────────

def _expand_query(question: str) -> list[str]:
    """
    Return up to 4 semantically related search strings for the same question.
    Improves recall for vague or high-level questions.
    """
    q = question.lower()
    variants: list[str] = [question]

    if any(w in q for w in ["architecture", "structure", "overview", "layout", "project"]):
        variants += ["folder structure files modules", "main entry point application"]

    if any(w in q for w in ["auth", "login", "session", "oauth", "jwt", "password", "secure"]):
        variants += ["authentication provider session token", "NextAuth OAuth adapter"]

    if any(w in q for w in ["database", "db", "prisma", "postgres", "sql", "orm", "schema"]):
        variants += ["PrismaClient database connection schema model"]

    if any(w in q for w in ["config", "env", "environment", "variable", "secret", "setup"]):
        variants += ["environment variables configuration dotenv"]

    if any(w in q for w in ["docker", "deploy", "container", "compose", "run", "start"]):
        variants += ["docker-compose services ports volumes", "how to run start server"]

    if any(w in q for w in ["depend", "librar", "package", "import", "install", "crate", "cargo", "npm"]):
        variants += ["dependencies imports packages libraries"]

    if any(w in q for w in ["function", "method", "class", "how does", "what does", "explain"]):
        variants += ["function implementation logic code"]

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result[:4]


# ── Chain ─────────────────────────────────────────────────────────────────────

class CustomConversationalChain:
    def __init__(
        self,
        vectorstore,
        llm_type: str = "openai",
        code_id: str | None = None,
        subscription: bool = False,
    ):
        self.vectorstore = vectorstore
        self.llm_type = llm_type
        self.code_id = code_id
        self.subscription = subscription
        self.chat_history: list[dict] = []
        # Track consecutive gate hits to catch persistent rephrasing attempts
        self._gate_hit_count: int = 0

        if llm_type == "openai":
            self.llm = ChatOpenAI(
                model=os.environ.get("GITHUB_MODEL_NAME", "gpt-4o"),
                api_key=os.environ.get("GITHUB_TOKEN", ""),
                base_url="https://models.inference.ai.azure.com",
                temperature=0.0,
            )
        elif llm_type == "groq":
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError(f"Unsupported llm_type '{llm_type}'. Choose 'openai' or 'groq'.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _format_history(self) -> list[MockMessage]:
        return [
            MockMessage("human" if m["role"] == "user" else "ai", m["content"])
            for m in self.chat_history
        ]

    def _save_turn(self, question: str, answer: str) -> None:
        self.chat_history.append({"role": "user",      "content": question})
        self.chat_history.append({"role": "assistant", "content": answer})

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def _retrieve(self, question: str, k: int = 8, code_id: str | None = None) -> tuple[list, str]:
        queries = _expand_query(question)
        seen_ids: set[int] = set()
        unique_docs: list = []

        for query in queries:
            metadata_filter = {"code_id": code_id} if code_id else None
            hits = self.vectorstore.similarity_search(query, k=k, metadata_filter=metadata_filter)
            for doc in hits:
                # Keep a defensive filter in case the vectorstore implementation ignores metadata_filter.
                if code_id and doc.metadata.get("code_id") != code_id:
                    continue

                doc_key = hash(doc.page_content[:200])
                if doc_key not in seen_ids:
                    seen_ids.add(doc_key)
                    unique_docs.append(doc)

        selected = unique_docs[:12]

        context_parts: list[str] = []
        for doc in selected:
            meta = doc.metadata
            score = meta.get("similarity_score", "")
            score_str = f"  |  Score: {score:.3f}" if isinstance(score, float) else ""
            header = (
                f"### File: {meta.get('source', meta.get('filename', 'unknown'))}\n"
                f"Language: {meta.get('language', 'unknown')}  |  "
                f"Repo: {meta.get('repo_name', 'unknown')}{score_str}"
            )
            context_parts.append(f"{header}\n\n```\n{doc.page_content}\n```")

        return selected, "\n\n---\n\n".join(context_parts)

    # ── Invoke ────────────────────────────────────────────────────────────────

    def invoke(self, inputs: dict) -> dict:
        question: str = inputs.get("question", "").strip()
        subscription = bool(inputs.get("subscription", self.subscription))

        # ── Empty question ────────────────────────────────────────────────────
        if not question:
            return {
                "answer": "Please ask a question.",
                "source_documents": [],
                "chat_history": self._format_history(),
            }

        # ── Subscription gate ─────────────────────────────────────────────────
        if _is_gated(question) and not subscription:
            self._gate_hit_count += 1

            self._save_turn(question, NON_SUBSCRIPTION_RESPONSE)
            return {
                "answer": NON_SUBSCRIPTION_RESPONSE,
                "source_documents": [],
                "chat_history": self._format_history(),
            }

        # Reset gate counter on a legitimate question
        self._gate_hit_count = 0

        effective_code_id = (inputs.get("code_id") or self.code_id or "").strip()
        if not effective_code_id:
            answer = "A code_id is required to answer questions in a scoped session."
            self._save_turn(question, answer)
            return {
                "answer": answer,
                "source_documents": [],
                "chat_history": self._format_history(),
            }

        # ── Retrieve context ──────────────────────────────────────────────────
        source_docs, context_text = self._retrieve(question, code_id=effective_code_id)

        if not source_docs:
            answer = (
                f"I couldn't find matching context for code_id '{effective_code_id}'. "
                "Please verify the code_id or initialize a session for the right repository snapshot."
            )
            self._save_turn(question, answer)
            return {
                "answer": answer,
                "source_documents": [],
                "chat_history": self._format_history(),
            }

        # ── Build messages ────────────────────────────────────────────────────
        system_prompt = SYSTEM_TEMPLATE.format(context=context_text)
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.chat_history[-10:])   # last 5 exchanges
        messages.append({"role": "user", "content": question})

        # ── Call LLM ──────────────────────────────────────────────────────────
        try:
            if self.llm_type == "openai":
                response = self.llm.invoke(messages)
                answer: str = response.content if isinstance(response.content, str) else str(response.content)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=2048,
                )
                answer = response.choices[0].message.content

        except Exception as e:
            print(f"\n❌ LLM API ERROR ({self.llm_type}): {e}\n")
            answer = (
                f"I couldn't reach the LLM ({self.llm_type}). "
                f"Error: {e}\n\n"
                "Please check your API key and network connection."
            )

        # Defensive gate if model returns restricted marker text.
        if "SQUIRREL_GATED" in answer and not subscription:
            answer = NON_SUBSCRIPTION_RESPONSE

        # ── Persist ───────────────────────────────────────────────────────────
        self._save_turn(question, answer)

        return {
            "answer": answer,
            "source_documents": source_docs,
            "chat_history": self._format_history(),
        }


# ── Public factory ────────────────────────────────────────────────────────────

def build_conversational_chain(
    vectorstore,
    llm_type: str = "groq",
    code_id: str | None = None,
    subscription: bool = False,
) -> CustomConversationalChain:
    return CustomConversationalChain(vectorstore, llm_type, code_id, subscription)