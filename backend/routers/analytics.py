"""Analytics router - Real predictive analytics and reporting"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def calculate_pass_probability(exam_attempts: list, student_data: dict = None) -> dict:
    """Calculate pass probability based on real performance data"""
    probability = 50.0
    factors = []
    
    if not exam_attempts:
        return {
            "probability": 50,
            "risk_level": "unknown",
            "factors": [{"factor": "No exam history", "impact": "0%", "status": "neutral"}],
            "recommendation": "Start practicing to build your performance profile."
        }
    
    # Factor 1: Practice frequency (last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_attempts = [a for a in exam_attempts if a.get("created_at", "") > thirty_days_ago]
    practice_count = len(recent_attempts)
    
    if practice_count >= 15:
        probability += 18
        factors.append({"factor": "Excellent practice frequency", "impact": "+18%", "status": "positive"})
    elif practice_count >= 10:
        probability += 12
        factors.append({"factor": "Good practice frequency", "impact": "+12%", "status": "positive"})
    elif practice_count >= 5:
        probability += 5
        factors.append({"factor": "Moderate practice frequency", "impact": "+5%", "status": "positive"})
    elif practice_count < 2:
        probability -= 12
        factors.append({"factor": "Low practice frequency", "impact": "-12%", "status": "negative"})
    
    # Factor 2: Score trend analysis
    scores = [a.get("score", 0) for a in exam_attempts if a.get("score") is not None]
    if len(scores) >= 3:
        recent_scores = scores[-5:] if len(scores) >= 5 else scores
        older_scores = scores[:-5] if len(scores) > 5 else scores[:len(scores)//2]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
        
        if recent_avg > older_avg * 1.1:
            probability += 15
            factors.append({"factor": "Strong improvement trend", "impact": "+15%", "status": "positive"})
        elif recent_avg > older_avg:
            probability += 8
            factors.append({"factor": "Steady improvement", "impact": "+8%", "status": "positive"})
        elif recent_avg < older_avg * 0.9:
            probability -= 10
            factors.append({"factor": "Declining performance", "impact": "-10%", "status": "negative"})
    
    # Factor 3: Overall performance level
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        if avg_score >= 85:
            probability += 22
            factors.append({"factor": "Outstanding average score", "impact": "+22%", "status": "positive"})
        elif avg_score >= 75:
            probability += 15
            factors.append({"factor": "Strong average score", "impact": "+15%", "status": "positive"})
        elif avg_score >= 65:
            probability += 8
            factors.append({"factor": "Good average score", "impact": "+8%", "status": "positive"})
        elif avg_score < 50:
            probability -= 18
            factors.append({"factor": "Below passing average", "impact": "-18%", "status": "negative"})
        
        # Best score bonus
        if max_score >= 90:
            probability += 5
            factors.append({"factor": "Achieved 90+ in practice", "impact": "+5%", "status": "positive"})
    
    # Factor 4: Consistency
    if len(scores) >= 5:
        score_variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
        if score_variance < 100:
            probability += 5
            factors.append({"factor": "Consistent performance", "impact": "+5%", "status": "positive"})
        elif score_variance > 400:
            probability -= 5
            factors.append({"factor": "Inconsistent performance", "impact": "-5%", "status": "negative"})
    
    # Factor 5: Section coverage
    sections_practiced = set(a.get("section") for a in exam_attempts if a.get("section"))
    required_sections = {"reading", "listening", "writing", "speaking"}
    coverage = len(sections_practiced.intersection(required_sections)) / len(required_sections)
    
    if coverage >= 1.0:
        probability += 8
        factors.append({"factor": "All sections practiced", "impact": "+8%", "status": "positive"})
    elif coverage < 0.5:
        probability -= 8
        factors.append({"factor": "Limited section coverage", "impact": "-8%", "status": "negative"})
    
    # Ensure bounds
    probability = max(5, min(95, probability))
    
    # Risk level and recommendation
    if probability >= 80:
        risk_level = "low"
        recommendation = "Excellent preparation! Maintain your practice schedule and focus on any remaining weak areas."
    elif probability >= 65:
        risk_level = "low-medium"
        recommendation = "Good progress. Continue practicing and consider extra focus on sections with lower scores."
    elif probability >= 50:
        risk_level = "medium"
        recommendation = "More practice needed. Increase frequency and work on improving weak sections."
    elif probability >= 35:
        risk_level = "medium-high"
        recommendation = "Significant improvement needed. Consider intensive practice and possibly rescheduling exam date."
    else:
        risk_level = "high"
        recommendation = "Substantial preparation required. Focus on fundamentals and consider delaying exam if possible."
    
    return {
        "probability": round(probability),
        "risk_level": risk_level,
        "factors": factors,
        "recommendation": recommendation,
        "data_points": len(exam_attempts),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0
    }

@router.get("/student/predictive")
async def get_student_predictive_analytics(current_user: dict = Depends(get_current_user)):
    """Get predictive analytics for current student"""
    if current_user["user_type"] not in ["student", "individual"]:
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get exam attempts
    attempts = await db.exam_attempts.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Calculate prediction
    prediction = calculate_pass_probability(attempts, current_user)
    
    # Section breakdown
    section_stats = {}
    for attempt in attempts:
        section = attempt.get("section", "unknown")
        if section not in section_stats:
            section_stats[section] = {"scores": [], "count": 0}
        if attempt.get("score") is not None:
            section_stats[section]["scores"].append(attempt["score"])
            section_stats[section]["count"] += 1
    
    section_analysis = {}
    for section, data in section_stats.items():
        if data["scores"]:
            avg = sum(data["scores"]) / len(data["scores"])
            section_analysis[section] = {
                "average": round(avg, 1),
                "attempts": data["count"],
                "best": max(data["scores"]),
                "trend": "improving" if len(data["scores"]) >= 2 and data["scores"][-1] > data["scores"][0] else "stable"
            }
    
    # Weak areas
    weak_sections = [s for s, d in section_analysis.items() if d["average"] < 60]
    strong_sections = [s for s, d in section_analysis.items() if d["average"] >= 75]
    
    return {
        "prediction": prediction,
        "section_analysis": section_analysis,
        "weak_areas": weak_sections,
        "strong_areas": strong_sections,
        "total_practice_time": sum(a.get("time_spent", 0) for a in attempts),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/institution/overview")
async def get_institution_analytics(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics overview for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    inst_id = current_user["id"]
    start_date = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    
    # Student count
    total_students = await db.users.count_documents({"institution_id": inst_id, "user_type": "student"})
    
    # Active students
    active_student_ids = await db.exam_attempts.distinct(
        "user_id",
        {"institution_id": inst_id, "created_at": {"$gte": start_date}}
    )
    
    # Exam attempts in period
    attempts_in_period = await db.exam_attempts.find(
        {"institution_id": inst_id, "created_at": {"$gte": start_date}},
        {"_id": 0, "score": 1, "exam_type": 1, "section": 1, "created_at": 1, "user_id": 1}
    ).to_list(10000)
    
    # Score distribution
    scores = [a["score"] for a in attempts_in_period if a.get("score") is not None]
    score_distribution = {
        "0-50": len([s for s in scores if s < 50]),
        "50-65": len([s for s in scores if 50 <= s < 65]),
        "65-75": len([s for s in scores if 65 <= s < 75]),
        "75-85": len([s for s in scores if 75 <= s < 85]),
        "85-100": len([s for s in scores if s >= 85])
    }
    
    # Exam type distribution
    exam_distribution = {}
    for a in attempts_in_period:
        exam_type = a.get("exam_type", "unknown")
        exam_distribution[exam_type] = exam_distribution.get(exam_type, 0) + 1
    
    # Section performance
    section_scores = {}
    for a in attempts_in_period:
        section = a.get("section", "unknown")
        if section not in section_scores:
            section_scores[section] = []
        if a.get("score") is not None:
            section_scores[section].append(a["score"])
    
    section_averages = {
        s: round(sum(scores) / len(scores), 1) 
        for s, scores in section_scores.items() if scores
    }
    
    # Daily activity
    daily_activity = {}
    for a in attempts_in_period:
        date = a.get("created_at", "")[:10]
        daily_activity[date] = daily_activity.get(date, 0) + 1
    
    # AI usage
    ai_credits = await db.ai_credits.find_one({"user_id": inst_id}, {"_id": 0})
    ai_usage = await db.ai_agent_history.count_documents({
        "institution_id": inst_id,
        "created_at": {"$gte": start_date}
    })
    
    # Calculate average prediction for all students
    student_predictions = []
    for student_id in active_student_ids[:50]:  # Limit for performance
        student_attempts = [a for a in attempts_in_period if a.get("user_id") == student_id]
        if student_attempts:
            pred = calculate_pass_probability(student_attempts)
            student_predictions.append(pred["probability"])
    
    avg_prediction = round(sum(student_predictions) / len(student_predictions)) if student_predictions else 50
    
    return {
        "period_days": period_days,
        "students": {
            "total": total_students,
            "active": len(active_student_ids),
            "activity_rate": round(len(active_student_ids) / max(total_students, 1) * 100, 1)
        },
        "exams": {
            "total_attempts": len(attempts_in_period),
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "score_distribution": score_distribution,
            "exam_distribution": exam_distribution
        },
        "sections": {
            "averages": section_averages,
            "weakest": min(section_averages, key=section_averages.get) if section_averages else None,
            "strongest": max(section_averages, key=section_averages.get) if section_averages else None
        },
        "ai_usage": {
            "interactions": ai_usage,
            "credits_available": (ai_credits.get("total_credits", 0) - ai_credits.get("used_credits", 0)) if ai_credits else 0
        },
        "prediction": {
            "avg_pass_probability": avg_prediction,
            "students_analyzed": len(student_predictions)
        },
        "daily_activity": daily_activity,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/institution/students-at-risk")
async def get_students_at_risk(
    threshold: int = Query(default=50, ge=20, le=70),
    current_user: dict = Depends(get_current_user)
):
    """Get list of students with low pass probability"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    inst_id = current_user["id"]
    
    # Get all students
    students = await db.users.find(
        {"institution_id": inst_id, "user_type": "student"},
        {"_id": 0, "id": 1, "name": 1, "email": 1, "current_exam": 1}
    ).to_list(500)
    
    at_risk = []
    for student in students:
        attempts = await db.exam_attempts.find(
            {"user_id": student["id"]},
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        if attempts:
            prediction = calculate_pass_probability(attempts)
            if prediction["probability"] < threshold:
                at_risk.append({
                    "student_id": student["id"],
                    "name": student["name"],
                    "email": student["email"],
                    "exam_type": student.get("current_exam"),
                    "probability": prediction["probability"],
                    "risk_level": prediction["risk_level"],
                    "attempts": len(attempts),
                    "factors": prediction["factors"][:3],  # Top 3 factors
                    "recommendation": prediction["recommendation"]
                })
    
    # Sort by probability (lowest first)
    at_risk.sort(key=lambda x: x["probability"])
    
    return {
        "threshold": threshold,
        "students_at_risk": at_risk,
        "total_at_risk": len(at_risk),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/platform/overview")
async def get_platform_analytics(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get platform-wide analytics (Superadmin only)"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    
    # Total counts
    total_institutions = await db.users.count_documents({"user_type": "institution"})
    total_students = await db.users.count_documents({"user_type": "student"})
    total_individuals = await db.users.count_documents({"user_type": "individual"})
    
    # Exam attempts
    total_attempts = await db.exam_attempts.count_documents({"created_at": {"$gte": start_date}})
    
    # Average scores by exam type
    score_pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": "$exam_type",
            "avg_score": {"$avg": "$score"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    exam_scores = await db.exam_attempts.aggregate(score_pipeline).to_list(20)
    
    # AI usage
    ai_interactions = await db.ai_agent_history.count_documents({"created_at": {"$gte": start_date}})
    
    # Revenue from credits
    credits_pipeline = [
        {"$group": {
            "_id": None,
            "total_purchased": {"$sum": "$purchased_credits"},
            "total_used": {"$sum": "$used_credits"}
        }}
    ]
    credits_data = await db.ai_credits.aggregate(credits_pipeline).to_list(1)
    
    # Growth metrics
    prev_start = (datetime.now(timezone.utc) - timedelta(days=period_days * 2)).isoformat()
    prev_end = start_date
    
    prev_attempts = await db.exam_attempts.count_documents({
        "created_at": {"$gte": prev_start, "$lt": prev_end}
    })
    growth_rate = ((total_attempts - prev_attempts) / max(prev_attempts, 1)) * 100 if prev_attempts else 0
    
    return {
        "period_days": period_days,
        "users": {
            "institutions": total_institutions,
            "students": total_students,
            "individuals": total_individuals,
            "total": total_institutions + total_students + total_individuals
        },
        "exams": {
            "total_attempts": total_attempts,
            "growth_rate": round(growth_rate, 1),
            "by_type": {e["_id"]: {"avg_score": round(e["avg_score"], 1), "count": e["count"]} for e in exam_scores if e["_id"]}
        },
        "ai": {
            "total_interactions": ai_interactions,
            "total_credits_purchased": credits_data[0]["total_purchased"] if credits_data else 0,
            "total_credits_used": credits_data[0]["total_used"] if credits_data else 0
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
