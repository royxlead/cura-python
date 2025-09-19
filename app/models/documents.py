"""
MongoDB document models for Cura Medical AI Assistant
Using Beanie ODM for async MongoDB operations with Pydantic validation
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr, validator
from pymongo import IndexModel
import bcrypt
from bson import ObjectId

class UserRole(str, Enum):
    """User role enumeration"""
    PATIENT = "patient"
    HEALTHCARE_PROVIDER = "healthcare_provider" 
    ADMIN = "admin"

class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class RecordType(str, Enum):
    """Medical record types"""
    CONSULTATION = "consultation"
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    VITAL_SIGNS = "vital_signs"
    ALLERGY = "allergy"
    IMMUNIZATION = "immunization"

class SeverityLevel(str, Enum):
    """Severity levels for medical conditions"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# Embedded document models
class Address(BaseModel):
    """Address information"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"

class MedicalHistory(BaseModel):
    """Medical history information"""
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    surgical_history: List[str] = Field(default_factory=list)

class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str
    relationship: str
    phone: str
    email: Optional[EmailStr] = None

# Main document models
class User(Document):
    """User document model"""
    
    # Authentication fields
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    
    # Profile information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    
    # Medical information
    medical_history: Optional[MedicalHistory] = None
    emergency_contact: Optional[EmergencyContact] = None
    
    # Account management
    role: UserRole = UserRole.PATIENT
    is_active: bool = True
    is_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Privacy and consent
    privacy_consent: bool = False
    data_sharing_consent: bool = False
    marketing_consent: bool = False
    
    class Settings:
        collection = "users"
        indexes = [
            IndexModel("email", unique=True),
            IndexModel("username", unique=True),
            IndexModel("created_at"),
            IndexModel("role")
        ]
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email

class ChatSession(Document):
    """Chat session document model"""
    
    user_id: Indexed(ObjectId)
    title: str = "New Chat"
    
    # Session metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Session configuration
    model_used: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Session statistics
    message_count: int = 0
    total_tokens_used: int = 0
    
    # Session flags
    is_active: bool = True
    is_medical_consultation: bool = False
    
    # Privacy and compliance
    contains_phi: bool = False  # Protected Health Information
    retention_until: Optional[datetime] = None
    
    class Settings:
        collection = "chat_sessions"
        indexes = [
            IndexModel("user_id"),
            IndexModel("created_at"),
            IndexModel("is_active"),
            IndexModel("is_medical_consultation")
        ]

class Message(Document):
    """Chat message document model"""
    
    session_id: Indexed(ObjectId)
    
    # Message content
    role: MessageRole
    content: str
    
    # Message metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tokens_used: Optional[int] = None
    
    # AI response metadata
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None
    response_time_ms: Optional[int] = None
    
    # Source citations (for RAG responses)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Message flags
    is_edited: bool = False
    is_deleted: bool = False
    contains_phi: bool = False
    
    # Attachments
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Settings:
        collection = "messages"
        indexes = [
            IndexModel("session_id"),
            IndexModel("timestamp"),
            IndexModel("role"),
            IndexModel("contains_phi")
        ]

class MedicalRecord(Document):
    """Medical record document model"""
    
    user_id: Indexed(ObjectId)
    record_type: Indexed(RecordType)
    
    # Record content
    title: str
    description: str
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Clinical information
    diagnosis_codes: List[str] = Field(default_factory=list)  # ICD-10 codes
    procedure_codes: List[str] = Field(default_factory=list)  # CPT codes
    severity: Optional[SeverityLevel] = None
    
    # Provider information
    provider_name: Optional[str] = None
    provider_id: Optional[str] = None
    facility: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    record_date: datetime  # Date when the medical event occurred
    updated_at: Optional[datetime] = None
    
    # Compliance and privacy
    is_phi: bool = True
    access_level: str = "restricted"
    retention_until: Optional[datetime] = None
    
    class Settings:
        collection = "medical_records"
        indexes = [
            IndexModel("user_id"),
            IndexModel("record_type"),
            IndexModel("created_at"),
            IndexModel("record_date"),
            IndexModel("diagnosis_codes"),
            IndexModel("access_level")
        ]

class Symptom(Document):
    """Symptom tracking document model"""
    
    user_id: Indexed(ObjectId)
    
    # Symptom details
    name: str
    description: Optional[str] = None
    severity: SeverityLevel
    duration_hours: Optional[int] = None
    
    # Associated data
    triggers: List[str] = Field(default_factory=list)
    relieving_factors: List[str] = Field(default_factory=list)
    associated_symptoms: List[str] = Field(default_factory=list)
    
    # Location and characteristics
    body_location: Optional[str] = None
    pain_scale: Optional[int] = Field(None, ge=0, le=10)
    
    # Timestamps
    onset_date: datetime
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    # Tracking flags
    is_active: bool = True
    requires_attention: bool = False
    
    class Settings:
        collection = "symptoms"
        indexes = [
            IndexModel("user_id"),
            IndexModel("onset_date"),
            IndexModel("severity"),
            IndexModel("is_active"),
            IndexModel("requires_attention")
        ]

class Medication(Document):
    """Medication tracking document model"""
    
    user_id: Indexed(ObjectId)
    
    # Medication details
    name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: str
    route: str = "oral"  # oral, topical, injection, etc.
    
    # Prescription information
    prescribed_by: Optional[str] = None
    prescription_date: Optional[datetime] = None
    prescription_number: Optional[str] = None
    
    # Usage tracking
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    
    # Monitoring
    side_effects: List[str] = Field(default_factory=list)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    
    # Drug information
    drug_class: Optional[str] = None
    ndc_number: Optional[str] = None  # National Drug Code
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    class Settings:
        collection = "medications"
        indexes = [
            IndexModel("user_id"),
            IndexModel("name"),
            IndexModel("is_active"),
            IndexModel("start_date"),
            IndexModel("drug_class")
        ]

class InteractionCheck(Document):
    """Drug interaction checking document model"""
    
    user_id: Indexed(ObjectId)
    
    # Medications involved
    medication_ids: List[ObjectId]
    medication_names: List[str]
    
    # Interaction details
    interaction_type: str  # drug-drug, drug-food, drug-condition
    severity: SeverityLevel
    description: str
    clinical_significance: str
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    requires_monitoring: bool = False
    contraindicated: bool = False
    
    # Check metadata
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    check_source: str = "ai_analysis"
    confidence_score: Optional[float] = None
    
    # Status
    is_acknowledged: bool = False
    acknowledged_by: Optional[ObjectId] = None
    acknowledged_at: Optional[datetime] = None
    
    class Settings:
        collection = "interaction_checks"
        indexes = [
            IndexModel("user_id"),
            IndexModel("checked_at"),
            IndexModel("severity"),
            IndexModel("contraindicated"),
            IndexModel("is_acknowledged")
        ]

class VitalSigns(Document):
    """Vital signs tracking document model"""
    
    user_id: Indexed(ObjectId)
    
    # Vital sign measurements
    systolic_bp: Optional[int] = None  # mmHg
    diastolic_bp: Optional[int] = None  # mmHg
    heart_rate: Optional[int] = None  # bpm
    temperature: Optional[float] = None  # Fahrenheit
    respiratory_rate: Optional[int] = None  # breaths per minute
    oxygen_saturation: Optional[int] = None  # percentage
    weight: Optional[float] = None  # pounds
    height: Optional[float] = None  # inches
    bmi: Optional[float] = None
    
    # Measurement metadata
    measured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    measurement_method: Optional[str] = None  # manual, device, estimated
    device_used: Optional[str] = None
    measured_by: Optional[str] = None
    
    # Context
    notes: Optional[str] = None
    activity_level: Optional[str] = None  # resting, post-exercise, etc.
    
    # Analysis flags
    is_normal: Optional[bool] = None
    requires_attention: bool = False
    alert_triggered: bool = False
    
    class Settings:
        collection = "vital_signs"
        indexes = [
            IndexModel("user_id"),
            IndexModel("measured_at"),
            IndexModel("requires_attention"),
            IndexModel("alert_triggered")
        ]

# Function to get all document models for Beanie initialization
def get_document_models():
    """Return list of all document models for Beanie initialization"""
    return [
        User, ChatSession, Message, MedicalRecord,
        Symptom, Medication, InteractionCheck, VitalSigns
    ]

# Export all models
__all__ = [
    "User", "ChatSession", "Message", "MedicalRecord",
    "Symptom", "Medication", "InteractionCheck", "VitalSigns",
    "UserRole", "MessageRole", "RecordType", "SeverityLevel",
    "Address", "MedicalHistory", "EmergencyContact",
    "get_document_models"
]