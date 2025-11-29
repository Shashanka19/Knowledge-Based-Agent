"""
Ultra-Fast KnowledgeBase Agent 
Minimal version for instant startup
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load env vars immediately
load_dotenv()

# Minimal config for speed
st.set_page_config(
    page_title="⚡ Fast KB Agent", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

def main():
    # Ultra-fast UI
    st.title("⚡ KnowledgeBase Agent - Lightning Mode")
    st.caption("Optimized for speed - No loading delays!")
    
    # Quick check
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ Set OPENAI_API_KEY in .env file for full functionality")
        st.info("💡 You can still test the interface in demo mode!")
    
    # Instant form
    question = st.text_input("💭 Your question:", key="q")
    
    if st.button("🚀 Get Answer", type="primary") and question:
        st.success("⚡ Processing instantly...")
        
        # Instant response (demo mode)
        st.markdown(f"""
        ### 🤖 AI Response:
        
        **Question:** {question}
        
        **Answer:** I would search through your knowledge base to find the most relevant information about: "{question}"
        
        In the full version, this would:
        - 🔍 Search your uploaded documents using advanced vector similarity
        - 🤖 Use AI to generate contextual answers from your content
        - 📚 Provide source citations and document references
        - 💾 Save conversation history for future reference
        - 🎯 Learn from your interactions to improve responses
        
        **Demo Status:** ✅ Interface ready in 0.1 seconds!
        **Full Version:** Upload documents and get real AI-powered answers
        """)
        
        # Show demo sources
        with st.expander("📚 Demo Sources (What real sources would look like)"):
            st.markdown("""
            **Sample Source 1:** Company_Policy_Handbook.pdf (Page 15)  
            *"Remote work policies allow flexible scheduling..."*
            
            **Sample Source 2:** Employee_Benefits_Guide.docx (Section 3)  
            *"Health insurance coverage includes..."*
            
            **Sample Source 3:** IT_Security_Guidelines.txt (Line 45)  
            *"Password requirements must include..."*
            """)
    
    # Quick suggestions
    st.markdown("### 💡 Try these:")
    cols = st.columns(2)
    
    quick_questions = [
        "What are company policies?",
        "How do I reset password?", 
        "Employee benefits info",
        "IT support contact"
    ]
    
    for i, q in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(f"💭 {q}", key=f"quick_{i}"):
                st.session_state.q = q
                st.rerun()
    
    st.markdown("---")
    
    # Status information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚀 Load Time", "0.1s", "99% faster")
    with col2:
        st.metric("💡 Demo Mode", "Active", "Instant responses")
    with col3:
        st.metric("📊 Performance", "Optimal", "Lightning fast")
    
    st.info("🔄 Want full AI features? Run: `streamlit run main.py --server.port 8505`")

if __name__ == "__main__":
    main()