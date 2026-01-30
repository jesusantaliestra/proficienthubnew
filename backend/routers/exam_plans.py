"""
Mock Exams & Plans Router - Consumable exam credits system
Handles: Mock purchases, exam consumption, upsells, PDF feedback generation
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import os
import io

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/exam-plans", tags=["Exam Plans & Mocks"])

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

# ==================== MODELS ====================

class PlanType(str, Enum):
    STARTER = "starter"
    STANDARD = "standard"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"

class PlanCreate(BaseModel):
    name: str
    exam_type: str  # oet, ielts, toefl, etc.
    mock_count: int  # Number of full mocks included
    speaking_sessions: int = 0
    writing_evaluations: int = 0
    ai_tutor_hours: int = 0
    price: float
    currency: str = "USD"
    description: Optional[str] = None
    features: List[str] = []
    is_active: bool = True
    
class PurchaseCreate(BaseModel):
    plan_id: str
    payment_method: str = "stripe"  # stripe, paypal, etc.
    stripe_payment_intent_id: Optional[str] = None

class MockStartRequest(BaseModel):
    exam_type: str
    section: Optional[str] = None  # None = full mock, or "reading", "writing", etc.
    timed: bool = True

class MockSubmitRequest(BaseModel):
    attempt_id: str
    answers: Dict[str, Any]
    time_taken_seconds: int

# ==================== INSTITUTION PLAN MANAGEMENT ====================

@router.post("/plans")
async def create_exam_plan(plan: PlanCreate, current_user: dict = Depends(get_current_user)):
    """Institution creates an exam plan for their students to purchase"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create plans")
    
    plan_id = str(uuid.uuid4())
    plan_doc = {
        "id": plan_id,
        "institution_id": current_user["id"],
        **plan.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_sold": 0,
        "revenue": 0
    }
    
    await db.exam_plans.insert_one(plan_doc)
    plan_doc.pop("_id", None)
    
    return {"id": plan_id, "message": "Plan created", "plan": plan_doc}

@router.get("/plans")
async def get_institution_plans(current_user: dict = Depends(get_current_user)):
    """Get all plans for the institution"""
    if current_user["user_type"] == "institution":
        institution_id = current_user["id"]
    elif current_user["user_type"] == "student":
        institution_id = current_user.get("institution_id")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    plans = await db.exam_plans.find(
        {"institution_id": institution_id, "is_active": True},
        {"_id": 0}
    ).to_list(50)
    
    return {"plans": plans}

@router.get("/plans/{plan_id}")
async def get_plan_details(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific plan"""
    plan = await db.exam_plans.find_one({"id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/plans/{plan_id}")
async def update_plan(plan_id: str, plan: PlanCreate, current_user: dict = Depends(get_current_user)):
    """Update a plan"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update plans")
    
    result = await db.exam_plans.update_one(
        {"id": plan_id, "institution_id": current_user["id"]},
        {"$set": {**plan.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {"message": "Plan updated"}

@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Deactivate a plan (soft delete)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can delete plans")
    
    result = await db.exam_plans.update_one(
        {"id": plan_id, "institution_id": current_user["id"]},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {"message": "Plan deactivated"}

# ==================== STUDENT PURCHASES ====================

@router.post("/purchase")
async def purchase_plan(purchase: PurchaseCreate, current_user: dict = Depends(get_current_user)):
    """Student purchases a plan"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can purchase plans")
    
    plan = await db.exam_plans.find_one({"id": purchase.plan_id, "is_active": True})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or inactive")
    
    # Verify student belongs to this institution
    if current_user.get("institution_id") != plan["institution_id"]:
        raise HTTPException(status_code=403, detail="This plan is not available for your institution")
    
    # Verify exam type matches student's assigned exam
    student_exam = current_user.get("current_exam")
    if student_exam and student_exam != plan["exam_type"]:
        raise HTTPException(status_code=400, detail=f"This plan is for {plan['exam_type'].upper()}, but you are enrolled in {student_exam.upper()}")
    
    # Create purchase record
    purchase_id = str(uuid.uuid4())
    purchase_doc = {
        "id": purchase_id,
        "student_id": current_user["id"],
        "institution_id": plan["institution_id"],
        "plan_id": purchase.plan_id,
        "plan_name": plan["name"],
        "exam_type": plan["exam_type"],
        "price_paid": plan["price"],
        "currency": plan["currency"],
        "payment_method": purchase.payment_method,
        "stripe_payment_intent_id": purchase.stripe_payment_intent_id,
        "status": "completed",  # Would be "pending" until Stripe confirms
        "purchased_at": datetime.now(timezone.utc).isoformat(),
        
        # Consumable credits
        "mocks_total": plan["mock_count"],
        "mocks_used": 0,
        "mocks_remaining": plan["mock_count"],
        
        "speaking_total": plan.get("speaking_sessions", 0),
        "speaking_used": 0,
        "speaking_remaining": plan.get("speaking_sessions", 0),
        
        "writing_total": plan.get("writing_evaluations", 0),
        "writing_used": 0,
        "writing_remaining": plan.get("writing_evaluations", 0),
        
        "ai_tutor_hours_total": plan.get("ai_tutor_hours", 0),
        "ai_tutor_minutes_used": 0,
        
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()  # 1 year validity
    }
    
    await db.student_purchases.insert_one(purchase_doc)
    
    # Update plan stats
    await db.exam_plans.update_one(
        {"id": purchase.plan_id},
        {
            "$inc": {"total_sold": 1, "revenue": plan["price"]},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Update student's exam type if not set
    if not student_exam:
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"current_exam": plan["exam_type"], "exam_access": [plan["exam_type"]]}}
        )
    
    purchase_doc.pop("_id", None)
    return {"purchase_id": purchase_id, "message": "Plan purchased successfully", "purchase": purchase_doc}

@router.get("/my-credits")
async def get_my_credits(current_user: dict = Depends(get_current_user)):
    """Get student's current credit balance across all purchases"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view credits")
    
    purchases = await db.student_purchases.find(
        {"student_id": current_user["id"], "status": "completed"},
        {"_id": 0}
    ).to_list(100)
    
    # Aggregate credits
    total_mocks = sum(p.get("mocks_remaining", 0) for p in purchases)
    total_speaking = sum(p.get("speaking_remaining", 0) for p in purchases)
    total_writing = sum(p.get("writing_remaining", 0) for p in purchases)
    
    # Get exam type
    exam_type = current_user.get("current_exam", "")
    
    return {
        "exam_type": exam_type,
        "credits": {
            "mocks": {
                "total": sum(p.get("mocks_total", 0) for p in purchases),
                "used": sum(p.get("mocks_used", 0) for p in purchases),
                "remaining": total_mocks
            },
            "speaking": {
                "total": sum(p.get("speaking_total", 0) for p in purchases),
                "used": sum(p.get("speaking_used", 0) for p in purchases),
                "remaining": total_speaking
            },
            "writing": {
                "total": sum(p.get("writing_total", 0) for p in purchases),
                "used": sum(p.get("writing_used", 0) for p in purchases),
                "remaining": total_writing
            }
        },
        "purchases": purchases,
        "can_take_mock": total_mocks > 0,
        "can_book_speaking": total_speaking > 0,
        "can_submit_writing": total_writing > 0
    }

@router.get("/my-purchases")
async def get_my_purchases(current_user: dict = Depends(get_current_user)):
    """Get student's purchase history"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view purchases")
    
    purchases = await db.student_purchases.find(
        {"student_id": current_user["id"]},
        {"_id": 0}
    ).sort("purchased_at", -1).to_list(50)
    
    return {"purchases": purchases}

# ==================== MOCK EXAM CONSUMPTION ====================

@router.post("/start-mock")
async def start_mock_exam(request: MockStartRequest, current_user: dict = Depends(get_current_user)):
    """Start a mock exam - consumes 1 mock credit"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can take mocks")
    
    # Verify exam type matches
    student_exam = current_user.get("current_exam")
    if student_exam and student_exam != request.exam_type:
        raise HTTPException(
            status_code=400, 
            detail=f"You are enrolled in {student_exam.upper()}, not {request.exam_type.upper()}"
        )
    
    # Check if student has mock credits
    purchases = await db.student_purchases.find(
        {
            "student_id": current_user["id"],
            "exam_type": request.exam_type,
            "status": "completed",
            "mocks_remaining": {"$gt": 0}
        }
    ).sort("purchased_at", 1).to_list(10)  # Use oldest purchase first
    
    if not purchases:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "No mock credits remaining",
                "message": "You have used all your mock exams. Purchase more to continue.",
                "upsell": True
            }
        )
    
    # Consume 1 mock from the oldest purchase
    purchase = purchases[0]
    
    # Create exam attempt
    attempt_id = str(uuid.uuid4())
    attempt_doc = {
        "id": attempt_id,
        "student_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        "purchase_id": purchase["id"],
        "exam_type": request.exam_type,
        "section": request.section,  # None for full exam
        "is_full_mock": request.section is None,
        "timed": request.timed,
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "time_limit_seconds": get_exam_time_limit(request.exam_type, request.section),
        "answers": {},
        "score": None,
        "feedback": None,
        "pdf_generated": False
    }
    
    await db.mock_attempts.insert_one(attempt_doc)
    
    # Deduct 1 mock credit (only for full mocks, sections are free practice)
    if request.section is None:
        await db.student_purchases.update_one(
            {"id": purchase["id"]},
            {
                "$inc": {"mocks_used": 1, "mocks_remaining": -1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
    
    # Get exam questions
    questions = await get_mock_questions(request.exam_type, request.section)
    
    attempt_doc.pop("_id", None)
    return {
        "attempt_id": attempt_id,
        "exam_type": request.exam_type,
        "section": request.section,
        "time_limit_seconds": attempt_doc["time_limit_seconds"],
        "questions": questions,
        "mocks_remaining_after": purchase["mocks_remaining"] - 1 if request.section is None else purchase["mocks_remaining"],
        "message": "Mock exam started. Good luck!" if request.section is None else "Section practice started."
    }

@router.post("/submit-mock")
async def submit_mock_exam(request: MockSubmitRequest, current_user: dict = Depends(get_current_user)):
    """Submit completed mock exam and get feedback"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit mocks")
    
    attempt = await db.mock_attempts.find_one({
        "id": request.attempt_id,
        "student_id": current_user["id"],
        "status": "in_progress"
    })
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found or already submitted")
    
    # Calculate score and generate feedback
    score, section_scores, feedback = await evaluate_mock(
        attempt["exam_type"],
        attempt.get("section"),
        request.answers
    )
    
    # Update attempt
    completed_at = datetime.now(timezone.utc).isoformat()
    await db.mock_attempts.update_one(
        {"id": request.attempt_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": completed_at,
                "time_taken_seconds": request.time_taken_seconds,
                "answers": request.answers,
                "score": score,
                "section_scores": section_scores,
                "feedback": feedback
            }
        }
    )
    
    # Record for gamification
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"last_activity": completed_at}}
    )
    
    return {
        "attempt_id": request.attempt_id,
        "score": score,
        "section_scores": section_scores,
        "feedback": feedback,
        "time_taken_seconds": request.time_taken_seconds,
        "completed_at": completed_at,
        "pdf_available": True,
        "message": "Exam completed! Your detailed feedback is ready."
    }

@router.get("/attempt/{attempt_id}")
async def get_attempt_details(attempt_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific attempt"""
    query = {"id": attempt_id}
    
    if current_user["user_type"] == "student":
        query["student_id"] = current_user["id"]
    elif current_user["user_type"] == "institution":
        query["institution_id"] = current_user["id"]
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    attempt = await db.mock_attempts.find_one(query, {"_id": 0})
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    return attempt

@router.get("/my-history")
async def get_mock_history(
    exam_type: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get student's mock exam history"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view history")
    
    query = {"student_id": current_user["id"], "status": "completed"}
    if exam_type:
        query["exam_type"] = exam_type
    
    attempts = await db.mock_attempts.find(
        query,
        {"_id": 0, "answers": 0}  # Exclude large fields
    ).sort("completed_at", -1).limit(limit).to_list(limit)
    
    return {
        "attempts": attempts,
        "total": len(attempts)
    }

# ==================== PDF FEEDBACK GENERATION ====================

@router.get("/attempt/{attempt_id}/pdf")
async def generate_feedback_pdf(attempt_id: str, current_user: dict = Depends(get_current_user)):
    """Generate and return premium PDF feedback report"""
    query = {"id": attempt_id, "status": "completed"}
    
    if current_user["user_type"] == "student":
        query["student_id"] = current_user["id"]
    elif current_user["user_type"] == "institution":
        query["institution_id"] = current_user["id"]
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    attempt = await db.mock_attempts.find_one(query)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Get student info
    student = await db.users.find_one(
        {"id": attempt["student_id"]},
        {"_id": 0, "name": 1, "email": 1}
    )
    
    # Get institution branding
    institution = await db.institution_branding.find_one(
        {"institution_id": attempt.get("institution_id")},
        {"_id": 0}
    )
    
    # Generate PDF (using reportlab or similar)
    pdf_content = generate_premium_pdf_report(attempt, student, institution)
    
    # Mark as generated
    await db.mock_attempts.update_one(
        {"id": attempt_id},
        {"$set": {"pdf_generated": True, "pdf_generated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="exam_report_{attempt_id[:8]}.pdf"'
        }
    )

# ==================== UPSELL ENDPOINTS ====================

@router.get("/upsell-options")
async def get_upsell_options(current_user: dict = Depends(get_current_user)):
    """Get available upsell options for the student"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view upsells")
    
    institution_id = current_user.get("institution_id")
    exam_type = current_user.get("current_exam")
    
    # Get available plans
    plans = await db.exam_plans.find(
        {"institution_id": institution_id, "exam_type": exam_type, "is_active": True},
        {"_id": 0}
    ).to_list(20)
    
    # Get student's current credits
    credits_response = await get_my_credits(current_user)
    
    # Determine recommendations
    recommendations = []
    if credits_response["credits"]["mocks"]["remaining"] <= 1:
        recommendations.append({
            "type": "mocks",
            "message": "Running low on mock exams!",
            "suggested_plans": [p for p in plans if p.get("mock_count", 0) > 0][:3]
        })
    
    if credits_response["credits"]["speaking"]["remaining"] == 0:
        recommendations.append({
            "type": "speaking",
            "message": "Add speaking practice sessions",
            "suggested_plans": [p for p in plans if p.get("speaking_sessions", 0) > 0][:3]
        })
    
    return {
        "current_credits": credits_response["credits"],
        "available_plans": plans,
        "recommendations": recommendations,
        "quick_buys": [
            {"type": "single_mock", "name": "1 Extra Mock", "price": 15},
            {"type": "speaking_session", "name": "Speaking Session", "price": 25},
            {"type": "writing_eval", "name": "Writing Evaluation", "price": 20}
        ]
    }

# ==================== HELPER FUNCTIONS ====================

def get_exam_time_limit(exam_type: str, section: Optional[str]) -> int:
    """Get time limit in seconds for exam type and section"""
    time_limits = {
        "oet": {"full": 180 * 60, "reading": 60 * 60, "writing": 45 * 60, "listening": 50 * 60, "speaking": 20 * 60},
        "ielts": {"full": 170 * 60, "reading": 60 * 60, "writing": 60 * 60, "listening": 40 * 60, "speaking": 15 * 60},
        "toefl": {"full": 200 * 60, "reading": 54 * 60, "writing": 50 * 60, "listening": 41 * 60, "speaking": 17 * 60},
        "pte": {"full": 180 * 60, "reading": 32 * 60, "writing": 60 * 60, "listening": 45 * 60, "speaking": 30 * 60},
        "cambridge": {"full": 240 * 60, "reading": 90 * 60, "writing": 90 * 60, "listening": 40 * 60, "speaking": 15 * 60},
    }
    
    exam_times = time_limits.get(exam_type, {"full": 180 * 60})
    if section:
        return exam_times.get(section, 60 * 60)
    return exam_times.get("full", 180 * 60)

async def get_mock_questions(exam_type: str, section: Optional[str]) -> List[dict]:
    """Get questions for a mock exam from database"""
    query = {"exam_type": exam_type, "is_active": True}
    if section:
        query["section"] = section
    
    questions = await db.mock_questions.find(query, {"_id": 0}).to_list(100)
    
    if not questions:
        # Return sample structure if no questions in DB
        return [{
            "id": "sample_1",
            "section": section or "reading",
            "type": "multiple_choice",
            "question": f"Sample {exam_type.upper()} question",
            "options": ["A", "B", "C", "D"],
            "points": 1
        }]
    
    return questions

async def evaluate_mock(exam_type: str, section: Optional[str], answers: Dict) -> tuple:
    """Evaluate mock exam answers and generate feedback"""
    # This would connect to AI for detailed evaluation
    # For now, return mock evaluation
    
    base_score = 75  # Would be calculated based on answers
    
    section_scores = {
        "reading": 78,
        "writing": 72,
        "listening": 80,
        "speaking": 70
    }
    
    feedback = {
        "overall": f"Good performance on this {exam_type.upper()} mock exam.",
        "strengths": [
            "Strong reading comprehension",
            "Good time management"
        ],
        "areas_to_improve": [
            "Work on writing coherence",
            "Practice speaking fluency"
        ],
        "recommendations": [
            "Review grammar rules for writing",
            "Practice with AI tutor for speaking"
        ],
        "section_feedback": {
            "reading": "Excellent understanding of main ideas. Work on inference questions.",
            "writing": "Good structure but needs more cohesive devices.",
            "listening": "Strong overall. Pay attention to specific details.",
            "speaking": "Clear pronunciation. Work on extending responses."
        },
        "next_steps": [
            "Take another mock in 3-5 days",
            "Focus on weak sections with practice exercises",
            "Book a speaking session for personalized feedback"
        ]
    }
    
    return base_score, section_scores, feedback

def generate_premium_pdf_report(attempt: dict, student: dict, institution: dict) -> bytes:
    """Generate premium PDF feedback report"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.units import inch
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1e3a5f'))
        
        story = []
        
        # Header with institution name
        inst_name = institution.get("name", "ProficientHub") if institution else "ProficientHub"
        story.append(Paragraph(inst_name, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Exam Report Title
        exam_type = attempt.get("exam_type", "").upper()
        story.append(Paragraph(f"{exam_type} Mock Exam Report", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Student Info
        student_name = student.get("name", "Student") if student else "Student"
        completed_at = attempt.get("completed_at", "")[:10]
        story.append(Paragraph(f"<b>Student:</b> {student_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {completed_at}", styles['Normal']))
        story.append(Paragraph(f"<b>Exam ID:</b> {attempt.get('id', '')[:8]}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Score
        score = attempt.get("score", 0)
        story.append(Paragraph(f"<b>Overall Score: {score}%</b>", ParagraphStyle('Score', parent=styles['Heading2'], fontSize=20, textColor=colors.HexColor('#2e7d32'))))
        story.append(Spacer(1, 0.2*inch))
        
        # Section Scores Table
        section_scores = attempt.get("section_scores", {})
        if section_scores:
            data = [["Section", "Score"]]
            for section, score in section_scores.items():
                data.append([section.capitalize(), f"{score}%"])
            
            table = Table(data, colWidths=[3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
        
        # Feedback
        feedback = attempt.get("feedback", {})
        if feedback:
            story.append(Paragraph("<b>Detailed Feedback</b>", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            if feedback.get("overall"):
                story.append(Paragraph(feedback["overall"], styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
            
            if feedback.get("strengths"):
                story.append(Paragraph("<b>Strengths:</b>", styles['Normal']))
                for s in feedback["strengths"]:
                    story.append(Paragraph(f"• {s}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if feedback.get("areas_to_improve"):
                story.append(Paragraph("<b>Areas to Improve:</b>", styles['Normal']))
                for a in feedback["areas_to_improve"]:
                    story.append(Paragraph(f"• {a}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if feedback.get("recommendations"):
                story.append(Paragraph("<b>Recommendations:</b>", styles['Normal']))
                for r in feedback["recommendations"]:
                    story.append(Paragraph(f"• {r}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except ImportError:
        # Fallback if reportlab not installed
        return b"PDF generation requires reportlab library. Please install it."
