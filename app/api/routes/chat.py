"""
Chat API routes
Handles advanced chat sessions with medical AI capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from ...services import chat_service, ai_service, medical_knowledge_service, health_monitoring_service
from ...services.chat_service import ChatService
from ...schemas import ChatRequest, ChatResponse, ChatHistory, ChatMessage
from ...models import User
from .auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
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

manager = ConnectionManager()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a chat message and get advanced AI response with medical intelligence"""
    try:
        # Create session if not provided
        if not request.session_id:
            session = await chat_service.create_session(
                user_id=str(current_user.id),
                title="New Chat"
            )
            session_id = str(session.id)
        else:
            session_id = request.session_id
        
        # Get user context for personalized responses
        user_context = {
            "user_id": str(current_user.id),
            "demographics": {
                "age": getattr(current_user, 'age', None),
                "gender": getattr(current_user, 'gender', None)
            },
            "medical_history": getattr(current_user, 'medical_history', None)
        }
        
        # Use intelligent response routing for advanced medical analysis
        result = await ChatService.intelligent_response_routing(
            message=request.message,
            session_id=session_id,
            user_context=user_context
        )
        
        # Handle different response types
        if result.get("response_type") == "emergency_guidance":
            return ChatResponse(
                message=result["message"],
                session_id=session_id,
                timestamp=datetime.utcnow(),
                sources=[],
                tokens_used=0,
                response_type="emergency",
                priority=result["priority"],
                follow_up_suggestions=result.get("follow_up", [])
            )
        
        elif result.get("response_type") == "differential_diagnosis":
            # Store user message and AI response
            await chat_service.add_message(session_id, request.message, "user", str(current_user.id))
            
            diagnosis_summary = f"""
Based on your symptoms, here are the potential conditions to consider:

**Most Likely Conditions:**
{chr(10).join(['• ' + cond['condition'] + f' (Probability: {cond["probability"]})' for cond in result["analysis"].get("differential_diagnoses", [])[:3]])}

**Recommended Actions:**
{chr(10).join(['• ' + action for action in result["analysis"].get("recommendations", [])])}

**When to Seek Care:**
{chr(10).join(['• ' + warning for warning in result["analysis"].get("red_flag_warnings", [])])}
            """
            
            ai_message = await chat_service.add_message(session_id, diagnosis_summary, "assistant", tokens_used=150)
            
            return ChatResponse(
                message=diagnosis_summary,
                session_id=session_id,
                timestamp=ai_message.timestamp,
                sources=result["analysis"].get("sources", []),
                tokens_used=150,
                response_type="differential_diagnosis",
                analysis=result["analysis"],
                follow_up_suggestions=result.get("follow_up", [])
            )
        
        elif result.get("response_type") == "medication_analysis":
            await chat_service.add_message(session_id, request.message, "user", str(current_user.id))
            
            med_summary = f"""
**Medication Analysis:**

**Interactions Found:** {len(result["analysis"].get("interactions", []))}
{chr(10).join(['⚠️ ' + interaction['description'] for interaction in result["analysis"].get("interactions", [])])}

**Side Effects to Monitor:**
{chr(10).join(['• ' + effect for effect in result["analysis"].get("side_effects_to_monitor", [])])}

**Recommendations:**
{chr(10).join(['• ' + rec for rec in result["analysis"].get("recommendations", [])])}
            """
            
            ai_message = await chat_service.add_message(session_id, med_summary, "assistant", tokens_used=120)
            
            return ChatResponse(
                message=med_summary,
                session_id=session_id,
                timestamp=ai_message.timestamp,
                sources=[],
                tokens_used=120,
                response_type="medication_analysis",
                analysis=result["analysis"],
                follow_up_suggestions=result.get("follow_up", [])
            )
        
        else:
            # Standard contextual response
            standard_result = await chat_service.process_user_message(
                session_id=session_id,
                user_message=request.message,
                user_id=str(current_user.id),
                include_sources=request.include_sources,
                temperature=request.temperature
            )
            
            if "error" in standard_result:
                raise HTTPException(status_code=500, detail=standard_result["error"])
            
            ai_message = standard_result["ai_message"]
            
            return ChatResponse(
                message=ai_message.content,
                session_id=session_id,
                timestamp=ai_message.timestamp,
                sources=standard_result.get("sources", []),
                tokens_used=ai_message.tokens_used,
                response_type="contextual_response",
                follow_up_suggestions=result.get("follow_up", [])
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_chat_sessions(
    limit: int = 20,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get user's chat sessions"""
    try:
        sessions = await chat_service.get_user_sessions(
            user_id=str(current_user.id),
            limit=limit,
            skip=skip
        )
        
        return {
            "sessions": [
                {
                    "id": str(session.id),
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                    "message_count": session.message_count
                }
                for session in sessions
            ],
            "total": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/history", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get chat history for a session"""
    try:
        history = await chat_service.get_chat_history(session_id, format_for_api=True)
        
        if "error" in history:
            raise HTTPException(status_code=404, detail=history["error"])
        
        return ChatHistory(
            messages=[
                ChatMessage(**msg) for msg in history["messages"]
            ],
            total_messages=history["total_messages"],
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    current_user: User = Depends(get_current_user)
):
    """Update chat session title"""
    try:
        success = await chat_service.update_session_title(session_id, title)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Title updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    try:
        success = await chat_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analysis")
async def get_conversation_analysis(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get advanced conversation analysis with medical insights"""
    try:
        analysis = await ChatService.analyze_conversation_context(session_id)
        
        return {
            "session_id": session_id,
            "analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/differential-diagnosis")
async def get_differential_diagnosis(
    symptoms: List[str],
    patient_history: Optional[Dict[str, Any]] = None,
    demographics: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """Get differential diagnosis for symptoms"""
    try:
        if not ai_service.is_initialized():
            await ai_service.initialize()
        
        result = await ai_service.differential_diagnosis(
            symptoms=symptoms,
            patient_history=patient_history,
            demographics=demographics
        )
        
        return {
            "differential_diagnoses": result.get("differential_diagnoses", []),
            "recommendations": result.get("recommendations", []),
            "red_flag_warnings": result.get("red_flag_warnings", []),
            "follow_up_needed": result.get("follow_up_needed", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medication-analysis")
async def analyze_medications(
    medications: List[Dict[str, Any]],
    patient_profile: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """Analyze medications for interactions and effects"""
    try:
        if not ai_service.is_initialized():
            await ai_service.initialize()
        
        result = await ai_service.medication_analysis(
            medications=medications,
            patient_profile=patient_profile
        )
        
        return {
            "interactions": result.get("interactions", []),
            "side_effects_to_monitor": result.get("side_effects_to_monitor", []),
            "dosage_considerations": result.get("dosage_considerations", []),
            "recommendations": result.get("recommendations", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document-analysis")
async def analyze_medical_document(
    document_text: str,
    document_type: str = "lab_result",
    current_user: User = Depends(get_current_user)
):
    """Analyze medical documents (lab results, reports, etc.)"""
    try:
        if not ai_service.is_initialized():
            await ai_service.initialize()
        
        result = await ai_service.medical_document_analysis(
            document_text=document_text,
            document_type=document_type
        )
        
        return {
            "key_findings": result.get("key_findings", []),
            "abnormal_values": result.get("abnormal_values", []),
            "clinical_significance": result.get("clinical_significance", ""),
            "recommendations": result.get("recommendations", []),
            "follow_up_needed": result.get("follow_up_needed", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drug-information/{drug_name}")
async def get_drug_information(
    drug_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive drug information"""
    try:
        if not medical_knowledge_service.is_initialized():
            await medical_knowledge_service.initialize()
        
        drug_info = await medical_knowledge_service.get_drug_information(drug_name)
        
        if not drug_info:
            raise HTTPException(status_code=404, detail="Drug information not found")
        
        return drug_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drug-interactions")
async def check_drug_interactions(
    medications: List[str],
    current_user: User = Depends(get_current_user)
):
    """Check for drug-drug interactions"""
    try:
        if not medical_knowledge_service.is_initialized():
            await medical_knowledge_service.initialize()
        
        interactions = await medical_knowledge_service.check_drug_interactions(medications)
        
        return interactions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symptom-analysis")
async def analyze_symptoms(
    symptoms: List[str],
    current_user: User = Depends(get_current_user)
):
    """Analyze symptom patterns for clinical insights"""
    try:
        if not medical_knowledge_service.is_initialized():
            await medical_knowledge_service.initialize()
        
        analysis = await medical_knowledge_service.analyze_symptom_pattern(symptoms)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clinical-guidelines/{condition}")
async def get_clinical_guidelines(
    condition: str,
    current_user: User = Depends(get_current_user)
):
    """Get clinical practice guidelines for a condition"""
    try:
        if not medical_knowledge_service.is_initialized():
            await medical_knowledge_service.initialize()
        
        guidelines = await medical_knowledge_service.get_clinical_guideline(condition)
        
        if not guidelines:
            raise HTTPException(status_code=404, detail="Clinical guidelines not found")
        
        return guidelines
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-protocols")
async def get_emergency_protocols(
    symptoms: List[str],
    severity: str = "unknown",
    current_user: User = Depends(get_current_user)
):
    """Get emergency protocols and triage guidance"""
    try:
        if not medical_knowledge_service.is_initialized():
            await medical_knowledge_service.initialize()
        
        protocols = await medical_knowledge_service.emergency_protocols(symptoms, severity)
        
        return protocols
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Enhanced WebSocket endpoint for real-time medical chat"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                # Process chat message with advanced routing
                user_message = message_data.get("message", "")
                session_id = message_data.get("session_id")
                
                if not session_id:
                    # Create new session
                    session = await chat_service.create_session(
                        user_id=user_id,
                        title="WebSocket Chat"
                    )
                    session_id = str(session.id)
                
                # Use intelligent response routing
                result = await ChatService.intelligent_response_routing(
                    message=user_message,
                    session_id=session_id,
                    user_context={"user_id": user_id}
                )
                
                # Send appropriate response based on type
                if result.get("response_type") == "emergency_guidance":
                    response = {
                        "type": "emergency",
                        "session_id": session_id,
                        "message": result["message"],
                        "priority": result["priority"],
                        "follow_up": result.get("follow_up", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    response = {
                        "type": "response",
                        "session_id": session_id,
                        "message": result.get("response", result.get("message", "")),
                        "response_type": result.get("response_type", "standard"),
                        "follow_up": result.get("follow_up", []),
                        "analysis": result.get("analysis"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                await manager.send_personal_message(json.dumps(response), user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)

__all__ = ["router"]