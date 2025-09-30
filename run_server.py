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

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
from colorama import init, Fore, Style
import json
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import simple AI service
try:
    from app.services.simple_ai_service import ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_SERVICE_AVAILABLE = False
    logging.warning(f"AI service not available: {e}")

# Initialize colorama
init()

# Enhanced FastAPI app
app = FastAPI(
    title="Cura Medical AI Assistant",
    description="AI-powered medical assistant",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize AI service on startup
@app.on_event("startup")
async def startup_event():
    """Initialize AI service on startup"""
    if AI_SERVICE_AVAILABLE:
        await ai_service.initialize()
        print(f"{Fore.GREEN}✓ AI Service initialized{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ AI Service not available{Style.RESET_ALL}")

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

# AI-powered chat endpoint
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """AI-powered chat endpoint using Gemini"""
    try:
        message = request.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use AI service if available
        if AI_SERVICE_AVAILABLE and ai_service.is_initialized:
            response_data = await ai_service.generate_response(message)
            
            return {
                "message": response_data.get("message", "I'm sorry, I couldn't generate a response."),
                "timestamp": response_data.get("timestamp", datetime.now().isoformat()),
                "session_id": "guest_session",
                "response_type": response_data.get("response_type", "standard"),
                "sources": [],
                "follow_up_suggestions": []
            }
        else:
            # Fallback to simple responses
            response = generate_simple_response(message)
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "session_id": "guest_session",
                "response_type": "standard"
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

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "chat": "operational"
        }
    }

# Serve the main page
@app.get("/")
async def serve_index():
    """Serve the main application page"""
    return FileResponse("frontend/index.html")

# Simple WebSocket for real-time chat (optional)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Generate response
            response = generate_simple_response(message_data.get("message", ""))
            
            # Send response back
            response_data = {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "type": "ai_response"
            }
            
            await manager.send_message(json.dumps(response_data), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print(f"{Fore.GREEN}🚀 Starting Cura Medical AI Assistant...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📱 Frontend: http://localhost:8000{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📚 API Docs: http://localhost:8000/docs{Style.RESET_ALL}")
    
    uvicorn.run(
        "run_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )