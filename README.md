# CURA 🩺

CURA is an **AI-powered medical assistant** designed to streamline healthcare tasks by enabling users to interact with medical data, ask queries, and retrieve information efficiently.  
It leverages **FAISS indexing**, **Hugging Face models**, and **LangChain pipelines** to provide intelligent, retrieval-augmented responses in a simple web-based interface.

---

## 📑 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [UI](#-ui)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#-usage)
- [Directory Structure](#-directory-structure)
- [Workflow](#-workflow)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Features
- **Conversational AI Chatbot** – Ask medical queries using Hugging Face-powered LLMs.  
- **PDF Knowledge Extraction** – Upload and analyze medical PDFs for interactive Q&A.  
- **FAISS Vector Store** – Efficient indexing for fast and relevant information retrieval.  
- **Retrieval-Augmented Generation (RAG)** – Smarter responses by blending embeddings with generative AI.  
- **Web Interface** – Lightweight HTML/CSS/JS frontend for seamless interaction.  
- **FastAPI Backend** – Scalable and modular API for healthcare-related tasks.  

---

## 🏗 Architecture
CURA follows a modular pipeline:  

1. **Frontend** – Simple web UI built with HTML, CSS, JS.  
2. **Backend** – FastAPI server handling chat, PDF ingestion, and retrieval requests.  
3. **Data Processing** –  
   - PDF parsing via `PyPDF2`.  
   - FAISS vector indexing for document retrieval.  
4. **AI Models** –  
   - Hugging Face `transformers` for language generation.  
   - LangChain-powered RAG pipeline for contextual Q&A.  

---

## 🖼 UI
| Chatbot Interface | Chat Output |
|-------------------|-------------|
| ![UI Screenshot 1](assets/chat1.png) | ![UI Screenshot 2](assets/chat2.png) |

---

## ⚙️ Installation

### Prerequisites
- Python **3.10+**  
- Node.js *(optional, for frontend dependencies)*  
- `pip` package manager  
- Hugging Face models (configured in `config.py`)  

### Setup
```bash
# Clone repo
git clone https://github.com/royxdev/CURA.git
cd CURA

# Setup virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure models in config.py (LLM_MODEL, EMBEDDING_MODEL)
````

Run the server:

```bash
python run_server.py
```

---

## 💻 Usage

1. Place medical PDFs in `data/pdfs/`.
2. Start the backend server:

   ```bash
   python run_server.py
   ```
3. Open `frontend/index.html` in a browser.
4. Interact with the chatbot — ask questions, analyze PDFs, and retrieve insights.
5. (Optional) Run terminal-based chat:

   ```bash
   python main.py
   ```

---

## 📂 Directory Structure

```
CURA/
├── chains/            # RAG pipeline
├── chatbot/           # Conversational logic
├── data/
│   └── pdfs/          # Medical documents
├── faiss_index/       # Vector stores
├── models/            # Model loaders
├── utils/             # Utilities (PDF, prompts, vector ops)
├── frontend/          # Web interface (HTML, CSS, JS)
├── run_server.py      # FastAPI entrypoint
├── requirements.txt   # Dependencies
└── config.py          # Model configs
```

---

## 🔄 Workflow

1. **Extract PDF text** → `utils/pdf_utils.py`.
2. **Build FAISS vector store** → `utils/vector_store.py`.
3. **Load LLM** → `models/llm_loader.py`.
4. **RAG pipeline setup** → `chains/rag_pipeline.py`.
5. **Interact** → via web UI or terminal chatbot.

---

## 🛠 Roadmap

* ✅ Core features: PDF ingestion, FAISS indexing, chatbot.
* 🚀 Future:

  * Support for more medical file formats.
  * Smarter conversational context handling.
  * Full web deployment (Docker/Cloud hosting).

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit & push changes
4. Submit a Pull Request 🚀

---

## 📜 License

CURA is released under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

* [Hugging Face](https://huggingface.co/) – for model libraries
* [LangChain](https://www.langchain.com/) – for RAG pipeline
* [FAISS](https://faiss.ai/) – for efficient vector indexing
* Open-source contributors who made this possible ♥
