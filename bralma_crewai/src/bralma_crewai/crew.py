"""  
Bralma CrewAI - Simplified 2-agent orchestration.
RAG Agent: Retrieves context from vector DB.
Answer Agent: Generates answers with quizzes.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from .tools.pdf_tools import (
    retrieve_context_tool,
    answer_with_rag_tool
)

load_dotenv()


@CrewBase
class PDFProcessingCrew():
    """
    Simplified document RAG system (PDF + PPTX) with 2 collaborating agents.
    RAG Agent → Answer Agent workflow.
    """

    @agent
    def rag_agent(self) -> Agent:
        """Handles context retrieval from vector database"""
        return Agent(
            config=self.agents_config['rag_agent'],
            tools=[retrieve_context_tool],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def answer_agent(self) -> Agent:
        """Generates answers with quizzes using context"""
        return Agent(
            config=self.agents_config['answer_agent'],
            tools=[answer_with_rag_tool],
            verbose=True,
            allow_delegation=False
        )

    @task
    def retrieve_task(self) -> Task:
        """Retrieve relevant context for question"""
        return Task(
            config=self.tasks_config['retrieve_task'],
            async_execution=False
        )

    @task
    def answer_task(self) -> Task:
        """Generate answer with quiz"""
        return Task(
            config=self.tasks_config['answer_task'],
            async_execution=False
        )

    @crew
    def crew(self) -> Crew:
        """
        Sequential workflow:
        1. RAG Agent retrieves context
        2. Answer Agent generates answer + quiz
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )

