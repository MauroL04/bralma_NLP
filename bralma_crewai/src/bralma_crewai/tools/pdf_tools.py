""" 
Document RAG Tools (PDF + PPTX) - CrewAI wrappers for langchain_agent & groq_answer_llm.
CrewAI orchestreert de workflow.
"""

import sys
from pathlib import Path
from crewai.tools import BaseTool

# Add parent directory to import existing modules
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import existing modules (source of truth)
import langchain_agent
import groq_answer_llm


class RetrieveContextTool(BaseTool):
    name: str = "Retrieve Context from Vector Database"
    description: str = "Retrieve relevant context from ChromaDB using semantic search. Args: question (str), k (int, default=4)"

    def _run(self, question: str, k: int = 4) -> str:
        """Get top-k relevant chunks via semantic search"""
        return langchain_agent.get_context_for_question(question, k=k)


class AnswerWithRAGTool(BaseTool):
    name: str = "Generate Answer with Quiz"
    description: str = "Generate answer using RAG context and create educational quiz. Args: question (str), context (str)"

    def _run(self, question: str, context: str = "") -> str:
        """Generate answer + quiz via Groq LLM"""
        return groq_answer_llm.answer_and_maybe_quiz(question, context)


# Export tool instances
retrieve_context_tool = RetrieveContextTool()
answer_with_rag_tool = AnswerWithRAGTool()