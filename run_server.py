import os
import sys

# Suppress Google ALTS warnings before any other imports
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['GRPC_TRACE'] = ''

# Also suppress Python warnings if needed
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google")

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from colorama import init, Fore, Style
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.services.simple_ai_service import ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_SERVICE_AVAILABLE = False
    logging.warning(f"AI service not available: {e}")

init()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{Fore.GREEN}🚀 Starting Cura Medical AI Assistant...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📱 Frontend: http://localhost:8000{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📚 API Docs: http://localhost:8000/docs{Style.RESET_ALL}")
    
    if AI_SERVICE_AVAILABLE:
        await ai_service.initialize()
        if ai_service.is_initialized:
            print(f"{Fore.GREEN}✓ AI Service initialized{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ AI Service initialization failed{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ AI Service not available{Style.RESET_ALL}")
    
    yield
    print(f"{Fore.YELLOW}🛑 Shutting down Cura Medical AI Assistant...{Style.RESET_ALL}")

app = FastAPI(
    title="Cura Medical AI Assistant",
    description="RAG-powered medical assistant",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """RAG-enabled chat endpoint"""
    try:
        message = request.get("message", "")
        use_rag = request.get("use_rag", True)
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if AI_SERVICE_AVAILABLE and ai_service.is_initialized:
            response_data = await ai_service.generate_response(message, use_rag=use_rag)
            
            return {
                "message": response_data.get("message", "I'm sorry, I couldn't generate a response."),
                "timestamp": response_data.get("timestamp", datetime.now().isoformat()),
                "session_id": "guest_session",
                "response_type": response_data.get("response_type", "standard"),
                "sources": response_data.get("source_documents", []),
                "follow_up_suggestions": [],
                "rag_enabled": use_rag
            }
        else:
            response = generate_simple_response(message)
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "session_id": "guest_session",
                "response_type": "fallback",
                "sources": [],
                "rag_enabled": False
            }
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_simple_response(message: str) -> str:
    """Generate a simple medical AI response"""
    message_lower = message.lower()
    
    # Basic keyword-based responses
    if any(word in message_lower for word in ["headache", "pain", "hurt"]):
        return "I understand you're experiencing pain. For headaches, consider rest, hydration, and over-the-counter pain relievers if appropriate. If pain persists or worsens, please consult a healthcare professional."
    
    elif any(word in message_lower for word in ["fever", "temperature", "hot"]):
        return "Fever can be a sign of infection. Stay hydrated, rest, and monitor your temperature. If fever is high (over 101°F/38.3°C) or persists, please seek medical attention."
    
    elif any(word in message_lower for word in ["cold", "cough", "sneezing"]):
        return "Cold symptoms are common. Rest, fluids, and time usually help. If symptoms worsen or last more than 10 days, consider seeing a healthcare provider."
    
    elif any(word in message_lower for word in ["stomach", "nausea", "vomit"]):
        return "Stomach issues can have various causes. Try clear fluids, bland foods, and rest. If symptoms are severe or persistent, please consult a healthcare professional."
    
    elif any(word in message_lower for word in ["emergency", "urgent", "serious"]):
        return "If this is a medical emergency, please call emergency services immediately (911 in the US). I'm an AI assistant and cannot provide emergency medical care."
    
    else:
        return "Thank you for your message. While I can provide general health information, I always recommend consulting with a qualified healthcare professional for personalized medical advice and treatment."

@app.post("/api/search")
async def search_documents(request: dict):
    """Search medical documents using RAG"""
    try:
        query = request.get("query", "").strip()
        k = request.get("k", 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        if AI_SERVICE_AVAILABLE and hasattr(ai_service, 'search_medical_documents'):
            results = await ai_service.search_medical_documents(query, k)
            return {
                "query": query,
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "query": query,
                "results": [],
                "count": 0,
                "message": "Document search not available",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def service_status():
    """Get comprehensive service status including RAG"""
    try:
        base_status = {
            "service": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "ai_service_available": AI_SERVICE_AVAILABLE
        }
        
        if AI_SERVICE_AVAILABLE and hasattr(ai_service, 'get_status'):
            ai_status = ai_service.get_status()
            base_status["ai_details"] = ai_status
        
        return base_status
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return {
            "service": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "chat": "operational",
            "rag": "available" if AI_SERVICE_AVAILABLE else "unavailable"
        }
    }

@app.get("/")
async def serve_index():
    """Serve the main application page"""
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "run_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )