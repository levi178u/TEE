# import os
# from dotenv import load_dotenv
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# load_dotenv()

# EMBEDDING_MODEL = os.getenv(
#     "EMBEDDING_MODEL",
#     "sentence-transformers/all-MiniLM-L6-v2"
# )

# embeddings = HuggingFaceEmbeddings(
#     model_name=EMBEDDING_MODEL
# )

# vector_db_path = "faiss_index"

# def create_vectorstore(docs):

#     texts = [doc["content"] for doc in docs]
#     metadatas = [doc["metadata"] for doc in docs]

#     vectorstore = FAISS.from_texts(
#         texts=texts,
#         embedding=embeddings,
#         metadatas=metadatas
#     )
#     vectorstore.save_local(vector_db_path)

#     return vectorstore

# def create_vectorstore(docs):
#     # ADD TEXT SPLITTER
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000, 
#         chunk_overlap=200,
#         separators=["\n\n", "\n", " ", ""]
#     )
    
#     split_texts = []
#     split_metadatas = []
    
#     for doc in docs:
#         # Split each document's content into chunks
#         chunks = text_splitter.split_text(doc["content"])
#         for chunk in chunks:
#             split_texts.append(chunk)
#             split_metadatas.append(doc["metadata"])

#     # Create vectorstore from the chunks instead of full files
#     vectorstore = FAISS.from_texts(
#         texts=split_texts,
#         embedding=embeddings,
#         metadatas=split_metadatas
#     )
#     vectorstore.save_local(vector_db_path)

#     return vectorstore

# def load_vectorstore():
#     if os.path.exists(vector_db_path):
#         # allow_dangerous_deserialization is required by recent langchain versions
#         vectorstore = FAISS.load_local(
#             vector_db_path,
#             embeddings,
#             allow_dangerous_deserialization=True,
#         )
#         return vectorstore
#     return None

# import faiss
# import numpy as np

# dimension = 384
# index = faiss.IndexFlatL2(dimension)

# documents = []

# def add_document(text, embedding):
#     index.add(np.array([embedding]).astype("float32"))
#     documents.append(text)

# def search(query_embedding, k=3):
#     distances, indices = index.search(
#         np.array([query_embedding]).astype("float32"), k
#     )
#     results = [documents[i] for i in indices[0]]
#     return results

# import os
# import json
# import numpy as np
# import faiss
# from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer

# load_dotenv()

# EMBEDDING_MODEL = os.getenv(
#     "EMBEDDING_MODEL",
#     "sentence-transformers/all-MiniLM-L6-v2"
# )

# vector_db_path = "faiss_index"

# class Document:
#     """Mock document class to mimic LangChain's structure for llm.py"""
#     def __init__(self, page_content: str, metadata: dict):
#         self.page_content = page_content
#         self.metadata = metadata

# class CustomFAISS:
#     """A wrapper to handle FAISS vector search and map results back to text."""
#     def __init__(self, index, texts, metadatas, model):
#         self.index = index
#         self.texts = texts
#         self.metadatas = metadatas
#         self.model = model

#     def similarity_search(self, query: str, k: int = 5):
#         # 1. Embed the query
#         query_vector = self.model.encode([query]).astype('float32')
        
#         # 2. Search the FAISS index
#         distances, indices = self.index.search(query_vector, k)
        
#         # 3. Map indices back to our text chunks
#         results = []
#         for idx in indices[0]:
#             if idx != -1 and idx < len(self.texts):
#                 results.append(
#                     Document(
#                         page_content=self.texts[idx], 
#                         metadata=self.metadatas[idx]
#                     )
#                 )
#         return results

# def simple_text_splitter(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
#     """A native sliding-window text chunker to replace LangChain's RecursiveCharacterTextSplitter."""
#     chunks = []
#     start = 0
#     text_length = len(text)
    
#     while start < text_length:
#         end = min(start + chunk_size, text_length)
#         chunks.append(text[start:end])
#         if end == text_length:
#             break
#         start += (chunk_size - chunk_overlap)
        
#     return chunks

# def create_vectorstore(docs):
#     model = SentenceTransformer(EMBEDDING_MODEL)
    
#     split_texts = []
#     split_metadatas = []
    
#     # 1. Split the documents
#     for doc in docs:
#         chunks = simple_text_splitter(doc["content"])
#         for chunk in chunks:
#             split_texts.append(chunk)
#             split_metadatas.append(doc["metadata"])

#     # 2. Embed all chunks into vectors
#     print(f"Embedding {len(split_texts)} chunks...")
#     embeddings = model.encode(split_texts).astype('float32')
    
#     # 3. Create the FAISS index
#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)
    
#     # 4. Save everything locally
#     os.makedirs(vector_db_path, exist_ok=True)
    
#     # Save the vector index
#     faiss.write_index(index, os.path.join(vector_db_path, "index.faiss"))
    
#     # Save the text and metadata mappings
#     with open(os.path.join(vector_db_path, "metadata.json"), "w", encoding="utf-8") as f:
#         json.dump({"texts": split_texts, "metadatas": split_metadatas}, f)
        
#     return CustomFAISS(index, split_texts, split_metadatas, model)

# def load_vectorstore():
#     index_file = os.path.join(vector_db_path, "index.faiss")
#     meta_file = os.path.join(vector_db_path, "metadata.json")
    
#     if os.path.exists(index_file) and os.path.exists(meta_file):
#         # 1. Load the FAISS index
#         index = faiss.read_index(index_file)
        
#         # 2. Load the text mappings
#         with open(meta_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
            
#         # 3. Load the embedding model
#         model = SentenceTransformer(EMBEDDING_MODEL)
        
#         return CustomFAISS(index, data["texts"], data["metadatas"], model)
        
#     return None

import os
import json
import hashlib
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

vector_db_path = "faiss_index"


# ── Document wrapper ──────────────────────────────────────────────────────────

class Document:
    """Mimics LangChain's Document so llm.py works without changes."""
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        src = self.metadata.get("source", self.metadata.get("filename", "?"))
        return f"Document(source={src!r}, chars={len(self.page_content)})"


# ── Smart text splitter ───────────────────────────────────────────────────────

def smart_text_splitter(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[str]:
    """
    Splits on natural boundaries in priority order:
      1. Blank lines (paragraph / function boundaries)
      2. Single newlines
      3. Sentences (". ")
      4. Hard character limit as last resort

    This keeps functions, classes, and logical blocks intact instead of
    cutting mid-word like a pure character splitter does.
    """
    if not text or not text.strip():
        return []

    # Ordered separators — try each until chunks are small enough
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_by(src: str, sep: str) -> list[str]:
        if not sep:
            # Hard cut — last resort
            return [src[i : i + chunk_size] for i in range(0, len(src), chunk_size - chunk_overlap)]
        parts = src.split(sep)
        merged, buf = [], ""
        for part in parts:
            candidate = buf + sep + part if buf else part
            if len(candidate) <= chunk_size:
                buf = candidate
            else:
                if buf:
                    merged.append(buf)
                # If a single part is still too big, recurse with next separator
                if len(part) > chunk_size:
                    next_sep_idx = separators.index(sep) + 1
                    if next_sep_idx < len(separators):
                        merged.extend(_split_by(part, separators[next_sep_idx]))
                    else:
                        merged.extend(_split_by(part, ""))
                else:
                    buf = part
        if buf:
            merged.append(buf)
        return merged

    raw_chunks = _split_by(text, separators[0])

    # Apply sliding-window overlap between adjacent chunks
    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return [c for c in raw_chunks if c.strip()]

    overlapped: list[str] = [raw_chunks[0]]
    for i in range(1, len(raw_chunks)):
        prev_tail = raw_chunks[i - 1][-chunk_overlap:]
        overlapped.append(prev_tail + raw_chunks[i])

    return [c.strip() for c in overlapped if c.strip()]


# ── FAISS wrapper ─────────────────────────────────────────────────────────────

class CustomFAISS:
    """
    Wraps a FAISS IndexFlatIP (cosine similarity after L2-normalisation).
    Stores full metadata + chunk content so every search result is rich.
    """

    def __init__(
        self,
        index: faiss.Index,
        chunks: list[dict],   # {"text": str, "metadata": dict, "chunk_hash": str}
        model: SentenceTransformer,
    ):
        self.index = index
        self.chunks = chunks
        self.model = model

    # ── Search ────────────────────────────────────────────────────────────────

    def similarity_search(
        self,
        query: str,
        k: int = 8,
        metadata_filter: dict | None = None,
    ) -> list[Document]:
        """
        Cosine-similarity search.
        Returns up to k Document objects with full metadata attached.
        """
        if not query or not query.strip():
            return []

        requested_k = min(k, len(self.chunks))
        if requested_k == 0:
            return []

        search_k = requested_k
        if metadata_filter:
            search_k = min(len(self.chunks), max(requested_k * 5, requested_k))

        vec = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, indices = self.index.search(vec, search_k)

        results: list[Document] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]

            if metadata_filter:
                matches_filter = True
                for key, value in metadata_filter.items():
                    if chunk["metadata"].get(key) != value:
                        matches_filter = False
                        break
                if not matches_filter:
                    continue

            meta = dict(chunk["metadata"])   # copy so we don't mutate stored data
            meta["similarity_score"] = float(score)
            results.append(Document(page_content=chunk["text"], metadata=meta))

            if len(results) >= requested_k:
                break

        return results

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        repos = {c["metadata"].get("repo_name", "unknown") for c in self.chunks}
        langs = {c["metadata"].get("language", "unknown") for c in self.chunks}
        files = {c["metadata"].get("source", "") for c in self.chunks}
        code_ids = {c["metadata"].get("code_id", "") for c in self.chunks if c["metadata"].get("code_id")}
        return {
            "total_chunks": len(self.chunks),
            "repos": sorted(repos),
            "code_ids": sorted(code_ids),
            "languages": sorted(langs),
            "unique_files": len(files),
            "index_size": self.index.ntotal,
        }


# ── Build vectorstore ─────────────────────────────────────────────────────────

def create_vectorstore(docs: list[dict]) -> CustomFAISS:
    """
    1. Smart-split each doc into overlapping chunks.
    2. Deduplicate by content hash (avoids re-embedding identical code).
    3. Embed all unique chunks with sentence-transformers.
    4. Build a cosine FAISS index (IndexFlatIP after L2 normalisation).
    5. Persist index + full metadata to disk.
    """
    model = SentenceTransformer(EMBEDDING_MODEL)

    # ── 1 + 2. Split & deduplicate ────────────────────────────────────────────
    seen_hashes: set[str] = set()
    chunks: list[dict] = []

    for doc in docs:
        content = doc.get("content", "").strip()
        meta    = doc.get("metadata", {})

        if not content:
            continue

        for chunk_text in smart_text_splitter(content):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
            if chunk_hash in seen_hashes:
                continue
            seen_hashes.add(chunk_hash)

            chunks.append({
                "text":       chunk_text,
                "metadata":   meta,
                "chunk_hash": chunk_hash,
            })

    if not chunks:
        raise ValueError("No text chunks produced from the provided documents.")

    print(f"  📦 Embedding {len(chunks)} unique chunks "
          f"(from {len(docs)} documents, {len(seen_hashes)} deduped)...")

    # ── 3. Embed ──────────────────────────────────────────────────────────────
    texts = [c["text"] for c in chunks]

    # Batch in groups of 256 to avoid OOM on large repos
    BATCH = 256
    all_vecs: list[np.ndarray] = []
    for i in range(0, len(texts), BATCH):
        batch_vecs = model.encode(
            texts[i : i + BATCH],
            normalize_embeddings=True,   # required for cosine via IndexFlatIP
            show_progress_bar=False,
        ).astype("float32")
        all_vecs.append(batch_vecs)

    embeddings = np.vstack(all_vecs)

    # ── 4. FAISS index (cosine = inner product on L2-normalised vecs) ─────────
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # ── 5. Persist ────────────────────────────────────────────────────────────
    os.makedirs(vector_db_path, exist_ok=True)

    faiss.write_index(index, os.path.join(vector_db_path, "index.faiss"))

    with open(os.path.join(vector_db_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "model":  EMBEDDING_MODEL,
                "total":  len(chunks),
                "chunks": chunks,          # full text + metadata + hash
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    store = CustomFAISS(index, chunks, model)
    s = store.stats()
    print(f"  ✅ Vectorstore ready — {s['total_chunks']} chunks | "
          f"{s['unique_files']} files | repos: {s['repos']} | langs: {s['languages']}")
    return store


# ── Load vectorstore ──────────────────────────────────────────────────────────

def load_vectorstore() -> CustomFAISS | None:
    """
    Reload a previously saved FAISS index + metadata from disk.
    Returns None if no cache exists yet.
    """
    index_file = os.path.join(vector_db_path, "index.faiss")
    meta_file  = os.path.join(vector_db_path, "metadata.json")

    if not (os.path.exists(index_file) and os.path.exists(meta_file)):
        return None

    index = faiss.read_index(index_file)

    with open(meta_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    saved_model = data.get("model", EMBEDDING_MODEL)
    if saved_model != EMBEDDING_MODEL:
        print(f"  ⚠️  Warning: index was built with '{saved_model}' "
              f"but current EMBEDDING_MODEL is '{EMBEDDING_MODEL}'. "
              "Rebuild with /init for consistent results.")

    model  = SentenceTransformer(saved_model)
    chunks = data["chunks"]

    store = CustomFAISS(index, chunks, model)
    s = store.stats()
    print(f"  ✅ Loaded cached vectorstore — {s['total_chunks']} chunks | "
          f"{s['unique_files']} files | repos: {s['repos']}")
    return store