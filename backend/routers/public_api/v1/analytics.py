"""
Public API v1 - Analytics Endpoints
Advanced analytics and reporting via API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read

router = APIRouter(prefix="/analytics", tags=["Analytics API"])

# Models
class OverviewMetrics(BaseModel):
    total_students: int
    active_students: int
    total_exams: int
    average_score: float
    pass_rate: float
    ai_interactions: int
    period_days: int

class TrendData(BaseModel):
    date: str
    students: int
    exams: int
    avg_score: float

class RiskAnalysis(BaseModel):
    student_id: str
    student_name: str
    risk_level: str  # low, medium, high
    risk_score: float
    factors: List[str]
    recommendation: str

# Endpoints
@router.get("/overview", response_model=OverviewMetrics)
async def get_analytics_overview(
    institution_id: Optional[str] = None,
    period_days: int = Query(30, ge=1, le=365),
    api_auth: dict = Depends(require_read)
):
    """
    Get analytics overview for the platform or a specific institution.
    
    - **institution_id**: Filter by institution (optional)
    - **period_days**: Analysis period in days (default: 30)
    """
    start_date = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    
    # Build queries
    student_query = {"user_type": "student"}
    exam_query = {"created_at": {"$gte": start_date}}
    
    if institution_id:
        student_query["institution_id"] = institution_id
        exam_query["institution_id"] = institution_id
    
    # Student counts
    total_students = await db.users.count_documents(student_query)
    active_query = {**student_query, "last_activity": {"$gte": start_date}}
    active_students = await db.users.count_documents(active_query)
    
    # Exam stats
    total_exams = await db.exam_attempts.count_documents(exam_query)
    
    avg_pipeline = [
        {"$match": exam_query},
        {"$group": {"_id": None, "avg": {"$avg": "$score"}}}
    ]
    avg_result = await db.exam_attempts.aggregate(avg_pipeline).to_list(1)
    average_score = avg_result[0]["avg"] if avg_result else 0
    
    # Pass rate (60% threshold)
    passed_exams = await db.exam_attempts.count_documents({**exam_query, "score": {"$gte": 60}})
    pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0
    
    # AI interactions
    ai_query = {"created_at": {"$gte": start_date}}
    if institution_id:
        ai_query["institution_id"] = institution_id
    ai_interactions = await db.ai_agent_history.count_documents(ai_query)
    
    return OverviewMetrics(
        total_students=total_students,
        active_students=active_students,
        total_exams=total_exams,
        average_score=round(average_score, 2) if average_score else 0,
        pass_rate=round(pass_rate, 2),
        ai_interactions=ai_interactions,
        period_days=period_days
    )

@router.get("/trends", response_model=List[TrendData])
async def get_analytics_trends(
    institution_id: Optional[str] = None,
    period_days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", enum=["day", "week", "month"]),
    api_auth: dict = Depends(require_read)
):
    """
    Get trend data over time.
    
    - **granularity**: Group by day, week, or month
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
    
    # Date format based on granularity
    date_formats = {
        "day": "%Y-%m-%d",
        "week": "%Y-W%U",
        "month": "%Y-%m"
    }
    
    match_stage = {"created_at": {"$gte": start_date.isoformat()}}
    if institution_id:
        match_stage["institution_id"] = institution_id
    
    # Student registrations by date
    student_pipeline = [
        {"$match": {**match_stage, "user_type": "student"}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    student_trends = await db.users.aggregate(student_pipeline).to_list(period_days)
    student_by_date = {s["_id"]: s["count"] for s in student_trends}
    
    # Exam attempts by date
    exam_pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$score"}
        }},
        {"$sort": {"_id": 1}}
    ]
    exam_trends = await db.exam_attempts.aggregate(exam_pipeline).to_list(period_days)
    
    # Combine data
    result = []
    for e in exam_trends:
        result.append(TrendData(
            date=e["_id"],
            students=student_by_date.get(e["_id"], 0),
            exams=e["count"],
            avg_score=round(e["avg_score"], 2) if e["avg_score"] else 0
        ))
    
    return result

@router.get("/at-risk-students", response_model=List[RiskAnalysis])
async def get_at_risk_students(
    institution_id: Optional[str] = None,
    threshold: float = Query(0.6, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    api_auth: dict = Depends(require_read)
):
    """
    Identify students at risk of failing based on multiple factors.
    
    - **threshold**: Risk threshold (0-1, default: 0.6)
    - **limit**: Maximum students to return
    """
    query = {"user_type": "student", "is_active": True}
    if institution_id:
        query["institution_id"] = institution_id
    
    students = await db.users.find(
        query,
        {"_id": 0, "id": 1, "name": 1, "email": 1}
    ).to_list(1000)
    
    at_risk = []
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    for student in students:
        factors = []
        risk_score = 0
        
        # Factor 1: Recent exam performance
        recent_exams = await db.exam_attempts.find(
            {"user_id": student["id"], "created_at": {"$gte": month_ago}},
            {"_id": 0, "score": 1}
        ).to_list(100)
        
        if recent_exams:
            avg_score = sum(e["score"] for e in recent_exams) / len(recent_exams)
            if avg_score < 50:
                risk_score += 0.4
                factors.append(f"Low average score ({avg_score:.1f}%)")
            elif avg_score < 65:
                risk_score += 0.2
                factors.append(f"Below target score ({avg_score:.1f}%)")
        else:
            risk_score += 0.3
            factors.append("No recent exam attempts")
        
        # Factor 2: Activity level
        recent_activity = await db.exam_attempts.count_documents({
            "user_id": student["id"],
            "created_at": {"$gte": week_ago}
        })
        
        if recent_activity == 0:
            risk_score += 0.3
            factors.append("No activity in last 7 days")
        elif recent_activity < 2:
            risk_score += 0.1
            factors.append("Low activity level")
        
        # Factor 3: Score trend
        if len(recent_exams) >= 3:
            scores = [e["score"] for e in recent_exams]
            if scores[-1] < scores[0]:
                risk_score += 0.2
                factors.append("Declining score trend")
        
        # Factor 4: AI tutor usage
        ai_usage = await db.ai_agent_history.count_documents({
            "user_id": student["id"],
            "created_at": {"$gte": month_ago}
        })
        
        if ai_usage == 0:
            risk_score += 0.1
            factors.append("Not using AI tutor resources")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= threshold:
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = "high"
                recommendation = "Immediate intervention needed. Schedule a one-on-one session and create a focused study plan."
            elif risk_score >= 0.6:
                risk_level = "medium"
                recommendation = "Encourage more practice and AI tutor usage. Consider additional support."
            else:
                risk_level = "low"
                recommendation = "Monitor progress. Suggest targeted practice for weak areas."
            
            at_risk.append(RiskAnalysis(
                student_id=student["id"],
                student_name=student["name"],
                risk_level=risk_level,
                risk_score=round(risk_score, 2),
                factors=factors,
                recommendation=recommendation
            ))
    
    # Sort by risk score and limit
    at_risk.sort(key=lambda x: x.risk_score, reverse=True)
    return at_risk[:limit]

@router.get("/cohort-analysis")
async def get_cohort_analysis(
    institution_id: Optional[str] = None,
    cohort_by: str = Query("month", enum=["week", "month", "quarter"]),
    api_auth: dict = Depends(require_read)
):
    """
    Analyze student cohorts by registration date.
    Shows retention and performance metrics per cohort.
    """
    # Get all students grouped by registration cohort
    query = {"user_type": "student"}
    if institution_id:
        query["institution_id"] = institution_id
    
    students = await db.users.find(
        query,
        {"_id": 0, "id": 1, "created_at": 1}
    ).to_list(10000)
    
    # Group by cohort
    cohorts = {}
    for s in students:
        if not s.get("created_at"):
            continue
            
        date = s["created_at"][:10]
        if cohort_by == "week":
            cohort_key = date[:8] + "W" + str(int(date[8:10]) // 7)
        elif cohort_by == "month":
            cohort_key = date[:7]
        else:  # quarter
            month = int(date[5:7])
            quarter = (month - 1) // 3 + 1
            cohort_key = f"{date[:4]}-Q{quarter}"
        
        if cohort_key not in cohorts:
            cohorts[cohort_key] = {"student_ids": [], "count": 0}
        cohorts[cohort_key]["student_ids"].append(s["id"])
        cohorts[cohort_key]["count"] += 1
    
    # Calculate metrics per cohort
    result = []
    for cohort_key, cohort_data in sorted(cohorts.items()):
        student_ids = cohort_data["student_ids"]
        
        # Active count (had activity in last 30 days)
        month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        active_count = await db.exam_attempts.distinct(
            "user_id",
            {"user_id": {"$in": student_ids}, "created_at": {"$gte": month_ago}}
        )
        
        # Exam performance
        exam_pipeline = [
            {"$match": {"user_id": {"$in": student_ids}}},
            {"$group": {
                "_id": None,
                "total_exams": {"$sum": 1},
                "avg_score": {"$avg": "$score"}
            }}
        ]
        exam_stats = await db.exam_attempts.aggregate(exam_pipeline).to_list(1)
        
        result.append({
            "cohort": cohort_key,
            "total_students": cohort_data["count"],
            "active_students": len(active_count),
            "retention_rate": round(len(active_count) / cohort_data["count"] * 100, 1) if cohort_data["count"] > 0 else 0,
            "total_exams": exam_stats[0]["total_exams"] if exam_stats else 0,
            "average_score": round(exam_stats[0]["avg_score"], 2) if exam_stats and exam_stats[0]["avg_score"] else 0,
            "exams_per_student": round(exam_stats[0]["total_exams"] / cohort_data["count"], 1) if exam_stats and cohort_data["count"] > 0 else 0
        })
    
    return {"cohorts": result, "cohort_by": cohort_by}

@router.get("/performance-benchmarks")
async def get_performance_benchmarks(
    exam_type: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """
    Get performance benchmarks across the platform.
    Useful for comparing institution/student performance against platform averages.
    """
    match_stage = {}
    if exam_type:
        match_stage["exam_type"] = exam_type
    
    # Overall benchmarks
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$exam_type",
            "total_attempts": {"$sum": 1},
            "avg_score": {"$avg": "$score"},
            "median_score": {"$avg": "$score"},  # Approximation
            "p25_score": {"$min": "$score"},  # Approximation
            "p75_score": {"$max": "$score"},  # Approximation
            "std_dev": {"$stdDevPop": "$score"}
        }}
    ]
    
    benchmarks = await db.exam_attempts.aggregate(pipeline).to_list(20)
    
    result = {}
    for b in benchmarks:
        if b["_id"]:
            result[b["_id"]] = {
                "total_attempts": b["total_attempts"],
                "average_score": round(b["avg_score"], 2) if b["avg_score"] else 0,
                "std_deviation": round(b["std_dev"], 2) if b["std_dev"] else 0,
                "percentiles": {
                    "p25": round(b["avg_score"] - b["std_dev"], 2) if b["avg_score"] and b["std_dev"] else 0,
                    "p50": round(b["avg_score"], 2) if b["avg_score"] else 0,
                    "p75": round(b["avg_score"] + b["std_dev"], 2) if b["avg_score"] and b["std_dev"] else 0
                }
            }
    
    return {
        "benchmarks": result,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
