"""
Medical Service for health-related operations
Handles symptoms, medications, vitals, and medical analysis
"""

import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from bson import ObjectId

from ..models import Symptom, Medication, VitalSigns, MedicalRecord, User, SeverityLevel
from ..core.database import get_database
from .ai_service import ai_service

logger = logging.getLogger(__name__)

class BodySystem(Enum):
    """Body systems for symptom categorization"""
    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORY = "respiratory"
    GASTROINTESTINAL = "gastrointestinal"
    NEUROLOGICAL = "neurological"
    MUSCULOSKELETAL = "musculoskeletal"
    DERMATOLOGICAL = "dermatological"
    GENITOURINARY = "genitourinary"
    ENDOCRINE = "endocrine"
    HEMATOLOGICAL = "hematological"
    PSYCHIATRIC = "psychiatric"
    OPHTHALMOLOGICAL = "ophthalmological"
    OTOLARYNGOLOGICAL = "otolaryngological"

@dataclass
class SymptomAssessment:
    """Complete symptom assessment result"""
    symptoms: List[Dict[str, Any]]
    primary_system: str
    urgency_level: str
    preliminary_conditions: List[Dict[str, Any]]
    recommendations: List[str]
    red_flags: List[str]
    follow_up_questions: List[str]
    assessment_id: str
    created_at: str

class MedicalService:
    """Service for medical data management and analysis"""
    
    def __init__(self):
        self.symptom_database = self._load_symptom_database()
        self.condition_database = self._load_condition_database()
        self.red_flag_symptoms = self._load_red_flags()
    
    def _load_symptom_database(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive symptom database"""
        return {
            "chest_pain": {
                "name": "Chest Pain",
                "body_system": BodySystem.CARDIOVASCULAR,
                "severity_indicators": {
                    "crushing": "critical",
                    "squeezing": "severe", 
                    "sharp": "moderate",
                    "dull": "mild"
                },
                "associated_conditions": ["myocardial_infarction", "angina", "pericarditis"],
                "red_flags": ["radiating to arm", "shortness of breath", "sweating", "nausea"]
            },
            "shortness_of_breath": {
                "name": "Shortness of Breath",
                "body_system": BodySystem.RESPIRATORY,
                "severity_indicators": {
                    "at_rest": "critical",
                    "with_minimal_activity": "severe",
                    "with_moderate_activity": "moderate",
                    "with_strenuous_activity": "mild"
                },
                "associated_conditions": ["asthma", "pneumonia", "heart_failure"],
                "red_flags": ["blue lips", "confusion", "severe distress"]
            },
            "headache": {
                "name": "Headache",
                "body_system": BodySystem.NEUROLOGICAL,
                "severity_indicators": {
                    "worst_headache_ever": "critical",
                    "severe_sudden_onset": "severe",
                    "throbbing": "moderate",
                    "mild_tension": "mild"
                },
                "associated_conditions": ["migraine", "tension_headache", "cluster_headache"],
                "red_flags": ["fever", "stiff neck", "vision changes", "confusion"]
            }
        }
    
    def _load_condition_database(self) -> Dict[str, Dict[str, Any]]:
        """Load medical conditions database"""
        return {
            "myocardial_infarction": {
                "name": "Heart Attack",
                "urgency": "critical",
                "common_symptoms": ["chest_pain", "shortness_of_breath", "nausea", "sweating"],
                "description": "Blockage of blood flow to heart muscle"
            },
            "migraine": {
                "name": "Migraine",
                "urgency": "moderate",
                "common_symptoms": ["headache", "nausea", "light_sensitivity"],
                "description": "Neurological condition causing severe headaches"
            }
        }
    
    def _load_red_flags(self) -> List[str]:
        """Load red flag symptoms requiring immediate attention"""
        return [
            "chest_pain_with_radiation",
            "sudden_severe_headache",
            "difficulty_breathing_at_rest",
            "loss_of_consciousness",
            "severe_abdominal_pain",
            "high_fever_with_stiff_neck",
            "sudden_vision_loss",
            "paralysis_or_weakness"
        ]
    
    async def analyze_symptoms(
        self,
        symptoms: List[Dict[str, Any]],
        patient_info: Optional[Dict[str, Any]] = None
    ) -> SymptomAssessment:
        """Comprehensive symptom analysis"""
        try:
            # Process symptoms
            processed_symptoms = []
            red_flags = []
            body_systems = set()
            
            for symptom_data in symptoms:
                symptom_name = symptom_data.get("name", "").lower().replace(" ", "_")
                
                if symptom_name in self.symptom_database:
                    db_symptom = self.symptom_database[symptom_name]
                    processed_symptoms.append({
                        "name": db_symptom["name"],
                        "severity": symptom_data.get("severity", "mild"),
                        "body_system": db_symptom["body_system"].value,
                        "description": symptom_data.get("description", ""),
                        "duration": symptom_data.get("duration", "")
                    })
                    body_systems.add(db_symptom["body_system"])
                    
                    # Check for red flags
                    for flag in db_symptom.get("red_flags", []):
                        if flag.lower() in symptom_data.get("description", "").lower():
                            red_flags.append(f"Red flag detected: {flag}")
            
            # Determine primary body system
            primary_system = max(body_systems, key=lambda x: len([s for s in processed_symptoms if s["body_system"] == x.value])).value if body_systems else "unknown"
            
            # Determine urgency level
            urgency_level = "mild"
            if red_flags:
                urgency_level = "critical"
            elif any(s["severity"] in ["severe", "critical"] for s in processed_symptoms):
                urgency_level = "severe"
            elif any(s["severity"] == "moderate" for s in processed_symptoms):
                urgency_level = "moderate"
            
            # Generate recommendations
            recommendations = [
                "Consult with a healthcare professional for proper diagnosis",
                "Keep track of symptom progression",
                "Stay hydrated and get adequate rest"
            ]
            
            if urgency_level == "critical":
                recommendations.insert(0, "⚠️ SEEK IMMEDIATE MEDICAL ATTENTION")
            elif urgency_level == "severe":
                recommendations.insert(0, "Schedule urgent medical consultation within 24 hours")
            
            # Generate follow-up questions
            follow_up_questions = [
                "When did these symptoms first appear?",
                "Have you experienced similar symptoms before?",
                "Are you currently taking any medications?",
                "Do you have any known medical conditions?"
            ]
            
            assessment = SymptomAssessment(
                symptoms=processed_symptoms,
                primary_system=primary_system,
                urgency_level=urgency_level,
                preliminary_conditions=[],  # Could be enhanced with AI analysis
                recommendations=recommendations,
                red_flags=red_flags,
                follow_up_questions=follow_up_questions,
                assessment_id=f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Symptom analysis failed: {e}")
            raise
    
    @staticmethod
    async def add_symptom(
        user_id: str,
        name: str,
        severity: SeverityLevel,
        description: Optional[str] = None,
        duration_hours: Optional[int] = None,
        body_location: Optional[str] = None,
        pain_scale: Optional[int] = None
    ) -> Symptom:
        """Add a new symptom record"""
        symptom = Symptom(
            user_id=ObjectId(user_id),
            name=name,
            severity=severity,
            description=description,
            duration_hours=duration_hours,
            body_location=body_location,
            pain_scale=pain_scale,
            onset_date=datetime.now(timezone.utc),
            reported_at=datetime.now(timezone.utc),
            is_active=True
        )
        await symptom.insert()
        return symptom
    
    @staticmethod
    async def get_user_symptoms(
        user_id: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Symptom]:
        """Get user's symptoms"""
        query = Symptom.user_id == ObjectId(user_id)
        if active_only:
            query = query & (Symptom.is_active == True)
        
        return await Symptom.find(query).sort(-Symptom.reported_at).limit(limit).to_list()
    
    @staticmethod
    async def add_medication(
        user_id: str,
        name: str,
        dosage: str,
        frequency: str,
        route: str = "oral",
        prescribed_by: Optional[str] = None,
        start_date: Optional[datetime] = None
    ) -> Medication:
        """Add a new medication record"""
        medication = Medication(
            user_id=ObjectId(user_id),
            name=name,
            dosage=dosage,
            frequency=frequency,
            route=route,
            prescribed_by=prescribed_by,
            start_date=start_date or datetime.now(timezone.utc),
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        await medication.insert()
        return medication
    
    @staticmethod
    async def get_user_medications(
        user_id: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Medication]:
        """Get user's medications"""
        query = Medication.user_id == ObjectId(user_id)
        if active_only:
            query = query & (Medication.is_active == True)
        
        return await Medication.find(query).sort(-Medication.created_at).limit(limit).to_list()
    
    @staticmethod
    async def add_vital_signs(
        user_id: str,
        **vital_data
    ) -> VitalSigns:
        """Add vital signs record"""
        vitals = VitalSigns(
            user_id=ObjectId(user_id),
            measured_at=datetime.now(timezone.utc),
            **vital_data
        )
        
        # Calculate BMI if height and weight provided
        if vitals.height and vitals.weight:
            height_m = vitals.height * 0.0254  # inches to meters
            weight_kg = vitals.weight * 0.453592  # pounds to kg
            vitals.bmi = round(weight_kg / (height_m ** 2), 1)
        
        # Check for abnormal values
        vitals.is_normal = MedicalService._assess_vitals_normalcy(vitals)
        vitals.requires_attention = not vitals.is_normal
        
        await vitals.insert()
        return vitals
    
    @staticmethod
    def _assess_vitals_normalcy(vitals: VitalSigns) -> bool:
        """Assess if vital signs are within normal ranges"""
        normal = True
        
        # Blood pressure check
        if vitals.systolic_bp and vitals.diastolic_bp:
            if vitals.systolic_bp > 140 or vitals.diastolic_bp > 90:
                normal = False
            if vitals.systolic_bp < 90 or vitals.diastolic_bp < 60:
                normal = False
        
        # Heart rate check
        if vitals.heart_rate:
            if vitals.heart_rate > 100 or vitals.heart_rate < 60:
                normal = False
        
        # Temperature check (assuming Fahrenheit)
        if vitals.temperature:
            if vitals.temperature > 99.5 or vitals.temperature < 97.0:
                normal = False
        
        # Oxygen saturation check  
        if vitals.oxygen_saturation:
            if vitals.oxygen_saturation < 95:
                normal = False
        
        return normal
    
    @staticmethod
    async def get_user_vitals(
        user_id: str,
        days: int = 30,
        limit: int = 100
    ) -> List[VitalSigns]:
        """Get user's vital signs"""
        cutoff_date = datetime.now(timezone.utc) - timezone.timedelta(days=days)
        
        return await VitalSigns.find(
            VitalSigns.user_id == ObjectId(user_id),
            VitalSigns.measured_at >= cutoff_date
        ).sort(-VitalSigns.measured_at).limit(limit).to_list()
    
    @staticmethod
    async def analyze_symptoms(user_id: str, symptom_ids: List[str]) -> Dict[str, Any]:
        """Analyze user's symptoms using AI"""
        try:
            # Get symptom details
            symptoms = []
            for symptom_id in symptom_ids:
                symptom = await Symptom.get(ObjectId(symptom_id))
                if symptom and symptom.user_id == ObjectId(user_id):
                    symptoms.append({
                        "name": symptom.name,
                        "severity": symptom.severity,
                        "description": symptom.description,
                        "duration_hours": symptom.duration_hours,
                        "body_location": symptom.body_location,
                        "pain_scale": symptom.pain_scale
                    })
            
            if not symptoms:
                return {"error": "No valid symptoms found"}
            
            # Use AI service for analysis
            analysis = await ai_service.analyze_symptoms(symptoms)
            
            return {
                "analysis": analysis["response"],
                "sources": analysis.get("sources", []),
                "symptoms_analyzed": len(symptoms),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Symptom analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    @staticmethod
    async def check_drug_interactions(user_id: str) -> Dict[str, Any]:
        """Check for drug interactions in user's medications"""
        try:
            # Get active medications
            medications = await MedicalService.get_user_medications(
                user_id=user_id,
                active_only=True
            )
            
            if len(medications) < 2:
                return {"message": "Need at least 2 medications to check interactions"}
            
            med_names = [med.name for med in medications]
            
            # Use AI service for interaction check
            interaction_check = await ai_service.check_drug_interactions(med_names)
            
            return {
                "interaction_analysis": interaction_check["response"],
                "sources": interaction_check.get("sources", []),
                "medications_checked": med_names,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Drug interaction check failed: {e}")
            return {"error": f"Interaction check failed: {str(e)}"}
    
    @staticmethod
    async def get_medical_summary(user_id: str) -> Dict[str, Any]:
        """Get comprehensive medical summary for user"""
        try:
            # Get recent data
            symptoms = await MedicalService.get_user_symptoms(user_id, limit=10)
            medications = await MedicalService.get_user_medications(user_id, limit=10)
            vitals = await MedicalService.get_user_vitals(user_id, days=30, limit=5)
            
            # Format for response
            summary = {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_symptoms": len([s for s in symptoms if s.is_active]),
                "total_symptoms": len(symptoms),
                "active_medications": len([m for m in medications if m.is_active]),
                "total_medications": len(medications),
                "recent_vitals": len(vitals),
                "latest_vital_signs": vitals[0] if vitals else None,
                "requires_attention": any(v.requires_attention for v in vitals) or 
                                   any(s.requires_attention for s in symptoms)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Medical summary generation failed: {e}")
            return {"error": f"Summary generation failed: {str(e)}"}

# Global medical service instance
medical_service = MedicalService()

__all__ = ["medical_service", "MedicalService"]