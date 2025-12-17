#!/usr/bin/env python
"""
CrewAI Orchestration Entry Point.
Demonstrates multi-agent workflow for document RAG system (PDF + PPTX).
"""

import warnings
from bralma_crewai.crew import PDFProcessingCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run_pdf_rag_workflow(question: str, pdf_context: str = ""):
    """
    Run multi-agent workflow: RAG retrieval → Answer + Quiz.

    Args:
        question: User's question
        pdf_context: Optional document context (if already extracted)

    Returns:
        Answer with quiz (orchestrated by CrewAI agents)
    """
    try:
        crew = PDFProcessingCrew()
        return crew.crew().kickoff(inputs={
            'question': question,
            'context': pdf_context
        })
    except Exception as e:
        raise Exception(f"CrewAI workflow error: {e}")


if __name__ == "__main__":
    question = "What are the main topics in this document?"
    result = run_pdf_rag_workflow(question)
    print(result)
