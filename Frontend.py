import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import warnings
import json
import langchain_agent

# Ensure package path is available for CrewAI module imports
PROJECT_ROOT = Path(__file__).resolve().parent
CREW_SRC = PROJECT_ROOT / "bralma_crewai" / "src"
if str(CREW_SRC) not in sys.path:
    sys.path.insert(0, str(CREW_SRC))

# Import direct LLM modules + RAG
from bralma_crewai.main import run_pdf_rag_workflow

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore")
 
 
# Page configuration
st.set_page_config(
    page_title="Document Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Custom CSS for chatbot design
st.markdown("""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        border-right: 1px solid #404040;
    }
   
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e0e0e0;
    }
    
    /* Force sidebar to always be visible and expanded */
    section[data-testid="stSidebar"] {
        display: block !important;
        transform: none !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
        width: 21rem !important;
        margin-left: 0 !important;
    }
    
    /* Hide the collapse/expand button completely */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    button[kind="header"] {
        display: none !important;
    }
    
    /* Override any aria-expanded state */
    section[data-testid="stSidebar"][aria-expanded="true"],
    section[data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        transform: translateX(0) !important;
    }
   
    /* Main container styling */
    .main {
        background-color: #2d2d2d;
        color: white;
    }
   
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
   
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
   
    /* Chat message styling */
    .chat-message {
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
   
    .chat-message.user {
        background-color: #3a3a3a;
        margin-left: 20%;
    }
   
    .chat-message.bot {
        background-color: #1e1e1e;
        margin-right: 20%;
        border: 1px solid #404040;
    }
   
    .message-content {
        color: #e0e0e0;
        line-height: 1.6;
    }
   
    .message-header {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #a0a0a0;
        font-size: 0.85rem;
    }
   
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
   
    /* Chat input styling */
    .stChatInput {
        position: fixed;
        bottom: 2rem;
        left: calc(50% + 10.5rem);
        transform: translateX(-50%);
        width: 70%;
        max-width: 800px;
        background-color: transparent;
        padding: 0;
        z-index: 100;
    }
   
    .stChatInput > div {
        background-color: #f5f5f5;
        border-radius: 2rem;
        border: 2px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
   
    .stChatInput > div:hover {
        border-color: #4a90e2;
        box-shadow: 0 6px 16px rgba(74, 144, 226, 0.3);
    }
   
    .stChatInput input {
        color: #333 !important;
        font-size: 1rem;
    }
   
    .stChatInput input::placeholder {
        color: #999 !important;
    }
    
    /* Style the submit button to match input background */
    .stChatInput button {
        background-color: #f5f5f5 !important;
        color: #333 !important;
    }
    
    .stChatInput button:hover {
        background-color: #e0e0e0 !important;
    }
   
    /* File upload overlay */
    .upload-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.9);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    }
   
    .upload-box {
        border: 3px dashed #666;
        border-radius: 1rem;
        padding: 3rem;
        text-align: center;
        color: white;
        font-size: 1.5rem;
    }
   
    /* File status badge */
    .file-badge {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background-color: #3a3a3a;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        color: #4CAF50;
        border: 1px solid #4CAF50;
        z-index: 1000;
    }
   
    /* Title styling */
    h1 {
        color: white !important;
        text-align: center;
        margin-bottom: 0.5rem;
    }
   
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
   
    /* Streamlit elements color fix */
    .stMarkdown, p {
        color: #e0e0e0;
    }
   
    /* Info box styling */
    .stAlert {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #404040;
    }
    </style>
    """, unsafe_allow_html=True)
 
# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = []  # List of saved chat sessions
if 'current_session_name' not in st.session_state:
    st.session_state.current_session_name = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []  # [{"name": str, "chunks": int, "sig": str}]
if 'processed_upload_sigs' not in st.session_state:
    st.session_state.processed_upload_sigs = []

# Hydrate uploaded files list from existing ChromaDB on startup
if not st.session_state.uploaded_files:
    persisted = langchain_agent.list_ingested_sources()
    if persisted:
        st.session_state.uploaded_files = [
            {"name": p.get("name", "unknown"), "chunks": p.get("chunks", 0), "sig": p.get("name", "unknown")}
            for p in persisted
        ]
        st.session_state.processed_upload_sigs = [p.get("name", "unknown") for p in persisted]

# Simple on-disk persistence for saved chats
CHAT_STORE = PROJECT_ROOT / "chat_sessions.json"


def load_saved_chats():
    if not CHAT_STORE.exists():
        return []
    try:
        with CHAT_STORE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def persist_chats():
    try:
        serializable = []
        for sess in st.session_state.chat_sessions:
            msgs = []
            for m in sess.get("messages", []):
                msgs.append({
                    "role": m.get("role"),
                    "content": m.get("content"),
                    "timestamp": m.get("timestamp").isoformat() if hasattr(m.get("timestamp"), "isoformat") else m.get("timestamp")
                })
            serializable.append({
                "name": sess.get("name"),
                "timestamp": sess.get("timestamp").isoformat() if hasattr(sess.get("timestamp"), "isoformat") else sess.get("timestamp"),
                "messages": msgs
            })
        with CHAT_STORE.open("w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# Hydrate chat sessions from disk on startup
if not st.session_state.chat_sessions:
    saved = load_saved_chats()
    if saved:
        st.session_state.chat_sessions = saved
 
def get_bot_response(user_question):
    """
    Calls the CrewAI workflow to get an answer (and optional quiz).
    Context retrieval happens from ChromaDB via CrewAI tools.
    """
    try:
        result = run_pdf_rag_workflow(user_question, "")
        return str(result)
    except Exception as e:
        return f"Error from CrewAI workflow: {e}"
 
# Sidebar for uploaded files and chat history
with st.sidebar:
    st.title("📋 Menu")
    st.markdown("---")
    
    with st.expander("📚 Uploaded Documents", expanded=True):
        if st.session_state.uploaded_files:
            st.markdown(f"**{len(st.session_state.uploaded_files)} file(s) ingested**")
            for i, f in enumerate(st.session_state.uploaded_files, 1):
                st.markdown(f"{i}. **{f['name']}** — {f.get('chunks', 0)} chunks")
        else:
            st.info("No files ingested yet")

    st.markdown("")

    # Chat History Section
    with st.expander("💬 Chat History", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            if st.button("💾 Save Chat", use_container_width=True, disabled=len(st.session_state.messages) == 0):
                if st.session_state.messages:
                    session_name = f"Chat {len(st.session_state.chat_sessions) + 1} - {datetime.now().strftime('%m/%d %H:%M')}"
                    st.session_state.chat_sessions.append({
                        "name": session_name,
                        "messages": st.session_state.messages.copy(),
                        "timestamp": datetime.now()
                    })
                    st.session_state.current_session_name = session_name
                    persist_chats()
                    st.rerun()
        with col2:
            if st.button("🗑️ New Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.current_session_name = None
                persist_chats()
                st.rerun()
        
        st.markdown("")
        
        if st.session_state.chat_sessions:
            st.markdown(f"**{len(st.session_state.chat_sessions)} saved chat(s)**")
            for idx, session in enumerate(reversed(st.session_state.chat_sessions)):
                actual_idx = len(st.session_state.chat_sessions) - 1 - idx
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"💬 {session['name']}", key=f"load_session_{actual_idx}", use_container_width=True):
                        st.session_state.messages = session['messages'].copy()
                        st.session_state.current_session_name = session['name']
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_session_{actual_idx}", help="Delete chat"):
                        st.session_state.chat_sessions.pop(actual_idx)
                        persist_chats()
                        st.rerun()
        else:
            st.info("No saved chats")
 
# App header
st.title("What's on the agenda today?")
 
# File upload section (drag & drop for PDF and PPT)
uploaded_file = st.file_uploader(
    "Drop your PDF or PowerPoint file here",
    type=['pdf', 'ppt', 'pptx'],
    help="Drag and drop a PDF or PowerPoint file to upload",
    label_visibility="collapsed"
)
 
# Process uploaded file (PDF or PPTX)
if uploaded_file is not None:
    file_sig = uploaded_file.name  # use filename-based signature for debouncing and persistence hydration
    already = file_sig in st.session_state.processed_upload_sigs

    if already:
        st.info(f"✅ {uploaded_file.name} uploaded")
    else:
        with st.spinner(f"Ingesting {uploaded_file.type} into ChromaDB..."):
            file_bytes = uploaded_file.read()
            try:
                ingest_result = langchain_agent.ingest_pdf(file_bytes, uploaded_file.name)
                ingested = {
                    "name": uploaded_file.name,
                    "chunks": ingest_result.get('chunks_ingested', 0),
                    "sig": file_sig
                }
                st.session_state.uploaded_files.append(ingested)
                st.session_state.processed_upload_sigs.append(file_sig)
                st.success(f"✅ {uploaded_file.name} uploaded")
                st.toast(f"Uploaded {uploaded_file.name}")
            except Exception as e:
                st.error(f"Failed to ingest {uploaded_file.name}: {e}")
 
# Display welcome message or chat history
if not st.session_state.messages:
    st.markdown('<div class="subtitle">Drop a PDF or PowerPoint file to ingest into ChromaDB, then ask me anything.</div>', unsafe_allow_html=True)
else:
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user">
                        <div class="message-header">You</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message bot">
                        <div class="message-header">Assistant</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
 
# Add spacing before input
st.markdown("<br>" * 3, unsafe_allow_html=True)
 
# Chat input at the bottom
user_input = st.chat_input("Ask anything")
 
if user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
   
    # Get bot response
    with st.spinner("🤔 Thinking..."):
        bot_response = get_bot_response(user_input)
   
    # Add bot response to chat
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": datetime.now()
    })
   
    # Rerun to update chat display
    st.rerun()
 
 