import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings


BASE_DIR = Path(__file__).parent
PERSIST_DIR = str(BASE_DIR / "chroma_db")
PDF_STORE = str(BASE_DIR / "pdf_store")

os.makedirs(PDF_STORE, exist_ok=True)

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def ingest_pdf(file_bytes: bytes, filename: str) -> Dict:
    """Ingest a PDF using LangChain loader and splitter, store chunks in Chroma."""
    path = Path(PDF_STORE) / f"{filename}__{int(datetime.utcnow().timestamp())}.pdf"
    with open(path, "wb") as f:
        f.write(file_bytes)

    loader = PyMuPDFLoader(str(path))
    docs = loader.load()
    docs = splitter.split_documents(docs) 

    # attach source metadata
    for d in docs:
        if not d.metadata:
            d.metadata = {}
        d.metadata.setdefault("source", filename)

    os.makedirs(PERSIST_DIR, exist_ok=True)
    db = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=PERSIST_DIR)
    db.persist()

    return {"filename": filename, "chunks_ingested": len(docs), "persist_directory": PERSIST_DIR}

def query(question: str, k: int = 4) -> List[Dict]:
    try:
        db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    except Exception:
        return []

    docs_and_scores = db.similarity_search_with_score(question, k=k)
    out = []
    for doc, score in docs_and_scores:
        out.append({"page_content": doc.page_content, "metadata": getattr(doc, 'metadata', {}), "score": float(score)})
    return out


def get_context_for_question(question: str, k: int = 4) -> str:
    hits = query(question, k=k)
    parts = []
    for i, h in enumerate(hits, start=1):
        src = h.get("metadata", {}).get("source", "unknown")
        parts.append(f"--- Source: {src} | Chunk {i} | Score: {h.get('score'):.4f} ---\n{h.get('page_content')}\n")
    return "\n".join(parts)


__all__ = ["ingest_pdf", "query", "get_context_for_question"]