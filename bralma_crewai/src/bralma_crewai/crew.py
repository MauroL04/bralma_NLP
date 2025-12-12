from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
from .tools.pdf_tools import (
    ingest_pdf_tool, 
    retrieve_context_tool,
    answer_question_with_context_tool
)

# Load environment variables
load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class PDFProcessingCrew():
    """PDF Processing Crew - Multi-agent system for PDF ingestion and question-answering"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    @agent
    def pdf_ingestion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_ingestion_agent'],
            tools=[ingest_pdf_tool],
            verbose=True
        )

    @agent
    def pdf_retrieval_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_retrieval_agent'],
            tools=[retrieve_context_tool],
            verbose=True
        )

    @agent
    def pdf_answering_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_answering_agent'],
            tools=[answer_question_with_context_tool],
            verbose=True
        )

    # Tasks - PDF Processing workflow
    @task
    def ingest_pdf(self) -> Task:
        return Task(
            config=self.tasks_config['ingest_pdf']
        )

    @task
    def retrieve_context(self) -> Task:
        return Task(
            config=self.tasks_config['retrieve_context'],
            depends_on=[self.ingest_pdf()]
        )

    @task
    def answer_question(self) -> Task:
        return Task(
            config=self.tasks_config['answer_question'],
            depends_on=[self.retrieve_context()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PDFProcessingCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False  # Disabled to avoid OpenAI embedding requirement
        )

