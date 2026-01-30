"""
Advanced Analytics Dashboard Router
Provides advanced analytics, forecasting, and insights for institutions
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import os

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/analytics-dashboard", tags=["Analytics Dashboard"])

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

# ==================== EXECUTIVE SUMMARY ====================

@router.get("/executive-summary")
async def get_executive_summary(
    period: str = "month",  # week, month, quarter, year
    current_user: dict = Depends(get_current_user)
):
    """Get executive summary with key KPIs"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user.get("id")
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = (now - timedelta(days=7)).isoformat()
        prev_start = (now - timedelta(days=14)).isoformat()
    elif period == "quarter":
        start_date = (now - timedelta(days=90)).isoformat()
        prev_start = (now - timedelta(days=180)).isoformat()
    elif period == "year":
        start_date = (now - timedelta(days=365)).isoformat()
        prev_start = (now - timedelta(days=730)).isoformat()
    else:  # month
        start_date = (now - timedelta(days=30)).isoformat()
        prev_start = (now - timedelta(days=60)).isoformat()
    
    # Get current period data
    students = await db.users.find({
        "institution_id": institution_id,
        "user_type": "student"
    }).to_list(10000)
    
    leads_query = {"created_by": institution_id} if current_user["user_type"] == "institution" else {}
    leads = await db.crm_leads.find(leads_query).to_list(1000)
    
    # Current period stats
    current_students = len([s for s in students if s.get("created_at", "") >= start_date])
    current_leads = len([l for l in leads if l.get("created_at", "") >= start_date])
    won_leads = [l for l in leads if l.get("stage") == "won" and l.get("updated_at", "") >= start_date]
    current_revenue = sum(l.get("estimated_value", 0) for l in won_leads)
    
    # Previous period stats for comparison
    prev_students = len([s for s in students if prev_start <= s.get("created_at", "") < start_date])
    prev_leads = len([l for l in leads if prev_start <= l.get("created_at", "") < start_date])
    prev_won = [l for l in leads if l.get("stage") == "won" and prev_start <= l.get("updated_at", "") < start_date]
    prev_revenue = sum(l.get("estimated_value", 0) for l in prev_won)
    
    # Calculate growth percentages
    def calc_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round((current - previous) / previous * 100, 1)
    
    # Exam attempts
    attempts = await db.exam_attempts.find({
        "user_id": {"$in": [s["id"] for s in students]}
    }).to_list(10000)
    current_attempts = len([a for a in attempts if a.get("created_at", "") >= start_date])
    
    # Active students (logged in recently)
    active_students = len([s for s in students if s.get("last_login", s.get("created_at", "")) >= start_date])
    
    return {
        "period": period,
        "kpis": {
            "total_students": {
                "value": len(students),
                "change": calc_growth(current_students, prev_students),
                "trend": "up" if current_students > prev_students else "down"
            },
            "active_students": {
                "value": active_students,
                "percentage": round(active_students / len(students) * 100, 1) if students else 0
            },
            "total_leads": {
                "value": len(leads),
                "change": calc_growth(current_leads, prev_leads),
                "trend": "up" if current_leads > prev_leads else "down"
            },
            "revenue": {
                "value": current_revenue,
                "change": calc_growth(current_revenue, prev_revenue),
                "trend": "up" if current_revenue > prev_revenue else "down",
                "currency": "USD"
            },
            "exam_attempts": {
                "value": current_attempts,
                "avg_per_student": round(current_attempts / active_students, 1) if active_students else 0
            },
            "conversion_rate": {
                "value": round(len(won_leads) / len(leads) * 100, 1) if leads else 0,
                "unit": "%"
            }
        },
        "quick_insights": [
            f"{current_students} new students enrolled this {period}",
            f"Revenue {'increased' if current_revenue > prev_revenue else 'decreased'} by {abs(calc_growth(current_revenue, prev_revenue))}%",
            f"{active_students} students active ({round(active_students/len(students)*100)}% engagement)" if students else "No students yet"
        ]
    }

# ==================== REVENUE ANALYTICS ====================

@router.get("/revenue")
async def get_revenue_analytics(
    months: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Get revenue analytics with monthly breakdown and forecasting"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    leads_query = {"created_by": current_user["id"]} if current_user["user_type"] == "institution" else {}
    leads = await db.crm_leads.find(leads_query).to_list(5000)
    
    # Monthly revenue breakdown
    monthly_data = {}
    now = datetime.now(timezone.utc)
    
    for i in range(months):
        month_date = now - timedelta(days=30 * i)
        month_key = month_date.strftime("%Y-%m")
        monthly_data[month_key] = {
            "revenue": 0,
            "deals_won": 0,
            "deals_lost": 0,
            "avg_deal_size": 0
        }
    
    won_leads = [l for l in leads if l.get("stage") == "won"]
    lost_leads = [l for l in leads if l.get("stage") == "lost"]
    
    for lead in won_leads:
        updated = lead.get("updated_at", lead.get("created_at", ""))[:7]
        if updated in monthly_data:
            monthly_data[updated]["revenue"] += lead.get("estimated_value", 0)
            monthly_data[updated]["deals_won"] += 1
    
    for lead in lost_leads:
        updated = lead.get("updated_at", lead.get("created_at", ""))[:7]
        if updated in monthly_data:
            monthly_data[updated]["deals_lost"] += 1
    
    # Calculate averages
    for month in monthly_data:
        if monthly_data[month]["deals_won"] > 0:
            monthly_data[month]["avg_deal_size"] = round(
                monthly_data[month]["revenue"] / monthly_data[month]["deals_won"], 2
            )
    
    # Convert to sorted list
    monthly_list = [
        {"month": k, **v} 
        for k, v in sorted(monthly_data.items())
    ]
    
    # Simple forecasting (moving average)
    recent_revenues = [m["revenue"] for m in monthly_list[-3:] if m["revenue"] > 0]
    avg_recent = sum(recent_revenues) / len(recent_revenues) if recent_revenues else 0
    growth_rate = 1.05  # Assume 5% growth
    
    forecast = []
    for i in range(1, 4):
        future_month = (now + timedelta(days=30 * i)).strftime("%Y-%m")
        forecast.append({
            "month": future_month,
            "predicted_revenue": round(avg_recent * (growth_rate ** i), 2),
            "confidence": max(0.6, 0.9 - (i * 0.1))
        })
    
    return {
        "summary": {
            "total_revenue": sum(l.get("estimated_value", 0) for l in won_leads),
            "total_deals_won": len(won_leads),
            "total_deals_lost": len(lost_leads),
            "avg_deal_size": round(sum(l.get("estimated_value", 0) for l in won_leads) / len(won_leads), 2) if won_leads else 0,
            "win_rate": round(len(won_leads) / (len(won_leads) + len(lost_leads)) * 100, 1) if (won_leads or lost_leads) else 0
        },
        "monthly_breakdown": monthly_list,
        "forecast": forecast,
        "insights": {
            "best_month": max(monthly_list, key=lambda x: x["revenue"])["month"] if monthly_list else None,
            "trend": "growing" if len(recent_revenues) >= 2 and recent_revenues[-1] > recent_revenues[0] else "stable"
        }
    }

# ==================== LEAD SOURCE ANALYTICS ====================

@router.get("/lead-sources")
async def get_lead_source_analytics(current_user: dict = Depends(get_current_user)):
    """Get analytics by lead source with conversion rates"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    leads_query = {"created_by": current_user["id"]} if current_user["user_type"] == "institution" else {}
    leads = await db.crm_leads.find(leads_query).to_list(5000)
    
    # Group by source
    sources = {}
    for lead in leads:
        source = lead.get("source", "unknown")
        if source not in sources:
            sources[source] = {
                "total": 0,
                "won": 0,
                "lost": 0,
                "in_pipeline": 0,
                "total_value": 0,
                "won_value": 0
            }
        
        sources[source]["total"] += 1
        sources[source]["total_value"] += lead.get("estimated_value", 0)
        
        if lead.get("stage") == "won":
            sources[source]["won"] += 1
            sources[source]["won_value"] += lead.get("estimated_value", 0)
        elif lead.get("stage") == "lost":
            sources[source]["lost"] += 1
        else:
            sources[source]["in_pipeline"] += 1
    
    # Calculate metrics
    source_analytics = []
    for source, data in sources.items():
        closed = data["won"] + data["lost"]
        source_analytics.append({
            "source": source,
            "label": source.replace("_", " ").title(),
            "leads": data["total"],
            "won": data["won"],
            "lost": data["lost"],
            "in_pipeline": data["in_pipeline"],
            "conversion_rate": round(data["won"] / closed * 100, 1) if closed > 0 else 0,
            "total_value": data["total_value"],
            "won_value": data["won_value"],
            "avg_deal_value": round(data["won_value"] / data["won"], 2) if data["won"] > 0 else 0,
            "roi_score": round((data["won_value"] / data["total_value"] * 100), 1) if data["total_value"] > 0 else 0
        })
    
    # Sort by conversion rate
    source_analytics.sort(key=lambda x: x["conversion_rate"], reverse=True)
    
    return {
        "sources": source_analytics,
        "top_performing": source_analytics[0]["source"] if source_analytics else None,
        "recommendations": [
            f"Focus more on '{source_analytics[0]['label']}' - highest conversion rate ({source_analytics[0]['conversion_rate']}%)" if source_analytics else "Start adding leads to see insights",
            f"Consider reducing investment in low-converting sources" if any(s["conversion_rate"] < 10 for s in source_analytics) else None
        ]
    }

# ==================== STUDENT ENGAGEMENT ANALYTICS ====================

@router.get("/student-engagement")
async def get_student_engagement(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed student engagement analytics"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user.get("id")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    students = await db.users.find({
        "institution_id": institution_id,
        "user_type": "student"
    }, {"_id": 0}).to_list(10000)
    
    # Get exam attempts for these students
    student_ids = [s["id"] for s in students]
    attempts = await db.exam_attempts.find({
        "user_id": {"$in": student_ids}
    }).to_list(50000)
    
    # Categorize students
    active = []
    at_risk = []
    inactive = []
    
    for student in students:
        student_attempts = [a for a in attempts if a["user_id"] == student["id"]]
        recent_attempts = [a for a in student_attempts if a.get("created_at", "") >= cutoff]
        
        student_data = {
            "id": student["id"],
            "name": student.get("name", "Unknown"),
            "email": student.get("email", ""),
            "total_attempts": len(student_attempts),
            "recent_attempts": len(recent_attempts),
            "last_activity": max([a.get("created_at", "") for a in student_attempts]) if student_attempts else None,
            "avg_score": round(sum(a.get("score", 0) for a in student_attempts) / len(student_attempts), 1) if student_attempts else 0
        }
        
        if len(recent_attempts) >= 3:
            active.append(student_data)
        elif 0 < len(recent_attempts) < 3:
            at_risk.append(student_data)
        else:
            inactive.append(student_data)
    
    # Calculate engagement trends
    daily_activity = {}
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_activity[day] = 0
    
    for attempt in attempts:
        day = attempt.get("created_at", "")[:10]
        if day in daily_activity:
            daily_activity[day] += 1
    
    activity_trend = [{"date": k, "attempts": v} for k, v in sorted(daily_activity.items())]
    
    return {
        "summary": {
            "total_students": len(students),
            "active": len(active),
            "at_risk": len(at_risk),
            "inactive": len(inactive),
            "engagement_rate": round(len(active) / len(students) * 100, 1) if students else 0
        },
        "categories": {
            "active": {
                "count": len(active),
                "description": "3+ activities in last 30 days",
                "students": active[:10]
            },
            "at_risk": {
                "count": len(at_risk),
                "description": "1-2 activities in last 30 days",
                "students": at_risk[:10]
            },
            "inactive": {
                "count": len(inactive),
                "description": "No activity in last 30 days",
                "students": inactive[:10]
            }
        },
        "daily_activity": activity_trend,
        "recommendations": [
            f"Send re-engagement emails to {len(at_risk)} at-risk students",
            f"Consider reaching out to {len(inactive)} inactive students",
            "Top performers can be featured in success stories"
        ]
    }

# ==================== PIPELINE VELOCITY ====================

@router.get("/pipeline-velocity")
async def get_pipeline_velocity(current_user: dict = Depends(get_current_user)):
    """Get pipeline velocity metrics - how fast deals move through stages"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    leads_query = {"created_by": current_user["id"]} if current_user["user_type"] == "institution" else {}
    leads = await db.crm_leads.find(leads_query).to_list(5000)
    
    # Calculate average time in each stage
    stage_times = {
        "new_to_contacted": [],
        "contacted_to_demo": [],
        "demo_to_proposal": [],
        "proposal_to_close": [],
        "total_cycle": []
    }
    
    won_leads = [l for l in leads if l.get("stage") == "won"]
    
    for lead in won_leads:
        activities = lead.get("activities", [])
        stage_changes = [a for a in activities if a.get("type") == "stage_change"]
        
        if len(stage_changes) >= 2:
            # Calculate total cycle time
            created = lead.get("created_at", "")
            closed = lead.get("updated_at", "")
            if created and closed:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    closed_dt = datetime.fromisoformat(closed.replace("Z", "+00:00"))
                    total_days = (closed_dt - created_dt).days
                    stage_times["total_cycle"].append(total_days)
                except:
                    pass
    
    # Calculate averages
    velocity = {}
    for stage, times in stage_times.items():
        if times:
            velocity[stage] = {
                "avg_days": round(sum(times) / len(times), 1),
                "min_days": min(times),
                "max_days": max(times),
                "samples": len(times)
            }
        else:
            velocity[stage] = {"avg_days": 0, "min_days": 0, "max_days": 0, "samples": 0}
    
    # Pipeline health check
    current_pipeline = [l for l in leads if l.get("stage") not in ["won", "lost"]]
    stale_leads = []
    
    now = datetime.now(timezone.utc)
    for lead in current_pipeline:
        updated = lead.get("updated_at", lead.get("created_at", ""))
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                days_stale = (now - updated_dt).days
                if days_stale > 14:
                    stale_leads.append({
                        "id": lead["id"],
                        "name": lead.get("institution_name", ""),
                        "stage": lead.get("stage", ""),
                        "days_stale": days_stale
                    })
            except:
                pass
    
    return {
        "velocity": velocity,
        "pipeline_health": {
            "total_in_pipeline": len(current_pipeline),
            "stale_leads": len(stale_leads),
            "stale_percentage": round(len(stale_leads) / len(current_pipeline) * 100, 1) if current_pipeline else 0
        },
        "stale_leads": sorted(stale_leads, key=lambda x: x["days_stale"], reverse=True)[:10],
        "benchmarks": {
            "ideal_cycle_days": 30,
            "warning_threshold_days": 45,
            "critical_threshold_days": 60
        }
    }

# ==================== COHORT ANALYSIS ====================

@router.get("/cohort-analysis")
async def get_cohort_analysis(current_user: dict = Depends(get_current_user)):
    """Get student cohort analysis by enrollment month"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user.get("id")
    
    students = await db.users.find({
        "institution_id": institution_id,
        "user_type": "student"
    }).to_list(10000)
    
    # Group by enrollment month
    cohorts = {}
    for student in students:
        created = student.get("created_at", "")[:7]  # YYYY-MM
        if created:
            if created not in cohorts:
                cohorts[created] = {
                    "enrolled": 0,
                    "active": 0,
                    "completed_exams": 0,
                    "avg_score": 0,
                    "scores": []
                }
            cohorts[created]["enrolled"] += 1
    
    # Get exam data for each cohort
    all_attempts = await db.exam_attempts.find({
        "user_id": {"$in": [s["id"] for s in students]}
    }).to_list(50000)
    
    student_cohort = {s["id"]: s.get("created_at", "")[:7] for s in students}
    
    for attempt in all_attempts:
        cohort = student_cohort.get(attempt.get("user_id", ""))
        if cohort and cohort in cohorts:
            cohorts[cohort]["completed_exams"] += 1
            if attempt.get("score"):
                cohorts[cohort]["scores"].append(attempt["score"])
    
    # Calculate averages
    for cohort in cohorts:
        scores = cohorts[cohort]["scores"]
        cohorts[cohort]["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0
        cohorts[cohort]["exams_per_student"] = round(
            cohorts[cohort]["completed_exams"] / cohorts[cohort]["enrolled"], 1
        ) if cohorts[cohort]["enrolled"] > 0 else 0
        del cohorts[cohort]["scores"]  # Remove raw scores
    
    cohort_list = [{"cohort": k, **v} for k, v in sorted(cohorts.items())]
    
    return {
        "cohorts": cohort_list,
        "insights": {
            "best_performing_cohort": max(cohort_list, key=lambda x: x["avg_score"])["cohort"] if cohort_list else None,
            "most_engaged_cohort": max(cohort_list, key=lambda x: x["exams_per_student"])["cohort"] if cohort_list else None,
            "total_cohorts": len(cohort_list)
        }
    }

# ==================== EXPORT REPORTS ====================

@router.get("/export/{report_type}")
async def export_report(
    report_type: str,  # executive, revenue, leads, students
    format: str = "json",  # json, csv
    current_user: dict = Depends(get_current_user)
):
    """Export analytics report"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get data based on report type
    if report_type == "executive":
        data = await get_executive_summary(current_user=current_user)
    elif report_type == "revenue":
        data = await get_revenue_analytics(current_user=current_user)
    elif report_type == "leads":
        data = await get_lead_source_analytics(current_user=current_user)
    elif report_type == "students":
        data = await get_student_engagement(current_user=current_user)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    if format == "csv":
        # For CSV, return a simpler structure
        return {
            "format": "csv",
            "report_type": report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "note": "Use a CSV library to convert the data structure"
        }
    
    return {
        "format": "json",
        "report_type": report_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "institution_id": current_user.get("id"),
        "data": data
    }
