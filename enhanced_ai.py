"""
Enhanced KnowledgeBase Agent with External AI Integration
Integrates ChatGPT, GitHub Copilot, and Google Search
"""

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.components.external_ai import ExternalAIIntegrator
except ImportError:
    st.error("External AI integration module not found!")
    st.stop()

# Load environment variables
load_dotenv()

# Configure Streamlit
st.set_page_config(
    page_title="🌟 Enhanced KB Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better appearance
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.source-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    color: white;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.chatgpt-card {
    background: linear-gradient(135deg, #00c851 0%, #007e33 100%);
}

.copilot-card {
    background: linear-gradient(135deg, #4285f4 0%, #0f4c75 100%);
}

.google-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.kb-card {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    color: #333;
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'ai_integrator' not in st.session_state:
        st.session_state.ai_integrator = ExternalAIIntegrator()
    
    if 'enhanced_chat_history' not in st.session_state:
        st.session_state.enhanced_chat_history = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""

def check_api_keys():
    """Check and display API key status"""
    st.sidebar.title("🔑 API Configuration")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") 
    google_cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
    
    st.sidebar.markdown("### Status:")
    st.sidebar.write(f"🤖 ChatGPT: {'✅ Ready' if openai_key else '❌ Missing'}")
    st.sidebar.write(f"⚡ Copilot: {'✅ Ready' if openai_key else '❌ Missing'}")
    st.sidebar.write(f"🔍 Google: {'✅ Ready' if (google_key and google_cx) else '❌ Missing'}")
    
    if not openai_key:
        st.sidebar.error("Add OPENAI_API_KEY to .env file")
    
    if not (google_key and google_cx):
        st.sidebar.warning("Add GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_CX for Google Search")
        st.sidebar.info("Get them from Google Cloud Console")
    
    return openai_key is not None

def main():
    """Enhanced main function with AI integration"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌟 Enhanced KnowledgeBase Agent</h1>
        <h3>Powered by ChatGPT + GitHub Copilot + Google Search</h3>
        <p>Get comprehensive answers from multiple AI sources</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize
    init_session_state()
    
    # Check API keys
    has_openai = check_api_keys()
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💭 Ask Your Question")
        
        # Question input with form
        with st.form("enhanced_question_form", clear_on_submit=True):
            question = st.text_area(
                "What would you like to know?", 
                value=st.session_state.current_question,
                placeholder="Ask anything... I'll search your knowledge base, ChatGPT, Copilot, and Google!",
                height=100
            )
            
            col_submit, col_sources = st.columns([1, 1])
            
            with col_submit:
                submitted = st.form_submit_button("🚀 Get Comprehensive Answer", type="primary")
            
            with col_sources:
                query_mode = st.selectbox(
                    "Query Mode:",
                    ["All Sources", "ChatGPT Only", "Copilot Only", "Google Only", "Knowledge Base Only"],
                    index=0
                )
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        # Predefined questions
        if st.button("💼 Company Policies", use_container_width=True):
            st.session_state.current_question = "What are our company policies and procedures?"
            st.rerun()
            
        if st.button("🔐 Password Reset", use_container_width=True):
            st.session_state.current_question = "How do I reset my password and account security?"
            st.rerun()
            
        if st.button("💻 Technical Support", use_container_width=True):
            st.session_state.current_question = "How do I get technical support and IT help?"
            st.rerun()
            
        if st.button("📋 HR Benefits", use_container_width=True):
            st.session_state.current_question = "What employee benefits and HR services are available?"
            st.rerun()
        
        # Clear history
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.enhanced_chat_history = []
            st.rerun()
    
    # Process question
    if submitted and question:
        process_enhanced_query(question, query_mode, has_openai)
    
    # Display chat history
    display_enhanced_chat_history()

def process_enhanced_query(question: str, query_mode: str, has_openai: bool):
    """Process query using selected AI sources"""
    
    if not has_openai and query_mode != "Knowledge Base Only":
        st.error("❌ OpenAI API key required for ChatGPT and Copilot integration")
        return
    
    start_time = datetime.now()
    
    try:
        if query_mode == "All Sources":
            # Query all sources
            st.info("🔍 Querying multiple AI sources... This may take a moment.")
            
            # Get knowledge base response (simulated)
            kb_response = {
                "success": True,
                "answer": f"**Knowledge Base Response:** Based on our internal documents, here's what I found about '{question}'. In a real implementation, this would search through uploaded documents using vector similarity and provide relevant information with citations.",
                "sources": ["Internal Documents"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Query external sources
            external_results = st.session_state.ai_integrator.query_all_sources(
                question, 
                kb_response.get('answer', '')
            )
            
            # Combine results
            final_response = st.session_state.ai_integrator.format_multi_source_response(
                question, external_results, kb_response
            )
            
        elif query_mode == "ChatGPT Only":
            with st.spinner("🤖 Asking ChatGPT..."):
                final_response = st.session_state.ai_integrator.query_chatgpt(question)
                
        elif query_mode == "Copilot Only":
            with st.spinner("⚡ Consulting GitHub Copilot..."):
                final_response = st.session_state.ai_integrator.simulate_copilot_response(question)
                
        elif query_mode == "Google Only":
            with st.spinner("🔍 Searching Google..."):
                final_response = st.session_state.ai_integrator.query_google_search(question)
                
        else:  # Knowledge Base Only
            final_response = {
                "success": True,
                "answer": f"**Knowledge Base Response:** This would search through your uploaded documents for information about '{question}'. In the full implementation, vector search would find relevant chunks from PDFs, DOCs, and text files, then use AI to generate a comprehensive answer with proper citations.",
                "sources": ["Internal Knowledge Base"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Store in history
        chat_entry = {
            "question": question,
            "response": final_response,
            "query_mode": query_mode,
            "processing_time": processing_time,
            "timestamp": start_time.isoformat()
        }
        
        st.session_state.enhanced_chat_history.append(chat_entry)
        st.success(f"✅ Response generated in {processing_time:.2f} seconds!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing query: {str(e)}")

def display_enhanced_chat_history():
    """Display enhanced chat history with source indicators"""
    
    if not st.session_state.enhanced_chat_history:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); border-radius: 15px; color: white; margin: 2rem 0;">
            <h2>🚀 Ready to Get Started!</h2>
            <p>Ask any question and I'll search across multiple AI sources to give you comprehensive answers!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("---")
    st.markdown("## 💬 Enhanced Chat History")
    
    # Display recent conversations
    for i, chat in enumerate(reversed(st.session_state.enhanced_chat_history[-5:])):
        chat_num = len(st.session_state.enhanced_chat_history) - i
        
        with st.expander(f"🔍 Query {chat_num}: {chat['question'][:60]}...", expanded=i < 2):
            
            # Question
            st.markdown(f"**❓ Question:** {chat['question']}")
            
            # Query info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mode", chat['query_mode'])
            with col2:
                st.metric("Time", f"{chat['processing_time']:.1f}s")
            with col3:
                st.metric("Sources", len(chat['response'].get('sources', [])))
            
            # Response
            response = chat['response']
            if response.get('success'):
                st.markdown("**🤖 Response:**")
                st.markdown(response['answer'])
                
                # Source indicators
                if response.get('sources'):
                    st.markdown("**📚 Sources Used:**")
                    source_cols = st.columns(min(len(response['sources']), 4))
                    
                    for idx, source in enumerate(response['sources'][:4]):
                        with source_cols[idx]:
                            if "ChatGPT" in source:
                                st.markdown('<div class="source-card chatgpt-card">🤖 ChatGPT</div>', unsafe_allow_html=True)
                            elif "Copilot" in source:
                                st.markdown('<div class="source-card copilot-card">⚡ GitHub Copilot</div>', unsafe_allow_html=True)
                            elif "Google" in source:
                                st.markdown('<div class="source-card google-card">🔍 Google Search</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="source-card kb-card">📚 Knowledge Base</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ {response.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()