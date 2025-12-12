# from typing import Dict
# from langchain_agent import ingest_pdf as lc_ingest_pdf, get_context_for_question as lc_get_context_for_question

# import groq_answer_llm

# def ingest_and_store_pdf_langchain(file_bytes: bytes, filename: str) -> Dict:
#     return lc_ingest_pdf(file_bytes, filename)


# def answer_question_langchain(question: str, k: int = 4) -> Dict:
#     context = lc_get_context_for_question(question, k=k)

#     answer = groq_answer_llm.answer_and_maybe_quiz(question, context)
#     return {"answer": answer, "context": context}


# __all__ = ["ingest_and_store_pdf", "answer_question"]
