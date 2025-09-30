# 🏥 Cura Medical AI Assistant

**Advanced RAG-powered medical assistant with professional-grade diagnostic capabilities**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-3.0+-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-purple.svg)](https://langchain.com)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Advanced Medical AI Features

### 🧠 RAG-Powered Intelligence
- **Document-Based Responses**: AI answers backed by medical literature and documents
- **Vector Search**: FAISS-powered similarity search across medical knowledge base
- **Intelligent Fallback**: Automatic fallback to standard AI when RAG unavailable
- **Source Attribution**: Every response includes relevant source documents

### 🔍 Core Capabilities
- **Medical Consultation**: Evidence-based medical guidance and information
- **Symptom Analysis**: Comprehensive symptom assessment and recommendations
- **Emergency Detection**: Automatic triage and emergency protocol guidance
- **Drug Information**: Medication guidance and interaction checking

## 🛠️ Technology Stack

### Core Framework
- **FastAPI**: Modern Python web framework with lifespan events
- **LangChain**: RAG pipeline framework for AI applications
- **Google Gemini 2.5 Flash**: Latest AI model with 100K token capacity
- **FAISS**: Vector similarity search with AVX2 optimization
- **HuggingFace Embeddings**: sentence-transformers/all-MiniLM-L6-v2

### RAG Architecture
- **Vector Store**: FAISS index with 60K+ medical document embeddings
- **Document Processing**: Automatic PDF processing and intelligent chunking
- **Intelligent Retrieval**: MMR-based document retrieval with relevance scoring
- **Fallback System**: Multi-tier response system ensuring 100% availability
- **No Database**: Pure file-based system with zero external dependencies

## 📋 Prerequisites

- Python 3.9+
- Google API Key (for Gemini)
- 4GB+ RAM (for embeddings)
- Medical PDF documents (optional)

## ⚡ Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/royxlead/cura-python.git
cd cura-python
python -m venv myenv
myenv/Scripts/activate  # Windows
# source myenv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Create .env file with your Google API key
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

### 3. Run the Server (Vector Store Included!)
```bash
python run_server.py
```

**Note**: The project includes a pre-built vector store with 60K+ medical documents ready to use!

Visit http://localhost:8000 for the web interface!

## 🔧 Configuration

### Environment Variables (.env)
```env
# AI Configuration
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-2.5-flash
LLM_MAX_TOKENS=100000
LLM_TEMPERATURE=0.7

# Vector Store Configuration
DEVICE=cpu
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=faiss_index
PDF_DATA_PATH=data/pdfs

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🏗️ Project Structure

```
cura-python/
├── app/
│   └── services/          # Business logic services
│       ├── simple_ai_service.py    # Enhanced RAG-enabled AI service
│       └── __init__.py
├── chains/                # RAG pipeline
│   └── rag_pipeline.py    # Medical RAG implementation
├── utils/                 # Utility functions
│   ├── vector_store.py    # Vector store management & CLI
│   └── prompts.py         # Medical prompt templates
├── data/                  # Medical documents
│   └── pdfs/              # PDF documents for RAG (60K+ docs)
├── faiss_index/           # Pre-built vector store
│   ├── index.faiss        # FAISS vector index
│   └── index.pkl          # Document metadata
├── frontend/              # Progressive Web App
│   ├── index.html         # Main interface
│   ├── app.js             # Client logic
│   └── app.css            # Styling
├── myenv/                 # Virtual environment
├── run_server.py          # Main FastAPI server
└── requirements.txt       # Python dependencies
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `GET /api/health` - Health check
- `GET /api/status` - Service status including RAG

### Chat & RAG
- `POST /api/chat` - RAG-enabled chat
  ```json
  {
    "message": "What are the symptoms of diabetes?",
    "use_rag": true
  }
  ```
- `POST /api/search` - Direct document search
  ```json
  {
    "query": "diabetes symptoms",
    "k": 5
  }
  ```

### Advanced Features Added
- **Modern FastAPI**: Uses lifespan events instead of deprecated startup events
- **Zero Database Dependencies**: Pure file-based system with no external database requirements
- **Pre-built Vector Store**: Ready-to-use with 60K+ medical documents indexed
- **Enhanced Error Handling**: Comprehensive error responses and logging
- **Source Attribution**: Every RAG response includes relevant source documents
- **Intelligent Fallback**: Automatic detection and graceful degradation when RAG unavailable

### Manual Testing
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are diabetes symptoms?", "use_rag": true}'

# Test document search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes", "k": 3}'

# Check service status
curl http://localhost:8000/api/status
```

## 🚀 Advanced Usage

### Custom Document Processing
```python
from utils.vector_store import build_vector_store, load_documents_from_directory

# Load custom documents
documents = load_documents_from_directory("path/to/your/pdfs")
vector_store = build_vector_store(documents)
```

### Direct RAG Usage
```python
from chains.rag_pipeline import rag_pipeline

# Initialize and use RAG
rag_pipeline.initialize()
response = rag_pipeline.get_rag_response("What is hypertension?")
print(response["answer"])
```

## 📊 Performance

- **RAG Response Time**: ~2-5 seconds for document-backed responses
- **Fallback Time**: ~1-2 seconds for standard AI responses  
- **Vector Search**: ~100ms for similarity search across 60K+ documents
- **Memory Usage**: ~2-4GB with embeddings loaded (sentence-transformers)
- **Index Size**: 60,698 medical documents pre-indexed
- **Startup Time**: ~10-15 seconds for full system initialization

## 🛡️ Medical Disclaimers

**IMPORTANT**: This AI assistant provides general medical information only and should never replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical concerns.

## 🔒 Security Features

- **API Rate Limiting**: Built-in request throttling
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Configurable cross-origin policies
- **Error Handling**: Secure error responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FAISS Documentation](https://faiss.ai/)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚡ Quick Commands

```bash
# Start development server (with auto-reload)
python run_server.py

# Build new vector store (if adding documents)
python -m utils.vector_store

# Check system status
curl http://localhost:8000/api/status

# Test RAG functionality
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is diabetes?", "use_rag": true}'

# Search medical documents directly
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes symptoms", "k": 5}'
```

---

**Built with ❤️ for better healthcare accessibility**