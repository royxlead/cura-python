"""
Advanced AI Service for Medical Assistance
Provides specialized medical AI capabilities including differential diagnosis,
drug interactions, symptom analysis, and medical document processing
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI service for LLM and RAG operations"""
    
    def __init__(self):
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.vector_store: Optional[FAISS] = None
        self.qa_chain: Optional[RetrievalQA] = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize AI components"""
        if self._initialized:
            return
        
        try:
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.gemini_api_key,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={"device": "cpu"}
            )
            
            # Load vector store if available
            await self._load_vector_store()
            
            # Setup QA chain
            if self.vector_store:
                self._setup_qa_chain()
            
            self._initialized = True
            logger.info("AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"AI service initialization failed: {e}")
            raise
    
    async def _load_vector_store(self) -> None:
        """Load FAISS vector store"""
        try:
            if settings.vector_store_path.exists():
                self.vector_store = FAISS.load_local(
                    str(settings.vector_store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Vector store loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load vector store: {e}")
    
    def _setup_qa_chain(self) -> None:
        """Setup retrieval QA chain"""
        prompt_template = """
        You are Cura, a knowledgeable medical AI assistant. Use the provided context to answer medical questions accurately and professionally.
        
        Context: {context}
        
        Question: {question}
        
        Guidelines:
        - Provide accurate, evidence-based information
        - Include relevant medical disclaimers
        - Suggest consulting healthcare professionals when appropriate
        - Be empathetic and supportive
        - Use clear, understandable language
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    async def process_chat_message(
        self, 
        message: str, 
        include_sources: bool = True,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process chat message and return response"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.qa_chain:
                # Use RAG pipeline
                result = self.qa_chain.invoke({"query": message})
                
                sources = []
                if include_sources and "source_documents" in result:
                    sources = [
                        {
                            "content": doc.page_content[:200] + "...",
                            "metadata": doc.metadata
                        }
                        for doc in result["source_documents"]
                    ]
                
                return {
                    "response": result["result"],
                    "sources": sources,
                    "method": "rag"
                }
            else:
                # Direct LLM response
                if temperature:
                    # Create temporary LLM with different temperature
                    temp_llm = ChatGoogleGenerativeAI(
                        model=settings.llm_model,
                        google_api_key=settings.gemini_api_key,
                        temperature=temperature,
                        max_tokens=settings.llm_max_tokens
                    )
                    response = await temp_llm.ainvoke(message)
                else:
                    response = await self.llm.ainvoke(message)
                
                return {
                    "response": response.content,
                    "sources": [],
                    "method": "direct"
                }
                
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "sources": [],
                "method": "error",
                "error": str(e)
            }
    
    async def analyze_symptoms(self, symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze symptoms and provide recommendations"""
        if not self._initialized:
            await self.initialize()
        
        symptoms_text = "\n".join([
            f"- {s.get('name', 'Unknown')}: {s.get('description', '')} (Severity: {s.get('severity', 'unknown')})"
            for s in symptoms
        ])
        
        prompt = f"""
        As a medical AI assistant, analyze these symptoms and provide recommendations:
        
        Symptoms:
        {symptoms_text}
        
        Please provide:
        1. Possible conditions to consider
        2. Recommended actions
        3. Urgency level
        4. When to seek medical attention
        
        Remember to include appropriate medical disclaimers.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return result
    
    async def check_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """Check for drug interactions"""
        if not self._initialized:
            await self.initialize()
        
        meds_text = ", ".join(medications)
        
        prompt = f"""
        Analyze potential drug interactions for these medications:
        {meds_text}
        
        Please provide:
        1. Known interactions between these medications
        2. Severity levels of interactions
        3. Recommendations for safe use
        4. When to consult a healthcare provider
        
        Include appropriate medical disclaimers about consulting healthcare professionals.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return result
    
    async def differential_diagnosis(
        self, 
        symptoms: List[str], 
        patient_history: Optional[Dict[str, Any]] = None,
        demographics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advanced differential diagnosis with medical reasoning"""
        if not self._initialized:
            await self.initialize()
        
        # Build comprehensive prompt with medical reasoning structure
        demographics_text = ""
        if demographics:
            age = demographics.get("age", "not specified")
            gender = demographics.get("gender", "not specified")
            demographics_text = f"Patient: {age} years old, {gender}"
        
        history_text = ""
        if patient_history:
            medical_history = patient_history.get("conditions", [])
            medications = patient_history.get("medications", [])
            allergies = patient_history.get("allergies", [])
            
            if medical_history:
                history_text += f"Medical History: {', '.join(medical_history)}\n"
            if medications:
                history_text += f"Current Medications: {', '.join(medications)}\n"
            if allergies:
                history_text += f"Allergies: {', '.join(allergies)}\n"
        
        symptoms_text = "\n".join([f"- {symptom}" for symptom in symptoms])
        
        prompt = f"""
        Perform a systematic differential diagnosis analysis:
        
        {demographics_text}
        
        {history_text}
        
        Presenting Symptoms:
        {symptoms_text}
        
        Please provide a structured analysis:
        
        1. PRIMARY DIFFERENTIAL DIAGNOSES (most likely):
           - List top 3-5 conditions with brief rationale
           - Include probability assessment (high/medium/low likelihood)
        
        2. RED FLAG SYMPTOMS (if present):
           - Identify any concerning symptoms requiring immediate attention
           - Explain why they're significant
        
        3. ADDITIONAL INFORMATION NEEDED:
           - What additional symptoms to assess
           - What physical exam findings would be helpful
           - What diagnostic tests might be indicated
        
        4. CLINICAL REASONING:
           - Explain the thought process
           - Discuss why certain conditions are more/less likely
        
        5. IMMEDIATE RECOMMENDATIONS:
           - Urgency level (emergency, urgent, routine)
           - Next steps for patient
        
        MEDICAL DISCLAIMER: This analysis is for educational purposes only and should not replace professional medical evaluation. Recommend consultation with qualified healthcare provider for diagnosis and treatment decisions.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return {
            "analysis": result["response"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat(),
            "type": "differential_diagnosis"
        }
    
    async def medication_analysis(
        self, 
        medications: List[Dict[str, Any]], 
        patient_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive medication analysis including interactions, contraindications, and optimization"""
        if not self._initialized:
            await self.initialize()
        
        # Format medication list
        med_details = []
        for med in medications:
            name = med.get("name", "Unknown")
            dose = med.get("dose", "not specified")
            frequency = med.get("frequency", "not specified")
            med_details.append(f"- {name} {dose} {frequency}")
        
        medications_text = "\n".join(med_details)
        
        profile_text = ""
        if patient_profile:
            age = patient_profile.get("age", "not specified")
            conditions = patient_profile.get("conditions", [])
            allergies = patient_profile.get("allergies", [])
            
            profile_text = f"""
            Patient Profile:
            - Age: {age}
            - Medical Conditions: {', '.join(conditions) if conditions else 'None reported'}
            - Known Allergies: {', '.join(allergies) if allergies else 'None reported'}
            """
        
        prompt = f"""
        Perform comprehensive medication analysis:
        
        {profile_text}
        
        Current Medications:
        {medications_text}
        
        Please analyze:
        
        1. DRUG INTERACTIONS:
           - Drug-drug interactions (severity: major/moderate/minor)
           - Clinical significance and mechanism
           - Management recommendations
        
        2. CONTRAINDICATIONS & PRECAUTIONS:
           - Age-related considerations
           - Condition-specific contraindications
           - Allergy cross-reactivity risks
        
        3. DOSING OPTIMIZATION:
           - Appropriate dosing for patient profile
           - Timing and administration considerations
           - Potential dose adjustments needed
        
        4. THERAPEUTIC MONITORING:
           - Parameters to monitor
           - Frequency of monitoring
           - Warning signs to watch for
        
        5. MEDICATION SAFETY:
           - Common side effects
           - Serious adverse reactions to monitor
           - Patient education points
        
        6. OPTIMIZATION OPPORTUNITIES:
           - More effective alternatives
           - Cost-effective options
           - Simplified regimens
        
        MEDICAL DISCLAIMER: This analysis is for informational purposes. All medication decisions should be made in consultation with qualified healthcare professionals who can assess the complete clinical picture.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return {
            "analysis": result["response"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat(),
            "type": "medication_analysis"
        }
    
    async def medical_document_analysis(self, document_text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze medical documents (lab results, reports, etc.)"""
        if not self._initialized:
            await self.initialize()
        
        analysis_prompts = {
            "lab_results": """
            Analyze these laboratory results:
            
            {document_text}
            
            Please provide:
            1. ABNORMAL VALUES:
               - List values outside normal ranges
               - Clinical significance of each abnormality
               - Potential causes
            
            2. PATTERNS & TRENDS:
               - Overall pattern interpretation
               - Related abnormalities
               - System-based analysis
            
            3. CLINICAL CORRELATIONS:
               - What conditions these results might suggest
               - Additional tests that might be helpful
               - Follow-up recommendations
            
            4. PATIENT COMMUNICATION:
               - How to explain results in simple terms
               - What questions patients might ask
               - Reassurance or concern level
            """,
            
            "radiology": """
            Analyze this radiology report:
            
            {document_text}
            
            Please provide:
            1. KEY FINDINGS:
               - Normal findings
               - Abnormal findings with significance
               - Incidental findings
            
            2. CLINICAL IMPLICATIONS:
               - What these findings suggest
               - Urgency of findings
               - Need for follow-up imaging
            
            3. DIFFERENTIAL CONSIDERATIONS:
               - Possible diagnoses based on findings
               - Additional imaging that might help
               - Clinical correlation needed
            
            4. PATIENT EXPLANATION:
               - Simplified explanation of findings
               - Prognosis implications
               - Next steps
            """,
            
            "general": """
            Analyze this medical document:
            
            {document_text}
            
            Please provide:
            1. DOCUMENT SUMMARY:
               - Key medical information
               - Important findings or recommendations
               - Action items
            
            2. CLINICAL SIGNIFICANCE:
               - What this means for patient care
               - Priority level of information
               - Impact on treatment decisions
            
            3. QUESTIONS TO ASK:
               - Important follow-up questions
               - Clarifications needed
               - Additional information to gather
            
            4. PATIENT EDUCATION:
               - How to explain this information
               - Key points for patient understanding
               - Resources for more information
            """
        }
        
        prompt_template = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        prompt = prompt_template.format(document_text=document_text)
        
        prompt += "\n\nMEDICAL DISCLAIMER: This analysis is for educational purposes only. All medical documents should be reviewed by qualified healthcare professionals for clinical decision-making."
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return {
            "analysis": result["response"],
            "document_type": analysis_type,
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat(),
            "type": "document_analysis"
        }
    
    async def health_risk_assessment(
        self, 
        risk_factors: Dict[str, Any], 
        family_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive health risk assessment"""
        if not self._initialized:
            await self.initialize()
        
        # Format risk factors
        risk_text = []
        for category, factors in risk_factors.items():
            if isinstance(factors, list):
                risk_text.append(f"{category.title()}: {', '.join(map(str, factors))}")
            else:
                risk_text.append(f"{category.title()}: {factors}")
        
        family_text = ""
        if family_history:
            family_text = f"Family History: {', '.join(family_history)}"
        
        prompt = f"""
        Perform comprehensive health risk assessment:
        
        Risk Factors:
        {chr(10).join(risk_text)}
        
        {family_text}
        
        Please analyze:
        
        1. CARDIOVASCULAR RISK:
           - Risk factors present
           - Estimated risk level
           - Prevention strategies
        
        2. CANCER SCREENING:
           - Age-appropriate screenings
           - Family history considerations
           - Risk-based recommendations
        
        3. METABOLIC HEALTH:
           - Diabetes risk factors
           - Thyroid considerations
           - Metabolic syndrome indicators
        
        4. LIFESTYLE MODIFICATIONS:
           - Diet recommendations
           - Exercise prescriptions
           - Stress management
           - Sleep hygiene
        
        5. PREVENTIVE CARE:
           - Recommended screenings and timeline
           - Vaccinations needed
           - Health monitoring schedule
        
        6. RISK REDUCTION STRATEGIES:
           - Modifiable risk factors
           - Specific interventions
           - Monitoring parameters
        
        MEDICAL DISCLAIMER: This assessment is for educational purposes only. Comprehensive health evaluations should be performed by qualified healthcare professionals who can assess individual risk factors and medical history.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return {
            "assessment": result["response"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat(),
            "type": "risk_assessment"
        }
    
    async def treatment_planning(
        self, 
        diagnosis: str, 
        patient_factors: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate evidence-based treatment planning recommendations"""
        if not self._initialized:
            await self.initialize()
        
        # Format patient factors
        factors_text = []
        for factor, value in patient_factors.items():
            factors_text.append(f"- {factor.title()}: {value}")
        
        preferences_text = ""
        if preferences:
            pref_list = []
            for pref, value in preferences.items():
                pref_list.append(f"- {pref.title()}: {value}")
            preferences_text = f"Patient Preferences:\n{chr(10).join(pref_list)}"
        
        prompt = f"""
        Develop evidence-based treatment planning recommendations:
        
        Diagnosis/Condition: {diagnosis}
        
        Patient Factors:
        {chr(10).join(factors_text)}
        
        {preferences_text}
        
        Please provide:
        
        1. TREATMENT OPTIONS:
           - First-line treatments with evidence level
           - Alternative treatments
           - Combination therapy considerations
        
        2. PATIENT-SPECIFIC CONSIDERATIONS:
           - Age-appropriate modifications
           - Comorbidity interactions
           - Contraindications to consider
        
        3. SHARED DECISION-MAKING:
           - Benefits and risks of each option
           - Quality of life considerations
           - Patient preference integration
        
        4. MONITORING PLAN:
           - Parameters to track
           - Follow-up schedule
           - Adjustment criteria
        
        5. LIFESTYLE INTERVENTIONS:
           - Non-pharmacological approaches
           - Behavioral modifications
           - Support resources
        
        6. TREATMENT GOALS:
           - Short-term objectives
           - Long-term outcomes
           - Success metrics
        
        MEDICAL DISCLAIMER: Treatment planning must be individualized by qualified healthcare professionals. This information is for educational purposes and should not replace professional medical advice.
        """
        
        result = await self.process_chat_message(prompt, include_sources=True)
        return {
            "plan": result["response"],
            "diagnosis": diagnosis,
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat(),
            "type": "treatment_planning"
        }

    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized

# Global AI service instance
ai_service = AIService()

__all__ = ["ai_service", "AIService"]