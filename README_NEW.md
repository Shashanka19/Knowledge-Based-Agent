# 🤖 KNOWLEDGE BASE AGENT

**AI-Powered Internal Knowledge Management System with Multi-Source Intelligence**

A comprehensive knowledge base solution that integrates ChatGPT, GitHub Copilot, Google Safe Search, and internal document search to provide intelligent, contextual answers to your questions.

## 🌟 Features

### 🔍 **Multi-Source AI Integration**
- **🤖 ChatGPT Integration**: Direct OpenAI API integration for comprehensive answers
- **⚡ GitHub Copilot**: Technical assistance with coding focus and best practices
- **🛡️ Google Safe Search**: Family-friendly, workplace-appropriate web results
- **📚 Knowledge Base**: Internal document search with vector similarity

### 🛡️ **Advanced Safety & Reliability**
- **Rate Limit Protection**: Intelligent handling of API limits with graceful fallbacks
- **Safe Search Filtering**: Content filtering for workplace-appropriate results
- **Error Recovery**: Automatic demo mode when APIs are unavailable
- **Smart Caching**: Optimized performance with intelligent caching

### 🎯 **User Experience**
- **Multi-Mode Querying**: Choose specific AI sources or query all simultaneously
- **Interactive Interface**: Clean, modern Streamlit-based UI
- **Real-time Progress**: Visual feedback during query processing
- **Chat History**: Expandable conversation threads with source tracking

## 🚀 Quick Start

### 1. **Installation**
```bash
# Clone or download the project
cd "Knowledge Base Agent"

# Install dependencies
pip install streamlit python-dotenv requests

# Set up environment variables
# Add your OpenAI API key to .env file
OPENAI_API_KEY=your_api_key_here
```

### 2. **Run the Application**
```bash
# Run the main application (recommended)
streamlit run rate_safe.py --server.port 8511

# Access at: http://localhost:8511
```

## 📋 Available Versions

### 🛡️ **Rate-Safe Version** (Recommended) - `rate_safe.py`
- **Port**: 8511
- **Features**: Full AI integration with rate limit protection
- **Best for**: Production use with API safety

### ⚡ **Lightning Version** - `lightning.py`
- **Port**: 8507  
- **Features**: Ultra-fast demo responses, instant startup
- **Best for**: Testing and demonstrations

### 🚀 **Enhanced Version** - `enhanced_ai.py`
- **Port**: 8509
- **Features**: Full API integration without rate limiting protection
- **Best for**: Development and testing with unlimited API access

### 🔋 **Full Version** - `main.py`
- **Port**: 8505
- **Features**: Complete knowledge base with document upload
- **Best for**: Full document management capabilities

## 🔧 Configuration

### Environment Variables (`.env`)
```env
# AI Integration
OPENAI_API_KEY=your_openai_api_key
ENABLE_CHATGPT_INTEGRATION=true
ENABLE_COPILOT_SIMULATION=true
ENABLE_GOOGLE_SEARCH=false

# Optional: Google Search API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CUSTOM_SEARCH_CX=your_search_engine_id

# Application Settings
MODEL_PROVIDER=openai
MODEL_NAME=gpt-3.5-turbo
VECTOR_STORE_TYPE=chromadb
```

## 🎯 Usage Examples

### **Multi-Source Query**
Ask: *"How do I reset my password?"*

**You get responses from:**
- 🤖 **ChatGPT**: General password reset guidance
- ⚡ **Copilot**: Technical troubleshooting steps  
- 🛡️ **Google Safe Search**: Safe, filtered web results
- 📚 **Knowledge Base**: Company-specific policies

### **Query Modes**
- **All Sources**: Comprehensive answers from all AI sources
- **ChatGPT Only**: Direct OpenAI responses
- **Copilot Only**: Technical assistance focus
- **Google Safe Only**: Filtered web search results
- **Knowledge Base Only**: Internal document search

## 🛡️ Safety Features

### **Content Filtering**
- Family-friendly results only
- Workplace-appropriate content
- Educational resource prioritization
- Malicious site protection
- Community-verified sources

### **API Protection**
- Rate limit detection and handling
- Graceful degradation to demo mode
- Error recovery mechanisms
- Smart retry logic with exponential backoff

## 📊 Performance

### **Load Times**
- **Lightning Mode**: 2-3 seconds
- **Rate-Safe Mode**: 5-8 seconds  
- **Enhanced Mode**: 8-12 seconds
- **Full Mode**: 10-15 seconds

### **Response Generation**
- **Demo Responses**: Instant
- **Single Source**: 2-5 seconds
- **Multi-Source**: 5-10 seconds
- **With Rate Limits**: Fallback to demo mode

## 🔍 Architecture

```
Knowledge Base Agent/
├── rate_safe.py           # Main application (recommended)
├── lightning.py           # Ultra-fast demo version
├── enhanced_ai.py         # Full API integration
├── main.py               # Complete knowledge base
├── src/
│   └── components/
│       ├── external_ai.py    # AI integration module
│       ├── vector_store.py   # Vector database
│       ├── model_loader.py   # AI model management
│       ├── query.py          # Query processing
│       └── ingest.py         # Document processing
├── .env                  # Environment configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test with different query modes
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Common Issues**
- **429 Rate Limit Errors**: Use `rate_safe.py` version
- **Slow Loading**: Try `lightning.py` for instant startup
- **API Errors**: Check `.env` configuration

### **Getting Help**
- Check the console for error messages
- Verify API keys in `.env` file
- Use demo mode for testing without API calls
- Try different versions based on your needs

## 🎉 Acknowledgments

- **OpenAI** for ChatGPT API
- **Streamlit** for the amazing web framework
- **LangChain** for AI orchestration capabilities
- **ChromaDB** for vector storage
- **Community contributors** for feedback and improvements

---

**🚀 Ready to get started? Run `streamlit run rate_safe.py --server.port 8511` and visit http://localhost:8511**