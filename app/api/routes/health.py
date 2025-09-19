"""
Health Monitoring API routes
Handles vitals tracking, health trends, and monitoring endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from ...services.health_monitoring_service import health_monitoring_service, VitalType, AlertLevel
from ...models import User
from .auth import get_current_user

router = APIRouter(prefix="/health", tags=["health-monitoring"])

@router.post("/vitals/record")
async def record_vital_sign(
    vital_type: VitalType,
    value: Union[float, Dict[str, float]],
    notes: Optional[str] = None,
    source: str = "manual",
    current_user: User = Depends(get_current_user)
):
    """Record a vital sign reading"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        result = await health_monitoring_service.record_vital(
            user_id=str(current_user.id),
            vital_type=vital_type,
            value=value,
            notes=notes,
            source=source
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to record vital"))
        
        return {
            "message": "Vital sign recorded successfully",
            "vital_id": result["vital_id"],
            "analysis": result["analysis"],
            "alerts": result["alerts"],
            "recorded_at": result["recorded_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vitals/{vital_type}/history")
async def get_vital_history(
    vital_type: VitalType,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """Get vital sign history"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        history = await health_monitoring_service.get_vital_history(
            user_id=str(current_user.id),
            vital_type=vital_type,
            days=days
        )
        
        return {
            "vital_type": vital_type.value,
            "period_days": days,
            "readings": history,
            "total_readings": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vitals/{vital_type}/trends")
async def get_health_trends(
    vital_type: VitalType,
    days: int = Query(30, ge=7, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user)
):
    """Analyze health trends for a specific vital type"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        trends = await health_monitoring_service.analyze_health_trends(
            user_id=str(current_user.id),
            vital_type=vital_type,
            days=days
        )
        
        return trends
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_health_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive health dashboard"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        dashboard = await health_monitoring_service.get_health_dashboard(
            user_id=str(current_user.id)
        )
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_health_alerts(
    days: int = Query(7, ge=1, le=30, description="Days to retrieve alerts"),
    alert_level: Optional[AlertLevel] = Query(None, description="Filter by alert severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    current_user: User = Depends(get_current_user)
):
    """Get health monitoring alerts"""
    try:
        from ...core.database import db
        from datetime import timedelta
        
        # Build query
        query = {
            "user_id": str(current_user.id),
            "timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}
        }
        
        if alert_level:
            query["alert_level"] = alert_level.value
        
        if acknowledged is not None:
            query["acknowledged"] = acknowledged
        
        # Get alerts
        cursor = db.health_alerts.find(query).sort("timestamp", -1)
        alerts = await cursor.to_list(length=None)
        
        # Format response
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
            alert["timestamp"] = alert["timestamp"].isoformat()
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "period_days": days,
            "filters": {
                "alert_level": alert_level.value if alert_level else None,
                "acknowledged": acknowledged
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a health alert"""
    try:
        from ...core.database import db
        from bson import ObjectId
        
        result = await db.health_alerts.update_one(
            {"_id": ObjectId(alert_id), "user_id": str(current_user.id)},
            {"$set": {"acknowledged": True, "acknowledged_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert acknowledged successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vitals/bulk-record")
async def bulk_record_vitals(
    readings: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """Record multiple vital signs at once"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        results = []
        errors = []
        
        for reading in readings:
            try:
                vital_type = VitalType(reading["vital_type"])
                value = reading["value"]
                notes = reading.get("notes")
                source = reading.get("source", "manual")
                
                result = await health_monitoring_service.record_vital(
                    user_id=str(current_user.id),
                    vital_type=vital_type,
                    value=value,
                    notes=notes,
                    source=source
                )
                
                if result.get("success"):
                    results.append({
                        "vital_type": vital_type.value,
                        "vital_id": result["vital_id"],
                        "recorded_at": result["recorded_at"]
                    })
                else:
                    errors.append({
                        "vital_type": vital_type.value,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                errors.append({
                    "vital_type": reading.get("vital_type", "unknown"),
                    "error": str(e)
                })
        
        return {
            "message": f"Processed {len(readings)} readings",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vitals/summary")
async def get_vitals_summary(
    days: int = Query(30, ge=1, le=365, description="Summary period in days"),
    current_user: User = Depends(get_current_user)
):
    """Get summary of all vital signs"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        summary = {}
        vital_types = [VitalType.BLOOD_PRESSURE, VitalType.HEART_RATE, VitalType.WEIGHT, 
                      VitalType.BLOOD_GLUCOSE, VitalType.TEMPERATURE, VitalType.OXYGEN_SATURATION]
        
        for vital_type in vital_types:
            try:
                history = await health_monitoring_service.get_vital_history(
                    user_id=str(current_user.id),
                    vital_type=vital_type,
                    days=days
                )
                
                if history:
                    latest = history[0]  # Most recent reading
                    trends = await health_monitoring_service.analyze_health_trends(
                        user_id=str(current_user.id),
                        vital_type=vital_type,
                        days=days
                    )
                    
                    summary[vital_type.value] = {
                        "latest_reading": {
                            "value": latest["value"],
                            "timestamp": latest["timestamp"],
                            "unit": latest["unit"]
                        },
                        "total_readings": len(history),
                        "trend": {
                            "direction": trends.get("trend_direction", "stable"),
                            "change_percentage": trends.get("change_percentage", 0)
                        }
                    }
                else:
                    summary[vital_type.value] = {
                        "latest_reading": None,
                        "total_readings": 0,
                        "trend": {"direction": "no_data", "change_percentage": 0}
                    }
                    
            except Exception as e:
                summary[vital_type.value] = {"error": str(e)}
        
        return {
            "summary": summary,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_health_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Get personalized health recommendations"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        # Get dashboard data for recommendations
        dashboard = await health_monitoring_service.get_health_dashboard(
            user_id=str(current_user.id)
        )
        
        recommendations = dashboard.get("recommendations", [])
        health_score = dashboard.get("health_score", 0)
        
        # Categorize recommendations
        categorized_recommendations = {
            "immediate_action": [],
            "lifestyle_changes": [],
            "monitoring": [],
            "general_wellness": []
        }
        
        for rec in recommendations:
            rec_lower = rec.lower()
            if any(word in rec_lower for word in ["emergency", "immediate", "urgent", "call"]):
                categorized_recommendations["immediate_action"].append(rec)
            elif any(word in rec_lower for word in ["diet", "exercise", "lifestyle", "sleep"]):
                categorized_recommendations["lifestyle_changes"].append(rec)
            elif any(word in rec_lower for word in ["monitor", "track", "measure", "check"]):
                categorized_recommendations["monitoring"].append(rec)
            else:
                categorized_recommendations["general_wellness"].append(rec)
        
        return {
            "health_score": health_score,
            "recommendations": categorized_recommendations,
            "total_recommendations": len(recommendations),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_health_data(
    days: int = Query(90, ge=1, le=365, description="Days of data to export"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    current_user: User = Depends(get_current_user)
):
    """Export health monitoring data"""
    try:
        if not health_monitoring_service.is_initialized():
            await health_monitoring_service.initialize()
        
        # Collect all vital data
        export_data = {
            "user_id": str(current_user.id),
            "export_date": datetime.utcnow().isoformat(),
            "period_days": days,
            "vitals": {}
        }
        
        vital_types = [VitalType.BLOOD_PRESSURE, VitalType.HEART_RATE, VitalType.WEIGHT, 
                      VitalType.BLOOD_GLUCOSE, VitalType.TEMPERATURE, VitalType.OXYGEN_SATURATION]
        
        for vital_type in vital_types:
            history = await health_monitoring_service.get_vital_history(
                user_id=str(current_user.id),
                vital_type=vital_type,
                days=days
            )
            export_data["vitals"][vital_type.value] = history
        
        if format == "json":
            return export_data
        else:
            # CSV format would require additional processing
            # For now, return JSON with message
            return {
                "message": "CSV export not yet implemented",
                "data": export_data
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]