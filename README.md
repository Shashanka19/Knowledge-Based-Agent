# KnowledgeBase Agent 🧠

A comprehensive AI-powered internal knowledge base system that allows employees to upload company documents and get instant answers to their questions using advanced RAG (Retrieval-Augmented Generation) technology.

## ✨ Features

- **📤 Document Upload**: Support for PDF, DOCX, and TXT files
- **🤖 Multi-Model Support**: OpenAI GPT, Claude, and Gemini models
- **🔍 Smart Search**: Vector-based similarity search with ChromaDB or Pinecone
- **📚 Source Citations**: Every answer includes source document references
- **🏷️ Document Categories**: Organize documents by HR, Policies, SOPs, etc.
- **💬 Interactive Chat**: User-friendly Streamlit interface
- **📊 Analytics**: Document and query statistics
- **🔄 Real-time Processing**: Live document ingestion and querying

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Document       │───▶│  Vector Store   │
│                 │    │  Processor      │    │  (ChromaDB/     │
└─────────────────┘    └─────────────────┘    │   Pinecone)     │
         │                       │             └─────────────────┘
         │                       │                       │
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐              │
│  Query Engine   │───▶│  LLM Models     │              │
│  (RAG Pipeline) │    │  (GPT/Claude/   │              │
└─────────────────┘    │   Gemini)       │              │
         │              └─────────────────┘              │
         │                                               │
         └───────────────────────────────────────────────┘
```

## 🚀 Quick Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd knowledge-base-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY (for embeddings and default model)
# Optional: ANTHROPIC_API_KEY, GOOGLE_API_KEY
```

### 4. Run the Application
```bash
streamlit run main.py
```

## ⚙️ Configuration Options

### Model Providers

#### OpenAI (Default)
```env
MODEL_PROVIDER=openai
MODEL_NAME=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo
OPENAI_API_KEY=your_openai_api_key_here
```

#### Anthropic Claude
```env
MODEL_PROVIDER=claude
MODEL_NAME=claude-2  # or claude-3-sonnet, claude-3-opus
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### Google Gemini
```env
MODEL_PROVIDER=gemini
MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_google_api_key_here
```

### Vector Stores

#### ChromaDB (Default - Local)
```env
VECTOR_STORE_TYPE=chromadb
CHROMA_COLLECTION_NAME=knowledgebase
CHROMA_PERSIST_DIR=./data/chroma_db
```

#### Pinecone (Cloud)
```env
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=knowledgebase
```

### Metadata Storage

#### Local JSON (Default)
```env
METADATA_DB_TYPE=local
LOCAL_DATA_DIR=./data
```

#### Firebase Firestore
```env
METADATA_DB_TYPE=firebase
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_SERVICE_ACCOUNT_PATH=./path/to/service-account.json
```

## 📋 Usage Guide

### 1. Upload Documents
1. Navigate to the **Upload** tab
2. Select document category (HR, Policies, SOPs, etc.)
3. Drag and drop or browse for files (PDF, DOCX, TXT)
4. Click "Process Documents"

### 2. Ask Questions
1. Go to the **Chat** tab
2. Type your question or select from example questions
3. Optionally filter by document category
4. Get instant answers with source citations

### 3. Manage Documents
1. Visit the **Manage** tab
2. View all uploaded documents
3. Check document statistics
4. View document details

## 🛠️ Advanced Configuration

### Custom Prompts
Edit the prompt templates in `src/components/query.py`:

```python
self.qa_prompt_template = """
Your custom prompt template here...
Context: {context}
Question: {question}
Answer:
"""
```

### Text Chunking
Modify chunking parameters in `src/components/ingest.py`:

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Increase for longer chunks
    chunk_overlap=200,    # Adjust overlap
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
```

### Retrieval Settings
Adjust search parameters in the Streamlit sidebar:
- Number of documents to retrieve (1-10)
- Category filtering
- Advanced mode toggle

## 📁 Project Structure

```
knowledge-base-agent/
├── main.py                     # Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
├── data/                      # Local data storage
│   ├── chroma_db/            # ChromaDB persistence
│   └── documents.json        # Local metadata
├── uploads/                   # Temporary upload directory
└── src/
    └── components/
        ├── __init__.py        # Package initializer
        ├── vector_store.py    # Vector database interfaces
        ├── model_loader.py    # LLM model management
        ├── ingest.py         # Document processing
        ├── query.py          # RAG query engine
        └── firebase_db.py    # Metadata storage
```

## 🔧 API Key Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create account and navigate to API Keys
3. Create new secret key
4. Add to `.env` file: `OPENAI_API_KEY=sk-...`

### Anthropic API Key
1. Visit [Anthropic Console](https://console.anthropic.com)
2. Create account and generate API key
3. Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

### Google AI API Key
1. Visit [Google AI Studio](https://aistudio.google.com)
2. Create project and generate API key
3. Add to `.env` file: `GOOGLE_API_KEY=AIza...`

### Pinecone API Key
1. Visit [Pinecone Console](https://app.pinecone.io)
2. Create account and new project
3. Get API key and environment
4. Add to `.env` file

## 🎯 Example Questions

- "What is the company's vacation policy?"
- "How do I submit an expense report?"
- "What are the working hours?"
- "What is the dress code policy?"
- "How do I access company resources?"
- "What are the safety protocols?"
- "How do I get IT support?"
- "What is the remote work policy?"

## 🚨 Troubleshooting

### Common Issues

#### "No module named 'components'"
```bash
# Ensure you're in the project root directory
cd knowledge-base-agent
python -m streamlit run main.py
```

#### ChromaDB Permission Issues
```bash
# Fix permissions on data directory
chmod -R 755 ./data
```

#### Large File Upload Errors
Add to `main.py`:
```python
st.set_page_config(
    page_title="KnowledgeBase Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

#### Memory Issues
- Reduce `chunk_size` in text splitter
- Use fewer documents for retrieval
- Consider using Pinecone instead of ChromaDB

### Performance Optimization

1. **Use Pinecone** for better scalability
2. **Adjust chunk size** based on your documents
3. **Enable caching** for repeated queries
4. **Use GPT-3.5** instead of GPT-4 for faster responses

## 📊 Monitoring & Analytics

The application tracks:
- Number of documents uploaded
- Total chunks created
- Document categories
- Query statistics
- Popular questions
- Search performance

Access analytics in the sidebar and Manage tab.

## 🔒 Security Considerations

1. **API Keys**: Store securely in `.env` file (never commit)
2. **Firebase**: Use service accounts with minimal permissions
3. **Documents**: Ensure no sensitive data in uploads
4. **Access**: Deploy with proper authentication if needed

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** - RAG framework
- **Streamlit** - Web interface
- **OpenAI** - Embeddings and LLM
- **ChromaDB** - Vector database
- **Pinecone** - Cloud vector database

---

<div align="center">
  <strong>Built with ❤️ for internal knowledge management</strong>
</div>