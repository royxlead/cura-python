"""Medical RAG Pipeline for Cura AI Assistant"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# LangChain imports
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Local imports
from utils.vector_store import load_vector_store, search_similar_documents
from utils.prompts import MEDICAL_RAG_PROMPT

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalRAGPipeline:
    """Medical RAG Pipeline using Google Gemini and FAISS"""
    
    def __init__(self):
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the RAG pipeline"""
        try:
            # Initialize LLM
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("Google API key not found in environment")
                return False
            
            model_name = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
            max_tokens = int(os.getenv('LLM_MAX_TOKENS', '100000'))
            temperature = float(os.getenv('LLM_TEMPERATURE', '0.1'))
            
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                convert_system_message_to_human=True
            )
            
            # Load vector store
            self.vector_store = load_vector_store()
            if not self.vector_store:
                logger.warning("Vector store not available - RAG will use fallback mode")
                self.is_initialized = True  # Still initialize for fallback
                return True
            
            # Create retrieval QA chain
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 8}
            )
            
            # Create custom prompt
            prompt = PromptTemplate(
                template=MEDICAL_RAG_PROMPT,
                input_variables=["context", "question"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            
            self.is_initialized = True
            logger.info("Medical RAG pipeline initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            self.is_initialized = False
            return False
    
    def get_rag_response(self, query: str, use_rag: bool = True) -> Dict[str, Any]:
        """Get response using RAG or fallback to standard LLM"""
        if not self.is_initialized:
            return {
                "answer": "RAG system is not available. Please try again later.",
                "source_documents": [],
                "response_type": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Try RAG first if available and requested
            if use_rag and self.qa_chain and self.vector_store:
                return self._get_rag_answer(query)
            else:
                # Fallback to standard LLM
                return self._get_standard_answer(query)
                
        except Exception as e:
            logger.error(f"Error in RAG response: {e}")
            # Try fallback
            try:
                return self._get_standard_answer(query)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return {
                    "answer": "I'm experiencing technical difficulties. Please try again.",
                    "source_documents": [],
                    "response_type": "error",
                    "timestamp": datetime.now().isoformat()
                }
    
    def _get_rag_answer(self, query: str) -> Dict[str, Any]:
        """Get answer using RAG pipeline"""
        result = self.qa_chain({"query": query})
        
        # Format source documents
        source_docs = []
        for doc in result.get("source_documents", []):
            source_docs.append({
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "metadata": doc.metadata
            })
        
        return {
            "answer": result["result"],
            "source_documents": source_docs,
            "response_type": "rag",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_standard_answer(self, query: str) -> Dict[str, Any]:
        """Get answer using standard LLM without RAG"""
        # Enhanced medical prompt for standard mode
        medical_prompt = f"""
You are CURA, a knowledgeable medical AI assistant. Provide accurate, helpful medical information while always recommending consultation with healthcare professionals for serious concerns.

User question: {query}

Guidelines:
- Provide clear, evidence-based medical information
- Always include appropriate disclaimers
- Recommend professional medical consultation when appropriate
- Be empathetic and supportive
- If this is an emergency, direct to emergency services

Response:"""
        
        response = self.llm.invoke(medical_prompt)
        
        return {
            "answer": response.content,
            "source_documents": [],
            "response_type": "standard",
            "timestamp": datetime.now().isoformat()
        }
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents directly without generating response"""
        return search_similar_documents(query, k)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of RAG pipeline components"""
        return {
            "initialized": self.is_initialized,
            "vector_store_available": self.vector_store is not None,
            "llm_available": self.llm is not None,
            "qa_chain_available": self.qa_chain is not None,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
rag_pipeline = MedicalRAGPipeline()

# Legacy function for backward compatibility
def setup_rag(vector_store, llm):
    """Legacy function - use MedicalRAGPipeline class instead"""
    logger.info("Setting up RAG pipeline...")
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 5})
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
