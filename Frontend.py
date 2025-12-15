import subprocess
import sys
import streamlit as st
from pathlib import Path
import PyPDF2
from pptx import Presentation
from datetime import datetime
from groq_answer_llm import answer_and_maybe_quiz
 
 
# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
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
        left: 50%;
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
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = []  # List of dicts: [{"filename": "...", "text": "..."}]
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = []  # List of saved chat sessions
if 'current_session_name' not in st.session_state:
    st.session_state.current_session_name = None
 
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_ppt(ppt_file):
    """Extract text from uploaded PowerPoint file"""
    try:
        prs = Presentation(ppt_file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"
 
def get_combined_documents_context():
    """Combine all uploaded documents (PDF and PPT) into one context string"""
    if not st.session_state.uploaded_pdfs:
        return ""
   
    combined = ""
    for idx, doc in enumerate(st.session_state.uploaded_pdfs):
        combined += f"\n\n=== Document {idx+1}: {doc['filename']} ===\n"
        combined += doc['text']
   
    return combined
 
def get_bot_response(user_question):
    """
    Calls the answer_and_maybe_quiz function from groq_answer_llm.py to get an LLM answer.
    If documents (PDF or PPT) are uploaded, include their combined text as context.
    """
    document_context = get_combined_documents_context()
    return answer_and_maybe_quiz(user_question, document_context)
 
# Sidebar for uploaded files and chat history
with st.sidebar:
    st.title("📋 Menu")
    st.markdown("---")
    
    # Uploaded Documents Section
    with st.expander("📚 Uploaded Documents", expanded=True):
        if st.session_state.uploaded_pdfs:
            st.markdown(f"**{len(st.session_state.uploaded_pdfs)} file(s) loaded**")
            st.markdown("")
           
            for idx, pdf in enumerate(st.session_state.uploaded_pdfs):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"📄 **{pdf['filename']}**")
                    st.caption(f"{len(pdf['text'])} chars")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}", help="Remove file"):
                        st.session_state.uploaded_pdfs.pop(idx)
                        st.rerun()
           
            if st.button("🗑️ Clear All Files", use_container_width=True, key="clear_files"):
                st.session_state.uploaded_pdfs = []
                st.rerun()
        else:
            st.info("No files uploaded")
    
    st.markdown("")
    
    # Chat History Section
    with st.expander("💬 Chat History", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            if st.button("💾 Save Chat", use_container_width=True, disabled=len(st.session_state.messages) == 0):
                if st.session_state.messages:
                    # Use the first user message as the session name
                    first_message = next((msg for msg in st.session_state.messages if msg["role"] == "user"), None)
                    if first_message:
                        # Truncate if too long (max 50 characters)
                        session_name = first_message["content"][:50]
                        if len(first_message["content"]) > 50:
                            session_name += "..."
                    else:
                        session_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
                    
                    st.session_state.chat_sessions.append({
                        "name": session_name,
                        "messages": st.session_state.messages.copy(),
                        "timestamp": datetime.now()
                    })
                    st.session_state.current_session_name = session_name
                    st.rerun()
        with col2:
            if st.button("🗑️ New Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.current_session_name = None
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
 
# Process uploaded file
if uploaded_file is not None:
    # Check if file already exists
    existing_names = [pdf['filename'] for pdf in st.session_state.uploaded_pdfs]
   
    if uploaded_file.name not in existing_names:
        with st.spinner(f"Processing {uploaded_file.type}..."):
            # Extract text based on file type
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type in ["application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
                text = extract_text_from_ppt(uploaded_file)
            else:
                text = ""
                st.error(f"Unsupported file type: {uploaded_file.type}")
            
            if text and not text.startswith("Error"):
                st.session_state.uploaded_pdfs.append({
                    "filename": uploaded_file.name,
                    "text": text
                })
                st.success(f"✅ Added {uploaded_file.name}")
                st.rerun()
            else:
                st.error(f"Failed to extract text from {uploaded_file.name}")
    else:
        st.info(f"📄 {uploaded_file.name} is already uploaded")
 
# Display welcome message or chat history
if not st.session_state.messages:
    if not st.session_state.uploaded_pdfs:
        st.markdown('<div class="subtitle">Drop a PDF or PowerPoint file to get started, or ask me anything</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="subtitle">{len(st.session_state.uploaded_pdfs)} PDF(s) loaded! Ask me anything about the documents.</div>', unsafe_allow_html=True)
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
 
 