"""
ERP Premium Module - Invoicing System
Complete invoicing with multi-currency, tax compliance, and e-invoicing
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import uuid

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user
from .config import SUPPORTED_CURRENCIES, FISCAL_REGIONS, INVOICE_FORMATS

router = APIRouter(prefix="/erp/invoices", tags=["ERP - Invoicing"])

# ==================== MODELS ====================

class InvoiceLineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    discount_percent: float = 0
    tax_rate: float = 0
    tax_code: Optional[str] = None
    account_code: Optional[str] = "4100"  # Default to subscription revenue

class InvoiceAddress(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    tax_id: Optional[str] = None

class InvoiceCreate(BaseModel):
    customer_id: str
    customer_type: str = "institution"  # institution, individual
    currency: str = "USD"
    billing_address: Optional[InvoiceAddress] = None
    items: List[InvoiceLineItem]
    payment_terms_days: int = 30
    po_number: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_send: bool = False

class RecurringInvoiceCreate(BaseModel):
    customer_id: str
    currency: str = "USD"
    items: List[InvoiceLineItem]
    frequency: str  # monthly, quarterly, annually
    start_date: str
    end_date: Optional[str] = None
    payment_terms_days: int = 30
    auto_send: bool = True

class InvoicePayment(BaseModel):
    amount: float
    payment_method: str  # card, bank_transfer, check, cash, other
    payment_date: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None

# ==================== HELPER FUNCTIONS ====================

async def get_next_invoice_number(institution_id: str, country: str = "US") -> str:
    """Generate sequential invoice number based on regional format"""
    year = datetime.now(timezone.utc).year
    
    # Get current count for this year
    count = await db.erp_invoices.count_documents({
        "institution_id": institution_id,
        "invoice_number": {"$regex": f"^.*{year}.*$"}
    })
    
    # Get format based on country
    format_template = INVOICE_FORMATS.get(country, INVOICE_FORMATS["default"])
    
    # Generate number
    invoice_number = format_template.format(
        prefix="INV",
        year=year,
        sequence=count + 1,
        month=datetime.now(timezone.utc).month,
        uuid=str(uuid.uuid4())[:8].upper()
    )
    
    return invoice_number

def calculate_invoice_totals(items: List[InvoiceLineItem], exchange_rate: float = 1.0) -> Dict:
    """Calculate all invoice totals including taxes"""
    subtotal = 0
    total_discount = 0
    total_tax = 0
    tax_breakdown = {}
    
    for item in items:
        line_gross = item.quantity * item.unit_price
        line_discount = line_gross * (item.discount_percent / 100)
        line_net = line_gross - line_discount
        line_tax = line_net * (item.tax_rate / 100)
        
        subtotal += line_gross
        total_discount += line_discount
        total_tax += line_tax
        
        # Track tax by code
        tax_code = item.tax_code or f"TAX_{item.tax_rate}"
        if tax_code not in tax_breakdown:
            tax_breakdown[tax_code] = {"rate": item.tax_rate, "taxable": 0, "tax": 0}
        tax_breakdown[tax_code]["taxable"] += line_net
        tax_breakdown[tax_code]["tax"] += line_tax
    
    total = subtotal - total_discount + total_tax
    
    return {
        "subtotal": round(subtotal, 2),
        "discount": round(total_discount, 2),
        "tax": round(total_tax, 2),
        "total": round(total, 2),
        "tax_breakdown": {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in tax_breakdown.items()},
        "base_currency_total": round(total * exchange_rate, 2) if exchange_rate != 1 else None
    }

async def update_accounting_entries(invoice: dict, action: str = "create"):
    """Create accounting journal entries for invoice"""
    entries = []
    
    if action == "create":
        # Debit Accounts Receivable
        entries.append({
            "id": str(uuid.uuid4()),
            "invoice_id": invoice["id"],
            "date": invoice["issue_date"],
            "account_code": "1120",  # Accounts Receivable
            "description": f"Invoice {invoice['invoice_number']}",
            "debit": invoice["totals"]["total"],
            "credit": 0,
            "currency": invoice["currency"]
        })
        
        # Credit Revenue
        entries.append({
            "id": str(uuid.uuid4()),
            "invoice_id": invoice["id"],
            "date": invoice["issue_date"],
            "account_code": "4100",  # Subscription Revenue
            "description": f"Invoice {invoice['invoice_number']}",
            "debit": 0,
            "credit": invoice["totals"]["subtotal"] - invoice["totals"]["discount"],
            "currency": invoice["currency"]
        })
        
        # Credit Tax Payable
        if invoice["totals"]["tax"] > 0:
            entries.append({
                "id": str(uuid.uuid4()),
                "invoice_id": invoice["id"],
                "date": invoice["issue_date"],
                "account_code": "2130",  # Tax Payable
                "description": f"Tax on Invoice {invoice['invoice_number']}",
                "debit": 0,
                "credit": invoice["totals"]["tax"],
                "currency": invoice["currency"]
            })
    
    elif action == "payment":
        # Debit Cash
        entries.append({
            "id": str(uuid.uuid4()),
            "invoice_id": invoice["id"],
            "date": datetime.now(timezone.utc).isoformat(),
            "account_code": "1110",  # Cash
            "description": f"Payment for Invoice {invoice['invoice_number']}",
            "debit": invoice["amount_paid"],
            "credit": 0,
            "currency": invoice["currency"]
        })
        
        # Credit Accounts Receivable
        entries.append({
            "id": str(uuid.uuid4()),
            "invoice_id": invoice["id"],
            "date": datetime.now(timezone.utc).isoformat(),
            "account_code": "1120",  # Accounts Receivable
            "description": f"Payment for Invoice {invoice['invoice_number']}",
            "debit": 0,
            "credit": invoice["amount_paid"],
            "currency": invoice["currency"]
        })
    
    if entries:
        await db.erp_journal_entries.insert_many(entries)

# ==================== ENDPOINTS ====================

@router.post("")
async def create_invoice(
    invoice_data: InvoiceCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new invoice"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can create invoices")
    
    # Validate currency
    if invoice_data.currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {invoice_data.currency}")
    
    # Get customer info
    customer = await db.users.find_one({"id": invoice_data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Calculate totals
    totals = calculate_invoice_totals(invoice_data.items)
    
    # Generate invoice number
    country = invoice_data.billing_address.country if invoice_data.billing_address else "US"
    invoice_number = await get_next_invoice_number(current_user["id"], country)
    
    invoice_id = str(uuid.uuid4())
    issue_date = datetime.now(timezone.utc)
    due_date = issue_date + timedelta(days=invoice_data.payment_terms_days)
    
    invoice_doc = {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "institution_id": current_user["id"],
        "customer_id": invoice_data.customer_id,
        "customer_type": invoice_data.customer_type,
        "customer_name": customer.get("institution_name", customer.get("name", "")),
        "customer_email": customer.get("email"),
        "billing_address": invoice_data.billing_address.dict() if invoice_data.billing_address else None,
        "currency": invoice_data.currency,
        "currency_symbol": SUPPORTED_CURRENCIES[invoice_data.currency]["symbol"],
        "items": [item.dict() for item in invoice_data.items],
        "totals": totals,
        "status": "draft",
        "issue_date": issue_date.isoformat(),
        "due_date": due_date.isoformat(),
        "payment_terms_days": invoice_data.payment_terms_days,
        "po_number": invoice_data.po_number,
        "notes": invoice_data.notes,
        "internal_notes": invoice_data.internal_notes,
        "metadata": invoice_data.metadata,
        "amount_paid": 0,
        "amount_due": totals["total"],
        "payments": [],
        "created_at": issue_date.isoformat(),
        "created_by": current_user["id"]
    }
    
    await db.erp_invoices.insert_one(invoice_doc)
    
    # Create accounting entries
    background_tasks.add_task(update_accounting_entries, invoice_doc, "create")
    
    # Auto-send if requested
    if invoice_data.auto_send:
        invoice_doc["status"] = "sent"
        invoice_doc["sent_at"] = issue_date.isoformat()
        await db.erp_invoices.update_one(
            {"id": invoice_id},
            {"$set": {"status": "sent", "sent_at": issue_date.isoformat()}}
        )
    
    return {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "status": invoice_doc["status"],
        "totals": totals,
        "currency": invoice_data.currency,
        "due_date": due_date.isoformat()
    }

@router.get("")
async def list_invoices(
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    currency: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    overdue_only: bool = False,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List invoices with filtering"""
    query = {"institution_id": current_user["id"]}
    
    if status:
        query["status"] = status
    if customer_id:
        query["customer_id"] = customer_id
    if currency:
        query["currency"] = currency
    if from_date:
        query["issue_date"] = {"$gte": from_date}
    if to_date:
        if "issue_date" in query:
            query["issue_date"]["$lte"] = to_date
        else:
            query["issue_date"] = {"$lte": to_date}
    if overdue_only:
        query["due_date"] = {"$lt": datetime.now(timezone.utc).isoformat()}
        query["status"] = {"$nin": ["paid", "cancelled"]}
    
    total = await db.erp_invoices.count_documents(query)
    skip = (page - 1) * per_page
    
    invoices = await db.erp_invoices.find(
        query,
        {"_id": 0, "internal_notes": 0}
    ).sort("issue_date", -1).skip(skip).limit(per_page).to_list(per_page)
    
    return {
        "invoices": invoices,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single invoice"""
    invoice = await db.erp_invoices.find_one(
        {"id": invoice_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    email_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Mark invoice as sent (and optionally send email)"""
    invoice = await db.erp_invoices.find_one(
        {"id": invoice_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    await db.erp_invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": "sent", "sent_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # TODO: Implement actual email sending
    
    return {"message": "Invoice sent", "status": "sent"}

@router.post("/{invoice_id}/payments")
async def record_payment(
    invoice_id: str,
    payment: InvoicePayment,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Record a payment against an invoice"""
    invoice = await db.erp_invoices.find_one(
        {"id": invoice_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")
    
    payment_id = str(uuid.uuid4())
    payment_date = payment.payment_date or datetime.now(timezone.utc).isoformat()
    
    payment_doc = {
        "id": payment_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "payment_date": payment_date,
        "reference": payment.reference,
        "notes": payment.notes,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "recorded_by": current_user["id"]
    }
    
    new_amount_paid = invoice["amount_paid"] + payment.amount
    new_amount_due = invoice["totals"]["total"] - new_amount_paid
    new_status = "paid" if new_amount_due <= 0 else "partial"
    
    await db.erp_invoices.update_one(
        {"id": invoice_id},
        {
            "$push": {"payments": payment_doc},
            "$set": {
                "amount_paid": new_amount_paid,
                "amount_due": max(new_amount_due, 0),
                "status": new_status,
                "paid_at": payment_date if new_status == "paid" else None
            }
        }
    )
    
    # Create accounting entries for payment
    invoice["amount_paid"] = payment.amount
    background_tasks.add_task(update_accounting_entries, invoice, "payment")
    
    return {
        "payment_id": payment_id,
        "amount_paid": new_amount_paid,
        "amount_due": max(new_amount_due, 0),
        "status": new_status
    }

@router.post("/{invoice_id}/void")
async def void_invoice(
    invoice_id: str,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Void an invoice"""
    invoice = await db.erp_invoices.find_one(
        {"id": invoice_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] == "paid":
        raise HTTPException(status_code=400, detail="Cannot void a paid invoice. Create a credit note instead.")
    
    await db.erp_invoices.update_one(
        {"id": invoice_id},
        {
            "$set": {
                "status": "void",
                "void_reason": reason,
                "voided_at": datetime.now(timezone.utc).isoformat(),
                "voided_by": current_user["id"]
            }
        }
    )
    
    return {"message": "Invoice voided", "status": "void"}

@router.post("/{invoice_id}/duplicate")
async def duplicate_invoice(
    invoice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a copy of an existing invoice"""
    invoice = await db.erp_invoices.find_one(
        {"id": invoice_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Create new invoice with same details
    new_id = str(uuid.uuid4())
    country = invoice.get("billing_address", {}).get("country", "US")
    new_number = await get_next_invoice_number(current_user["id"], country)
    issue_date = datetime.now(timezone.utc)
    
    new_invoice = {
        **invoice,
        "id": new_id,
        "invoice_number": new_number,
        "status": "draft",
        "issue_date": issue_date.isoformat(),
        "due_date": (issue_date + timedelta(days=invoice["payment_terms_days"])).isoformat(),
        "amount_paid": 0,
        "amount_due": invoice["totals"]["total"],
        "payments": [],
        "created_at": issue_date.isoformat(),
        "sent_at": None,
        "paid_at": None
    }
    
    await db.erp_invoices.insert_one(new_invoice)
    
    return {
        "id": new_id,
        "invoice_number": new_number,
        "message": "Invoice duplicated"
    }

@router.get("/stats/summary")
async def get_invoice_stats(
    period: str = Query("month", enum=["week", "month", "quarter", "year"]),
    currency: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get invoice statistics summary"""
    # Calculate date range
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=365)
    
    query = {
        "institution_id": current_user["id"],
        "issue_date": {"$gte": start_date.isoformat()}
    }
    if currency:
        query["currency"] = currency
    
    # Aggregate stats
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total": {"$sum": "$totals.total"},
            "paid": {"$sum": "$amount_paid"}
        }}
    ]
    
    stats = await db.erp_invoices.aggregate(pipeline).to_list(10)
    
    # Format results
    result = {
        "period": period,
        "currency": currency or "all",
        "by_status": {s["_id"]: {"count": s["count"], "total": s["total"], "paid": s["paid"]} for s in stats},
        "totals": {
            "invoiced": sum(s["total"] for s in stats),
            "collected": sum(s["paid"] for s in stats),
            "outstanding": sum(s["total"] - s["paid"] for s in stats)
        }
    }
    
    return result

# ==================== RECURRING INVOICES ====================

@router.post("/recurring")
async def create_recurring_invoice(
    recurring_data: RecurringInvoiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a recurring invoice schedule"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    recurring_id = str(uuid.uuid4())
    
    recurring_doc = {
        "id": recurring_id,
        "institution_id": current_user["id"],
        "customer_id": recurring_data.customer_id,
        "currency": recurring_data.currency,
        "items": [item.dict() for item in recurring_data.items],
        "totals": calculate_invoice_totals(recurring_data.items),
        "frequency": recurring_data.frequency,
        "start_date": recurring_data.start_date,
        "end_date": recurring_data.end_date,
        "next_invoice_date": recurring_data.start_date,
        "payment_terms_days": recurring_data.payment_terms_days,
        "auto_send": recurring_data.auto_send,
        "status": "active",
        "invoices_generated": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.erp_recurring_invoices.insert_one(recurring_doc)
    
    return {
        "id": recurring_id,
        "message": "Recurring invoice created",
        "next_invoice_date": recurring_data.start_date
    }

@router.get("/recurring")
async def list_recurring_invoices(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List recurring invoice schedules"""
    query = {"institution_id": current_user["id"]}
    if status:
        query["status"] = status
    
    recurring = await db.erp_recurring_invoices.find(query, {"_id": 0}).to_list(100)
    
    return {"recurring_invoices": recurring}
