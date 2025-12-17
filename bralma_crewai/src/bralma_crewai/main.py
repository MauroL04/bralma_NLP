#!/usr/bin/env python
"""
CrewAI Orchestration Entry Point.
Demonstrates full multi-agent workflow for document RAG system (PDF + PPTX).
"""

import warnings
from pathlib import Path

from bralma_crewai.crew import PDFProcessingCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run_pdf_rag_workflow(question: str, pdf_context: str = ""):
    """
    Run multi-agent workflow: RAG retrieval → Answer + Quiz
    
    Args:
        question: User's question
        pdf_context: Optional document context (if already extracted)
        
    Returns:
        Answer with quiz (orchestrated by CrewAI agents)
    """
    try:
        print(f"\n🚀 CrewAI Multi-Agent Workflow Starting...")
        print(f"❓ Question: {question}\n")
        
        crew = PDFProcessingCrew()
        
        result = crew.crew().kickoff(inputs={
            'question': question,
            'context': pdf_context
        })
        
        print(f"\n✅ Workflow Complete!\n")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        raise Exception(f"CrewAI workflow error: {e}")


if __name__ == "__main__":
    # Demo workflow
    question = "What are the main topics in this document?"
    result = run_pdf_rag_workflow(question)
    print(result)
