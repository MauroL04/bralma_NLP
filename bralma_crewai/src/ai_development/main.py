#!/usr/bin/env python
import sys
import warnings
from pathlib import Path
from datetime import datetime

from ai_development.crew import PDFProcessingCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Project path configuration
PROJECT_PATH = str(Path(__file__).parent.parent.parent.parent.parent)

def run():
    """
    Run the PDF processing crew.
    Handles PDF ingestion, context retrieval, and question-answering.
    """
    inputs = {
        'project_path': PROJECT_PATH
    }

    try:
        print(f"\n🚀 Starting PDF Processing Crew...")
        print(f"📁 Project at: {PROJECT_PATH}")
        print(f"⏱️  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        result = PDFProcessingCrew().crew().kickoff(inputs=inputs)
        
        print(f"\n✅ PDF Processing Complete!")
        print(f"⏱️  Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'project_path': PROJECT_PATH
    }
    try:
        PDFProcessingCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        PDFProcessingCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


if __name__ == "__main__":
    run()
