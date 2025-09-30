"""
Simple AI Service for Cura Medical Assistant
Uses Google Gemini API for medical responses without database dependencies
"""

import os
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SimpleAIService:
    """Simple AI service using Google Gemini"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the AI service"""
        try:
            # Get API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Get model name from environment or use default
            model_name = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
            
            # Initialize the model
            self.model = genai.GenerativeModel(model_name)
            
            self.is_initialized = True
            logger.info("AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.is_initialized = False
            
    async def generate_response(self, message: str, context: str = "") -> Dict[str, Any]:
        """Generate AI response for medical queries"""
        if not self.is_initialized:
            return {
                "message": "AI service is not available. Please try again later.",
                "error": True
            }
        
        try:
            # Create medical context prompt
            system_prompt = """You are CURA, a helpful and knowledgeable medical AI assistant. 

Key guidelines:
- Provide accurate, helpful medical information
- Always recommend consulting healthcare professionals for serious concerns
- Be empathetic and supportive
- Give clear, easy-to-understand explanations
- Include relevant disclaimers when appropriate
- If asked about emergencies, always recommend calling emergency services

IMPORTANT RESPONSE FORMAT:
- Provide ONLY the response content, no chat interface elements
- Do not include timestamps, sender names, or chat formatting
- Do not include "Cura AI:" or similar prefixes
- Just provide the direct medical information response

IMPORTANT DISCLAIMERS:
- You are an AI assistant providing general medical information only
- This is not a substitute for professional medical advice, diagnosis, or treatment
- Always consult qualified healthcare professionals for medical concerns
- In medical emergencies, call emergency services immediately

Respond in a caring, professional manner while being informative and helpful."""

            # Combine system prompt with user message
            full_prompt = f"{system_prompt}\n\nUser question: {message}"
            
            if context:
                full_prompt += f"\n\nPrevious context: {context}"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return {
                "message": response.text,
                "timestamp": datetime.now().isoformat(),
                "response_type": "standard",
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "message": "I'm experiencing some technical difficulties. Please try again in a moment.",
                "timestamp": datetime.now().isoformat(),
                "response_type": "error",
                "error": True
            }

# Global instance
ai_service = SimpleAIService()

__all__ = ["ai_service", "SimpleAIService"]