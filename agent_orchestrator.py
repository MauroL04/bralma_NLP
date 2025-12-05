from typing import Dict
from rag_agent import ingest_pdf, get_context_for_question
import groq_llm


def ingest_and_store_pdf(file_bytes: bytes, filename: str) -> Dict:
    return ingest_pdf(file_bytes, filename)


def answer_question(question: str, k: int = 4) -> Dict:
    context = get_context_for_question(question, k=10)
    print("[Orchestrator] Context sent to LLM:\n" + context[:1000])
    if context:
        answer = groq_llm.ask_question_with_context(question, context)
    else:
        answer = groq_llm.ask_question(question)
    return {"answer": answer, "context": context}


__all__ = ["ingest_and_store_pdf", "answer_question"]
