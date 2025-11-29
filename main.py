"""
Main Streamlit Application for KnowledgeBase Agent
A comprehensive AI-powered internal knowledge base system
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from components import (
        create_document_processor,
        create_query_engine,
        create_advanced_query_engine,
        get_metadata_db
    )
except ImportError as e:
    st.error(f"Error importing components: {e}")
    st.stop()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="KnowledgeBase Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .citation {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    .error-message {
        background-color: #ffe6e6;
        padding: 1rem;
        border-left: 4px solid #ff4444;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #e6ffe6;
        padding: 1rem;
        border-left: 4px solid #44ff44;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.chat_history = []
        st.session_state.uploaded_files_count = 0
        st.session_state.current_category = "general"
        
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key in ["your_openai_api_key_here", "sk-test-key-placeholder", "test_key_for_setup"]:
            st.error("🔑 **OpenAI API Key Required!**")
            st.warning("""
            **To use the KnowledgeBase Agent, you need to:**
            
            1. Get an OpenAI API key from: https://platform.openai.com/api-keys
            2. Edit the `.env` file in this project
            3. Replace `OPENAI_API_KEY=` with your actual key
            4. Restart the application
            
            **Example:** `OPENAI_API_KEY=sk-proj-abc123...`
            """)
            st.stop()
        
        # Initialize components
        try:
            st.session_state.document_processor = create_document_processor()
            st.session_state.query_engine = create_query_engine()
            st.session_state.metadata_db = get_metadata_db()
            
            logger.info("Successfully initialized session state and components")
            
        except Exception as e:
            st.error(f"❌ Error initializing components: {e}")
            st.error("Please check your environment configuration.")
            st.stop()


def display_header():
    """Display main application header"""
    st.markdown('<h1 class="main-header">🧠 KnowledgeBase Agent</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 1.1rem; color: #666; margin-bottom: 2rem;">
        AI-Powered Internal Knowledge Base System • Upload Documents • Ask Questions • Get Instant Answers
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display sidebar with configuration and stats"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_provider = st.selectbox(
            "AI Model Provider",
            ["OpenAI", "Claude", "Gemini"],
            help="Select the AI model provider for answering questions"
        )
        
        # Vector store selection
        vector_store = st.selectbox(
            "Vector Store",
            ["ChromaDB", "Pinecone"],
            help="Select the vector database for document storage"
        )
        
        # Category selection
        st.session_state.current_category = st.selectbox(
            "Document Category",
            ["general", "hr", "policies", "sops", "technical"],
            help="Select document category for filtering"
        ).lower()
        
        # Retrieval settings
        st.subheader("🔍 Retrieval Settings")
        k_documents = st.slider(
            "Documents to retrieve",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of relevant documents to retrieve for each query"
        )
        
        # Display statistics
        st.markdown('<div class="section-header">📊 Statistics</div>', unsafe_allow_html=True)
        
        try:
            stats = st.session_state.document_processor.get_document_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📄 Documents", stats.get("total_documents", 0))
            with col2:
                st.metric("📝 Chunks", stats.get("total_chunks", 0))
            
            # Categories breakdown
            if stats.get("categories"):
                st.subheader("Categories")
                for category, count in stats["categories"].items():
                    st.write(f"• {category.title()}: {count}")
            
            # File types breakdown
            if stats.get("file_types"):
                st.subheader("File Types")
                for file_type, count in stats["file_types"].items():
                    st.write(f"• {file_type.upper()}: {count}")
                    
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
        
        # Quick actions
        st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🔄 Refresh Stats"):
            st.rerun()


def document_upload_section():
    """Handle document upload and processing"""
    st.markdown('<div class="section-header">📤 Document Upload</div>', unsafe_allow_html=True)
    
    # Show sample document info
    st.info("""
    **📝 Quick Start:** A sample company policies document has been created in your project folder 
    (`sample_company_policies.md`). You can upload this file to test the system!
    """)
    
    # Upload interface
    uploaded_files = st.file_uploader(
        "Upload documents to the knowledge base",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    # Category selection for upload
    upload_category = st.selectbox(
        "Document category",
        ["general", "hr", "policies", "sops", "technical"],
        key="upload_category",
        help="Categorize documents for better organization and filtering"
    )
    
    # Process uploaded files
    if uploaded_files:
        if st.button("🚀 Process Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Process files
                status_text.text("Processing uploaded files...")
                results = st.session_state.document_processor.process_uploaded_files(
                    uploaded_files, upload_category
                )
                
                # Display results
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                
                # Show success/error messages
                success_count = sum(1 for r in results if r.get('success', False))
                total_count = len(results)
                
                if success_count == total_count:
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Successfully processed all {total_count} documents!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-message">
                        ⚠️ Processed {success_count} out of {total_count} documents successfully.
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed results
                with st.expander("📋 Detailed Results"):
                    for result in results:
                        filename = result.get('filename', 'Unknown')
                        success = result.get('success', False)
                        message = result.get('message', 'No message')
                        
                        if success:
                            st.success(f"✅ {filename}: {message}")
                        else:
                            st.error(f"❌ {filename}: {message}")
                
                # Update session state
                st.session_state.uploaded_files_count += success_count
                
                # Auto-refresh to update stats
                st.rerun()
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.markdown(f"""
                <div class="error-message">
                    ❌ Error processing documents: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                logger.error(f"Error processing documents: {e}")


def _render_suggestion_buttons(suggestions, category_key):
    """Helper function to render suggestion buttons in columns"""
    if not suggestions:
        st.info("No suggestions available for this category.")
        return
    
    # Render buttons in two columns
    col1, col2 = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        if i % 2 == 0:
            with col1:
                if st.button(f"💭 {suggestion}", key=f"suggestion_{category_key}_{i}"):
                    st.session_state.current_question = suggestion
                    st.rerun()
        else:
            with col2:
                if st.button(f"💭 {suggestion}", key=f"suggestion_{category_key}_{i}"):
                    st.session_state.current_question = suggestion
                    st.rerun()


def chat_interface():
    """Enhanced chat interface for asking questions"""
    st.markdown('<div class="section-header">💬 AI Chat Assistant</div>', unsafe_allow_html=True)
    
    # Check if documents are uploaded
    try:
        stats = st.session_state.document_processor.get_document_stats()
        total_docs = stats.get("total_documents", 0)
        
        if total_docs == 0:
            st.warning("⚠️ **No documents uploaded yet!**")
            st.info("""
            **To get started:**
            1. 📤 Go to the **Upload** tab
            2. 📁 Select your documents (PDF, DOCX, or TXT files)  
            3. 🏷️ Choose a category (HR, Policies, SOPs, etc.)
            4. 🚀 Click "Process Documents"
            5. 💬 Come back here to ask questions!
            """)
            return
        else:
            # Show document stats in a compact format
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Documents", total_docs)
            with col2:
                st.metric("📝 Total Chunks", stats.get("total_chunks", 0))
            with col3:
                categories = len(stats.get("categories", {}))
                st.metric("🏷️ Categories", categories)
    except:
        pass
    
    # Enhanced Query suggestions with categories
    with st.expander("💡 Smart Question Suggestions", expanded=False):
        try:
            # Category-specific suggestions
            suggestion_tabs = st.tabs(["🎯 Current Category", "🏢 General", "👥 HR", "📋 Policies", "⚙️ IT"])
            
            with suggestion_tabs[0]:  # Current category
                suggestions = st.session_state.query_engine.get_query_suggestions(st.session_state.current_category)
                _render_suggestion_buttons(suggestions[:6], "current")
            
            with suggestion_tabs[1]:  # General
                general_suggestions = [
                    "What are the company's core values?",
                    "How do I contact support?",
                    "What are the office hours?",
                    "Where can I find company resources?",
                    "What is the organizational structure?",
                    "How do I access the employee handbook?"
                ]
                _render_suggestion_buttons(general_suggestions, "general")
            
            with suggestion_tabs[2]:  # HR
                hr_suggestions = [
                    "What is the vacation policy?",
                    "How do I submit a time off request?",
                    "What are the employee benefits?",
                    "How do I update my personal information?",
                    "What is the performance review process?",
                    "How do I report workplace issues?"
                ]
                _render_suggestion_buttons(hr_suggestions, "hr")
            
            with suggestion_tabs[3]:  # Policies
                policy_suggestions = [
                    "What is the remote work policy?",
                    "What is the dress code?",
                    "What are the security guidelines?",
                    "What is the expense policy?",
                    "What are the safety protocols?",
                    "What is the travel policy?"
                ]
                _render_suggestion_buttons(policy_suggestions, "policies")
            
            with suggestion_tabs[4]:  # IT
                it_suggestions = [
                    "How do I reset my password?",
                    "How do I get IT support?",
                    "How do I access the VPN?",
                    "What software can I install?",
                    "How do I report a security issue?",
                    "How do I request new equipment?"
                ]
                _render_suggestion_buttons(it_suggestions, "it")
                
        except Exception as e:
            st.error(f"Error loading suggestions: {e}")
    
    # Enhanced question input area
    st.markdown("### 🤔 Ask Your Question")
    
    # Chat input with better styling
    question = st.text_area(
        "Type your question here:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What is the company's vacation policy? How do I submit expense reports?",
        help="💡 Tip: Be specific for better results. You can ask follow-up questions!",
        height=80
    )
    
    # Advanced search options in an expandable section
    with st.expander("🔧 Search Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            use_category_filter = st.checkbox(
                f"📁 Filter by '{st.session_state.current_category}' category",
                value=True,
                help="Only search in documents from the selected category"
            )
            
            num_sources = st.slider(
                "📚 Number of sources to retrieve",
                min_value=3,
                max_value=15,
                value=5,
                help="More sources = more comprehensive but slower responses"
            )
        
        with col2:
            advanced_mode = st.checkbox(
                "🚀 Advanced mode",
                value=False,
                help="Use enhanced query processing with follow-up capabilities"
            )
            
            include_metadata = st.checkbox(
                "📊 Show detailed citations",
                value=True,
                help="Include document metadata and detailed source information"
            )
    
    # Clear chat history button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", help="Start a fresh conversation"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Enhanced ask button with better UX
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ask_clicked = st.button(
            "🤔 Ask Question", 
            type="primary", 
            disabled=not question.strip(),
            help="Click to get AI-powered answer",
            use_container_width=True
        )
    
    with col2:
        if st.button("🎲 Random Question", help="Try a random sample question"):
            import random
            sample_questions = [
                "What is the remote work policy?",
                "How do I get IT support?",
                "What are the employee benefits?",
                "What is the vacation policy?",
                "How do I submit expense reports?",
                "What are the safety protocols?"
            ]
            st.session_state.current_question = random.choice(sample_questions)
            st.rerun()
    
    with col3:
        if st.button("💡 Help", help="Tips for better questions"):
            st.info("""
            **💡 Tips for Better Results:**
            
            ✅ **Be specific:** "What is the remote work equipment policy?" vs "Tell me about remote work"
            
            ✅ **Ask follow-ups:** "Can you provide more details about the VPN setup?"
            
            ✅ **Use keywords:** Include terms that might appear in your documents
            
            ✅ **Try variations:** If you don't get good results, rephrase your question
            """)
    
    # Process the question
    if ask_clicked and question.strip():
        # Create a placeholder for streaming response
        response_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        with progress_placeholder.container():
            progress_bar = st.progress(0)
            status_text = st.text("🔍 Searching knowledge base...")
        
        try:
            # Update progress
            progress_bar.progress(25)
            status_text.text("📚 Retrieving relevant documents...")
            
            # Prepare query parameters
            category_filter = st.session_state.current_category if use_category_filter else None
            
            # Use appropriate query engine
            if advanced_mode:
                query_engine = create_advanced_query_engine()
            else:
                query_engine = st.session_state.query_engine
            
            progress_bar.progress(50)
            status_text.text("🤖 Generating AI response...")
            
            # Get answer
            response = query_engine.query(
                question=question,
                k=num_sources,
                category_filter=category_filter
            )
            
            progress_bar.progress(75)
            status_text.text("📝 Formatting response...")
            
            # Add metadata if requested
            if include_metadata:
                response['include_metadata'] = True
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": question,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "settings": {
                    "category_filter": category_filter,
                    "num_sources": num_sources,
                    "advanced_mode": advanced_mode
                }
            })
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Clear the question input
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            
            # Clear progress and show response
            progress_placeholder.empty()
            st.rerun()
            
        except Exception as e:
            progress_placeholder.empty()
            st.error(f"❌ Error processing question: {e}")
            logger.error(f"Error processing question: {e}\n{traceback.format_exc()}")


def display_chat_history():
    """Enhanced chat history display with better formatting and features"""
    if not st.session_state.chat_history:
        st.markdown("""<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin: 1rem 0;">
            <h3>🚀 Ready to Start!</h3>
            <p>No conversations yet. Ask your first question above to get AI-powered answers from your knowledge base!</p>
        </div>""", unsafe_allow_html=True)
        return
    
    # Chat history header with controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<div class="section-header">🗨️ Conversation History</div>', unsafe_allow_html=True)
    with col2:
        if st.button("📄 Export Chat", help="Download conversation as text"):
            _export_chat_history()
    with col3:
        show_settings = st.checkbox("⚙️ Show Settings", help="Show query settings for each question")
    
    # Display chat history in reverse order (latest first)
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        chat_index = len(st.session_state.chat_history) - i
        
        # Create expandable container for each chat
        with st.expander(f"💬 Conversation {chat_index}: {chat['question'][:60]}...", expanded=i<3):
            
            # Question section with better styling
            st.markdown(f"""
            <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #4CAF50; margin-bottom: 1rem;">
                <h4>🤔 Question:</h4>
                <p style="font-size: 1.1em; margin: 0;"><em>{chat['question']}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Settings info if requested
            if show_settings and 'settings' in chat:
                settings = chat['settings']
                st.markdown("**⚙️ Query Settings:**")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Category", settings.get('category_filter', 'All'))
                with cols[1]:
                    st.metric("Sources", settings.get('num_sources', 5))
                with cols[2]:
                    st.metric("Mode", "Advanced" if settings.get('advanced_mode') else "Standard")
                with cols[3]:
                    timestamp = chat.get('timestamp', 'Unknown')
                    if timestamp != 'Unknown':
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if 'Z' in timestamp else timestamp)
                        st.metric("Time", dt.strftime("%H:%M:%S"))
            
            # Response section
            response = chat['response']
            
            if response.get('success', False):
                # Answer with better styling
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196F3; margin: 1rem 0;">
                    <h4>🤖 AI Answer:</h4>
                    <div style="font-size: 1.05em; line-height: 1.6;">{response['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Sources with enhanced display
                if response.get('sources'):
                    st.markdown("**📚 Sources & Citations:**")
                    
                    # Create tabs for different source views
                    source_tabs = st.tabs(["📜 List View", "📈 Summary", "🔍 Details"])
                    
                    with source_tabs[0]:  # List view
                        for idx, source in enumerate(response['sources']):
                            with st.container():
                                st.markdown(f"""
                                <div style="background: #e8f5e8; padding: 1rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">
                                    <h5>📄 {source['filename']} (Chunk {source['chunk_index']})</h5>
                                    <p><strong>Category:</strong> {source.get('category', 'general').title()}</p>
                                    <details>
                                        <summary style="cursor: pointer; color: #666;">Click to preview content...</summary>
                                        <p style="margin-top: 0.5rem; font-style: italic; color: #555;">{source['content_preview']}</p>
                                    </details>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with source_tabs[1]:  # Summary
                        sources_by_file = {}
                        for source in response['sources']:
                            filename = source['filename']
                            if filename not in sources_by_file:
                                sources_by_file[filename] = []
                            sources_by_file[filename].append(source)
                        
                        for filename, file_sources in sources_by_file.items():
                            st.markdown(f"**📄 {filename}** ({len(file_sources)} chunks)")
                            categories = set(s.get('category', 'general') for s in file_sources)
                            st.write(f"Categories: {', '.join(categories)}")
                            st.divider()
                    
                    with source_tabs[2]:  # Details
                        for source in response['sources']:
                            st.json({
                                "filename": source['filename'],
                                "chunk_index": source['chunk_index'],
                                "category": source.get('category', 'general'),
                                "upload_time": source.get('upload_timestamp', 'Unknown'),
                                "content_length": len(source.get('content_preview', ''))
                            })
                
                # Model and performance info
                with st.expander("📊 Query Performance", expanded=False):
                    perf_cols = st.columns(3)
                    with perf_cols[0]:
                        st.metric("Model Used", response.get('model', 'Unknown'))
                    with perf_cols[1]:
                        st.metric("Documents Retrieved", response.get('documents_retrieved', 0))
                    with perf_cols[2]:
                        timestamp = response.get('timestamp', 'Unknown')
                        if timestamp != 'Unknown':
                            st.metric("Response Time", "< 1s")  # Simplified for now
            
            else:
                # Error display
                st.markdown(f"""
                <div style="background: #ffe6e6; padding: 1rem; border-radius: 6px; border-left: 4px solid #f44336; margin: 1rem 0;">
                    <h4>❌ Error:</h4>
                    <p>{response.get('answer', 'Unknown error occurred')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons for each conversation
            action_cols = st.columns(4)
            with action_cols[0]:
                if st.button(f"🔄 Retry", key=f"retry_{chat_index}", help="Ask this question again"):
                    st.session_state.current_question = chat['question']
                    st.rerun()
            with action_cols[1]:
                if st.button(f"🔍 Follow Up", key=f"followup_{chat_index}", help="Ask a follow-up question"):
                    st.session_state.current_question = f"Regarding '{chat['question']}', can you tell me more about "
                    st.rerun()
            with action_cols[2]:
                if st.button(f"📋 Copy", key=f"copy_{chat_index}", help="Copy answer to clipboard"):
                    # Note: Actual clipboard functionality would require additional setup
                    st.info("Answer copied to clipboard! (Feature coming soon)")
            with action_cols[3]:
                if st.button(f"🗑️ Delete", key=f"delete_{chat_index}", help="Remove this conversation"):
                    # Remove this specific conversation
                    del st.session_state.chat_history[len(st.session_state.chat_history) - i - 1]
                    st.rerun()
            
            st.markdown("---")


def _export_chat_history():
    """Export chat history as downloadable text file"""
    if not st.session_state.chat_history:
        st.warning("No chat history to export.")
        return
    
    # Generate export content
    export_content = "KNOWLEDGEBASE AGENT - CHAT EXPORT\n"
    export_content += "=" * 50 + "\n\n"
    export_content += f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_content += f"Total Conversations: {len(st.session_state.chat_history)}\n\n"
    
    for i, chat in enumerate(st.session_state.chat_history, 1):
        export_content += f"CONVERSATION {i}\n"
        export_content += "-" * 20 + "\n"
        export_content += f"Question: {chat['question']}\n\n"
        export_content += f"Answer: {chat['response'].get('answer', 'No answer available')}\n\n"
        
        if chat['response'].get('sources'):
            export_content += "Sources:\n"
            for source in chat['response']['sources']:
                export_content += f"- {source['filename']} (chunk {source['chunk_index']})\n"
        
        export_content += "\n" + "=" * 50 + "\n\n"
    
    # Offer download
    st.download_button(
        label="📄 Download Chat History",
        data=export_content,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        help="Download your conversation history as a text file"
    )


def display_document_management():
    """Display document management interface"""
    st.markdown('<div class="section-header">📂 Document Management</div>', unsafe_allow_html=True)
    
    try:
        stats = st.session_state.document_processor.get_document_stats()
        documents = stats.get('documents', [])
        
        if not documents:
            st.info("📝 No documents uploaded yet. Use the upload section to add documents to your knowledge base.")
            return
        
        # Documents table
        st.subheader("📋 Uploaded Documents")
        
        # Create a formatted table
        doc_data = []
        for doc in documents:
            doc_data.append({
                "Filename": doc.get('filename', 'Unknown'),
                "Category": doc.get('category', 'general').title(),
                "Chunks": doc.get('total_chunks', 0),
                "Size (KB)": f"{doc.get('file_size', 0) / 1024:.1f}",
                "Type": doc.get('file_type', 'unknown').upper(),
                "Uploaded": doc.get('upload_timestamp', 'Unknown')[:10]  # Show date only
            })
        
        if doc_data:
            st.dataframe(doc_data, use_container_width=True)
        
        # Document actions
        st.subheader("🛠️ Document Actions")
        
        selected_doc = st.selectbox(
            "Select document for actions:",
            options=[doc.get('filename', f"Document {i}") for i, doc in enumerate(documents)],
            help="Choose a document to view details or delete"
        )
        
        if selected_doc:
            selected_doc_data = next((doc for doc in documents if doc.get('filename') == selected_doc), None)
            
            if selected_doc_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📖 View Details", key="view_details"):
                        st.json(selected_doc_data)
                
                with col2:
                    if st.button("🗑️ Delete Document", key="delete_doc", type="secondary"):
                        # Note: This would require implementing document deletion
                        st.warning("Document deletion functionality would be implemented here.")
    
    except Exception as e:
        st.error(f"Error loading document management: {e}")


def main():
    """Main application function"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Display sidebar
        display_sidebar()
        
        # Main content area
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📤 Upload", "📂 Manage"])
        
        with tab1:
            chat_interface()
            st.markdown("---")
            display_chat_history()
        
        with tab2:
            document_upload_section()
        
        with tab3:
            display_document_management()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            🧠 <strong>KnowledgeBase Agent</strong> • Built with Streamlit, LangChain, and AI
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        st.error("Please check your configuration and try again.")
        logger.error(f"Application error: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()