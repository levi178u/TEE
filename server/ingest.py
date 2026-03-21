import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in environment.")
    return psycopg2.connect(DATABASE_URL)


def list_available_repos() -> list[str]:
    """Return distinct repoName values from the Code table."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT DISTINCT "repoName" FROM "Code" ORDER BY "repoName"')
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def list_available_code_ids(repo_name: str | None = None) -> list[dict]:
    """Return available Code IDs (optionally filtered by repoName)."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if repo_name:
                cur.execute(
                    "SELECT c.id, c.\"repoName\", COALESCE((to_jsonb(c) ->> 'Subscription')::boolean, (to_jsonb(c) ->> 'subscription')::boolean, false) AS subscription FROM \"Code\" c WHERE c.\"repoName\" = %s ORDER BY c.\"createdAt\" ASC",
                    (repo_name,),
                )
            else:
                cur.execute("SELECT c.id, c.\"repoName\", COALESCE((to_jsonb(c) ->> 'Subscription')::boolean, (to_jsonb(c) ->> 'subscription')::boolean, false) AS subscription FROM \"Code\" c ORDER BY c.\"repoName\", c.\"createdAt\" ASC")

            rows = cur.fetchall()
            return [
                {
                    "code_id": str(r["id"]),
                    "repo_name": r["repoName"],
                    "subscription": bool(r.get("subscription", False)),
                }
                for r in rows
            ]
    finally:
        conn.close()


def get_code_subscription(code_id: str) -> bool:
    """Return subscription flag for a Code.id. Defaults to False when absent."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COALESCE((to_jsonb(c) ->> 'Subscription')::boolean, (to_jsonb(c) ->> 'subscription')::boolean, false) AS subscription FROM \"Code\" c WHERE c.id = %s",
                (code_id,),
            )
            row = cur.fetchone()
            if not row:
                return False
            return bool(row.get("subscription", False))
    finally:
        conn.close()


def load_codebase(
    repo_name: str | None = None,
    code_id: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """
    Load CodeBase rows joined with Code from the Prisma-managed Postgres schema.

    Prisma uses quoted CamelCase identifiers – e.g. "CodeBase", "createdAt".
    Returns a list of {"content": str, "metadata": dict} dicts ready for FAISS.
    """
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            where: list[str] = []
            params: list[object] = []

            if repo_name:
                where.append('c."repoName" = %s')
                params.append(repo_name)
            if code_id:
                where.append('cb."codeId" = %s')
                params.append(code_id)

            where_sql = f"WHERE {' AND '.join(where)}" if where else ""
            limit_sql = f"LIMIT {int(limit)}" if limit else ""

            query = f"""
                SELECT
                    cb.id,
                    cb.language,
                    cb.filename,
                    cb.route,
                    cb.text,
                    cb."codeId",
                    c."repoName"   AS "repoName",
                    COALESCE((to_jsonb(c) ->> 'Subscription')::boolean, (to_jsonb(c) ->> 'subscription')::boolean, false) AS "subscription",
                    cb."createdAt"
                FROM "CodeBase" cb
                JOIN "Code" c ON c.id = cb."codeId"
                {where_sql}
                ORDER BY cb."createdAt" ASC
                {limit_sql}
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()

            documents = []
            for row in rows:
                route    = row["route"]    or ""
                filename = row["filename"] or ""
                source   = f"{route}/{filename}".replace("//", "/")
                created_at = row.get("createdAt")

                metadata = {
                    "codebase_id": str(row["id"]),
                    "code_id":     str(row["codeId"]),
                    "subscription": bool(row.get("subscription", False)),
                    "repo_name":   row.get("repoName"),
                    "language":    row.get("language"),
                    "filename":    filename,
                    "route":       route,
                    "source":      source,
                    "created_at":  created_at.isoformat() if created_at else None,
                }
                content = row.get("text") or ""
                if content.strip():          # skip empty files
                    documents.append({"content": content, "metadata": metadata})

            return documents
    finally:
        conn.close()




# import os 
# import shutil
# import subprocess
# import tempfile
# from pathlib import Path
# from langchain.document_loaders import TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from markdown2 import markdown
# from tqdm import tqdm
# from utils import convert_markdown_to_text, clean_text, detect_language, normalize_path, is_supported_file, 
# # from ast_parser import extract_code_blocks

# text_ext ={'.txt', '.md', '.py', '.rs', '.csv', '.toml', '.yaml', '.yml', '.ini', '.cfg', '.log', '.java', '.js', '.json'}

# def clone_repo(repo_url, temp_dir):
#     try:
#         subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True)
#         return temp_dir
#     except subprocess.CalledProcessError as e:
#         print(f"Error cloning repository: {e}")
#         return None

# def load_documents(repo_path):
#     documents = []
#     for root, _, files in os.walk(repo_path):
#         if any(skip in root for skip in ['.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build']):
#             continue
        
#         for file in files:
#             if Path(file).suffix.lower() in text_ext:
#                 file_path = os.path.join(root, file)
#                 try:
#                     content = safe_read_file(file_path)

#                     if file_path.endswith('.md'):
#                         content = convert_markdown_to_text(content)
#                     content = clean_text(content)

#                     metadata = {
#                         "file_path": os.name.basename(file_path),
#                         "folder": os.path.dirname(file_path),
#                         "language": detect_language(file_path),
#                         "source": normalize_path(file_path)
#                     }
#                     documents.append({"content": content, "metadata": metadata})
#                 except Exception as e:
#                     print(f"Error loading {file_path}: {e}")
#     return documents

# def split_documents(documents):
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     split_docs = []
    
#     for doc in tqdm(documents, desc="Splitting documents"):
#         try:
#             chunks = text_splitter.split_text(doc["content"])
#             for chunk in chunks:
#                 split_docs.append({"content": chunk, "metadata": doc["metadata"]})
#         except Exception as e:
#             print(f"Error splitting document: {e}")
#     return split_docs

# def ingest_repo(github_url):
#     tmpdir = tempfile.mkdtemp(prefix="repo_ingest_")
#     repo_path = clone_repo(github_url, tmpdir)
#     if not repo_path:
#         return []
#     try:
#         documents = load_documents(repo_path)
#         split_docs = split_documents(documents)
#         return split_docs, tmpdir 

