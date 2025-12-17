import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredPowerPointLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings


BASE_DIR = Path(__file__).parent
PERSIST_DIR = str(BASE_DIR / "chroma_db")
PDF_STORE = str(BASE_DIR / "pdf_store")

os.makedirs(PDF_STORE, exist_ok=True)

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def ingest_pdf(file_bytes: bytes, filename: str) -> Dict:
    """Ingest a document (PDF or PPTX) using LangChain loader and splitter, store chunks in Chroma."""
    # Detect file type and save with correct extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ['.pdf', '.pptx']:
        file_ext = '.pdf'  # default to PDF
    
    path = Path(PDF_STORE) / f"{filename}__{int(datetime.utcnow().timestamp())}{file_ext}"
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "wb") as f:
            f.write(file_bytes)

        # Use appropriate loader based on file type
        if file_ext == '.pptx':
            loader = UnstructuredPowerPointLoader(str(path))
        else:
            loader = PyMuPDFLoader(str(path))
        
        docs = loader.load()
        docs = splitter.split_documents(docs)

        # attach source metadata (force filename only)
        for d in docs:
            if not d.metadata:
                d.metadata = {}
            d.metadata["source"] = filename

        os.makedirs(PERSIST_DIR, exist_ok=True)
        if Path(PERSIST_DIR).exists() and any(Path(PERSIST_DIR).iterdir()):
            db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
            db.add_documents(docs)
        else:
            db = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=PERSIST_DIR)
        db.persist()

        return {"filename": filename, "chunks_ingested": len(docs), "persist_directory": PERSIST_DIR}
    finally:
        # Remove temporary copy to avoid accumulation in pdf_store
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass

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


def list_ingested_sources() -> List[Dict]:
    """Return distinct sources and chunk counts currently persisted in ChromaDB."""
    if not Path(PERSIST_DIR).exists() or not any(Path(PERSIST_DIR).iterdir()):
        return []

    try:
        db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
        data = db.get(include=["metadatas"])
        metadatas = data.get("metadatas", []) or []
        counts = {}
        for meta in metadatas:
            raw = (meta or {}).get("source", "unknown")
            src = Path(str(raw)).name  # strip to filename
            # remove temp suffixes like '__1234567890.ext'
            if "__" in src:
                src = src.split("__", 1)[0]
            counts[src] = counts.get(src, 0) + 1
        return [{"name": k, "chunks": v} for k, v in counts.items()]
    except Exception:
        return []


def get_context_for_question(question: str, k: int = 4) -> str:
    hits = query(question, k=k)
    parts = []
    for i, h in enumerate(hits, start=1):
        src = h.get("metadata", {}).get("source", "unknown")
        parts.append(f"--- Source: {src} | Chunk {i} | Score: {h.get('score'):.4f} ---\n{h.get('page_content')}\n")
    return "\n".join(parts)


__all__ = ["ingest_pdf", "query", "get_context_for_question", "list_ingested_sources"]