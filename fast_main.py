"""
Fast-Loading KnowledgeBase Agent
Optimized for better performance and faster startup
"""

import streamlit as st
import os
from dotenv import load_dotenv
from functools import lru_cache
import logging
from datetime import datetime

# Configure Streamlit for faster loading
st.set_page_config(
    page_title="🚀 KnowledgeBase Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables early
load_dotenv()

# Cache expensive operations
@st.cache_resource
def init_components():
    """Initialize components once and cache them - simplified version"""
    try:
        # Try to import components, but don't fail if they're not available
        import sys
        import importlib.util
        
        # Check if components exist
        components_available = True
        required_modules = [
            'src.components.vector_store',
            'src.components.model_loader', 
            'src.components.query'
        ]
        
        for module_name in required_modules:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                components_available = False
                break
        
        if components_available:
            from src.components.vector_store import VectorStoreFactory
            from src.components.model_loader import ModelLoader
            from src.components.query import QueryEngine
            
            vector_store = VectorStoreFactory.create_vector_store("chromadb")
            model_loader = ModelLoader()
            query_engine = QueryEngine(vector_store=vector_store, model_loader=model_loader)
            
            return {
                'vector_store': vector_store,
                'model_loader': model_loader,
                'query_engine': query_engine,
                'available': True
            }
        else:
            return {'available': False, 'reason': 'Components not found'}
            
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        return {'available': False, 'reason': str(e)}

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_suggestions():
    """Get cached suggestions"""
    return [
        "What are our company policies?",
        "How do I submit a vacation request?",
        "What are the employee benefits?",
        "How do I reset my password?",
        "What is the remote work policy?",
        "Who should I contact for IT support?"
    ]

def main():
    """Fast main function"""
    
    # Quick CSS injection
    st.markdown("""
    <style>
    .main-header { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 2rem;
    }
    .fast-input { margin: 1rem 0; }
    .suggestion-btn { margin: 0.2rem; padding: 0.5rem; background: #f0f2f6; border: 1px solid #ddd; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 KnowledgeBase Agent - Fast Mode</h1>
        <p>Lightning-fast AI-powered knowledge base</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick API key check
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Please set your OPENAI_API_KEY in the .env file")
        st.stop()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Quick question input
    with st.form("quick_question", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input("💭 Ask your question:", placeholder="Type your question here...")
        with col2:
            submitted = st.form_submit_button("🔍 Ask", type="primary")
    
    # Quick suggestions
    st.markdown("**💡 Quick Suggestions:**")
    suggestions = get_suggestions()
    
    # Display suggestions in columns for faster rendering
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions[:6]):
        with cols[i % 3]:
            if st.button(f"💭 {suggestion[:30]}...", key=f"sugg_{i}"):
                question = suggestion
                submitted = True
    
    # Process question quickly
    if submitted and question:
        with st.spinner("🔍 Processing..."):
            try:
                # Try to initialize components
                components = init_components()
                
                if components and components.get('available'):
                    # Use real components if available
                    query_engine = components['query_engine']
                    response = query_engine.process_query(
                        question=question,
                        model_name='gpt-3.5-turbo',
                        num_sources=3
                    )
                else:
                    # Fallback to demo mode
                    st.warning("⚠️ Running in demo mode - components not fully available")
                    response = {
                        'success': True,
                        'answer': f"**Demo Response for:** {question}\n\n" + 
                                "This is a demonstration response. In full mode, the system would:\n\n" +
                                "• 🔍 Search through your uploaded documents\n" +
                                "• 🤖 Use advanced AI models to analyze content\n" + 
                                "• 📚 Provide relevant citations and sources\n" +
                                "• 💾 Maintain conversation context\n\n" +
                                f"**Your Question:** {question}\n\n" +
                                "**Demo Answer:** Based on your knowledge base, I would provide a comprehensive answer " +
                                "drawing from relevant documents and company policies. The system is designed to give " +
                                "accurate, contextual responses with proper source citations.",
                        'sources': [],
                        'model': 'demo-mode',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': question,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                st.success("✅ Answer generated successfully!")
                st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try the lightning.py version for instant responses!")
    
    # Display chat history quickly
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 💬 Recent Conversations")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-3:])):  # Show last 3
            with st.expander(f"Q{len(st.session_state.chat_history)-i}: {chat['question'][:50]}..."):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['response']['answer']}")
                st.caption(f"Time: {chat['timestamp']}")
    
    # Quick actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh App"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📊 Full Version"):
            st.info("Switch to main.py for full features!")

if __name__ == "__main__":
    main()