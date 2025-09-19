"""
Advanced Chat Service with Medical Context Management
Handles intelligent conversation management, medical history integration,
context-aware responses, and intelligent follow-up questions
"""

import logging
import json
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from collections import defaultdict

from ..models import ChatSession, Message, MessageRole, User
from ..core.database import get_database
from .ai_service import ai_service

logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat sessions and messages"""
    
    @staticmethod
    async def create_session(user_id: str, title: str = "New Chat") -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=ObjectId(user_id),
            title=title,
            created_at=datetime.now(timezone.utc)
        )
        await session.insert()
        return session
    
    @staticmethod
    async def get_user_sessions(
        user_id: str, 
        limit: int = 20, 
        skip: int = 0
    ) -> List[ChatSession]:
        """Get user's chat sessions"""
        return await ChatSession.find(
            ChatSession.user_id == ObjectId(user_id)
        ).sort(-ChatSession.created_at).limit(limit).skip(skip).to_list()
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        try:
            return await ChatSession.get(ObjectId(session_id))
        except Exception:
            return None
    
    @staticmethod
    async def get_session_messages(
        session_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Message]:
        """Get messages for a chat session"""
        return await Message.find(
            Message.session_id == ObjectId(session_id)
        ).sort(Message.timestamp).limit(limit).skip(skip).to_list()
    
    @staticmethod
    async def add_message(
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add message to chat session"""
        message = Message(
            session_id=ObjectId(session_id),
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        
        if metadata:
            if "sources" in metadata:
                message.sources = metadata["sources"]
            if "tokens_used" in metadata:
                message.tokens_used = metadata["tokens_used"]
            if "confidence_score" in metadata:
                message.confidence_score = metadata["confidence_score"]
            if "model_used" in metadata:
                message.model_used = metadata["model_used"]
        
        await message.insert()
        
        # Update session message count
        session = await ChatSession.get(ObjectId(session_id))
        if session:
            session.message_count += 1
            session.updated_at = datetime.now(timezone.utc)
            await session.save()
        
        return message
    
    @staticmethod
    async def process_user_message(
        session_id: str,
        user_message: str,
        user_id: str,
        include_sources: bool = True,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process user message and generate AI response"""
        try:
            # Add user message
            user_msg = await ChatService.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # Get AI response
            ai_result = await ai_service.process_chat_message(
                message=user_message,
                include_sources=include_sources,
                temperature=temperature
            )
            
            # Add AI response message
            ai_msg = await ChatService.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=ai_result["response"],
                metadata={
                    "sources": ai_result.get("sources", []),
                    "model_used": "gemini-1.5-pro",
                    "confidence_score": ai_result.get("confidence_score")
                }
            )
            
            return {
                "user_message": user_msg,
                "ai_message": ai_msg,
                "sources": ai_result.get("sources", []),
                "method": ai_result.get("method", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            
            # Add error response
            error_msg = await ChatService.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content="I apologize, but I'm experiencing technical difficulties. Please try again later."
            )
            
            return {
                "user_message": None,
                "ai_message": error_msg,
                "sources": [],
                "method": "error",
                "error": str(e)
            }
    
    @staticmethod
    async def update_session_title(session_id: str, title: str) -> bool:
        """Update chat session title"""
        try:
            session = await ChatSession.get(ObjectId(session_id))
            if session:
                session.title = title
                session.updated_at = datetime.now(timezone.utc)
                await session.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating session title: {e}")
            return False
    
    @staticmethod
    async def delete_session(session_id: str) -> bool:
        """Delete chat session and its messages"""
        try:
            # Delete all messages in the session
            await Message.find(
                Message.session_id == ObjectId(session_id)
            ).delete()
            
            # Delete the session
            session = await ChatSession.get(ObjectId(session_id))
            if session:
                await session.delete()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    @staticmethod
    async def get_chat_history(
        session_id: str,
        format_for_api: bool = True
    ) -> Dict[str, Any]:
        """Get formatted chat history"""
        try:
            session = await ChatService.get_session(session_id)
            if not session:
                return {"error": "Session not found"}
            
            messages = await ChatService.get_session_messages(session_id)
            
            if format_for_api:
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "sources": msg.sources if hasattr(msg, 'sources') else []
                    })
                
                return {
                    "session_id": session_id,
                    "title": session.title,
                    "messages": formatted_messages,
                    "total_messages": len(formatted_messages),
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None
                }
            
            return {
                "session": session,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def analyze_conversation_context(session_id: str) -> Dict[str, Any]:
        """Analyze conversation context to extract medical insights"""
        try:
            messages = await ChatService.get_session_messages(session_id)
            
            # Extract user messages for analysis
            user_messages = [msg.content for msg in messages if msg.role == MessageRole.USER]
            conversation_text = " ".join(user_messages)
            
            # Analyze for medical context
            context_analysis = {
                "symptoms_mentioned": ChatService._extract_symptoms(conversation_text),
                "medications_mentioned": ChatService._extract_medications(conversation_text),
                "urgency_indicators": ChatService._detect_urgency(conversation_text),
                "topic_evolution": ChatService._track_topic_changes(messages),
                "follow_up_needed": ChatService._suggest_follow_ups(conversation_text),
                "conversation_summary": await ChatService._generate_summary(user_messages)
            }
            
            return context_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation context: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _extract_symptoms(text: str) -> List[str]:
        """Extract mentioned symptoms from conversation"""
        symptom_patterns = [
            r'\b(?:pain|ache|hurt|sore|tender)\b',
            r'\b(?:fever|temperature|hot|chills)\b',
            r'\b(?:headache|migraine)\b',
            r'\b(?:nausea|vomiting|sick|queasy)\b',
            r'\b(?:dizzy|dizziness|lightheaded)\b',
            r'\b(?:tired|fatigue|exhausted|weak)\b',
            r'\b(?:cough|coughing)\b',
            r'\b(?:shortness of breath|breathing|breathless)\b',
            r'\b(?:rash|itchy|swelling)\b',
            r'\b(?:stomach|abdominal|belly)\b.*(?:pain|ache|hurt)\b',
            r'\b(?:chest|heart)\b.*(?:pain|pressure|tight)\b',
            r'\b(?:back|neck|shoulder)\b.*(?:pain|ache|stiff)\b'
        ]
        
        symptoms = []
        text_lower = text.lower()
        
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text_lower)
            symptoms.extend([match for match in matches if match not in symptoms])
        
        return symptoms[:10]  # Limit to top 10 symptoms
    
    @staticmethod
    def _extract_medications(text: str) -> List[str]:
        """Extract mentioned medications from conversation"""
        # Common medication patterns and names
        med_patterns = [
            r'\b(?:taking|medication|medicine|pill|tablet|drug)\s+(\w+)\b',
            r'\b(\w+(?:ine|ol|pam|cin|ril|ide|ate))\b',  # Common medication endings
            r'\b(aspirin|ibuprofen|acetaminophen|tylenol|advil|motrin)\b',
            r'\b(lisinopril|metformin|atorvastatin|amlodipine|omeprazole)\b',
            r'\b(amoxicillin|ciprofloxacin|azithromycin|doxycycline)\b'
        ]
        
        medications = []
        text_lower = text.lower()
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text_lower)
            if isinstance(matches[0] if matches else None, tuple):
                medications.extend([match[0] for match in matches])
            else:
                medications.extend(matches)
        
        # Remove duplicates and common false positives
        filtered_meds = []
        common_words = {'taking', 'medication', 'medicine', 'pill', 'tablet', 'drug'}
        
        for med in medications:
            if med not in common_words and med not in filtered_meds and len(med) > 2:
                filtered_meds.append(med)
        
        return filtered_meds[:10]  # Limit to top 10 medications
    
    @staticmethod
    def _detect_urgency(text: str) -> List[str]:
        """Detect urgency indicators in conversation"""
        urgency_patterns = [
            r'\b(?:emergency|urgent|severe|critical|immediate)\b',
            r'\b(?:can\'t breathe|trouble breathing|chest pain)\b',
            r'\b(?:bleeding|blood|hemorrhage)\b',
            r'\b(?:unconscious|fainted|passed out)\b',
            r'\b(?:sudden|acute|sharp)\b.*(?:pain|onset)\b',
            r'\b(?:worst|terrible|unbearable)\b.*(?:pain|headache)\b',
            r'\b(?:911|emergency room|hospital|ambulance)\b'
        ]
        
        urgency_indicators = []
        text_lower = text.lower()
        
        for pattern in urgency_patterns:
            if re.search(pattern, text_lower):
                urgency_indicators.append(pattern.replace('\\b', '').replace('(?:', '').replace(')', ''))
        
        return list(set(urgency_indicators))  # Remove duplicates
    
    @staticmethod
    def _track_topic_changes(messages: List[Message]) -> List[Dict[str, Any]]:
        """Track how conversation topics evolve"""
        topic_evolution = []
        current_topics = set()
        
        # Define topic keywords
        topic_keywords = {
            'symptoms': ['pain', 'ache', 'fever', 'nausea', 'dizzy', 'tired', 'cough'],
            'medications': ['medication', 'pill', 'drug', 'taking', 'prescription'],
            'diagnosis': ['diagnosed', 'condition', 'disease', 'disorder'],
            'treatment': ['treatment', 'therapy', 'cure', 'help', 'better'],
            'prevention': ['prevent', 'avoid', 'stop', 'reduce', 'lifestyle']
        }
        
        for i, message in enumerate(messages):
            if message.role == MessageRole.USER:
                message_topics = set()
                content_lower = message.content.lower()
                
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        message_topics.add(topic)
                
                # Detect topic changes
                if message_topics != current_topics:
                    topic_evolution.append({
                        "message_index": i,
                        "timestamp": message.timestamp.isoformat(),
                        "new_topics": list(message_topics - current_topics),
                        "dropped_topics": list(current_topics - message_topics),
                        "all_topics": list(message_topics)
                    })
                    current_topics = message_topics
        
        return topic_evolution
    
    @staticmethod
    def _suggest_follow_ups(conversation_text: str) -> List[str]:
        """Suggest intelligent follow-up questions based on conversation"""
        follow_ups = []
        text_lower = conversation_text.lower()
        
        # Symptom-based follow-ups
        if any(symptom in text_lower for symptom in ['pain', 'ache', 'hurt']):
            follow_ups.extend([
                "Can you describe the pain on a scale of 1-10?",
                "When did the pain first start?",
                "What makes the pain better or worse?"
            ])
        
        if any(symptom in text_lower for symptom in ['fever', 'temperature']):
            follow_ups.extend([
                "Have you measured your temperature? What was it?",
                "How long have you had the fever?",
                "Are you experiencing chills or sweating?"
            ])
        
        if any(symptom in text_lower for symptom in ['medication', 'taking']):
            follow_ups.extend([
                "What medications are you currently taking?",
                "Have you started any new medications recently?",
                "Are you experiencing any side effects?"
            ])
        
        # General health follow-ups
        if 'tired' in text_lower or 'fatigue' in text_lower:
            follow_ups.extend([
                "How long have you been feeling tired?",
                "How is your sleep quality?",
                "Have you noticed any other symptoms?"
            ])
        
        # Remove duplicates and limit
        return list(set(follow_ups))[:5]
    
    @staticmethod
    async def _generate_summary(user_messages: List[str]) -> str:
        """Generate AI summary of conversation"""
        if not user_messages:
            return "No user messages to summarize."
        
        try:
            conversation_text = " ".join(user_messages[-10:])  # Last 10 messages
            
            if not ai_service.is_initialized():
                await ai_service.initialize()
            
            summary_prompt = f"""
            Summarize this medical conversation in 2-3 sentences, focusing on:
            1. Main health concerns mentioned
            2. Key symptoms or issues discussed
            3. Overall context and urgency level
            
            Conversation: {conversation_text}
            
            Provide a concise, clinical summary suitable for medical record keeping.
            """
            
            result = await ai_service.process_chat_message(summary_prompt, include_sources=False)
            return result.get("response", "Unable to generate summary.")
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return f"Summary generation failed: {str(e)}"
    
    @staticmethod
    async def intelligent_response_routing(
        message: str, 
        session_id: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route messages to appropriate AI analysis based on content"""
        try:
            message_lower = message.lower()
            
            # Analyze message intent
            intent_analysis = {
                "needs_differential_diagnosis": any(word in message_lower for word in [
                    'symptoms', 'diagnose', 'condition', 'what could', 'might be'
                ]),
                "needs_medication_analysis": any(word in message_lower for word in [
                    'medication', 'drug', 'pill', 'interaction', 'side effect'
                ]),
                "needs_risk_assessment": any(word in message_lower for word in [
                    'risk', 'family history', 'prevention', 'screening'
                ]),
                "needs_document_analysis": any(word in message_lower for word in [
                    'lab result', 'test result', 'report', 'scan', 'x-ray'
                ]),
                "is_emergency": any(word in message_lower for word in [
                    'emergency', 'urgent', 'severe', 'can\'t breathe', 'chest pain'
                ])
            }
            
            # Get conversation context
            context = await ChatService.analyze_conversation_context(session_id)
            
            # Route to appropriate specialized AI analysis
            if intent_analysis["is_emergency"]:
                return {
                    "response_type": "emergency_guidance",
                    "priority": "critical",
                    "message": "⚠️ URGENT: If this is a medical emergency, please call 911 or go to the nearest emergency room immediately. Do not delay seeking professional medical care.",
                    "follow_up": ["Have you called emergency services?", "Are you in a safe location?"]
                }
            
            elif intent_analysis["needs_differential_diagnosis"] and context.get("symptoms_mentioned"):
                # Use advanced differential diagnosis
                symptoms = context.get("symptoms_mentioned", [])
                patient_history = user_context.get("medical_history") if user_context else None
                demographics = user_context.get("demographics") if user_context else None
                
                diagnosis_result = await ai_service.differential_diagnosis(
                    symptoms=symptoms,
                    patient_history=patient_history,
                    demographics=demographics
                )
                
                return {
                    "response_type": "differential_diagnosis",
                    "analysis": diagnosis_result,
                    "follow_up": context.get("follow_up_needed", [])
                }
            
            elif intent_analysis["needs_medication_analysis"] and context.get("medications_mentioned"):
                # Use medication analysis
                medications = [{"name": med} for med in context.get("medications_mentioned", [])]
                patient_profile = user_context if user_context else None
                
                med_result = await ai_service.medication_analysis(
                    medications=medications,
                    patient_profile=patient_profile
                )
                
                return {
                    "response_type": "medication_analysis",
                    "analysis": med_result,
                    "follow_up": ["Are you experiencing any side effects?", "When do you take these medications?"]
                }
            
            else:
                # Standard AI response with context
                context_prompt = f"""
                Conversation context:
                - Previous symptoms mentioned: {', '.join(context.get('symptoms_mentioned', []))}
                - Medications mentioned: {', '.join(context.get('medications_mentioned', []))}
                - Conversation summary: {context.get('conversation_summary', '')}
                
                Current message: {message}
                
                Provide a contextual response that acknowledges the conversation history.
                """
                
                result = await ai_service.process_chat_message(context_prompt, include_sources=True)
                
                return {
                    "response_type": "contextual_response",
                    "response": result["response"],
                    "sources": result.get("sources", []),
                    "follow_up": context.get("follow_up_needed", [])[:3]
                }
            
        except Exception as e:
            logger.error(f"Error in intelligent response routing: {e}")
            return {
                "response_type": "error",
                "message": "I apologize, but I encountered an error processing your message. Please try again.",
                "error": str(e)
            }

# Global chat service instance
chat_service = ChatService()

__all__ = ["chat_service", "ChatService"]