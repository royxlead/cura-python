"""
Medical Knowledge Service
Provides comprehensive medical reference data and clinical decision support
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

from app.core.config import settings
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class SeverityLevel(str, Enum):
    """Medical condition severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class UrgencyLevel(str, Enum):
    """Medical urgency classifications"""
    NON_URGENT = "non_urgent"
    SEMI_URGENT = "semi_urgent"
    URGENT = "urgent"
    EMERGENCY = "emergency"

@dataclass
class DrugInfo:
    """Comprehensive drug information"""
    name: str
    generic_name: str
    brand_names: List[str]
    drug_class: str
    mechanism_of_action: str
    indications: List[str]
    contraindications: List[str]
    common_side_effects: List[str]
    serious_side_effects: List[str]
    interactions: List[str]
    dosage_forms: List[str]
    pregnancy_category: str
    half_life: str
    monitoring_required: List[str]
    
@dataclass
class SymptomPattern:
    """Medical symptom pattern information"""
    symptom: str
    aliases: List[str]
    associated_conditions: List[str]
    red_flag_features: List[str]
    typical_onset: str
    duration_patterns: List[str]
    severity_indicators: Dict[str, List[str]]
    examination_findings: List[str]
    
@dataclass
class ClinicalGuideline:
    """Clinical practice guidelines"""
    condition: str
    guideline_source: str
    last_updated: str
    diagnostic_criteria: List[str]
    first_line_treatment: List[str]
    alternative_treatments: List[str]
    follow_up_recommendations: List[str]
    referral_indications: List[str]
    prevention_strategies: List[str]

class MedicalKnowledgeService:
    """Comprehensive medical knowledge and clinical decision support"""
    
    def __init__(self):
        self.drug_database: Dict[str, DrugInfo] = {}
        self.symptom_patterns: Dict[str, SymptomPattern] = {}
        self.clinical_guidelines: Dict[str, ClinicalGuideline] = {}
        self.interaction_matrix: Dict[Tuple[str, str], str] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize medical knowledge database"""
        if self._initialized:
            return
            
        logger.info("Initializing Medical Knowledge Service...")
        
        try:
            # Initialize core databases
            await self._load_drug_database()
            await self._load_symptom_patterns()
            await self._load_clinical_guidelines()
            await self._build_interaction_matrix()
            
            self._initialized = True
            logger.info("Medical Knowledge Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Medical Knowledge Service: {e}")
            raise
    
    async def _load_drug_database(self):
        """Load comprehensive drug information database"""
        # Essential medications database
        common_drugs = [
            {
                "name": "acetaminophen",
                "generic_name": "acetaminophen",
                "brand_names": ["Tylenol", "Panadol", "Excedrin"],
                "drug_class": "Analgesic/Antipyretic",
                "mechanism_of_action": "Inhibits cyclooxygenase in CNS, blocks pain impulses",
                "indications": ["Pain relief", "Fever reduction", "Headache", "Arthritis"],
                "contraindications": ["Severe liver disease", "Chronic alcohol use"],
                "common_side_effects": ["Nausea", "Rash", "Headache"],
                "serious_side_effects": ["Liver toxicity", "Stevens-Johnson syndrome"],
                "interactions": ["Warfarin", "Alcohol", "Phenytoin"],
                "dosage_forms": ["Tablet", "Capsule", "Liquid", "Suppository"],
                "pregnancy_category": "B",
                "half_life": "2-4 hours",
                "monitoring_required": ["Liver function tests with chronic use"]
            },
            {
                "name": "ibuprofen",
                "generic_name": "ibuprofen",
                "brand_names": ["Advil", "Motrin", "Nurofen"],
                "drug_class": "NSAID",
                "mechanism_of_action": "Non-selective COX inhibitor",
                "indications": ["Pain", "Inflammation", "Fever", "Arthritis"],
                "contraindications": ["Active GI bleeding", "Severe heart failure", "Severe kidney disease"],
                "common_side_effects": ["Stomach upset", "Nausea", "Dizziness", "Headache"],
                "serious_side_effects": ["GI bleeding", "Kidney damage", "Heart attack", "Stroke"],
                "interactions": ["Warfarin", "ACE inhibitors", "Lithium", "Methotrexate"],
                "dosage_forms": ["Tablet", "Capsule", "Liquid", "Gel"],
                "pregnancy_category": "C (D in 3rd trimester)",
                "half_life": "2-4 hours",
                "monitoring_required": ["Kidney function", "Blood pressure", "Signs of bleeding"]
            },
            {
                "name": "lisinopril",
                "generic_name": "lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ACE Inhibitor",
                "mechanism_of_action": "Inhibits angiotensin-converting enzyme",
                "indications": ["Hypertension", "Heart failure", "Post-MI", "Diabetic nephropathy"],
                "contraindications": ["Pregnancy", "Angioedema history", "Bilateral renal artery stenosis"],
                "common_side_effects": ["Dry cough", "Dizziness", "Headache", "Fatigue"],
                "serious_side_effects": ["Angioedema", "Hyperkalemia", "Acute kidney injury"],
                "interactions": ["Potassium supplements", "NSAIDs", "Diuretics"],
                "dosage_forms": ["Tablet"],
                "pregnancy_category": "D",
                "half_life": "12 hours",
                "monitoring_required": ["Blood pressure", "Kidney function", "Potassium levels"]
            },
            {
                "name": "metformin",
                "generic_name": "metformin",
                "brand_names": ["Glucophage", "Fortamet", "Glumetza"],
                "drug_class": "Biguanide",
                "mechanism_of_action": "Decreases hepatic glucose production, improves insulin sensitivity",
                "indications": ["Type 2 diabetes", "Prediabetes", "PCOS"],
                "contraindications": ["Severe kidney disease", "Metabolic acidosis", "Dehydration"],
                "common_side_effects": ["Nausea", "Diarrhea", "Stomach upset", "Metallic taste"],
                "serious_side_effects": ["Lactic acidosis", "Vitamin B12 deficiency"],
                "interactions": ["Contrast dye", "Alcohol", "Cimetidine"],
                "dosage_forms": ["Tablet", "Extended-release tablet"],
                "pregnancy_category": "B",
                "half_life": "4-9 hours",
                "monitoring_required": ["Kidney function", "Vitamin B12 levels", "Blood glucose"]
            }
        ]
        
        # Convert to DrugInfo objects
        for drug_data in common_drugs:
            drug_info = DrugInfo(**drug_data)
            self.drug_database[drug_data["name"].lower()] = drug_info
            
            # Add brand name lookups
            for brand in drug_data["brand_names"]:
                self.drug_database[brand.lower()] = drug_info
        
        logger.info(f"Loaded {len(common_drugs)} drugs into database")
    
    async def _load_symptom_patterns(self):
        """Load symptom pattern recognition database"""
        symptom_data = [
            {
                "symptom": "chest_pain",
                "aliases": ["chest pain", "chest discomfort", "chest pressure", "chest tightness"],
                "associated_conditions": ["Myocardial infarction", "Angina", "Pulmonary embolism", "Pneumonia", "GERD", "Anxiety"],
                "red_flag_features": ["Sudden onset", "Radiation to arm/jaw", "Diaphoresis", "Shortness of breath", "Nausea/vomiting"],
                "typical_onset": "Variable - sudden (MI, PE) vs gradual (angina, GERD)",
                "duration_patterns": ["Seconds to minutes (angina)", "Minutes to hours (MI)", "Constant (PE, pneumonia)"],
                "severity_indicators": {
                    "mild": ["Mild discomfort", "No radiation", "No associated symptoms"],
                    "moderate": ["Moderate pain", "Some radiation", "Mild shortness of breath"],
                    "severe": ["Severe crushing pain", "Radiation to multiple areas", "Severe dyspnea", "Diaphoresis"]
                },
                "examination_findings": ["Heart sounds", "Lung sounds", "Blood pressure", "Pulse", "Oxygen saturation"]
            },
            {
                "symptom": "headache",
                "aliases": ["headache", "head pain", "cephalgia", "migraine"],
                "associated_conditions": ["Tension headache", "Migraine", "Cluster headache", "Sinusitis", "Hypertension", "Brain tumor"],
                "red_flag_features": ["Sudden severe onset", "Fever and neck stiffness", "Vision changes", "Weakness", "Confusion"],
                "typical_onset": "Gradual (tension) vs sudden (SAH) vs recurrent (migraine)",
                "duration_patterns": ["Hours (tension)", "4-72 hours (migraine)", "15min-3hrs (cluster)"],
                "severity_indicators": {
                    "mild": ["Mild pain", "No functional impairment", "No associated symptoms"],
                    "moderate": ["Moderate pain", "Some functional impairment", "Mild nausea"],
                    "severe": ["Severe pain", "Significant impairment", "Vomiting", "Photophobia"]
                },
                "examination_findings": ["Neurological exam", "Fundoscopy", "Blood pressure", "Temperature", "Neck stiffness"]
            },
            {
                "symptom": "shortness_of_breath",
                "aliases": ["shortness of breath", "dyspnea", "breathlessness", "difficulty breathing"],
                "associated_conditions": ["Asthma", "COPD", "Heart failure", "Pulmonary embolism", "Pneumonia", "Anxiety"],
                "red_flag_features": ["Sudden onset", "Chest pain", "Leg swelling", "Hemoptysis", "Cyanosis"],
                "typical_onset": "Acute (PE, pneumonia) vs chronic (COPD, HF) vs episodic (asthma)",
                "duration_patterns": ["Minutes (acute)", "Days to weeks (subacute)", "Months to years (chronic)"],
                "severity_indicators": {
                    "mild": ["On exertion only", "No rest symptoms", "Normal speech"],
                    "moderate": ["Moderate exertion", "Occasional rest symptoms", "Short sentences"],
                    "severe": ["Minimal exertion", "Rest symptoms", "Single words only", "Accessory muscles"]
                },
                "examination_findings": ["Oxygen saturation", "Respiratory rate", "Lung sounds", "Heart sounds", "Leg edema"]
            }
        ]
        
        for symptom_data_item in symptom_data:
            symptom = SymptomPattern(**symptom_data_item)
            self.symptom_patterns[symptom_data_item["symptom"]] = symptom
            
            # Add alias lookups
            for alias in symptom_data_item["aliases"]:
                self.symptom_patterns[alias.lower().replace(" ", "_")] = symptom
        
        logger.info(f"Loaded {len(symptom_data)} symptom patterns")
    
    async def _load_clinical_guidelines(self):
        """Load clinical practice guidelines"""
        guidelines_data = [
            {
                "condition": "hypertension",
                "guideline_source": "AHA/ACC 2017",
                "last_updated": "2017-11-13",
                "diagnostic_criteria": [
                    "Stage 1: SBP 130-139 or DBP 80-89 mmHg",
                    "Stage 2: SBP ≥140 or DBP ≥90 mmHg",
                    "Confirmed on multiple occasions"
                ],
                "first_line_treatment": [
                    "ACE inhibitor or ARB",
                    "Thiazide or thiazide-like diuretic",
                    "Calcium channel blocker",
                    "Lifestyle modifications"
                ],
                "alternative_treatments": [
                    "Beta-blockers (specific indications)",
                    "Aldosterone antagonists",
                    "Direct renin inhibitors"
                ],
                "follow_up_recommendations": [
                    "Monthly until target BP achieved",
                    "Every 3-6 months once stable",
                    "Home BP monitoring"
                ],
                "referral_indications": [
                    "Resistant hypertension",
                    "Secondary hypertension suspected",
                    "Target organ damage"
                ],
                "prevention_strategies": [
                    "DASH diet",
                    "Weight loss",
                    "Regular exercise",
                    "Limit sodium and alcohol"
                ]
            },
            {
                "condition": "type_2_diabetes",
                "guideline_source": "ADA 2023",
                "last_updated": "2023-01-01",
                "diagnostic_criteria": [
                    "HbA1c ≥6.5%",
                    "Fasting glucose ≥126 mg/dL",
                    "2-hour OGTT ≥200 mg/dL",
                    "Random glucose ≥200 mg/dL with symptoms"
                ],
                "first_line_treatment": [
                    "Metformin",
                    "Lifestyle modifications",
                    "Diabetes education"
                ],
                "alternative_treatments": [
                    "GLP-1 receptor agonists",
                    "SGLT-2 inhibitors",
                    "Insulin",
                    "Sulfonylureas"
                ],
                "follow_up_recommendations": [
                    "HbA1c every 3 months initially",
                    "Every 6 months when stable",
                    "Annual comprehensive exam"
                ],
                "referral_indications": [
                    "HbA1c >9% at diagnosis",
                    "Difficult to control",
                    "Complications present"
                ],
                "prevention_strategies": [
                    "Weight management",
                    "Regular physical activity",
                    "Healthy diet",
                    "Regular screening"
                ]
            }
        ]
        
        for guideline_data in guidelines_data:
            guideline = ClinicalGuideline(**guideline_data)
            self.clinical_guidelines[guideline_data["condition"]] = guideline
        
        logger.info(f"Loaded {len(guidelines_data)} clinical guidelines")
    
    async def _build_interaction_matrix(self):
        """Build drug-drug interaction matrix"""
        # Major drug interactions
        interactions = [
            ("warfarin", "aspirin", "Major - Increased bleeding risk"),
            ("warfarin", "ibuprofen", "Major - Increased bleeding risk"),
            ("lisinopril", "ibuprofen", "Moderate - Decreased antihypertensive effect"),
            ("metformin", "contrast_dye", "Major - Increased lactic acidosis risk"),
            ("acetaminophen", "warfarin", "Moderate - Increased INR with chronic use"),
        ]
        
        for drug1, drug2, interaction in interactions:
            self.interaction_matrix[(drug1, drug2)] = interaction
            self.interaction_matrix[(drug2, drug1)] = interaction
        
        logger.info(f"Built interaction matrix with {len(interactions)} interactions")
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    async def get_drug_information(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive drug information"""
        try:
            if not self._initialized:
                await self.initialize()
            
            drug_key = drug_name.lower().strip()
            
            if drug_key in self.drug_database:
                drug_info = self.drug_database[drug_key]
                return asdict(drug_info)
            
            # If not in database, try AI-powered lookup
            return await self._ai_drug_lookup(drug_name)
            
        except Exception as e:
            logger.error(f"Error getting drug information for {drug_name}: {e}")
            return None
    
    async def _ai_drug_lookup(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """AI-powered drug information lookup"""
        try:
            if not ai_service.is_initialized():
                await ai_service.initialize()
            
            prompt = f"""
            Provide comprehensive information about the medication "{drug_name}" in the following JSON format:
            {{
                "name": "generic name",
                "generic_name": "generic name",
                "brand_names": ["brand1", "brand2"],
                "drug_class": "therapeutic class",
                "mechanism_of_action": "how it works",
                "indications": ["indication1", "indication2"],
                "contraindications": ["contraindication1", "contraindication2"],
                "common_side_effects": ["side_effect1", "side_effect2"],
                "serious_side_effects": ["serious_effect1", "serious_effect2"],
                "interactions": ["drug1", "drug2"],
                "dosage_forms": ["tablet", "capsule"],
                "pregnancy_category": "category",
                "half_life": "duration",
                "monitoring_required": ["parameter1", "parameter2"]
            }}
            
            Only provide information for FDA-approved medications. If the drug name is not recognized, return null.
            """
            
            result = await ai_service.process_chat_message(prompt, include_sources=False)
            response_text = result.get("response", "")
            
            try:
                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    drug_data = json.loads(json_str)
                    
                    # Cache the result
                    drug_info = DrugInfo(**drug_data)
                    self.drug_database[drug_name.lower()] = drug_info
                    
                    return drug_data
                    
            except json.JSONDecodeError:
                logger.warning(f"Could not parse AI drug lookup response for {drug_name}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in AI drug lookup for {drug_name}: {e}")
            return None
    
    async def check_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """Check for drug-drug interactions"""
        try:
            if not self._initialized:
                await self.initialize()
            
            interactions = []
            warnings = []
            
            # Check known interactions
            for i, med1 in enumerate(medications):
                for med2 in medications[i+1:]:
                    key1 = med1.lower().strip()
                    key2 = med2.lower().strip()
                    
                    interaction = self.interaction_matrix.get((key1, key2))
                    if interaction:
                        interactions.append({
                            "drug1": med1,
                            "drug2": med2,
                            "interaction": interaction,
                            "severity": self._classify_interaction_severity(interaction)
                        })
            
            # AI-powered interaction check for unknown combinations
            if len(medications) > 1:
                ai_interactions = await self._ai_interaction_check(medications)
                if ai_interactions:
                    interactions.extend(ai_interactions)
            
            # Generate warnings based on interactions
            for interaction in interactions:
                if interaction["severity"] in ["Major", "Critical"]:
                    warnings.append(f"⚠️ {interaction['severity']} interaction between {interaction['drug1']} and {interaction['drug2']}: {interaction['interaction']}")
            
            return {
                "interactions": interactions,
                "warnings": warnings,
                "total_interactions": len(interactions),
                "has_major_interactions": any(i["severity"] in ["Major", "Critical"] for i in interactions)
            }
            
        except Exception as e:
            logger.error(f"Error checking drug interactions: {e}")
            return {
                "error": str(e),
                "interactions": [],
                "warnings": ["Error checking interactions - consult pharmacist"],
                "total_interactions": 0,
                "has_major_interactions": False
            }
    
    def _classify_interaction_severity(self, interaction_text: str) -> str:
        """Classify interaction severity based on text"""
        interaction_lower = interaction_text.lower()
        
        if any(word in interaction_lower for word in ["critical", "life-threatening", "contraindicated"]):
            return "Critical"
        elif any(word in interaction_lower for word in ["major", "severe", "significant"]):
            return "Major"
        elif any(word in interaction_lower for word in ["moderate", "caution"]):
            return "Moderate"
        else:
            return "Minor"
    
    async def _ai_interaction_check(self, medications: List[str]) -> List[Dict[str, Any]]:
        """AI-powered drug interaction checking"""
        try:
            if not ai_service.is_initialized():
                await ai_service.initialize()
            
            medications_str = ", ".join(medications)
            
            prompt = f"""
            Check for drug-drug interactions among these medications: {medications_str}
            
            Provide the response in JSON format:
            {{
                "interactions": [
                    {{
                        "drug1": "medication name",
                        "drug2": "medication name", 
                        "interaction": "description of interaction",
                        "severity": "Minor|Moderate|Major|Critical"
                    }}
                ]
            }}
            
            Only include clinically significant interactions. If no interactions, return empty array.
            """
            
            result = await ai_service.process_chat_message(prompt, include_sources=False)
            response_text = result.get("response", "")
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    interaction_data = json.loads(json_str)
                    return interaction_data.get("interactions", [])
                    
            except json.JSONDecodeError:
                logger.warning("Could not parse AI interaction check response")
            
            return []
            
        except Exception as e:
            logger.error(f"Error in AI interaction check: {e}")
            return []
    
    async def analyze_symptom_pattern(self, symptoms: List[str]) -> Dict[str, Any]:
        """Analyze symptom patterns for clinical insights"""
        try:
            if not self._initialized:
                await self.initialize()
            
            analysis = {
                "recognized_patterns": [],
                "urgency_assessment": "non_urgent",
                "red_flags": [],
                "clinical_correlations": [],
                "examination_recommendations": [],
                "follow_up_needed": []
            }
            
            for symptom in symptoms:
                symptom_key = symptom.lower().replace(" ", "_")
                
                if symptom_key in self.symptom_patterns:
                    pattern = self.symptom_patterns[symptom_key]
                    
                    analysis["recognized_patterns"].append({
                        "symptom": pattern.symptom,
                        "associated_conditions": pattern.associated_conditions[:5],  # Top 5
                        "red_flags": pattern.red_flag_features,
                        "typical_onset": pattern.typical_onset
                    })
                    
                    # Check for red flags
                    analysis["red_flags"].extend(pattern.red_flag_features)
                    analysis["examination_recommendations"].extend(pattern.examination_findings)
            
            # Assess overall urgency
            all_red_flags = set(analysis["red_flags"])
            emergency_flags = {"sudden onset", "severe pain", "difficulty breathing", "chest pain", "loss of consciousness"}
            
            if any(flag in " ".join(all_red_flags).lower() for flag in emergency_flags):
                analysis["urgency_assessment"] = "emergency"
            elif len(all_red_flags) > 2:
                analysis["urgency_assessment"] = "urgent"
            elif len(all_red_flags) > 0:
                analysis["urgency_assessment"] = "semi_urgent"
            
            # Remove duplicates
            analysis["red_flags"] = list(set(analysis["red_flags"]))
            analysis["examination_recommendations"] = list(set(analysis["examination_recommendations"]))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing symptom patterns: {e}")
            return {"error": str(e)}
    
    async def get_clinical_guideline(self, condition: str) -> Optional[Dict[str, Any]]:
        """Get clinical practice guidelines for a condition"""
        try:
            if not self._initialized:
                await self.initialize()
            
            condition_key = condition.lower().replace(" ", "_")
            
            if condition_key in self.clinical_guidelines:
                guideline = self.clinical_guidelines[condition_key]
                return asdict(guideline)
            
            # AI-powered guideline lookup for conditions not in database
            return await self._ai_guideline_lookup(condition)
            
        except Exception as e:
            logger.error(f"Error getting clinical guideline for {condition}: {e}")
            return None
    
    async def _ai_guideline_lookup(self, condition: str) -> Optional[Dict[str, Any]]:
        """AI-powered clinical guideline lookup"""
        try:
            if not ai_service.is_initialized():
                await ai_service.initialize()
            
            prompt = f"""
            Provide current clinical practice guidelines for "{condition}" in JSON format:
            {{
                "condition": "condition name",
                "guideline_source": "professional organization/year",
                "last_updated": "YYYY-MM-DD",
                "diagnostic_criteria": ["criterion1", "criterion2"],
                "first_line_treatment": ["treatment1", "treatment2"],
                "alternative_treatments": ["alt1", "alt2"],
                "follow_up_recommendations": ["followup1", "followup2"],
                "referral_indications": ["indication1", "indication2"],
                "prevention_strategies": ["strategy1", "strategy2"]
            }}
            
            Use evidence-based guidelines from reputable medical organizations. If no established guidelines exist, return null.
            """
            
            result = await ai_service.process_chat_message(prompt, include_sources=False)
            response_text = result.get("response", "")
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    guideline_data = json.loads(json_str)
                    
                    # Cache the result
                    guideline = ClinicalGuideline(**guideline_data)
                    self.clinical_guidelines[condition.lower().replace(" ", "_")] = guideline
                    
                    return guideline_data
                    
            except json.JSONDecodeError:
                logger.warning(f"Could not parse AI guideline lookup response for {condition}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in AI guideline lookup for {condition}: {e}")
            return None
    
    async def emergency_protocols(self, symptoms: List[str], severity: str = "unknown") -> Dict[str, Any]:
        """Provide emergency protocols and triage guidance"""
        try:
            emergency_keywords = [
                "chest pain", "difficulty breathing", "unconscious", "severe bleeding",
                "stroke symptoms", "severe allergic reaction", "poisoning", "overdose"
            ]
            
            symptoms_text = " ".join(symptoms).lower()
            is_emergency = any(keyword in symptoms_text for keyword in emergency_keywords)
            
            if is_emergency or severity.lower() in ["severe", "critical"]:
                return {
                    "emergency_level": "CRITICAL",
                    "immediate_actions": [
                        "🚨 CALL 911 IMMEDIATELY",
                        "Do not delay seeking emergency medical care",
                        "If conscious, keep person calm and comfortable",
                        "Monitor breathing and pulse if trained",
                        "Do not give food, water, or medications unless directed by emergency services"
                    ],
                    "warning": "This appears to be a medical emergency. Professional evaluation is required immediately.",
                    "do_not_wait": True,
                    "estimated_response_time": "0-15 minutes"
                }
            
            # Semi-urgent conditions
            urgent_keywords = ["severe pain", "high fever", "persistent vomiting", "severe headache"]
            is_urgent = any(keyword in symptoms_text for keyword in urgent_keywords)
            
            if is_urgent:
                return {
                    "emergency_level": "URGENT",
                    "immediate_actions": [
                        "Seek medical attention within 2-4 hours",
                        "Consider urgent care or emergency department",
                        "Monitor symptoms closely",
                        "Contact healthcare provider",
                        "Do not drive yourself if symptoms impair ability"
                    ],
                    "warning": "These symptoms require prompt medical evaluation.",
                    "do_not_wait": False,
                    "estimated_response_time": "2-4 hours"
                }
            
            return {
                "emergency_level": "NON_URGENT",
                "immediate_actions": [
                    "Schedule appointment with healthcare provider",
                    "Monitor symptoms for changes",
                    "Implement appropriate self-care measures",
                    "Seek care if symptoms worsen"
                ],
                "warning": "Routine medical evaluation recommended.",
                "do_not_wait": False,
                "estimated_response_time": "24-48 hours"
            }
            
        except Exception as e:
            logger.error(f"Error in emergency protocols: {e}")
            return {
                "emergency_level": "UNKNOWN",
                "immediate_actions": ["Consult healthcare provider for proper evaluation"],
                "warning": "Unable to assess - seek medical advice",
                "error": str(e)
            }

# Global medical knowledge service instance
medical_knowledge_service = MedicalKnowledgeService()

__all__ = ["medical_knowledge_service", "MedicalKnowledgeService", "SeverityLevel", "UrgencyLevel"]