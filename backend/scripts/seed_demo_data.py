"""
Seed Demo Data for ERP and CRM Education
Creates realistic sample data for demonstration purposes
"""
import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
import uuid
import random

sys.path.append('/app/backend')
os.chdir('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Connect to MongoDB
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

# ==================== DEMO INSTITUTIONS ====================
DEMO_INSTITUTIONS = [
    {"name": "Global English Academy", "country": "Spain", "students": 450},
    {"name": "Oxford Language Center", "country": "UK", "students": 1200},
    {"name": "Tokyo English Institute", "country": "Japan", "students": 800},
    {"name": "Berlin Sprachschule", "country": "Germany", "students": 350},
    {"name": "Sydney IELTS Prep", "country": "Australia", "students": 600},
    {"name": "Toronto Language Hub", "country": "Canada", "students": 550},
    {"name": "Dubai English Academy", "country": "UAE", "students": 900},
    {"name": "Singapore Test Prep", "country": "Singapore", "students": 700},
    {"name": "Mumbai IELTS Center", "country": "India", "students": 1500},
    {"name": "São Paulo Language School", "country": "Brazil", "students": 400},
]

EXAM_TYPES = ["ielts", "toefl", "pte", "cambridge", "oet", "toeic", "celpip"]
SOURCES = ["website", "referral", "google_ads", "facebook", "linkedin", "event", "cold_outreach"]
ROLES = ["Director", "Academic Manager", "Marketing Manager", "Owner", "Department Head"]

CRM_STAGES = ["lead", "qualified", "demo_scheduled", "demo_completed", "trial", "proposal", "negotiation", "onboarding", "active"]

async def seed_crm_leads():
    """Create demo leads for CRM Education"""
    print("🎓 Seeding CRM Education leads...")
    
    # Get the demo institution
    demo_institution = await db.users.find_one({"email": "demo_academy@test.com"})
    if not demo_institution:
        print("❌ Demo institution not found. Creating leads without institution_id.")
        institution_id = "demo_institution"
    else:
        institution_id = demo_institution["id"]
    
    leads = []
    now = datetime.now(timezone.utc)
    
    for i, inst in enumerate(DEMO_INSTITUTIONS):
        # Distribute leads across stages
        stage = CRM_STAGES[i % len(CRM_STAGES)]
        
        lead_score = random.randint(30, 95)
        days_ago = random.randint(1, 60)
        
        lead = {
            "id": str(uuid.uuid4()),
            "institution_id": institution_id,
            "institution_name": inst["name"],
            "contact_name": f"{random.choice(['John', 'Maria', 'David', 'Sarah', 'Carlos', 'Anna', 'Ahmed', 'Yuki', 'Priya', 'Lucas'])} {random.choice(['Smith', 'García', 'Mueller', 'Tanaka', 'Patel', 'Silva', 'Al-Rahman', 'Chen', 'Kim', 'Brown'])}",
            "contact_email": f"contact@{inst['name'].lower().replace(' ', '')}.com",
            "contact_phone": f"+{random.randint(1, 99)} {random.randint(100, 999)} {random.randint(1000000, 9999999)}",
            "contact_role": random.choice(ROLES),
            "institution_type": random.choice(["language_school", "university", "corporate_training", "test_center"]),
            "estimated_students": inst["students"],
            "exam_types_interested": random.sample(EXAM_TYPES, k=random.randint(2, 5)),
            "country": inst["country"],
            "source": random.choice(SOURCES),
            "stage": stage,
            "lead_score": lead_score,
            "estimated_value": inst["students"] * random.randint(50, 150),
            "budget_timeline": random.choice(["immediate", "this_quarter", "this_year", "exploring"]),
            "notes": f"Interested in exam preparation for {inst['students']} students. Primary focus on IELTS and TOEFL.",
            "tags": random.sample(["high-potential", "enterprise", "education", "b2b", "priority"], k=random.randint(1, 3)),
            "assigned_to": None,
            "created_at": (now - timedelta(days=days_ago)).isoformat(),
            "updated_at": (now - timedelta(days=random.randint(0, days_ago))).isoformat(),
            "last_contact": (now - timedelta(days=random.randint(0, 14))).isoformat() if stage not in ["lead"] else None,
            "next_follow_up": (now + timedelta(days=random.randint(1, 7))).isoformat() if stage not in ["active", "churned", "lost"] else None,
            "activities": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "note",
                    "content": f"Initial contact via {random.choice(SOURCES)}",
                    "created_at": (now - timedelta(days=days_ago)).isoformat(),
                    "created_by": "system"
                }
            ]
        }
        leads.append(lead)
    
    # Add some extra leads for variety
    extra_leads = [
        {"name": "Paris Language School", "country": "France", "students": 280, "stage": "lead"},
        {"name": "Amsterdam English Center", "country": "Netherlands", "students": 320, "stage": "qualified"},
        {"name": "Seoul Test Academy", "country": "South Korea", "students": 950, "stage": "demo_scheduled"},
        {"name": "Mexico City IELTS", "country": "Mexico", "students": 420, "stage": "trial"},
        {"name": "Lagos English Institute", "country": "Nigeria", "students": 380, "stage": "proposal"},
    ]
    
    for inst in extra_leads:
        lead = {
            "id": str(uuid.uuid4()),
            "institution_id": institution_id,
            "institution_name": inst["name"],
            "contact_name": f"{random.choice(['Jean', 'Hans', 'Min-Ji', 'Roberto', 'Chioma'])} {random.choice(['Dupont', 'Van Berg', 'Park', 'Hernández', 'Okonkwo'])}",
            "contact_email": f"info@{inst['name'].lower().replace(' ', '')}.com",
            "contact_phone": f"+{random.randint(1, 99)} {random.randint(100, 999)} {random.randint(1000000, 9999999)}",
            "contact_role": random.choice(ROLES),
            "institution_type": "language_school",
            "estimated_students": inst["students"],
            "exam_types_interested": random.sample(EXAM_TYPES, k=random.randint(2, 4)),
            "country": inst["country"],
            "source": random.choice(SOURCES),
            "stage": inst["stage"],
            "lead_score": random.randint(40, 85),
            "estimated_value": inst["students"] * random.randint(60, 120),
            "budget_timeline": random.choice(["immediate", "this_quarter", "this_year"]),
            "created_at": (now - timedelta(days=random.randint(5, 30))).isoformat(),
            "updated_at": now.isoformat(),
        }
        leads.append(lead)
    
    # Clear existing demo leads and insert new ones
    await db.crm_edu_leads.delete_many({"institution_id": institution_id})
    await db.crm_edu_leads.insert_many(leads)
    print(f"✅ Created {len(leads)} CRM leads")
    
    return leads

async def seed_crm_tasks():
    """Create demo tasks for CRM"""
    print("📋 Seeding CRM tasks...")
    
    demo_institution = await db.users.find_one({"email": "demo_academy@test.com"})
    institution_id = demo_institution["id"] if demo_institution else "demo_institution"
    
    # Get leads
    leads = await db.crm_edu_leads.find({"institution_id": institution_id}).to_list(20)
    
    tasks = []
    now = datetime.now(timezone.utc)
    
    task_types = [
        ("call", "Follow-up call", "Schedule follow-up call to discuss pricing"),
        ("email", "Send proposal", "Prepare and send pricing proposal"),
        ("demo", "Product demo", "Schedule and conduct product demonstration"),
        ("follow_up", "Check trial progress", "Review trial usage and provide assistance"),
        ("onboarding", "Setup meeting", "Help with initial platform setup"),
    ]
    
    for lead in leads[:10]:
        task_type, title, description = random.choice(task_types)
        due_days = random.randint(-3, 7)  # Some overdue, some upcoming
        
        task = {
            "id": str(uuid.uuid4()),
            "institution_id": institution_id,
            "lead_id": lead["id"],
            "lead_name": lead["institution_name"],
            "task_type": task_type,
            "title": f"{title} - {lead['institution_name']}",
            "description": description,
            "priority": random.choice(["high", "medium", "low"]),
            "status": "completed" if due_days < -2 else ("overdue" if due_days < 0 else "pending"),
            "due_date": (now + timedelta(days=due_days)).isoformat(),
            "created_at": (now - timedelta(days=random.randint(5, 15))).isoformat(),
            "completed_at": (now - timedelta(days=abs(due_days))).isoformat() if due_days < -2 else None,
        }
        tasks.append(task)
    
    await db.crm_edu_tasks.delete_many({"institution_id": institution_id})
    await db.crm_edu_tasks.insert_many(tasks)
    print(f"✅ Created {len(tasks)} CRM tasks")

async def seed_erp_invoices():
    """Create demo invoices for ERP Dashboard"""
    print("💰 Seeding ERP invoices...")
    
    demo_institution = await db.users.find_one({"email": "demo_academy@test.com"})
    institution_id = demo_institution["id"] if demo_institution else "demo_institution"
    
    invoices = []
    now = datetime.now(timezone.utc)
    
    customers = [
        {"name": "Global English Academy", "country": "ES", "plan": "Enterprise"},
        {"name": "Oxford Language Center", "country": "GB", "plan": "Professional"},
        {"name": "Tokyo English Institute", "country": "JP", "plan": "Professional"},
        {"name": "Berlin Sprachschule", "country": "DE", "plan": "Starter"},
        {"name": "Sydney IELTS Prep", "country": "AU", "plan": "Professional"},
        {"name": "Toronto Language Hub", "country": "CA", "plan": "Enterprise"},
        {"name": "Dubai English Academy", "country": "AE", "plan": "Professional"},
        {"name": "Singapore Test Prep", "country": "SG", "plan": "Starter"},
    ]
    
    statuses = ["paid", "paid", "paid", "sent", "sent", "draft", "overdue"]
    
    for i, customer in enumerate(customers):
        # Create 2-3 invoices per customer
        num_invoices = random.randint(2, 3)
        
        for j in range(num_invoices):
            days_ago = random.randint(1, 90)
            invoice_date = now - timedelta(days=days_ago)
            due_date = invoice_date + timedelta(days=30)
            status = statuses[i % len(statuses)] if j == 0 else "paid"
            
            # Pricing based on plan
            base_prices = {"Starter": 299, "Professional": 799, "Enterprise": 1999}
            base_price = base_prices.get(customer["plan"], 499)
            
            # Random add-ons
            ai_credits = random.choice([0, 100, 500]) * 0.10
            extra_students = random.choice([0, 50, 100]) * 2
            
            subtotal = base_price + ai_credits + extra_students
            tax_rate = 0.20 if customer["country"] in ["GB", "DE", "ES"] else 0
            tax = subtotal * tax_rate
            total = subtotal + tax
            
            invoice = {
                "id": str(uuid.uuid4()),
                "institution_id": institution_id,
                "invoice_number": f"INV-2026-{1000 + i*10 + j}",
                "customer_id": str(uuid.uuid4()),
                "customer_name": customer["name"],
                "customer_email": f"billing@{customer['name'].lower().replace(' ', '')}.com",
                "currency": "USD" if customer["country"] in ["US", "CA", "AE", "SG"] else "EUR" if customer["country"] in ["ES", "DE"] else "GBP" if customer["country"] == "GB" else "USD",
                "status": status,
                "issue_date": invoice_date.isoformat(),
                "due_date": due_date.isoformat(),
                "paid_date": (due_date - timedelta(days=random.randint(1, 10))).isoformat() if status == "paid" else None,
                "items": [
                    {
                        "description": f"{customer['plan']} Plan - Monthly Subscription",
                        "quantity": 1,
                        "unit_price": base_price,
                        "tax_rate": tax_rate * 100,
                        "total": base_price
                    }
                ] + ([{
                    "description": "AI Tutor Credits (500)",
                    "quantity": 1,
                    "unit_price": ai_credits,
                    "tax_rate": tax_rate * 100,
                    "total": ai_credits
                }] if ai_credits > 0 else []) + ([{
                    "description": f"Additional Student Licenses ({int(extra_students/2)})",
                    "quantity": int(extra_students/2),
                    "unit_price": 2,
                    "tax_rate": tax_rate * 100,
                    "total": extra_students
                }] if extra_students > 0 else []),
                "totals": {
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total
                },
                "payment_terms_days": 30,
                "notes": f"Thank you for choosing ProficientHub {customer['plan']} Plan!",
                "created_at": invoice_date.isoformat(),
                "updated_at": now.isoformat(),
            }
            invoices.append(invoice)
    
    await db.erp_invoices.delete_many({"institution_id": institution_id})
    await db.erp_invoices.insert_many(invoices)
    print(f"✅ Created {len(invoices)} ERP invoices")
    
    return invoices

async def seed_erp_subscriptions():
    """Create demo subscriptions for ERP"""
    print("💳 Seeding ERP subscriptions...")
    
    demo_institution = await db.users.find_one({"email": "demo_academy@test.com"})
    institution_id = demo_institution["id"] if demo_institution else "demo_institution"
    
    subscriptions = []
    now = datetime.now(timezone.utc)
    
    plans = [
        {"name": "Starter", "price": 299, "interval": "monthly"},
        {"name": "Professional", "price": 799, "interval": "monthly"},
        {"name": "Enterprise", "price": 1999, "interval": "monthly"},
        {"name": "Professional Annual", "price": 7990, "interval": "yearly"},
        {"name": "Enterprise Annual", "price": 19990, "interval": "yearly"},
    ]
    
    customers = ["Global English Academy", "Oxford Language Center", "Tokyo English Institute", 
                 "Berlin Sprachschule", "Sydney IELTS Prep", "Toronto Language Hub"]
    
    for i, customer in enumerate(customers):
        plan = plans[i % len(plans)]
        start_date = now - timedelta(days=random.randint(30, 365))
        
        subscription = {
            "id": str(uuid.uuid4()),
            "institution_id": institution_id,
            "customer_name": customer,
            "customer_email": f"billing@{customer.lower().replace(' ', '')}.com",
            "plan_name": plan["name"],
            "plan_price": plan["price"],
            "currency": "USD",
            "billing_interval": plan["interval"],
            "status": "active",
            "current_period_start": (now - timedelta(days=random.randint(1, 28))).isoformat(),
            "current_period_end": (now + timedelta(days=random.randint(1, 28))).isoformat(),
            "started_at": start_date.isoformat(),
            "created_at": start_date.isoformat(),
            "updated_at": now.isoformat(),
        }
        subscriptions.append(subscription)
    
    await db.erp_subscriptions.delete_many({"institution_id": institution_id})
    await db.erp_subscriptions.insert_many(subscriptions)
    print(f"✅ Created {len(subscriptions)} ERP subscriptions")

async def main():
    """Run all seed functions"""
    print("\n" + "="*50)
    print("🌱 SEEDING DEMO DATA FOR PROFICIENTHUB")
    print("="*50 + "\n")
    
    await seed_crm_leads()
    await seed_crm_tasks()
    await seed_erp_invoices()
    await seed_erp_subscriptions()
    
    print("\n" + "="*50)
    print("✅ DEMO DATA SEEDING COMPLETE!")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
