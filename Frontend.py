import subprocess
import sys
import streamlit as st
from pathlib import Path
import PyPDF2
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
 
def get_combined_pdf_context():
    """Combine all uploaded PDF texts into one context string"""
    if not st.session_state.uploaded_pdfs:
        return ""
   
    combined = ""
    for idx, pdf in enumerate(st.session_state.uploaded_pdfs):
        combined += f"\n\n=== Document {idx+1}: {pdf['filename']} ===\n"
        combined += pdf['text'][:3000]  # Limit each PDF to avoid token overflow
   
    return combined
 
def get_bot_response(user_question):
    """
    Calls the answer_and_maybe_quiz function from groq_answer_llm.py to get an LLM answer.
    If PDFs are uploaded, include their combined text as context.
    """
    pdf_context = get_combined_pdf_context()
    return answer_and_maybe_quiz(user_question, pdf_context)
 
# Sidebar for uploaded files overview
with st.sidebar:
    st.header("📚 Uploaded Documents")
   
    if st.session_state.uploaded_pdfs:
        st.markdown(f"**{len(st.session_state.uploaded_pdfs)} file(s) uploaded**")
        st.markdown("---")
       
        for idx, pdf in enumerate(st.session_state.uploaded_pdfs):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"📄 **{pdf['filename']}**")
                st.caption(f"{len(pdf['text'])} characters")
            with col2:
                if st.button("🗑️", key=f"remove_{idx}", help="Remove file"):
                    st.session_state.uploaded_pdfs.pop(idx)
                    st.rerun()
       
        st.markdown("---")
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.uploaded_pdfs = []
            st.session_state.messages = []
            st.rerun()
    else:
        st.info("No files uploaded yet")
 
# App header
st.title("What's on the agenda today?")
 
# File upload section (same drag & drop as before)
uploaded_file = st.file_uploader(
    "Drop your PDF file here",
    type=['pdf'],
    help="Drag and drop a PDF file to upload",
    label_visibility="collapsed"
)
 
# Process uploaded file
if uploaded_file is not None:
    # Check if file already exists
    existing_names = [pdf['filename'] for pdf in st.session_state.uploaded_pdfs]
   
    if uploaded_file.name not in existing_names:
        with st.spinner("Processing PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.uploaded_pdfs.append({
                "filename": uploaded_file.name,
                "text": text
            })
        st.success(f"✅ Added {uploaded_file.name}")
        st.rerun()
    else:
        st.info(f"📄 {uploaded_file.name} is already uploaded")
 
# Display welcome message or chat history
if not st.session_state.messages:
    if not st.session_state.uploaded_pdfs:
        st.markdown('<div class="subtitle">Drop a PDF file to get started, or ask me anything</div>', unsafe_allow_html=True)
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
 
 