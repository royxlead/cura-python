"""Enhanced AI Service with RAG Integration for Cura Medical Assistant"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# RAG imports
try:
    from chains.rag_pipeline import rag_pipeline
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    logging.warning(f"RAG pipeline not available: {e}")

# Fallback imports
import google.generativeai as genai

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """Enhanced AI service with RAG integration and intelligent fallback"""
    
    def __init__(self):
        self.rag_pipeline = None
        self.fallback_model = None
        self.is_initialized = False
        self.rag_enabled = False
        
    async def initialize(self):
        """Initialize the AI service with RAG and fallback"""
        try:
            # Initialize RAG pipeline if available
            if RAG_AVAILABLE:
                self.rag_pipeline = rag_pipeline
                rag_success = self.rag_pipeline.initialize()
                if rag_success:
                    self.rag_enabled = True
                    logger.info("RAG pipeline initialized successfully")
                else:
                    logger.warning("RAG pipeline initialization failed, using fallback")
            
            # Initialize fallback Gemini model
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Google API key not found in environment variables")
            
            genai.configure(api_key=api_key)
            model_name = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
            self.fallback_model = genai.GenerativeModel(model_name)
            
            self.is_initialized = True
            logger.info(f"AI Service initialized - RAG: {self.rag_enabled}, Fallback: Available")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.is_initialized = False
            
    async def generate_response(self, message: str, use_rag: bool = True, context: str = "") -> Dict[str, Any]:
        """Generate AI response with RAG or fallback"""
        if not self.is_initialized:
            return {
                "message": "AI service is not available. Please try again later.",
                "error": True,
                "response_type": "error"
            }
        
        try:
            # Try RAG first if enabled and requested
            if use_rag and self.rag_enabled and self.rag_pipeline:
                rag_response = self.rag_pipeline.get_rag_response(message, use_rag=True)
                
                if rag_response.get("response_type") != "error":
                    return {
                        "message": rag_response["answer"],
                        "timestamp": rag_response["timestamp"],
                        "response_type": rag_response["response_type"],
                        "source_documents": rag_response.get("source_documents", []),
                        "error": False
                    }
                else:
                    logger.warning("RAG response failed, trying fallback")
            
            # Fallback to standard Gemini
            return await self._generate_fallback_response(message, context)
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return await self._generate_fallback_response(message, context)
    
    async def _generate_fallback_response(self, message: str, context: str = "") -> Dict[str, Any]:
        """Generate fallback response using standard Gemini"""
        try:
            # Enhanced medical prompt for fallback
            system_prompt = """You are CURA, a helpful and knowledgeable medical AI assistant.

Key guidelines:
- Provide accurate, helpful medical information
- Always recommend consulting healthcare professionals for serious concerns
- Be empathetic and supportive
- Give clear, easy-to-understand explanations
- Include relevant disclaimers when appropriate
- If asked about emergencies, always recommend calling emergency services

IMPORTANT DISCLAIMERS:
- You are an AI assistant providing general medical information only
- This is not a substitute for professional medical advice, diagnosis, or treatment
- Always consult qualified healthcare professionals for medical concerns
- In medical emergencies, call emergency services immediately

Respond in a caring, professional manner while being informative and helpful."""
            
            full_prompt = f"{system_prompt}\\n\\nUser question: {message}"
            if context:
                full_prompt += f"\\n\\nPrevious context: {context}"
            
            response = self.fallback_model.generate_content(full_prompt)
            
            return {
                "message": response.text,
                "timestamp": datetime.now().isoformat(),
                "response_type": "standard",
                "source_documents": [],
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Fallback response failed: {e}")
            return {
                "message": "I'm experiencing technical difficulties. Please try again in a moment.",
                "timestamp": datetime.now().isoformat(),
                "response_type": "error",
                "source_documents": [],
                "error": True
            }
    
    async def search_medical_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search medical documents using RAG"""
        if not self.rag_enabled or not self.rag_pipeline:
            return []
        
        try:
            return self.rag_pipeline.search_documents(query, k)
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of AI service"""
        status = {
            "initialized": self.is_initialized,
            "rag_available": RAG_AVAILABLE,
            "rag_enabled": self.rag_enabled,
            "fallback_available": self.fallback_model is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add RAG pipeline status if available
        if self.rag_enabled and self.rag_pipeline:
            rag_status = self.rag_pipeline.get_status()
            status["rag_details"] = rag_status
        
        return status

# Global instance
ai_service = EnhancedAIService()

__all__ = ["ai_service", "EnhancedAIService"]