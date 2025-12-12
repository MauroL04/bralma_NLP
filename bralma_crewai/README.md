# Bralma CrewAI - PDF Processing Crew

Welcome to the Bralma CrewAI project, powered by [crewAI](https://crewai.com). This multi-agent AI system handles PDF document ingestion, context retrieval, and intelligent question-answering using Groq LLM.

## Setup Instructions

### 1. Create Virtual Environment (Python 3.11)

cd bralma_crewai
rm -rf .venv
python3.11 -m venv .venv_crewai


### 2. Activate Virtual Environment

**macOS/Linux:**
source .venv_crewai/bin/activate


**Windows (Git Bash):**
source .venv_crewai/Scripts/activate


### 3. Upgrade pip en installeer alle requirements (voor Python 3.11!)
python3.11 -m pip install --upgrade pip;
python3.11 -m pip install -r requirements.txt;


### 4. Configure Environment Variables

Create `.env` files with your Groq API key:

**Root `.env`:**
```bash
MODEL=groq/llama-3.3-70b-versatile
GROQ_API_KEY=your_api_key_here
```

**`ai_development/.env`:**
```bash
MODEL=groq/llama-3.3-70b-versatile
GROQ_API_KEY=your_api_key_here
```

## Running the Project

### Option 1: Run Streamlit Frontend
```bash
streamlit run Frontend.py
```

Then click **"📊 Analyze Codebase"** in the sidebar to execute the PDF processing crew.

### Option 2: Run CrewAI Directly
```bash
cd ai_development
python -m ai_development.main
```