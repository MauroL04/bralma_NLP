import os
from io import BytesIO
from typing import List
from datetime import datetime
try:
    import fitz
    HAS_FITZ = True
except Exception:
    fitz = None
    HAS_FITZ = False
    import PyPDF2
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "pdf_docs"

try:
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
except Exception:
    device = "cpu"
text_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
client = chromadb.PersistentClient(path=PERSIST_DIR)


def _extract_pages(file_bytes: bytes) -> List[dict]:
    pages = []
    if HAS_FITZ:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text")
            images = []
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 4:
                    img_bytes = pix.tobytes("png")
                else:
                    pix0 = fitz.Pixmap(fitz.csRGB, pix)
                    img_bytes = pix0.tobytes("png")
                    pix0 = None
                pix = None
                images.append(img_bytes)
            pages.append({"page_number": i + 1, "text": text or "", "images": images})
    else:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append({"page_number": i + 1, "text": text, "images": []})
    return pages


def _embed_texts(texts: List[str]) -> np.ndarray:
    embs = text_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embs


def _embed_image_bytes_list(image_bytes_list: List[bytes]) -> np.ndarray:
    if not image_bytes_list:
        return np.array([])
    imgs = [Image.open(BytesIO(b)).convert("RGB") for b in image_bytes_list]
    inputs = clip_processor(images=imgs, return_tensors="pt")
    for k, v in inputs.items():
        inputs[k] = v.to(device)
    with torch.no_grad():
        feats = clip_model.get_image_features(**inputs)
    feats = feats.cpu().numpy()
    norms = np.linalg.norm(feats, axis=1, keepdims=True)
    norms[norms == 0] = 1
    feats = feats / norms
    return feats


def ingest_pdf(file_bytes: bytes, filename: str) -> dict:
    pages = _extract_pages(file_bytes)
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    for p in pages:
        page_text = p["text"].strip()
        # No logging here
        text_chunks = [page_text]
        image_embs = _embed_image_bytes_list(p["images"]) if p["images"] else np.array([])
        for idx, chunk in enumerate(text_chunks, start=1):
            text_emb = _embed_texts([chunk])[0]
            if image_embs.size:
                img_mean = image_embs.mean(axis=0)
                combined = np.concatenate([text_emb, img_mean])
            else:
                combined = np.concatenate([text_emb, np.zeros(768)])
            uid = f"{filename}::p{p['page_number']}::c{idx}::{datetime.utcnow().timestamp()}"
            ids.append(uid)
            documents.append(chunk)
            metadatas.append({"source": filename, "page": p["page_number"], "chunk": idx, "image_count": len(p["images"])} )
            embeddings.append(combined.tolist())
    if not os.path.isdir(PERSIST_DIR):
        os.makedirs(PERSIST_DIR, exist_ok=True)
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        collection = client.create_collection(name=COLLECTION_NAME)
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return {"filename": filename, "chunks_ingested": len(documents), "persist_directory": PERSIST_DIR}


def query(question: str, k: int = 4) -> List[dict]:
    text_emb = _embed_texts([question])[0]
    # Pad with zeros for image part so query embedding matches chunk embedding length
    q_emb = np.concatenate([text_emb, np.zeros(768)]).tolist()
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return []
    res = collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances"]) 
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    out = []
    for doc, meta, dist in zip(docs, metas, dists):
        out.append({"page_content": doc, "metadata": meta, "score": float(dist)})
    return out


def get_context_for_question(question: str, k: int = 4) -> str:
    hits = query(question, k=10)
    parts = []
    for i, h in enumerate(hits, start=1):
        src = h.get("metadata", {}).get("source", "unknown")
        parts.append(f"--- Source: {src} | Chunk {i} | Score: {h.get('score'):.4f} ---\n{h.get('page_content')}\n")
    context = "\n".join(parts)
    return context


__all__ = ["ingest_pdf", "query", "get_context_for_question"]
