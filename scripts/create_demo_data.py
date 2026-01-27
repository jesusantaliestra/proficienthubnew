import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import uuid
import random

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'proficienthub')

async def create_demo_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Creating comprehensive demo data...")
    
    # Demo Institution
    demo_institution_id = "demo_institution_001"
    
    # Update/Create demo institution
    await db.users.update_one(
        {"id": demo_institution_id},
        {"$set": {
            "id": demo_institution_id,
            "email": "demo_academy@test.com",
            "name": "Demo Academy Admin",
            "institution_name": "Demo Language Academy",
            "user_type": "institution",
            "plan": "enterprise",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
        }},
        upsert=True
    )
    
    # Create demo students
    student_names = [
        "María García", "Carlos López", "Ana Martínez", "Pedro Sánchez", 
        "Laura Fernández", "Diego Rodríguez", "Sofia González", "Miguel Torres",
        "Isabella Ruiz", "Daniel Moreno", "Valentina Díaz", "Alejandro Pérez"
    ]
    
    exam_types = ["ielts", "toefl", "cambridge", "trinity"]
    levels = ["A2", "B1", "B2", "C1"]
    
    for i, name in enumerate(student_names):
        student_id = f"demo_student_{i+1:03d}"
        exam = exam_types[i % len(exam_types)]
        level = levels[i % len(levels)]
        
        await db.users.update_one(
            {"id": student_id},
            {"$set": {
                "id": student_id,
                "email": f"student{i+1}@demo.com",
                "name": name,
                "user_type": "student",
                "institution_id": demo_institution_id,
                "current_exam": exam,
                "english_level": level,
                "credits": random.randint(5, 50),
                "credits_used": random.randint(0, 20),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(30, 150))).isoformat()
            }},
            upsert=True
        )
        
        # Create gamification profile
        xp = random.randint(100, 3000)
        streak = random.randint(0, 30)
        badges = random.sample(["first_exam", "streak_7", "streak_30", "perfect_score", "speed_demon"], k=random.randint(1, 4))
        
        await db.gamification_profiles.update_one(
            {"user_id": student_id},
            {"$set": {
                "user_id": student_id,
                "institution_id": demo_institution_id,
                "xp": xp,
                "level": min(10, xp // 500 + 1),
                "streak": streak,
                "longest_streak": max(streak, random.randint(streak, streak + 10)),
                "daily_xp": random.randint(10, 80),
                "badges": badges,
                "challenges_completed": random.randint(0, 15),
                "created_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
    
    # Create CRM Leads
    company_names = [
        "Oxford Academy", "Cambridge Institute", "Global English School",
        "Elite Language Center", "International Academy", "Premier Languages",
        "Success English Hub", "World Languages Institute"
    ]
    lead_stages = ["new", "contacted", "demo_scheduled", "proposal", "negotiation", "won"]
    
    for i, company in enumerate(company_names):
        stage = lead_stages[i % len(lead_stages)]
        
        await db.crm_leads.update_one(
            {"institution_id": demo_institution_id, "name": company},
            {"$set": {
                "id": f"lead_{i+1:03d}",
                "institution_id": demo_institution_id,
                "name": company,
                "contact": f"Director {['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'][i]}",
                "email": f"contact@{company.lower().replace(' ', '')}.com",
                "value": random.randint(5000, 50000),
                "stage": stage,
                "score": random.randint(40, 95),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(5, 90))).isoformat()
            }},
            upsert=True
        )
    
    # Create Vocabulary Lists
    vocab_lists = [
        {"name": "IELTS Academic Words", "words": ["hypothesis", "paradigm", "methodology", "empirical", "theoretical"]},
        {"name": "Business English", "words": ["stakeholder", "leverage", "synergy", "benchmark", "ROI"]},
        {"name": "Idioms & Expressions", "words": ["break the ice", "hit the nail", "once in a blue moon"]}
    ]
    
    for vocab in vocab_lists:
        await db.vocabularies.update_one(
            {"institution_id": demo_institution_id, "name": vocab["name"]},
            {"$set": {
                "id": str(uuid.uuid4()),
                "institution_id": demo_institution_id,
                "name": vocab["name"],
                "words": vocab["words"],
                "word_count": len(vocab["words"]),
                "has_flashcards": True,
                "offline_available": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
    
    # Enable gamification for demo institution
    await db.institution_settings.update_one(
        {"institution_id": demo_institution_id},
        {"$set": {
            "institution_id": demo_institution_id,
            "gamification": {
                "gamification_enabled": True,
                "xp_per_exam": 50,
                "xp_per_section": 20,
                "leaderboard_enabled": True,
                "badges_enabled": True,
                "challenges_enabled": True
            },
            "placement_test": {
                "placement_test_enabled": True,
                "placement_test_mandatory": False,
                "placement_test_free": True
            }
        }},
        upsert=True
    )
    
    print("✅ Demo data created successfully!")
    print(f"   - Institution: demo_academy@test.com / Demo123!")
    print(f"   - {len(student_names)} Students")
    print(f"   - {len(company_names)} CRM Leads")
    print(f"   - {len(vocab_lists)} Vocabulary Lists")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_data())
