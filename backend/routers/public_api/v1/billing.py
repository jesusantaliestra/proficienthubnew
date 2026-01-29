"""
Public API v1 - Billing Endpoints
Billing, subscriptions, and payment management via API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import uuid

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read, require_write, require_admin

router = APIRouter(prefix="/billing", tags=["Billing API"])

# Models
class InvoiceLineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class InvoiceCreate(BaseModel):
    institution_id: str
    items: List[InvoiceLineItem]
    currency: str = "USD"
    due_days: int = 30
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    institution_id: str
    institution_name: str
    items: List[InvoiceLineItem]
    subtotal: float
    tax: float
    total: float
    currency: str
    status: str  # draft, sent, paid, overdue, cancelled
    issue_date: str
    due_date: str
    paid_date: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_method: str  # card, bank_transfer, check, other
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    invoice_id: str
    amount: float
    payment_method: str
    status: str
    reference: Optional[str]
    created_at: str

class SubscriptionResponse(BaseModel):
    id: str
    institution_id: str
    plan: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    created_at: str

# Helper functions
async def generate_invoice_number() -> str:
    """Generate unique invoice number"""
    year = datetime.now(timezone.utc).year
    count = await db.invoices.count_documents({"invoice_number": {"$regex": f"^INV-{year}"}})
    return f"INV-{year}-{count + 1:05d}"

# Endpoints
@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    api_auth: dict = Depends(require_write)
):
    """Create a new invoice for an institution"""
    # Verify institution exists
    institution = await db.users.find_one(
        {"id": invoice_data.institution_id, "user_type": "institution"},
        {"_id": 0, "institution_name": 1, "name": 1}
    )
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Calculate totals
    subtotal = sum(item.total for item in invoice_data.items)
    tax = 0  # Tax calculation would be based on jurisdiction
    total = subtotal + tax
    
    invoice_id = str(uuid.uuid4())
    invoice_number = await generate_invoice_number()
    issue_date = datetime.now(timezone.utc)
    due_date = issue_date + timedelta(days=invoice_data.due_days)
    
    invoice_doc = {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "institution_id": invoice_data.institution_id,
        "institution_name": institution.get("institution_name", institution.get("name", "")),
        "items": [item.dict() for item in invoice_data.items],
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "currency": invoice_data.currency,
        "status": "draft",
        "issue_date": issue_date.isoformat(),
        "due_date": due_date.isoformat(),
        "paid_date": None,
        "notes": invoice_data.notes,
        "metadata": invoice_data.metadata,
        "created_at": issue_date.isoformat()
    }
    
    await db.invoices.insert_one(invoice_doc)
    
    return InvoiceResponse(**{k: v for k, v in invoice_doc.items() if k != "_id"})

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    institution_id: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    api_auth: dict = Depends(require_read)
):
    """List invoices with filtering"""
    query = {}
    
    if institution_id:
        query["institution_id"] = institution_id
    if status:
        query["status"] = status
    if from_date:
        query["issue_date"] = {"$gte": from_date}
    if to_date:
        if "issue_date" in query:
            query["issue_date"]["$lte"] = to_date
        else:
            query["issue_date"] = {"$lte": to_date}
    
    skip = (page - 1) * per_page
    invoices = await db.invoices.find(
        query,
        {"_id": 0}
    ).sort("issue_date", -1).skip(skip).limit(per_page).to_list(per_page)
    
    return [InvoiceResponse(**inv) for inv in invoices]

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get a single invoice by ID"""
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return InvoiceResponse(**invoice)

@router.patch("/invoices/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: str,
    status: str,
    api_auth: dict = Depends(require_write)
):
    """Update invoice status"""
    valid_statuses = ["draft", "sent", "paid", "overdue", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    update_data = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    
    if status == "paid":
        update_data["paid_date"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {"message": f"Invoice status updated to {status}"}

@router.post("/payments", response_model=PaymentResponse)
async def record_payment(
    payment_data: PaymentCreate,
    api_auth: dict = Depends(require_write)
):
    """Record a payment against an invoice"""
    # Verify invoice exists
    invoice = await db.invoices.find_one({"id": payment_data.invoice_id}, {"_id": 0})
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    payment_id = str(uuid.uuid4())
    
    payment_doc = {
        "id": payment_id,
        "invoice_id": payment_data.invoice_id,
        "institution_id": invoice["institution_id"],
        "amount": payment_data.amount,
        "payment_method": payment_data.payment_method,
        "status": "completed",
        "reference": payment_data.reference,
        "notes": payment_data.notes,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.payments.insert_one(payment_doc)
    
    # Check if invoice is fully paid
    total_payments = await db.payments.aggregate([
        {"$match": {"invoice_id": payment_data.invoice_id, "status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    total_paid = total_payments[0]["total"] if total_payments else 0
    
    if total_paid >= invoice["total"]:
        await db.invoices.update_one(
            {"id": payment_data.invoice_id},
            {"$set": {"status": "paid", "paid_date": datetime.now(timezone.utc).isoformat()}}
        )
    
    return PaymentResponse(
        id=payment_id,
        invoice_id=payment_data.invoice_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        status="completed",
        reference=payment_data.reference,
        created_at=payment_doc["created_at"]
    )

@router.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    invoice_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """List payments with filtering"""
    query = {}
    
    if invoice_id:
        query["invoice_id"] = invoice_id
    if institution_id:
        query["institution_id"] = institution_id
    if from_date:
        query["created_at"] = {"$gte": from_date}
    if to_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = to_date
        else:
            query["created_at"] = {"$lte": to_date}
    
    payments = await db.payments.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    return [PaymentResponse(**p) for p in payments]

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    institution_id: Optional[str] = None,
    status: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """List active subscriptions"""
    query = {}
    
    if institution_id:
        query["institution_id"] = institution_id
    if status:
        query["status"] = status
    
    subscriptions = await db.subscriptions.find(query, {"_id": 0}).to_list(100)
    
    return [SubscriptionResponse(**s) for s in subscriptions]

@router.get("/revenue-summary")
async def get_revenue_summary(
    period: str = Query("month", enum=["week", "month", "quarter", "year"]),
    currency: str = "USD",
    api_auth: dict = Depends(require_read)
):
    """Get revenue summary for the specified period"""
    # Calculate date range
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Revenue from paid invoices
    revenue_pipeline = [
        {
            "$match": {
                "status": "paid",
                "currency": currency,
                "paid_date": {"$gte": start_date.isoformat()}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total"},
                "invoice_count": {"$sum": 1}
            }
        }
    ]
    
    revenue = await db.invoices.aggregate(revenue_pipeline).to_list(1)
    
    # Outstanding invoices
    outstanding_pipeline = [
        {
            "$match": {
                "status": {"$in": ["sent", "overdue"]},
                "currency": currency
            }
        },
        {
            "$group": {
                "_id": None,
                "total_outstanding": {"$sum": "$total"},
                "invoice_count": {"$sum": 1}
            }
        }
    ]
    
    outstanding = await db.invoices.aggregate(outstanding_pipeline).to_list(1)
    
    # MRR calculation (from active subscriptions)
    mrr_pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "total_mrr": {"$sum": "$monthly_amount"}}}
    ]
    mrr = await db.subscriptions.aggregate(mrr_pipeline).to_list(1)
    
    return {
        "period": period,
        "currency": currency,
        "revenue": {
            "total": revenue[0]["total_revenue"] if revenue else 0,
            "invoice_count": revenue[0]["invoice_count"] if revenue else 0
        },
        "outstanding": {
            "total": outstanding[0]["total_outstanding"] if outstanding else 0,
            "invoice_count": outstanding[0]["invoice_count"] if outstanding else 0
        },
        "mrr": mrr[0]["total_mrr"] if mrr else 0,
        "arr": (mrr[0]["total_mrr"] * 12) if mrr else 0,
        "generated_at": now.isoformat()
    }

@router.get("/aging-report")
async def get_aging_report(
    institution_id: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """Get accounts receivable aging report"""
    now = datetime.now(timezone.utc)
    
    query = {"status": {"$in": ["sent", "overdue"]}}
    if institution_id:
        query["institution_id"] = institution_id
    
    invoices = await db.invoices.find(query, {"_id": 0}).to_list(1000)
    
    aging_buckets = {
        "current": {"count": 0, "total": 0},
        "1-30_days": {"count": 0, "total": 0},
        "31-60_days": {"count": 0, "total": 0},
        "61-90_days": {"count": 0, "total": 0},
        "over_90_days": {"count": 0, "total": 0}
    }
    
    for inv in invoices:
        due_date = datetime.fromisoformat(inv["due_date"].replace('Z', '+00:00'))
        days_overdue = (now - due_date).days
        
        if days_overdue <= 0:
            bucket = "current"
        elif days_overdue <= 30:
            bucket = "1-30_days"
        elif days_overdue <= 60:
            bucket = "31-60_days"
        elif days_overdue <= 90:
            bucket = "61-90_days"
        else:
            bucket = "over_90_days"
        
        aging_buckets[bucket]["count"] += 1
        aging_buckets[bucket]["total"] += inv["total"]
    
    total_outstanding = sum(b["total"] for b in aging_buckets.values())
    
    return {
        "aging_buckets": aging_buckets,
        "total_outstanding": total_outstanding,
        "invoice_count": sum(b["count"] for b in aging_buckets.values()),
        "generated_at": now.isoformat()
    }
