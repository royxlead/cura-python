"""Vector Store Utilities for Medical RAG System"""

import os
import sys
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

# Third-party imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

# PDF processing
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
    print("Warning: PyPDF2 not installed. PDF processing will not be available.")

# Load environment variables
load_dotenv()

# Configuration
DEVICE = os.getenv("DEVICE", "cpu")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "faiss_index")
PDF_DATA_PATH = os.getenv("PDF_DATA_PATH", "data/pdfs")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file"""
    if not PyPDF2:
        raise ImportError("PyPDF2 is required for PDF processing")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def load_documents_from_directory(directory: str) -> List[str]:
    """Load and extract text from all PDF files in a directory"""
    texts = []
    pdf_dir = Path(directory)
    
    if not pdf_dir.exists():
        logger.warning(f"PDF directory {directory} does not exist")
        return texts
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
    
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file.name}...")
        text = extract_text_from_pdf(str(pdf_file))
        if text.strip():
            texts.append(text)
        else:
            logger.warning(f"No text extracted from {pdf_file.name}")
    
    return texts

def build_vector_store(texts: List[str] = None) -> FAISS:
    """Build and save FAISS vector store from documents"""
    logger.info("Building vector store...")
    
    # Load texts if not provided
    if texts is None:
        texts = load_documents_from_directory(PDF_DATA_PATH)
    
    if not texts:
        logger.error("No documents found to build vector store")
        raise ValueError("No documents available for vector store creation")
    
    # Configuration
    chunk_size = 1000
    chunk_overlap = 200
    
    # Initialize text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Create documents and split into chunks
    documents = [Document(page_content=text) for text in texts]
    chunks = splitter.split_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks from {len(texts)} documents")
    logger.info(f"Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL, 
        model_kwargs={"device": DEVICE}
    )
    
    # Create FAISS vector store
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save locally
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_PATH)
    logger.info(f"Vector store saved to {VECTOR_STORE_PATH}")
    
    return vector_store

def load_vector_store() -> Optional[FAISS]:
    """Load existing FAISS vector store"""
    try:
        if not os.path.exists(VECTOR_STORE_PATH):
            logger.warning(f"Vector store not found at {VECTOR_STORE_PATH}")
            return None
        
        # Initialize embeddings (same as used for building)
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE}
        )
        
        # Load the vector store
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        logger.info(f"Vector store loaded from {VECTOR_STORE_PATH}")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")
        return None

def search_similar_documents(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar documents using the vector store"""
    vector_store = load_vector_store()
    
    if not vector_store:
        logger.warning("Vector store not available for search")
        return []
    
    try:
        # Perform similarity search
        results = vector_store.similarity_search_with_score(query, k=k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "score": float(score),
                "metadata": doc.metadata
            })
        
        logger.info(f"Found {len(formatted_results)} similar documents for query")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []

def get_vector_store_status() -> Dict[str, Any]:
    """Get status information about the vector store"""
    status = {
        "exists": os.path.exists(VECTOR_STORE_PATH),
        "path": VECTOR_STORE_PATH,
        "embedding_model": EMBEDDING_MODEL,
        "device": DEVICE
    }
    
    if status["exists"]:
        try:
            vector_store = load_vector_store()
            if vector_store:
                status["loaded"] = True
                status["index_size"] = vector_store.index.ntotal if hasattr(vector_store.index, 'ntotal') else "unknown"
            else:
                status["loaded"] = False
        except Exception as e:
            status["loaded"] = False
            status["error"] = str(e)
    else:
        status["loaded"] = False
    
    return status

def cli_initialize():
    """CLI function to initialize vector store"""
    print("Initializing Vector Store for Medical RAG...")
    print(f"PDF Directory: {PDF_DATA_PATH}")
    print(f"Vector Store Path: {VECTOR_STORE_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Device: {DEVICE}")
    
    try:
        # Check if PDFs exist
        if not os.path.exists(PDF_DATA_PATH):
            print(f"Error: PDF directory {PDF_DATA_PATH} not found")
            print("Please ensure you have medical PDF documents in the data/pdfs directory")
            return
        
        # Build vector store
        vector_store = build_vector_store()
        
        # Test the vector store
        test_results = search_similar_documents("fever symptoms treatment", k=2)
        print(f"\nTest search completed. Found {len(test_results)} results.")
        
        print("\n✅ Vector store initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python run_server.py")
        print("2. Test RAG functionality with medical queries")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Please check the error details and try again.")

if __name__ == "__main__":
    cli_initialize()
