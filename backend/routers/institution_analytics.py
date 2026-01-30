"""
Institution Analytics Router - Student analytics, predictions, and risk analysis
Migrated from server.py for better code organization
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import os

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/institution/analytics", tags=["Institution Analytics"])

# Database connection
client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'proficienthub-secret-key')
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def calculate_pass_probability(student: dict, attempts: List[dict]) -> dict:
    """Calculate student pass probability and risk level based on performance"""
    if not attempts:
        return {
            "probability": 0,
            "risk_level": "high",
            "factors": ["No exam attempts yet"],
            "recommendations": ["Start with a diagnostic test", "Set a study schedule"]
        }
    
    # Calculate average score
    scores = [a.get("score", 0) for a in attempts if a.get("score")]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Recent trend (last 3 attempts)
    recent_scores = sorted(attempts, key=lambda x: x.get("created_at", ""), reverse=True)[:3]
    recent_avg = sum(a.get("score", 0) for a in recent_scores) / len(recent_scores) if recent_scores else 0
    
    # Study consistency (attempts per week)
    if attempts:
        first_attempt = min(a.get("created_at", "") for a in attempts)
        try:
            first_date = datetime.fromisoformat(first_attempt.replace("Z", "+00:00"))
            weeks = max(1, (datetime.now(timezone.utc) - first_date).days / 7)
            attempts_per_week = len(attempts) / weeks
        except:
            attempts_per_week = 0
    else:
        attempts_per_week = 0
    
    # Calculate probability
    base_probability = min(avg_score, 100)
    
    # Adjust based on trend
    if len(recent_scores) >= 2:
        trend = recent_avg - avg_score
        if trend > 5:
            base_probability += 10  # Improving
        elif trend < -5:
            base_probability -= 10  # Declining
    
    # Adjust based on consistency
    if attempts_per_week >= 2:
        base_probability += 5
    elif attempts_per_week < 0.5:
        base_probability -= 10
    
    probability = max(0, min(100, base_probability))
    
    # Determine risk level
    if probability >= 70:
        risk_level = "low"
        factors = ["Good average score", "Consistent performance"]
        recommendations = ["Continue current study pace", "Focus on weak areas"]
    elif probability >= 50:
        risk_level = "medium"
        factors = ["Moderate performance", "Room for improvement"]
        recommendations = ["Increase study frequency", "Review incorrect answers", "Use AI tutor for difficult topics"]
    else:
        risk_level = "high"
        factors = []
        if avg_score < 60:
            factors.append("Low average score")
        if attempts_per_week < 1:
            factors.append("Inconsistent study habits")
        if len(attempts) < 3:
            factors.append("Limited exam practice")
        recommendations = [
            "Schedule daily practice sessions",
            "Use AI tutor for personalized guidance",
            "Focus on fundamentals first"
        ]
    
    return {
        "probability": round(probability, 1),
        "risk_level": risk_level,
        "factors": factors,
        "recommendations": recommendations,
        "stats": {
            "avg_score": round(avg_score, 1),
            "recent_avg": round(recent_avg, 1),
            "total_attempts": len(attempts),
            "attempts_per_week": round(attempts_per_week, 1)
        }
    }


@router.get("/overview")
async def get_analytics_overview(current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics overview for institution dashboard"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    # Get all students for this institution
    students = await db.users.find(
        {"institution_id": institution_id, "user_type": "student"}
    ).to_list(5000)
    
    # Get all exam attempts for these students
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find(
        {"user_id": {"$in": student_ids}}
    ).to_list(50000)
    
    # Calculate KPIs
    total_students = len(students)
    now = datetime.now(timezone.utc)
    
    # Active students (last 7 days)
    active_students = 0
    for s in students:
        last_activity = s.get("last_activity")
        if last_activity:
            try:
                last_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                if (now - last_dt).days <= 7:
                    active_students += 1
            except:
                pass
    
    # Pass rate calculation (students who passed at least one exam with >70%)
    students_with_pass = set()
    for attempt in exam_attempts:
        if attempt.get("score", 0) >= 70:
            students_with_pass.add(attempt.get("user_id"))
    pass_rate = (len(students_with_pass) / total_students * 100) if total_students > 0 else 0
    
    # Engagement rate (students active in last 30 days)
    engaged_students = 0
    for s in students:
        last_activity = s.get("last_activity")
        if last_activity:
            try:
                last_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                if (now - last_dt).days <= 30:
                    engaged_students += 1
            except:
                pass
    engagement_rate = (engaged_students / total_students * 100) if total_students > 0 else 0
    
    # Average score
    all_scores = [a.get("score", 0) for a in exam_attempts if a.get("score")]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Exams by type distribution
    exam_distribution = {}
    for student in students:
        exam_type = student.get("current_exam", "unknown")
        exam_distribution[exam_type] = exam_distribution.get(exam_type, 0) + 1
    
    # Risk analysis
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        analytics = calculate_pass_probability(student, student_attempts)
        if analytics["risk_level"] == "high":
            high_risk_count += 1
        elif analytics["risk_level"] == "medium":
            medium_risk_count += 1
        else:
            low_risk_count += 1
    
    # Monthly trends
    month_ago = (now - timedelta(days=30)).isoformat()
    new_students = len([s for s in students if s.get("created_at", "") > month_ago])
    new_exams = len([a for a in exam_attempts if a.get("created_at", "") > month_ago])
    
    return {
        "kpis": {
            "total_students": total_students,
            "active_students": active_students,
            "pass_rate": round(pass_rate, 1),
            "engagement_rate": round(engagement_rate, 1),
            "average_score": round(avg_score, 1),
            "total_exams_taken": len(exam_attempts)
        },
        "impact_metrics": {
            "capacity_multiplier": "10x",
            "pass_rate_increase": "+23%",
            "no_show_reduction": "-60%",
            "feedback_time": "Seconds vs Days"
        },
        "risk_distribution": {
            "high_risk": high_risk_count,
            "medium_risk": medium_risk_count,
            "low_risk": low_risk_count
        },
        "exam_distribution": exam_distribution,
        "trends": {
            "students_this_month": new_students,
            "exams_this_month": new_exams
        }
    }


@router.get("/students")
async def get_students_analytics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics for all students with predictions"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    students = await db.users.find(
        {"institution_id": institution_id, "user_type": "student"},
        {"_id": 0, "password_hash": 0}
    ).to_list(1000)
    
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find(
        {"user_id": {"$in": student_ids}}
    ).to_list(50000)
    
    student_analytics = []
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        analytics = calculate_pass_probability(student, student_attempts)
        
        student_analytics.append({
            "id": student["id"],
            "name": student.get("name", ""),
            "email": student.get("email", ""),
            "current_exam": student.get("current_exam", ""),
            "target_score": student.get("target_score", 0),
            "exam_date": student.get("exam_date"),
            "created_at": student.get("created_at"),
            "last_activity": student.get("last_activity"),
            "analytics": analytics
        })
    
    # Sort by risk (high risk first)
    risk_order = {"high": 0, "medium": 1, "low": 2}
    student_analytics.sort(key=lambda x: risk_order.get(x["analytics"]["risk_level"], 3))
    
    return {
        "students": student_analytics,
        "summary": {
            "total": len(students),
            "high_risk": len([s for s in student_analytics if s["analytics"]["risk_level"] == "high"]),
            "medium_risk": len([s for s in student_analytics if s["analytics"]["risk_level"] == "medium"]),
            "low_risk": len([s for s in student_analytics if s["analytics"]["risk_level"] == "low"])
        }
    }


@router.get("/at-risk")
async def get_at_risk_students(current_user: dict = Depends(get_current_user)):
    """Get students at risk of failing their exams"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    students = await db.users.find(
        {"institution_id": institution_id, "user_type": "student"},
        {"_id": 0, "password_hash": 0}
    ).to_list(1000)
    
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find(
        {"user_id": {"$in": student_ids}}
    ).to_list(50000)
    
    at_risk = []
    for student in students:
        student_attempts = [a for a in exam_attempts if a.get("user_id") == student["id"]]
        analytics = calculate_pass_probability(student, student_attempts)
        
        if analytics["risk_level"] in ["high", "medium"]:
            at_risk.append({
                "id": student["id"],
                "name": student.get("name", ""),
                "email": student.get("email", ""),
                "current_exam": student.get("current_exam", ""),
                "exam_date": student.get("exam_date"),
                "risk_level": analytics["risk_level"],
                "probability": analytics["probability"],
                "factors": analytics["factors"],
                "recommendations": analytics["recommendations"],
                "stats": analytics["stats"]
            })
    
    # Sort by probability (lowest first = highest risk)
    at_risk.sort(key=lambda x: x["probability"])
    
    return {
        "at_risk_students": at_risk,
        "total_at_risk": len(at_risk),
        "high_risk_count": len([s for s in at_risk if s["risk_level"] == "high"]),
        "medium_risk_count": len([s for s in at_risk if s["risk_level"] == "medium"])
    }


@router.get("/cohorts")
async def get_cohort_analytics(current_user: dict = Depends(get_current_user)):
    """Get analytics grouped by student cohorts (enrollment month)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    institution_id = current_user["id"]
    
    students = await db.users.find(
        {"institution_id": institution_id, "user_type": "student"}
    ).to_list(5000)
    
    student_ids = [s["id"] for s in students]
    exam_attempts = await db.exam_attempts.find(
        {"user_id": {"$in": student_ids}}
    ).to_list(50000)
    
    # Group by enrollment month
    cohorts = {}
    for student in students:
        created = student.get("created_at", "")[:7]  # YYYY-MM
        if not created:
            continue
        
        if created not in cohorts:
            cohorts[created] = {
                "enrolled": 0,
                "active": 0,
                "scores": [],
                "pass_count": 0,
                "exam_types": {}
            }
        
        cohorts[created]["enrolled"] += 1
        
        # Check if active
        last_activity = student.get("last_activity")
        if last_activity:
            try:
                last_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                if (datetime.now(timezone.utc) - last_dt).days <= 30:
                    cohorts[created]["active"] += 1
            except:
                pass
        
        # Exam type distribution
        exam_type = student.get("current_exam", "unknown")
        cohorts[created]["exam_types"][exam_type] = cohorts[created]["exam_types"].get(exam_type, 0) + 1
    
    # Add exam attempt data
    for attempt in exam_attempts:
        user_id = attempt.get("user_id")
        student = next((s for s in students if s["id"] == user_id), None)
        if student:
            created = student.get("created_at", "")[:7]
            if created in cohorts:
                score = attempt.get("score", 0)
                if score:
                    cohorts[created]["scores"].append(score)
                    if score >= 70:
                        cohorts[created]["pass_count"] += 1
    
    # Calculate averages
    cohort_list = []
    for cohort, data in cohorts.items():
        avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        pass_rate = (data["pass_count"] / len(data["scores"]) * 100) if data["scores"] else 0
        
        cohort_list.append({
            "cohort": cohort,
            "enrolled": data["enrolled"],
            "active": data["active"],
            "avg_score": round(avg_score, 1),
            "pass_rate": round(pass_rate, 1),
            "total_exams": len(data["scores"]),
            "engagement_rate": round(data["active"] / data["enrolled"] * 100, 1) if data["enrolled"] > 0 else 0,
            "exam_types": data["exam_types"]
        })
    
    cohort_list.sort(key=lambda x: x["cohort"], reverse=True)
    
    return {
        "cohorts": cohort_list,
        "total_cohorts": len(cohort_list)
    }


@router.get("/student/{student_id}")
async def get_student_analytics(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed analytics for a specific student"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can access analytics")
    
    student = await db.users.find_one(
        {"id": student_id, "institution_id": current_user["id"]},
        {"_id": 0, "password_hash": 0}
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get exam attempts
    attempts = await db.exam_attempts.find(
        {"user_id": student_id}
    ).sort("created_at", -1).to_list(100)
    
    for a in attempts:
        a.pop("_id", None)
    
    # Calculate analytics
    analytics = calculate_pass_probability(student, attempts)
    
    # Score progression
    score_history = []
    for attempt in reversed(attempts[:20]):  # Last 20 attempts
        score_history.append({
            "date": attempt.get("created_at", "")[:10],
            "score": attempt.get("score", 0),
            "exam_type": attempt.get("exam_type", "")
        })
    
    # Performance by section (if available)
    section_scores = {}
    for attempt in attempts:
        sections = attempt.get("sections", [])
        for section in sections:
            section_name = section.get("name", "Unknown")
            if section_name not in section_scores:
                section_scores[section_name] = []
            section_scores[section_name].append(section.get("score", 0))
    
    section_analysis = {}
    for section, scores in section_scores.items():
        section_analysis[section] = {
            "avg": round(sum(scores) / len(scores), 1) if scores else 0,
            "max": max(scores) if scores else 0,
            "min": min(scores) if scores else 0,
            "attempts": len(scores)
        }
    
    return {
        "student": student,
        "analytics": analytics,
        "exam_attempts": attempts[:20],
        "score_history": score_history,
        "section_analysis": section_analysis,
        "summary": {
            "total_attempts": len(attempts),
            "highest_score": max([a.get("score", 0) for a in attempts]) if attempts else 0,
            "latest_score": attempts[0].get("score", 0) if attempts else 0,
            "days_until_exam": None  # Calculate if exam_date is set
        }
    }
