"""
ERP Premium Module - Accounting System
Full double-entry accounting with financial reporting
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
from utils.auth import get_current_user
from .config import DEFAULT_CHART_OF_ACCOUNTS, SUPPORTED_CURRENCIES

router = APIRouter(prefix="/erp/accounting", tags=["ERP - Accounting"])

# ==================== MODELS ====================

class AccountCreate(BaseModel):
    code: str
    name: str
    type: str  # asset, liability, equity, revenue, expense
    parent_code: Optional[str] = None
    description: Optional[str] = None
    currency: str = "USD"
    is_active: bool = True

class JournalEntryLine(BaseModel):
    account_code: str
    description: str
    debit: float = 0
    credit: float = 0
    currency: str = "USD"
    exchange_rate: float = 1.0

class JournalEntryCreate(BaseModel):
    date: str
    reference: Optional[str] = None
    description: str
    lines: List[JournalEntryLine]
    metadata: Optional[Dict[str, Any]] = None

class BudgetCreate(BaseModel):
    account_code: str
    period: str  # YYYY-MM
    amount: float
    currency: str = "USD"
    notes: Optional[str] = None

# ==================== HELPER FUNCTIONS ====================

async def validate_journal_entry(lines: List[JournalEntryLine]) -> bool:
    """Validate that debits equal credits"""
    total_debit = sum(line.debit * line.exchange_rate for line in lines)
    total_credit = sum(line.credit * line.exchange_rate for line in lines)
    return abs(total_debit - total_credit) < 0.01  # Allow for rounding

async def get_account_balance(institution_id: str, account_code: str, as_of_date: str = None) -> Dict:
    """Calculate account balance from journal entries"""
    query = {
        "institution_id": institution_id,
        "account_code": account_code
    }
    if as_of_date:
        query["date"] = {"$lte": as_of_date}
    
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": None,
            "total_debit": {"$sum": "$debit"},
            "total_credit": {"$sum": "$credit"}
        }}
    ]
    
    result = await db.erp_journal_entries.aggregate(pipeline).to_list(1)
    
    if result:
        debit = result[0]["total_debit"]
        credit = result[0]["total_credit"]
        return {
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "balance": round(debit - credit, 2)
        }
    
    return {"debit": 0, "credit": 0, "balance": 0}

# ==================== CHART OF ACCOUNTS ====================

@router.get("/chart-of-accounts")
async def get_chart_of_accounts(
    current_user: dict = Depends(get_current_user)
):
    """Get the chart of accounts for the institution"""
    # Get custom accounts
    custom_accounts = await db.erp_accounts.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(500)
    
    if not custom_accounts:
        # Return default chart if no custom accounts
        return {
            "accounts": DEFAULT_CHART_OF_ACCOUNTS,
            "is_default": True
        }
    
    # Build hierarchical structure
    accounts = {a["code"]: a for a in custom_accounts}
    
    return {
        "accounts": accounts,
        "is_default": False,
        "total_accounts": len(custom_accounts)
    }

@router.post("/accounts")
async def create_account(
    account: AccountCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new account in the chart of accounts"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if code already exists
    existing = await db.erp_accounts.find_one({
        "institution_id": current_user["id"],
        "code": account.code
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    
    account_doc = {
        "id": str(uuid.uuid4()),
        "institution_id": current_user["id"],
        **account.dict(),
        "balance": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.erp_accounts.insert_one(account_doc)
    
    return {"message": "Account created", "code": account.code}

@router.get("/accounts/{account_code}")
async def get_account(
    account_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get account details with balance"""
    account = await db.erp_accounts.find_one(
        {"institution_id": current_user["id"], "code": account_code},
        {"_id": 0}
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get current balance
    balance = await get_account_balance(current_user["id"], account_code)
    account["current_balance"] = balance
    
    return account

@router.get("/accounts/{account_code}/transactions")
async def get_account_transactions(
    account_code: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get transactions (journal entries) for an account"""
    query = {
        "institution_id": current_user["id"],
        "account_code": account_code
    }
    
    if from_date:
        query["date"] = {"$gte": from_date}
    if to_date:
        if "date" in query:
            query["date"]["$lte"] = to_date
        else:
            query["date"] = {"$lte": to_date}
    
    total = await db.erp_journal_entries.count_documents(query)
    skip = (page - 1) * per_page
    
    entries = await db.erp_journal_entries.find(
        query,
        {"_id": 0}
    ).sort("date", -1).skip(skip).limit(per_page).to_list(per_page)
    
    # Calculate running balance
    running_balance = 0
    for entry in reversed(entries):
        running_balance += entry["debit"] - entry["credit"]
        entry["running_balance"] = round(running_balance, 2)
    
    return {
        "transactions": list(reversed(entries)),
        "total": total,
        "page": page,
        "per_page": per_page
    }

# ==================== JOURNAL ENTRIES ====================

@router.post("/journal-entries")
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a manual journal entry"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate debits = credits
    if not await validate_journal_entry(entry.lines):
        raise HTTPException(status_code=400, detail="Journal entry must balance (debits must equal credits)")
    
    entry_id = str(uuid.uuid4())
    
    # Create individual line entries
    for i, line in enumerate(entry.lines):
        line_doc = {
            "id": str(uuid.uuid4()),
            "journal_entry_id": entry_id,
            "institution_id": current_user["id"],
            "date": entry.date,
            "reference": entry.reference,
            "account_code": line.account_code,
            "description": line.description or entry.description,
            "debit": line.debit,
            "credit": line.credit,
            "currency": line.currency,
            "exchange_rate": line.exchange_rate,
            "base_debit": line.debit * line.exchange_rate,
            "base_credit": line.credit * line.exchange_rate,
            "line_number": i + 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": current_user["id"]
        }
        await db.erp_journal_entries.insert_one(line_doc)
    
    # Store the full entry for reference
    full_entry = {
        "id": entry_id,
        "institution_id": current_user["id"],
        "date": entry.date,
        "reference": entry.reference,
        "description": entry.description,
        "lines": [line.dict() for line in entry.lines],
        "total_debit": sum(line.debit for line in entry.lines),
        "total_credit": sum(line.credit for line in entry.lines),
        "metadata": entry.metadata,
        "status": "posted",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"]
    }
    await db.erp_journal_entry_headers.insert_one(full_entry)
    
    return {
        "id": entry_id,
        "message": "Journal entry created",
        "lines": len(entry.lines)
    }

@router.get("/journal-entries")
async def list_journal_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    account_code: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """List journal entry headers"""
    query = {"institution_id": current_user["id"]}
    
    if from_date:
        query["date"] = {"$gte": from_date}
    if to_date:
        if "date" in query:
            query["date"]["$lte"] = to_date
        else:
            query["date"] = {"$lte": to_date}
    
    total = await db.erp_journal_entry_headers.count_documents(query)
    skip = (page - 1) * per_page
    
    entries = await db.erp_journal_entry_headers.find(
        query,
        {"_id": 0}
    ).sort("date", -1).skip(skip).limit(per_page).to_list(per_page)
    
    return {
        "entries": entries,
        "total": total,
        "page": page,
        "per_page": per_page
    }

# ==================== FINANCIAL REPORTS ====================

@router.get("/reports/trial-balance")
async def get_trial_balance(
    as_of_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate trial balance report"""
    as_of = as_of_date or datetime.now(timezone.utc).isoformat()[:10]
    
    # Get all accounts with balances
    pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$lte": as_of}
            }
        },
        {
            "$group": {
                "_id": "$account_code",
                "debit": {"$sum": "$debit"},
                "credit": {"$sum": "$credit"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    balances = await db.erp_journal_entries.aggregate(pipeline).to_list(500)
    
    # Get account names
    accounts = await db.erp_accounts.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "code": 1, "name": 1, "type": 1}
    ).to_list(500)
    account_map = {a["code"]: a for a in accounts}
    
    # Build trial balance
    trial_balance = []
    total_debit = 0
    total_credit = 0
    
    for b in balances:
        account_info = account_map.get(b["_id"], {"name": "Unknown", "type": "unknown"})
        balance = b["debit"] - b["credit"]
        
        trial_balance.append({
            "account_code": b["_id"],
            "account_name": account_info["name"],
            "account_type": account_info["type"],
            "debit": round(b["debit"], 2),
            "credit": round(b["credit"], 2),
            "balance": round(balance, 2)
        })
        
        total_debit += b["debit"]
        total_credit += b["credit"]
    
    return {
        "as_of_date": as_of,
        "trial_balance": trial_balance,
        "totals": {
            "debit": round(total_debit, 2),
            "credit": round(total_credit, 2),
            "is_balanced": abs(total_debit - total_credit) < 0.01
        }
    }

@router.get("/reports/income-statement")
async def get_income_statement(
    from_date: str,
    to_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate income statement (P&L) report"""
    # Get revenue accounts (4xxx)
    revenue_pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$gte": from_date, "$lte": to_date},
                "account_code": {"$regex": "^4"}
            }
        },
        {
            "$group": {
                "_id": "$account_code",
                "credit": {"$sum": "$credit"},
                "debit": {"$sum": "$debit"}
            }
        }
    ]
    
    revenue = await db.erp_journal_entries.aggregate(revenue_pipeline).to_list(100)
    total_revenue = sum(r["credit"] - r["debit"] for r in revenue)
    
    # Get expense accounts (5xxx)
    expense_pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$gte": from_date, "$lte": to_date},
                "account_code": {"$regex": "^5"}
            }
        },
        {
            "$group": {
                "_id": "$account_code",
                "debit": {"$sum": "$debit"},
                "credit": {"$sum": "$credit"}
            }
        }
    ]
    
    expenses = await db.erp_journal_entries.aggregate(expense_pipeline).to_list(100)
    total_expenses = sum(e["debit"] - e["credit"] for e in expenses)
    
    # Get account names
    accounts = await db.erp_accounts.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "code": 1, "name": 1}
    ).to_list(500)
    account_map = {a["code"]: a["name"] for a in accounts}
    
    return {
        "period": {"from": from_date, "to": to_date},
        "revenue": {
            "items": [
                {
                    "account_code": r["_id"],
                    "account_name": account_map.get(r["_id"], "Unknown"),
                    "amount": round(r["credit"] - r["debit"], 2)
                }
                for r in revenue
            ],
            "total": round(total_revenue, 2)
        },
        "expenses": {
            "items": [
                {
                    "account_code": e["_id"],
                    "account_name": account_map.get(e["_id"], "Unknown"),
                    "amount": round(e["debit"] - e["credit"], 2)
                }
                for e in expenses
            ],
            "total": round(total_expenses, 2)
        },
        "net_income": round(total_revenue - total_expenses, 2),
        "gross_margin": round((total_revenue - total_expenses) / total_revenue * 100, 2) if total_revenue > 0 else 0
    }

@router.get("/reports/balance-sheet")
async def get_balance_sheet(
    as_of_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate balance sheet report"""
    as_of = as_of_date or datetime.now(timezone.utc).isoformat()[:10]
    
    # Get all account balances
    pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$lte": as_of}
            }
        },
        {
            "$group": {
                "_id": "$account_code",
                "debit": {"$sum": "$debit"},
                "credit": {"$sum": "$credit"}
            }
        }
    ]
    
    balances = await db.erp_journal_entries.aggregate(pipeline).to_list(500)
    
    # Get account info
    accounts = await db.erp_accounts.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "code": 1, "name": 1, "type": 1}
    ).to_list(500)
    account_map = {a["code"]: a for a in accounts}
    
    # Categorize
    assets = []
    liabilities = []
    equity = []
    total_assets = 0
    total_liabilities = 0
    total_equity = 0
    
    for b in balances:
        account_info = account_map.get(b["_id"], {"name": "Unknown", "type": "unknown"})
        balance = b["debit"] - b["credit"]
        
        item = {
            "account_code": b["_id"],
            "account_name": account_info["name"],
            "balance": round(abs(balance), 2)
        }
        
        if account_info["type"] == "asset" or b["_id"].startswith("1"):
            assets.append(item)
            total_assets += balance
        elif account_info["type"] == "liability" or b["_id"].startswith("2"):
            liabilities.append(item)
            total_liabilities += abs(balance)
        elif account_info["type"] == "equity" or b["_id"].startswith("3"):
            equity.append(item)
            total_equity += abs(balance)
    
    return {
        "as_of_date": as_of,
        "assets": {
            "items": assets,
            "total": round(total_assets, 2)
        },
        "liabilities": {
            "items": liabilities,
            "total": round(total_liabilities, 2)
        },
        "equity": {
            "items": equity,
            "total": round(total_equity, 2)
        },
        "liabilities_and_equity": round(total_liabilities + total_equity, 2),
        "is_balanced": abs(total_assets - (total_liabilities + total_equity)) < 0.01
    }

@router.get("/reports/cash-flow")
async def get_cash_flow_statement(
    from_date: str,
    to_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate cash flow statement"""
    # Operating activities (changes in working capital)
    # Investing activities
    # Financing activities
    
    # This is a simplified version - full implementation would track
    # actual cash movements
    
    # Get cash account changes
    cash_pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$gte": from_date, "$lte": to_date},
                "account_code": {"$regex": "^111"}  # Cash accounts
            }
        },
        {
            "$group": {
                "_id": None,
                "inflows": {"$sum": "$debit"},
                "outflows": {"$sum": "$credit"}
            }
        }
    ]
    
    cash_changes = await db.erp_journal_entries.aggregate(cash_pipeline).to_list(1)
    
    # Get receivables changes
    ar_pipeline = [
        {
            "$match": {
                "institution_id": current_user["id"],
                "date": {"$gte": from_date, "$lte": to_date},
                "account_code": "1120"  # Accounts Receivable
            }
        },
        {
            "$group": {
                "_id": None,
                "increase": {"$sum": "$debit"},
                "decrease": {"$sum": "$credit"}
            }
        }
    ]
    
    ar_changes = await db.erp_journal_entries.aggregate(ar_pipeline).to_list(1)
    
    inflows = cash_changes[0]["inflows"] if cash_changes else 0
    outflows = cash_changes[0]["outflows"] if cash_changes else 0
    ar_increase = ar_changes[0]["increase"] if ar_changes else 0
    ar_decrease = ar_changes[0]["decrease"] if ar_changes else 0
    
    return {
        "period": {"from": from_date, "to": to_date},
        "operating_activities": {
            "cash_received_from_customers": round(ar_decrease, 2),
            "cash_paid_for_expenses": round(outflows, 2),
            "net_cash_from_operations": round(ar_decrease - outflows, 2)
        },
        "investing_activities": {
            "net_cash_from_investing": 0  # Would track asset purchases
        },
        "financing_activities": {
            "net_cash_from_financing": 0  # Would track loans, equity
        },
        "net_change_in_cash": round(inflows - outflows, 2),
        "cash_at_period_end": round(inflows - outflows, 2)
    }

# ==================== BUDGETING ====================

@router.post("/budgets")
async def create_budget(
    budget: BudgetCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a budget for an account and period"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    budget_id = str(uuid.uuid4())
    
    budget_doc = {
        "id": budget_id,
        "institution_id": current_user["id"],
        **budget.dict(),
        "actual": 0,
        "variance": budget.amount,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert budget
    await db.erp_budgets.update_one(
        {
            "institution_id": current_user["id"],
            "account_code": budget.account_code,
            "period": budget.period
        },
        {"$set": budget_doc},
        upsert=True
    )
    
    return {"message": "Budget created/updated", "id": budget_id}

@router.get("/budgets/vs-actual")
async def get_budget_vs_actual(
    period: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get budget vs actual comparison"""
    query = {"institution_id": current_user["id"]}
    if period:
        query["period"] = period
    
    budgets = await db.erp_budgets.find(query, {"_id": 0}).to_list(500)
    
    # Calculate actuals for each budget
    result = []
    for budget in budgets:
        # Get actual spending
        period_start = f"{budget['period']}-01"
        period_end = f"{budget['period']}-31"
        
        actual_pipeline = [
            {
                "$match": {
                    "institution_id": current_user["id"],
                    "account_code": budget["account_code"],
                    "date": {"$gte": period_start, "$lte": period_end}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "actual": {"$sum": {"$subtract": ["$debit", "$credit"]}}
                }
            }
        ]
        
        actual = await db.erp_journal_entries.aggregate(actual_pipeline).to_list(1)
        actual_amount = actual[0]["actual"] if actual else 0
        
        variance = budget["amount"] - actual_amount
        variance_pct = (variance / budget["amount"] * 100) if budget["amount"] != 0 else 0
        
        result.append({
            "account_code": budget["account_code"],
            "period": budget["period"],
            "budget": round(budget["amount"], 2),
            "actual": round(actual_amount, 2),
            "variance": round(variance, 2),
            "variance_percent": round(variance_pct, 2),
            "status": "under" if variance > 0 else "over" if variance < 0 else "on_target"
        })
    
    return {"budget_comparison": result}
