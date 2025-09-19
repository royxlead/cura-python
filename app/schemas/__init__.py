"""
API schemas for request and response models
Pydantic models for API validation and serialization
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

# Authentication schemas
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    is_active: bool

# Chat schemas
class ChatMessage(BaseModel):
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    include_sources: bool = True
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    message: str
    session_id: str
    timestamp: datetime
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    tokens_used: Optional[int] = None
    response_type: Optional[str] = "standard"  # standard, emergency, differential_diagnosis, medication_analysis
    priority: Optional[str] = None  # low, medium, high, critical
    analysis: Optional[Dict[str, Any]] = None
    follow_up_suggestions: List[str] = Field(default_factory=list)

class ChatHistory(BaseModel):
    messages: List[ChatMessage]
    total_messages: int
    session_id: str

# Medical schemas  
class SymptomInput(BaseModel):
    name: str
    severity: str = Field(..., regex="^(low|moderate|high|critical)$")
    duration_hours: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    body_location: Optional[str] = None
    pain_scale: Optional[int] = Field(None, ge=0, le=10)

class MedicationInput(BaseModel):
    name: str
    dosage: str
    frequency: str
    route: str = "oral"
    start_date: datetime
    prescribed_by: Optional[str] = None

class VitalSignsInput(BaseModel):
    systolic_bp: Optional[int] = Field(None, ge=60, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=30, le=200)
    heart_rate: Optional[int] = Field(None, ge=30, le=300)
    temperature: Optional[float] = Field(None, ge=90.0, le=110.0)
    respiratory_rate: Optional[int] = Field(None, ge=8, le=60)
    oxygen_saturation: Optional[int] = Field(None, ge=70, le=100)
    weight: Optional[float] = Field(None, ge=50, le=1000)
    height: Optional[float] = Field(None, ge=24, le=120)

class DrugInteractionCheck(BaseModel):
    medications: List[str] = Field(..., min_items=2)

# Advanced Medical Analysis Schemas
class DifferentialDiagnosisRequest(BaseModel):
    symptoms: List[str] = Field(..., min_items=1)
    patient_history: Optional[Dict[str, Any]] = None
    demographics: Optional[Dict[str, Any]] = None
    duration: Optional[str] = None
    severity: Optional[str] = None

class DifferentialDiagnosisResponse(BaseModel):
    differential_diagnoses: List[Dict[str, Any]]
    recommendations: List[str]
    red_flag_warnings: List[str]
    follow_up_needed: List[str]
    confidence_level: str
    generated_at: datetime

class MedicationAnalysisRequest(BaseModel):
    medications: List[Dict[str, Any]] = Field(..., min_items=1)
    patient_profile: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None

class MedicationAnalysisResponse(BaseModel):
    interactions: List[Dict[str, Any]]
    side_effects_to_monitor: List[str]
    dosage_considerations: List[str]
    recommendations: List[str]
    safety_alerts: List[str]
    generated_at: datetime

class DocumentAnalysisRequest(BaseModel):
    document_text: str = Field(..., min_length=10)
    document_type: str = Field(..., regex="^(lab_result|imaging|pathology|clinical_note|prescription)$")
    patient_context: Optional[Dict[str, Any]] = None

class DocumentAnalysisResponse(BaseModel):
    key_findings: List[str]
    abnormal_values: List[Dict[str, Any]]
    clinical_significance: str
    recommendations: List[str]
    follow_up_needed: List[str]
    urgency_level: str
    generated_at: datetime

class HealthRiskAssessmentRequest(BaseModel):
    patient_data: Dict[str, Any]
    family_history: Optional[List[str]] = None
    lifestyle_factors: Optional[Dict[str, Any]] = None
    current_conditions: Optional[List[str]] = None

class HealthRiskAssessmentResponse(BaseModel):
    risk_factors: List[Dict[str, Any]]
    risk_score: int
    prevention_strategies: List[str]
    screening_recommendations: List[str]
    lifestyle_modifications: List[str]
    generated_at: datetime

# Health Monitoring Schemas
class VitalRecordingRequest(BaseModel):
    vital_type: str = Field(..., regex="^(blood_pressure|heart_rate|temperature|weight|blood_glucose|oxygen_saturation|respiratory_rate)$")
    value: Dict[str, float]  # For BP: {"systolic": 120, "diastolic": 80}, for others: {"value": 98.6}
    notes: Optional[str] = None
    source: str = "manual"
    measured_at: Optional[datetime] = None

class VitalRecordingResponse(BaseModel):
    success: bool
    vital_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    recorded_at: datetime

class HealthTrendAnalysis(BaseModel):
    vital_type: str
    trend_direction: str  # improving, stable, declining, concerning
    change_percentage: float
    time_period: str
    recent_average: float
    previous_average: float
    total_readings: int
    insights: List[str]
    recommendations: List[str]

class HealthDashboard(BaseModel):
    user_id: str
    health_score: int
    vital_summaries: Dict[str, Any]
    recent_alerts: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

class EmergencyProtocolRequest(BaseModel):
    symptoms: List[str] = Field(..., min_items=1)
    severity: str = "unknown"
    patient_conscious: bool = True
    vital_signs: Optional[Dict[str, Any]] = None

class EmergencyProtocolResponse(BaseModel):
    emergency_level: str  # NON_URGENT, SEMI_URGENT, URGENT, CRITICAL
    immediate_actions: List[str]
    warning: str
    do_not_wait: bool
    estimated_response_time: str
    emergency_contacts: Optional[List[str]] = None

# Conversation Analysis Schemas
class ConversationAnalysisResponse(BaseModel):
    symptoms_mentioned: List[str]
    medications_mentioned: List[str]
    urgency_indicators: List[str]
    topic_evolution: List[Dict[str, Any]]
    follow_up_needed: List[str]
    conversation_summary: str
    medical_context_score: int
    generated_at: datetime

# Voice interface schemas
class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    format: str = "wav"
    sample_rate: int = 16000

class VoiceResponse(BaseModel):
    text: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None

# Image analysis schemas
class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    analysis_type: str = Field(..., regex="^(general|dermatology|radiology|wound)$")
    additional_context: Optional[str] = None

class ImageAnalysisResponse(BaseModel):
    analysis: str
    confidence_score: float
    recommendations: List[str]
    requires_professional_review: bool

# System schemas
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    database: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None

# Pagination schemas
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

__all__ = [
    # Authentication
    "UserRegistration", "UserLogin", "Token", "UserProfile",
    
    # Chat
    "ChatMessage", "ChatRequest", "ChatResponse", "ChatHistory",
    
    # Basic Medical
    "SymptomInput", "MedicationInput", "VitalSignsInput", "DrugInteractionCheck",
    
    # Advanced Medical Analysis
    "DifferentialDiagnosisRequest", "DifferentialDiagnosisResponse",
    "MedicationAnalysisRequest", "MedicationAnalysisResponse", 
    "DocumentAnalysisRequest", "DocumentAnalysisResponse",
    "HealthRiskAssessmentRequest", "HealthRiskAssessmentResponse",
    
    # Health Monitoring
    "VitalRecordingRequest", "VitalRecordingResponse",
    "HealthTrendAnalysis", "HealthDashboard",
    "EmergencyProtocolRequest", "EmergencyProtocolResponse",
    "ConversationAnalysisResponse",
    
    # Media and System
    "VoiceRequest", "VoiceResponse",
    "ImageAnalysisRequest", "ImageAnalysisResponse", 
    "HealthCheckResponse", "ErrorResponse",
    "PaginationParams", "PaginatedResponse"
]