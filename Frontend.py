import subprocess
import sys
import streamlit as st
from pathlib import Path
import PyPDF2
from datetime import datetime
from groq_llm import ask_question


# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chatbot design
st.markdown("""
    <style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
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
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = ""

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

def get_bot_response(user_question, pdf_context):
    """
    Calls the ask_question function from groq.py to get an LLM answer.
    If a PDF is uploaded, include its text as context.
    """
    
    if pdf_context:
        prompt = f"{user_question}\n\nContext uit PDF:\n{pdf_context[:1500]}"
    else:
        prompt = user_question
    
    return ask_question(prompt)

# App header
st.title("What's on the agenda today?")

# File upload section (hidden but functional for drag & drop)
uploaded_file = st.file_uploader(
    "Drop your PDF file here",
    type=['pdf'],
    help="Drag and drop a PDF file to upload",
    label_visibility="collapsed"
)

# Process uploaded file
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.uploaded_filename:
        with st.spinner("Processing PDF..."):
            st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
            st.session_state.pdf_uploaded = True
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.messages = []  # Clear previous conversation

# Display file badge if PDF is uploaded
if st.session_state.pdf_uploaded:
    st.markdown(f"""
        <div class="file-badge">
            📄 {st.session_state.uploaded_filename}
        </div>
        """, unsafe_allow_html=True)

# Display welcome message or chat history
if not st.session_state.messages:
    if not st.session_state.pdf_uploaded:
        st.markdown('<div class="subtitle">Drop a PDF file to get started, or ask me anything</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="subtitle">PDF loaded! Ask me anything about the document.</div>', unsafe_allow_html=True)
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
        bot_response = get_bot_response(user_input, st.session_state.pdf_text)
    
    # Add bot response to chat
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": datetime.now()
    })
    
    # Rerun to update chat display
    st.rerun()
