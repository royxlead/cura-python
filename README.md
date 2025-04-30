# CURA

CURA is an AI-powered medical assistant designed to streamline healthcare-related tasks, enabling users to interact with medical data, ask questions, and retrieve information efficiently. By leveraging technologies like FAISS indexing, Hugging Face models, and LangChain pipelines, CURA provides a seamless and intelligent experience for both professionals and users in the healthcare domain.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Workflow](#workflow)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Interactive Chatbot:** Engage with a conversational AI powered by Hugging Face models for medical queries.
- **PDF Text Extraction:** Extract and process text from medical PDFs for analysis and interaction.
- **Vector Store Creation:** Organize medical data into efficient FAISS vector stores for quick retrieval.
- **Retrieval-Augmented Generation (RAG):** Enhance responses by integrating vector stores with language models.
- **Web-Based Interface:** Simple HTML/CSS/JS frontend for interacting with the chatbot.
- **FastAPI Backend:** A robust and scalable backend to process and manage requests.

---

## Architecture

CURA employs a modular architecture with distinct layers for data ingestion, processing, retrieval, and interaction:

1. **Frontend**: HTML/CSS/JS-based interface for user interaction.
2. **Backend**: FastAPI server for handling API requests and routing.
3. **Processing**:
   - PDF text extraction using PyPDF2.
   - FAISS vector store creation for efficient text retrieval.
4. **AI Models**:
   - Language generation via Hugging Face's `transformers`.
   - RAG pipeline for integrating embeddings and generative AI.

---

## UI

Below are the screenshots of the user interface:

![UI Screenshot 1](assets/chat1.png)

![UI Screenshot 2](assets/chat2.png)

---

## Installation

### Prerequisites

Ensure the following dependencies are installed:
- Python 3.10+
- Node.js (for managing frontend dependencies, if necessary)
- `pip` (Python package manager)
- Hugging Face's model dependencies (configured in `config.py`)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/heysouravroy/CURA.git
   cd CURA
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download or configure the required models:
   - Update `LLM_MODEL` and `EMBEDDING_MODEL` paths in `config.py` to point to valid Hugging Face models.

5. Start the backend server:
   ```bash
   python run_server.py
   ```

---

## Usage

1. **Prepare Data**:
   - Place your medical PDFs in the `data/pdfs/` directory.

2. **Run the Application**:
   - Start the backend server:
     ```bash
     python run_server.py
     ```
   - Open the `frontend/index.html` file in a browser to access the chatbot interface.

3. **Interact**:
   - Ask medical queries through the chatbot interface or via terminal using:
     ```bash
     python main.py
     ```

---

## Directory Structure

- **`chains/`**
  - `rag_pipeline.py`: Sets up the Retrieval-Augmented Generation pipeline.
- **`chatbot/`**
  - `interactive_chat.py`: Implements the chatbot interface for conversational queries.
- **`data/`**
  - `pdfs/`: Directory to store PDF files.
- **`faiss_index/`**
  - `index.faiss`, `index.pkl`: FAISS vector index files.
- **`models/`**
  - `llm_loader.py`: Loads and initializes the language model.
- **`utils/`**
  - `pdf_utils.py`: Extracts text from PDFs.
  - `prompts.py`: Defines default prompts for the chatbot.
  - `vector_store.py`: Creates vector stores from text data.
- **`frontend/`**
  - `index.html`: Web interface for the chatbot.
  - `style.css`: Styles for the frontend.
  - `scripts.js`: Client-side logic for API interaction.

---

## Workflow

1. **PDF Text Extraction**:
   - Extract text from PDFs using `extract_text_from_pdfs` in `utils/pdf_utils.py`.

2. **Vector Store Creation**:
   - Use `build_vector_store` in `utils/vector_store.py` to convert text into FAISS vector stores.

3. **Language Model Initialization**:
   - Load Hugging Face models via `initialize_llm` in `models/llm_loader.py`.

4. **RAG Pipeline**:
   - Set up the Retrieval-Augmented Generation pipeline using `setup_rag` in `chains/rag_pipeline.py`.

5. **Interactive Chat**:
   - Interact via the chatbot using `frontend/index.html` or the terminal interface.

---

## Roadmap

- **Version 1.0**:
  - Core features implemented (PDF extraction, vector store, RAG pipeline).
  - Functional chatbot interface.

- **Future Plans**:
  - Add support for more medical file formats.
  - Enhance chatbot conversational abilities.
  - Deploy the backend and frontend as a web application.

---

## Contributing

We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your fork and create a pull request:
   ```bash
   git push origin feature-name
   ```

Refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## License

CURA is licensed under the [MIT License](LICENSE). Feel free to use it in your projects.

---

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for the AI model libraries.
- [LangChain](https://langchain.com/) for the RAG pipeline.
- [FAISS](https://faiss.ai/) for the efficient vector indexing.
- All contributors and open-source libraries that make CURA possible.
