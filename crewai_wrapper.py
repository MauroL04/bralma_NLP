"""
CrewAI Wrapper - Bridge tussen Frontend en multi-agent workflow.
DIRECTE calls naar tools (zonder agent LLM overhead) voor BETERE antwoorden.

NOTE: CrewAI draait in aparte venv (.venv_crewai) om dependency conflicts te vermijden!
"""

import sys
import subprocess
from pathlib import Path

# Import existing modules DIRECT (geen CrewAI overhead)
import langchain_agent
import groq_answer_llm


def ingest_pdf_via_crew(file_bytes: bytes, filename: str) -> dict:
    """
    Ingest PDF into ChromaDB.
    
    Args:
        file_bytes: PDF content
        filename: PDF name
        
    Returns:
        Ingestion result
    """
    return langchain_agent.ingest_pdf(file_bytes, filename)


def answer_question_via_crew(question: str, context: str = "") -> str:
    """
    Answer question DIRECT via tools (geen CrewAI agent overhead).
    
    Workflow:
        1. RAG: Haal context op (semantic search)
        2. LLM: Generate answer + quiz (direct Groq call)
        
    Args:
        question: User question
        context: Optional PDF context (ignored, RAG retrieves from DB)
        
    Returns:
        Answer with quiz (DIRECT, geen agent filtering)
    """
    # Step 1: RAG retrieval (semantic search, k=4)
    rag_context = langchain_agent.get_context_for_question(question, k=4)
    
    # Step 2: LLM answer + quiz (direct Groq, geen agent tussenlaag)
    answer = groq_answer_llm.answer_and_maybe_quiz(question, rag_context)
    
    return answer


def kickoff_crew_workflow(question: str) -> str:
    """
    Full CrewAI multi-agent workflow (voor DEMO purposes).
    Draait in APARTE venv (.venv_crewai) om dependency conflicts te vermijden.
    
    Args:
        question: Question about PDFs
        
    Returns:
        Multi-agent orchestrated result
    """
    try:
        # Gebruik de aparte CrewAI venv Python interpreter
        BASE_DIR = Path(__file__).parent
        CREWAI_VENV_PYTHON = BASE_DIR / ".venv_crewai" / "bin" / "python"
        CREWAI_MAIN = BASE_DIR / "bralma_crewai" / "src" / "bralma_crewai" / "main.py"
        
        if not CREWAI_VENV_PYTHON.exists():
            raise FileNotFoundError(f"CrewAI venv not found at {CREWAI_VENV_PYTHON}. Run setup eerst!")
        
        # Run CrewAI in aparte venv via subprocess
        result = subprocess.run(
            [str(CREWAI_VENV_PYTHON), "-c", 
             f"import sys; sys.path.insert(0, '{BASE_DIR / 'bralma_crewai' / 'src'}'); "
             f"from bralma_crewai.main import run_pdf_rag_workflow; "
             f"print(run_pdf_rag_workflow('{question}', ''))"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(f"CrewAI error: {result.stderr}")
            
    except Exception as e:
        # Fallback to direct calls if CrewAI fails
        print(f"CrewAI workflow failed: {e}. Using direct calls.")
        return answer_question_via_crew(question)


__all__ = [
    "ingest_pdf_via_crew",
    "answer_question_via_crew", 
    "kickoff_crew_workflow"
]
