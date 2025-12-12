"""PDF ingestion and retrieval tools for CrewAI"""
import sys
from pathlib import Path
from typing import Dict
from crewai.tools import tool

# Voeg parent directory toe aan path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from langchain_agent import ingest_pdf, get_context_for_question
import groq_answer_llm


@tool
def ingest_pdf_tool(file_path: str, filename: str) -> Dict:
    """
    Ingest a PDF file and store it in the Chroma vector database.
    
    Args:
        file_path: Path to the PDF file
        filename: Display name for the PDF
    
    Returns:
        Dict with ingestion results
    """
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        result = ingest_pdf(file_bytes, filename)
        return {
            "status": "success",
            "filename": filename,
            "chunks_ingested": result.get("chunks_ingested"),
            "message": f"Successfully ingested {filename} with {result.get('chunks_ingested')} chunks"
        }
    except Exception as e:
        return {
            "status": "error",
            "filename": filename,
            "error": str(e)
        }


@tool
def retrieve_context_tool(question: str, k: int = 4) -> Dict:
    """
    Retrieve relevant context from ingested PDFs for a given question.
    
    Args:
        question: The user's question
        k: Number of context chunks to retrieve
    
    Returns:
        Dict with retrieved context
    """
    try:
        context = get_context_for_question(question, k=k)
        return {
            "status": "success",
            "question": question,
            "context": context,
            "chunks_retrieved": len(context.split("---"))
        }
    except Exception as e:
        return {
            "status": "error",
            "question": question,
            "error": str(e)
        }


@tool
def answer_question_with_context_tool(question: str, context: str = "") -> Dict:
    """
    Answer a question using Groq LLM, optionally with PDF context.
    
    Args:
        question: The user's question
        context: Optional context from retrieved PDFs
    
    Returns:
        Dict with answer and quiz
    """
    try:
        answer = groq_answer_llm.answer_and_maybe_quiz(question, context)
        return {
            "status": "success",
            "question": question,
            "answer": answer
        }
    except Exception as e:
        return {
            "status": "error",
            "question": question,
            "error": str(e)
        }


__all__ = [
    "ingest_pdf_tool",
    "retrieve_context_tool", 
    "answer_question_with_context_tool"
]
