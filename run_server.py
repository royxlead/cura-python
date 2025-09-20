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

# Import new modular components
try:
    from app.core.database import DatabaseManager
    from app.services.ai_service import ai_service
    from app.services.chat_service import chat_service
    from app.services.medical_knowledge_service import medical_knowledge_service
    from app.services.health_monitoring_service import health_monitoring_service
    from app.services.performance_service import performance_service
    DATABASE_AVAILABLE = True
    SERVICES_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    SERVICES_AVAILABLE = False
    logging.warning(f"Services not available: {e}")

init()  # Initialize colorama

# Enhanced FastAPI app with comprehensive features
app = FastAPI(
    title="Cura Medical AI Assistant",
    description="AI-powered medical assistant with advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Database and services lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and services on startup"""
    print(f"{Fore.CYAN}Initializing Cura Medical AI Services...{Style.RESET_ALL}")
    
    # Initialize database
    if DATABASE_AVAILABLE:
        try:
            db_manager = DatabaseManager()
            await db_manager.connect()
            print(f"{Fore.GREEN}✓ MongoDB connection established{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Database connection failed: {e}{Style.RESET_ALL}")
    
    # Initialize advanced services
    if SERVICES_AVAILABLE:
        try:
            # Initialize AI service
            await ai_service.initialize()
            print(f"{Fore.GREEN}✓ AI Service initialized{Style.RESET_ALL}")
            
            # Initialize medical knowledge service
            await medical_knowledge_service.initialize()
            print(f"{Fore.GREEN}✓ Medical Knowledge Service initialized{Style.RESET_ALL}")
            
            # Initialize health monitoring service
            await health_monitoring_service.initialize()
            print(f"{Fore.GREEN}✓ Health Monitoring Service initialized{Style.RESET_ALL}")
            
            # Initialize performance optimization service
            await performance_service.initialize()
            print(f"{Fore.GREEN}✓ Performance Optimization Service initialized{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}🚀 All services initialized successfully!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Service initialization failed: {e}{Style.RESET_ALL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections and services on shutdown"""
    print(f"{Fore.YELLOW}Shutting down Cura Medical AI Services...{Style.RESET_ALL}")
    
    if DATABASE_AVAILABLE:
        try:
            db_manager = DatabaseManager()
            await db_manager.disconnect()
            print(f"{Fore.YELLOW}✓ MongoDB connection closed{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Database disconnect failed: {e}{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}👋 Cura Medical AI shutdown complete{Style.RESET_ALL}")

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000", 
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],  # Specific origins when using credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Include enhanced modular API routes
try:
    print(f"{Fore.CYAN}Loading API routes...{Style.RESET_ALL}")
    
    from app.api.routes.chat import router as chat_router
    print(f"{Fore.GREEN}✓ Chat router loaded{Style.RESET_ALL}")
    
    from app.api.routes.user_auth import router as user_auth_router
    print(f"{Fore.GREEN}✓ User auth router loaded{Style.RESET_ALL}")
    
    from app.api.routes.health import router as health_router
    print(f"{Fore.GREEN}✓ Health router loaded{Style.RESET_ALL}")
    
    # from app.api.routes.test_auth import router as test_auth_router
    # print(f"{Fore.GREEN}✓ Test auth router loaded{Style.RESET_ALL}")
    
    app.include_router(chat_router, prefix="/api")
    print(f"{Fore.GREEN}✓ Chat router included{Style.RESET_ALL}")
    
    app.include_router(user_auth_router, prefix="/api")
    print(f"{Fore.GREEN}✓ User auth router included{Style.RESET_ALL}")
    
    app.include_router(health_router, prefix="/api")
    print(f"{Fore.GREEN}✓ Health router included{Style.RESET_ALL}")
    
    # app.include_router(test_auth_router, prefix="/api")
    # print(f"{Fore.GREEN}✓ Test auth router included{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}✓ Enhanced API routes enabled{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠ API routes not available: {e}{Style.RESET_ALL}")
    import traceback
    traceback.print_exc()

# Simple diagnostic route to test if routing works
@app.get("/api/diagnostic")
async def diagnostic():
    """Diagnostic endpoint to test routing"""
    return {"message": "Diagnostic endpoint working", "timestamp": "2025-09-20"}

@app.post("/api/diagnostic/test")
async def diagnostic_test():
    """Diagnostic POST endpoint"""
    return {"message": "Diagnostic POST working"}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)

manager = ConnectionManager()

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                # Process the chat message (integrate with existing chat logic)
                user_message = message_data.get("message", "")
                
                # Echo back for now - integrate with RAG pipeline
                response = {
                    "type": "response",
                    "message": f"Received: {user_message}",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
                await manager.send_personal_message(json.dumps(response), user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected from WebSocket")

# Enhanced root endpoint - serve the frontend
@app.get("/")
async def root():
    """Serve the main application"""
    try:
        return FileResponse("frontend/index.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Cura Medical AI</title></head>
            <body>
                <h1>Cura Medical AI Assistant</h1>
                <p>Frontend not found. Please check the frontend directory.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
                <p>API Status: <a href="/api/status">/api/status</a></p>
            </body>
        </html>
        """)

# Enhanced API status endpoint
@app.get("/api/status")
async def api_status():
    service_status = {}
    
    if SERVICES_AVAILABLE:
        try:
            service_status = {
                "ai_service": ai_service.is_initialized(),
                "medical_knowledge": medical_knowledge_service.is_initialized(),
                "health_monitoring": health_monitoring_service.is_initialized(),
                "performance_optimization": performance_service.is_initialized()
            }
        except:
            service_status = {"services": "unavailable"}
    
    return {
        "status": "healthy",
        "message": "Cura Medical AI Assistant API is running",
        "version": "3.0.0",
        "features": {
            "advanced_chat": True,
            "differential_diagnosis": True,
            "medication_analysis": True,
            "health_monitoring": True,
            "medical_knowledge_base": True,
            "performance_optimization": True,
            "authentication": True,
            "websocket_support": True,
            "database": DATABASE_AVAILABLE
        },
        "services": service_status,
        "timestamp": datetime.now().isoformat()
    }

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    # Check database health
    db_status = "operational" if DATABASE_AVAILABLE else "disabled"
    
    # Check service health
    service_health = {}
    if SERVICES_AVAILABLE:
        try:
            service_health = {
                "ai_service": "operational" if ai_service.is_initialized() else "initializing",
                "medical_knowledge": "operational" if medical_knowledge_service.is_initialized() else "initializing",
                "health_monitoring": "operational" if health_monitoring_service.is_initialized() else "initializing",
                "performance_optimization": "operational" if performance_service.is_initialized() else "initializing"
            }
        except Exception as e:
            service_health = {"error": str(e)}
    
    # Get performance metrics if available
    performance_data = {}
    if SERVICES_AVAILABLE and performance_service.is_initialized():
        try:
            performance_data = performance_service.get_system_performance()
        except:
            performance_data = {"status": "unavailable"}
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "websocket": "operational", 
            "database": db_status,
            "authentication": "operational",
            **service_health
        },
        "performance": performance_data
    }

# Serve consolidated frontend
@app.get("/app")
async def serve_app():
    try:
        return FileResponse("frontend/index.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Cura Medical AI</title></head>
            <body>
                <h1>Cura Medical AI Assistant</h1>
                <p>Frontend not found.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

# PWA Manifest
@app.get("/manifest.json")
async def get_manifest():
    try:
        return FileResponse("manifest.json")
    except FileNotFoundError:
        return {
            "name": "Cura Medical AI Assistant",
            "short_name": "Cura AI",
            "start_url": "/",
            "display": "standalone",
            "theme_color": "#2563eb",
            "background_color": "#ffffff"
        }

# Frontend static files
@app.get("/style.css")
async def get_styles():
    try:
        return FileResponse("frontend/style.css")
    except FileNotFoundError:
        return HTMLResponse("/* Styles not found */", media_type="text/css")

@app.get("/auth.js")
async def get_auth_script():
    try:
        return FileResponse("frontend/auth.js")
    except FileNotFoundError:
        return HTMLResponse("// Auth script not available", media_type="application/javascript")

@app.get("/scripts.js")
async def get_scripts():
    try:
        return FileResponse("frontend/scripts.js")
    except FileNotFoundError:
        return HTMLResponse("// Scripts not available", media_type="application/javascript")

# Service Worker
@app.get("/sw.js")
async def get_service_worker():
    try:
        return FileResponse("frontend/sw.js")
    except FileNotFoundError:
        return HTMLResponse("// Service worker not available", media_type="application/javascript")

# Performance monitoring endpoint
@app.get("/api/performance")
async def get_performance_metrics():
    """Get detailed performance metrics for system monitoring"""
    if not SERVICES_AVAILABLE:
        return {"error": "Performance monitoring not available"}
    
    try:
        return performance_service.get_system_performance()
    except Exception as e:
        return {"error": f"Failed to get performance metrics: {str(e)}"}

# Medical knowledge search endpoint
@app.get("/api/medical/search")
async def search_medical_knowledge(
    query: str,
    category: str = "general"
):
    """Search medical knowledge base"""
    if not SERVICES_AVAILABLE:
        return {"error": "Medical knowledge service not available"}
    
    try:
        # This would integrate with the medical knowledge service
        return {
            "query": query,
            "category": category,
            "results": [],
            "message": "Medical knowledge search endpoint - implementation pending"
        }
    except Exception as e:
        return {"error": str(e)}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Global exception: {exc}")
    return HTTPException(
        status_code=500,
        detail=str(exc)
    )

if __name__ == "__main__":
    print(f"\n{Fore.CYAN}Starting Cura Server...{Style.RESET_ALL}")
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=True)
