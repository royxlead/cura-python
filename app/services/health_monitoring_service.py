"""
Health Monitoring Service
Provides comprehensive health vitals tracking, trend analysis, and personalized health insights
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from bson import ObjectId

from app.core.database import db
from app.models import User
from app.services.ai_service import ai_service
from app.services.medical_knowledge_service import medical_knowledge_service

logger = logging.getLogger(__name__)

class VitalType(str, Enum):
    """Types of vital signs and health metrics"""
    BLOOD_PRESSURE = "blood_pressure"
    HEART_RATE = "heart_rate"
    TEMPERATURE = "temperature"
    WEIGHT = "weight"
    BLOOD_GLUCOSE = "blood_glucose"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    BMI = "bmi"
    SLEEP_HOURS = "sleep_hours"
    STEPS = "steps"
    EXERCISE_MINUTES = "exercise_minutes"

class AlertLevel(str, Enum):
    """Health alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class VitalReading:
    """Individual vital sign reading"""
    vital_type: VitalType
    value: Union[float, Dict[str, float]]  # Dict for BP (systolic/diastolic)
    unit: str
    timestamp: datetime
    notes: Optional[str] = None
    source: str = "manual"  # manual, device, app
    
@dataclass
class HealthAlert:
    """Health monitoring alert"""
    alert_id: str
    user_id: str
    vital_type: VitalType
    alert_level: AlertLevel
    message: str
    recommendations: List[str]
    timestamp: datetime
    acknowledged: bool = False
    
@dataclass
class TrendAnalysis:
    """Health trend analysis results"""
    vital_type: VitalType
    trend_direction: str  # "improving", "stable", "declining", "concerning"
    change_percentage: float
    time_period: str
    significant_changes: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    recommendations: List[str]

class HealthMonitoringService:
    """Comprehensive health monitoring and trend analysis"""
    
    def __init__(self):
        self.vital_ranges = self._initialize_vital_ranges()
        self._initialized = False
        
    async def initialize(self):
        """Initialize health monitoring service"""
        if self._initialized:
            return
            
        logger.info("Initializing Health Monitoring Service...")
        
        try:
            # Ensure medical knowledge service is available
            if not medical_knowledge_service.is_initialized():
                await medical_knowledge_service.initialize()
            
            self._initialized = True
            logger.info("Health Monitoring Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Health Monitoring Service: {e}")
            raise
    
    def _initialize_vital_ranges(self) -> Dict[VitalType, Dict[str, Any]]:
        """Initialize normal ranges for vital signs"""
        return {
            VitalType.BLOOD_PRESSURE: {
                "normal": {"systolic": (90, 120), "diastolic": (60, 80)},
                "elevated": {"systolic": (120, 129), "diastolic": (60, 80)},
                "stage1": {"systolic": (130, 139), "diastolic": (80, 89)},
                "stage2": {"systolic": (140, 180), "diastolic": (90, 120)},
                "crisis": {"systolic": (180, 999), "diastolic": (120, 999)},
                "unit": "mmHg"
            },
            VitalType.HEART_RATE: {
                "bradycardia": (0, 60),
                "normal": (60, 100),
                "tachycardia": (100, 150),
                "severe_tachycardia": (150, 999),
                "unit": "bpm"
            },
            VitalType.TEMPERATURE: {
                "hypothermia": (0, 95.0),
                "normal": (97.0, 99.5),
                "low_fever": (99.5, 100.4),
                "fever": (100.4, 103.0),
                "high_fever": (103.0, 999),
                "unit": "°F"
            },
            VitalType.BLOOD_GLUCOSE: {
                "hypoglycemia": (0, 70),
                "normal": (70, 140),
                "prediabetes": (140, 199),
                "diabetes": (200, 999),
                "unit": "mg/dL"
            },
            VitalType.OXYGEN_SATURATION: {
                "critical": (0, 90),
                "low": (90, 95),
                "normal": (95, 100),
                "unit": "%"
            },
            VitalType.RESPIRATORY_RATE: {
                "low": (0, 12),
                "normal": (12, 20),
                "elevated": (20, 25),
                "high": (25, 999),
                "unit": "breaths/min"
            },
            VitalType.BMI: {
                "underweight": (0, 18.5),
                "normal": (18.5, 24.9),
                "overweight": (25.0, 29.9),
                "obese_class1": (30.0, 34.9),
                "obese_class2": (35.0, 39.9),
                "obese_class3": (40.0, 999),
                "unit": "kg/m²"
            }
        }
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    async def record_vital(
        self, 
        user_id: str, 
        vital_type: VitalType, 
        value: Union[float, Dict[str, float]], 
        notes: Optional[str] = None,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """Record a vital sign reading"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Create vital reading
            vital_reading = VitalReading(
                vital_type=vital_type,
                value=value,
                unit=self.vital_ranges[vital_type]["unit"],
                timestamp=datetime.utcnow(),
                notes=notes,
                source=source
            )
            
            # Store in database
            vital_data = asdict(vital_reading)
            vital_data["user_id"] = user_id
            vital_data["_id"] = ObjectId()
            
            await db.vitals.insert_one(vital_data)
            
            # Analyze the reading
            analysis = await self._analyze_vital_reading(user_id, vital_reading)
            
            # Check for alerts
            alerts = await self._check_vital_alerts(user_id, vital_reading, analysis)
            
            return {
                "success": True,
                "vital_id": str(vital_data["_id"]),
                "analysis": analysis,
                "alerts": alerts,
                "recorded_at": vital_reading.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording vital for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_vital_reading(self, user_id: str, vital_reading: VitalReading) -> Dict[str, Any]:
        """Analyze a single vital reading"""
        try:
            vital_type = vital_reading.vital_type
            value = vital_reading.value
            ranges = self.vital_ranges.get(vital_type, {})
            
            analysis = {
                "category": "unknown",
                "severity": AlertLevel.INFO,
                "message": "",
                "recommendations": []
            }
            
            # Analyze based on vital type
            if vital_type == VitalType.BLOOD_PRESSURE and isinstance(value, dict):
                systolic = value.get("systolic", 0)
                diastolic = value.get("diastolic", 0)
                
                if systolic >= 180 or diastolic >= 120:
                    analysis.update({
                        "category": "crisis",
                        "severity": AlertLevel.CRITICAL,
                        "message": "Hypertensive crisis - seek immediate medical attention",
                        "recommendations": [
                            "🚨 Seek emergency medical care immediately",
                            "Do not delay - call 911 if symptoms present",
                            "Avoid physical exertion"
                        ]
                    })
                elif systolic >= 140 or diastolic >= 90:
                    analysis.update({
                        "category": "stage2",
                        "severity": AlertLevel.HIGH,
                        "message": "Stage 2 hypertension - medical consultation needed",
                        "recommendations": [
                            "Contact healthcare provider within 24-48 hours",
                            "Monitor blood pressure daily",
                            "Review medications and lifestyle factors"
                        ]
                    })
                elif systolic >= 130 or diastolic >= 80:
                    analysis.update({
                        "category": "stage1",
                        "severity": AlertLevel.MEDIUM,
                        "message": "Stage 1 hypertension - lifestyle changes recommended",
                        "recommendations": [
                            "Reduce sodium intake",
                            "Increase physical activity",
                            "Monitor blood pressure regularly"
                        ]
                    })
                else:
                    analysis.update({
                        "category": "normal",
                        "severity": AlertLevel.INFO,
                        "message": "Blood pressure within normal range",
                        "recommendations": ["Continue healthy lifestyle habits"]
                    })
            
            elif vital_type == VitalType.HEART_RATE:
                hr_value = float(value) if not isinstance(value, dict) else value.get("value", 0)
                
                if hr_value < 60:
                    analysis.update({
                        "category": "bradycardia",
                        "severity": AlertLevel.MEDIUM,
                        "message": "Heart rate below normal range",
                        "recommendations": [
                            "Monitor for symptoms (dizziness, fatigue)",
                            "Consider medical evaluation if symptomatic"
                        ]
                    })
                elif hr_value > 150:
                    analysis.update({
                        "category": "severe_tachycardia",
                        "severity": AlertLevel.HIGH,
                        "message": "Significantly elevated heart rate",
                        "recommendations": [
                            "Seek medical attention if persistent",
                            "Avoid stimulants",
                            "Monitor for other symptoms"
                        ]
                    })
                elif hr_value > 100:
                    analysis.update({
                        "category": "tachycardia",
                        "severity": AlertLevel.LOW,
                        "message": "Heart rate slightly elevated",
                        "recommendations": [
                            "Consider rest and hydration",
                            "Monitor if persistent"
                        ]
                    })
                else:
                    analysis.update({
                        "category": "normal",
                        "severity": AlertLevel.INFO,
                        "message": "Heart rate within normal range"
                    })
            
            # Add personalized context
            analysis["personalized_insights"] = await self._get_personalized_insights(user_id, vital_reading)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing vital reading: {e}")
            return {"error": str(e)}
    
    async def _get_personalized_insights(self, user_id: str, vital_reading: VitalReading) -> List[str]:
        """Get personalized insights based on user history"""
        try:
            # Get recent readings for comparison
            recent_readings = await self.get_vital_history(
                user_id, 
                vital_reading.vital_type, 
                days=30
            )
            
            insights = []
            
            if len(recent_readings) > 1:
                # Calculate trend
                trend = await self.analyze_health_trends(user_id, vital_reading.vital_type, days=30)
                
                if trend.get("trend_direction") == "improving":
                    insights.append("📈 Your readings show improvement over the past month")
                elif trend.get("trend_direction") == "declining":
                    insights.append("📉 Your readings show a concerning trend - consider medical consultation")
                
                # Compare to personal average
                values = [r["value"] for r in recent_readings if not isinstance(r["value"], dict)]
                if values:
                    avg = statistics.mean(values)
                    current = float(vital_reading.value) if not isinstance(vital_reading.value, dict) else None
                    
                    if current and abs(current - avg) > (avg * 0.1):  # 10% deviation
                        if current > avg:
                            insights.append(f"This reading is {((current - avg) / avg * 100):.1f}% higher than your recent average")
                        else:
                            insights.append(f"This reading is {((avg - current) / avg * 100):.1f}% lower than your recent average")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting personalized insights: {e}")
            return []
    
    async def _check_vital_alerts(
        self, 
        user_id: str, 
        vital_reading: VitalReading, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if vital reading triggers any alerts"""
        try:
            alerts = []
            
            # Create alert if severity is medium or higher
            if analysis.get("severity") in [AlertLevel.MEDIUM, AlertLevel.HIGH, AlertLevel.CRITICAL]:
                alert = HealthAlert(
                    alert_id=str(ObjectId()),
                    user_id=user_id,
                    vital_type=vital_reading.vital_type,
                    alert_level=analysis["severity"],
                    message=analysis["message"],
                    recommendations=analysis.get("recommendations", []),
                    timestamp=datetime.utcnow()
                )
                
                # Store alert in database
                alert_data = asdict(alert)
                await db.health_alerts.insert_one(alert_data)
                
                alerts.append(alert_data)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking vital alerts: {e}")
            return []
    
    async def get_vital_history(
        self, 
        user_id: str, 
        vital_type: VitalType, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get vital sign history for a user"""
        try:
            if not self._initialized:
                await self.initialize()
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            cursor = db.vitals.find({
                "user_id": user_id,
                "vital_type": vital_type.value,
                "timestamp": {"$gte": start_date}
            }).sort("timestamp", -1)
            
            readings = await cursor.to_list(length=None)
            
            # Convert ObjectId to string and format timestamps
            for reading in readings:
                reading["_id"] = str(reading["_id"])
                reading["timestamp"] = reading["timestamp"].isoformat()
            
            return readings
            
        except Exception as e:
            logger.error(f"Error getting vital history: {e}")
            return []
    
    async def analyze_health_trends(
        self, 
        user_id: str, 
        vital_type: VitalType, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze health trends over time"""
        try:
            if not self._initialized:
                await self.initialize()
            
            readings = await self.get_vital_history(user_id, vital_type, days)
            
            if len(readings) < 3:
                return {
                    "trend_direction": "insufficient_data",
                    "message": "Need more readings for trend analysis",
                    "recommendations": [f"Record {vital_type.value} regularly for better insights"]
                }
            
            # Extract values for analysis
            values = []
            timestamps = []
            
            for reading in readings:
                if isinstance(reading["value"], dict):
                    # For blood pressure, use systolic
                    if "systolic" in reading["value"]:
                        values.append(reading["value"]["systolic"])
                else:
                    values.append(float(reading["value"]))
                
                timestamps.append(datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00')))
            
            # Calculate trend
            if len(values) >= 2:
                recent_avg = statistics.mean(values[:len(values)//2])  # First half (most recent)
                older_avg = statistics.mean(values[len(values)//2:])   # Second half (older)
                
                change_percentage = ((recent_avg - older_avg) / older_avg) * 100
                
                # Determine trend direction
                if abs(change_percentage) < 5:
                    trend_direction = "stable"
                elif change_percentage > 5:
                    trend_direction = "increasing" if vital_type != VitalType.WEIGHT else "concerning"
                else:
                    trend_direction = "decreasing"
                
                # Generate insights using AI
                trend_insights = await self._generate_trend_insights(
                    user_id, vital_type, values, change_percentage, trend_direction
                )
                
                return {
                    "vital_type": vital_type.value,
                    "trend_direction": trend_direction,
                    "change_percentage": round(change_percentage, 1),
                    "time_period": f"{days} days",
                    "recent_average": round(recent_avg, 1),
                    "previous_average": round(older_avg, 1),
                    "total_readings": len(values),
                    "insights": trend_insights,
                    "recommendations": await self._get_trend_recommendations(vital_type, trend_direction, change_percentage)
                }
            
            return {"error": "Insufficient data for trend analysis"}
            
        except Exception as e:
            logger.error(f"Error analyzing health trends: {e}")
            return {"error": str(e)}
    
    async def _generate_trend_insights(
        self, 
        user_id: str, 
        vital_type: VitalType, 
        values: List[float], 
        change_percentage: float,
        trend_direction: str
    ) -> List[str]:
        """Generate AI-powered trend insights"""
        try:
            if not ai_service.is_initialized():
                await ai_service.initialize()
            
            # Get user context
            user = await User.get(user_id)
            user_context = ""
            if user:
                user_context = f"Age: {user.age if hasattr(user, 'age') else 'Unknown'}, Gender: {user.gender if hasattr(user, 'gender') else 'Unknown'}"
            
            prompt = f"""
            Analyze this health trend for a patient:
            
            Vital Type: {vital_type.value}
            Trend Direction: {trend_direction}
            Change Percentage: {change_percentage}%
            Recent Values: {values[:5]}  (most recent first)
            Patient Context: {user_context}
            
            Provide 2-3 concise insights about:
            1. What this trend might indicate
            2. Potential contributing factors
            3. Clinical significance
            
            Keep responses practical and patient-friendly.
            """
            
            result = await ai_service.process_chat_message(prompt, include_sources=False)
            
            # Parse insights from response
            response_text = result.get("response", "")
            insights = [insight.strip() for insight in response_text.split('\n') if insight.strip() and len(insight.strip()) > 10]
            
            return insights[:3]  # Limit to 3 insights
            
        except Exception as e:
            logger.error(f"Error generating trend insights: {e}")
            return ["Unable to generate detailed insights at this time"]
    
    async def _get_trend_recommendations(
        self, 
        vital_type: VitalType, 
        trend_direction: str, 
        change_percentage: float
    ) -> List[str]:
        """Get recommendations based on trend analysis"""
        recommendations = []
        
        if vital_type == VitalType.BLOOD_PRESSURE:
            if trend_direction == "increasing":
                recommendations.extend([
                    "Reduce sodium intake to less than 2300mg daily",
                    "Increase physical activity (150 min/week moderate exercise)",
                    "Monitor stress levels and practice relaxation techniques",
                    "Schedule follow-up with healthcare provider"
                ])
            elif trend_direction == "stable":
                recommendations.extend([
                    "Continue current management approach",
                    "Maintain regular monitoring schedule"
                ])
        
        elif vital_type == VitalType.WEIGHT:
            if trend_direction == "increasing" and change_percentage > 5:
                recommendations.extend([
                    "Review caloric intake and portion sizes",
                    "Increase physical activity gradually",
                    "Consider consulting with a nutritionist",
                    "Monitor for other symptoms"
                ])
            elif trend_direction == "decreasing" and change_percentage < -10:
                recommendations.extend([
                    "Ensure adequate caloric intake",
                    "Monitor for other symptoms",
                    "Consider medical evaluation for unintentional weight loss"
                ])
        
        elif vital_type == VitalType.BLOOD_GLUCOSE:
            if trend_direction == "increasing":
                recommendations.extend([
                    "Review carbohydrate intake and timing",
                    "Check medication adherence",
                    "Monitor physical activity levels",
                    "Consider diabetes educator consultation"
                ])
        
        # General recommendations
        if abs(change_percentage) > 15:
            recommendations.append("Discuss significant changes with healthcare provider")
        
        if not recommendations:
            recommendations.append("Continue regular monitoring and healthy lifestyle habits")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def get_health_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive health dashboard data"""
        try:
            if not self._initialized:
                await self.initialize()
            
            dashboard = {
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "vital_summaries": {},
                "recent_alerts": [],
                "health_score": 0,
                "trends": {},
                "recommendations": []
            }
            
            # Get recent readings for each vital type
            vital_types = [VitalType.BLOOD_PRESSURE, VitalType.HEART_RATE, VitalType.WEIGHT, VitalType.BLOOD_GLUCOSE]
            
            for vital_type in vital_types:
                recent_readings = await self.get_vital_history(user_id, vital_type, days=7)
                
                if recent_readings:
                    latest = recent_readings[0]
                    trend = await self.analyze_health_trends(user_id, vital_type, days=30)
                    
                    dashboard["vital_summaries"][vital_type.value] = {
                        "latest_value": latest["value"],
                        "latest_timestamp": latest["timestamp"],
                        "trend_direction": trend.get("trend_direction", "unknown"),
                        "change_percentage": trend.get("change_percentage", 0),
                        "total_readings": len(recent_readings)
                    }
                    
                    dashboard["trends"][vital_type.value] = trend
            
            # Get recent alerts
            alert_cursor = db.health_alerts.find({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).sort("timestamp", -1).limit(5)
            
            dashboard["recent_alerts"] = await alert_cursor.to_list(length=None)
            
            # Calculate health score
            dashboard["health_score"] = await self._calculate_health_score(user_id, dashboard["vital_summaries"])
            
            # Generate personalized recommendations
            dashboard["recommendations"] = await self._generate_dashboard_recommendations(user_id, dashboard)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating health dashboard: {e}")
            return {"error": str(e)}
    
    async def _calculate_health_score(self, user_id: str, vital_summaries: Dict[str, Any]) -> int:
        """Calculate overall health score (0-100)"""
        try:
            score = 100
            deductions = 0
            
            # Deduct points for concerning vitals
            for vital_type, summary in vital_summaries.items():
                trend_direction = summary.get("trend_direction", "stable")
                
                if trend_direction == "concerning":
                    deductions += 20
                elif trend_direction == "increasing" and vital_type in ["blood_pressure", "blood_glucose"]:
                    deductions += 15
                elif trend_direction == "decreasing" and vital_type == "weight":
                    change_pct = abs(summary.get("change_percentage", 0))
                    if change_pct > 10:
                        deductions += 15
            
            # Check for recent alerts
            recent_alerts = await db.health_alerts.find({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)},
                "alert_level": {"$in": [AlertLevel.HIGH.value, AlertLevel.CRITICAL.value]}
            }).count_documents({})
            
            deductions += min(recent_alerts * 10, 30)  # Max 30 points for alerts
            
            return max(score - deductions, 0)
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50  # Default neutral score
    
    async def _generate_dashboard_recommendations(self, user_id: str, dashboard: Dict[str, Any]) -> List[str]:
        """Generate personalized dashboard recommendations"""
        try:
            recommendations = []
            
            # Analyze trends for recommendations
            concerning_trends = []
            for vital_type, trend in dashboard.get("trends", {}).items():
                if trend.get("trend_direction") in ["concerning", "increasing"] and abs(trend.get("change_percentage", 0)) > 10:
                    concerning_trends.append(vital_type)
            
            if concerning_trends:
                recommendations.append(f"Monitor {', '.join(concerning_trends)} more closely - trends show concerning changes")
            
            # Check measurement frequency
            for vital_type, summary in dashboard.get("vital_summaries", {}).items():
                if summary.get("total_readings", 0) < 3:
                    recommendations.append(f"Increase frequency of {vital_type.replace('_', ' ')} measurements for better trend analysis")
            
            # Health score recommendations
            health_score = dashboard.get("health_score", 100)
            if health_score < 70:
                recommendations.append("Consider scheduling a comprehensive health check-up with your healthcare provider")
            elif health_score < 85:
                recommendations.append("Focus on lifestyle improvements to optimize your health metrics")
            
            # Add general wellness recommendations
            if len(recommendations) == 0:
                recommendations.extend([
                    "Great job maintaining your health metrics!",
                    "Continue regular monitoring and healthy lifestyle habits"
                ])
                
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating dashboard recommendations: {e}")
            return ["Continue monitoring your health regularly"]

# Global health monitoring service instance
health_monitoring_service = HealthMonitoringService()

__all__ = ["health_monitoring_service", "HealthMonitoringService", "VitalType", "AlertLevel"]