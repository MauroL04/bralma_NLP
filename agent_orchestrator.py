from typing import Dict
from langchain_agent import ingest_pdf as lc_ingest_pdf, get_context_for_question as lc_get_context_for_question
import groq_llm

def ingest_and_store_pdf_langchain(file_bytes: bytes, filename: str) -> Dict:
    return lc_ingest_pdf(file_bytes, filename)


def answer_question_langchain(question: str, k: int = 4) -> Dict:
    context = lc_get_context_for_question(question, k=k)
    if context:
        answer = groq_llm.ask_question_with_context(question, context)
    else:
        answer = groq_llm.ask_question(question)
    return {"answer": answer, "context": context}


__all__ = ["ingest_and_store_pdf", "answer_question"]
