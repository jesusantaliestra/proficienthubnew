"""
Content Library Router
Handles study materials, flashcards, and vocabulary management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/library", tags=["Content Library"])

# ==================== MODELS ====================
class LibraryItemCreate(BaseModel):
    title: str
    content: str
    item_type: str  # note, flashcard, vocabulary, summary
    exam_type: Optional[str] = None
    section: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False

class FlashcardCreate(BaseModel):
    front: str
    back: str
    deck_name: Optional[str] = "General"
    exam_type: Optional[str] = None
    tags: List[str] = []

class VocabularyCreate(BaseModel):
    word: str
    definition: str
    example_sentence: Optional[str] = None
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None
    exam_type: Optional[str] = None
    difficulty: str = "medium"

# ==================== LIBRARY ITEMS ====================
@router.post("/items")
async def create_library_item(
    item: LibraryItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new library item (note, summary, etc.)"""
    item_id = str(uuid.uuid4())
    
    item_doc = {
        "id": item_id,
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        **item.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.library_items.insert_one(item_doc)
    
    return {"id": item_id, "message": "Item created successfully"}

@router.get("/items")
async def get_library_items(
    item_type: Optional[str] = None,
    exam_type: Optional[str] = None,
    section: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's library items with filtering"""
    query = {"user_id": current_user["id"]}
    
    if item_type:
        query["item_type"] = item_type
    if exam_type:
        query["exam_type"] = exam_type
    if section:
        query["section"] = section
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    items = await db.library_items.find(query, {"_id": 0}).sort("updated_at", -1).to_list(100)
    
    return {"items": items}

@router.delete("/items/{item_id}")
async def delete_library_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a library item"""
    result = await db.library_items.delete_one({
        "id": item_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted"}

# ==================== FLASHCARDS ====================
@router.post("/flashcards")
async def create_flashcard(
    flashcard: FlashcardCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new flashcard"""
    card_id = str(uuid.uuid4())
    
    card_doc = {
        "id": card_id,
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        **flashcard.dict(),
        "review_count": 0,
        "correct_count": 0,
        "last_reviewed": None,
        "next_review": datetime.now(timezone.utc).isoformat(),
        "difficulty_score": 2.5,  # For spaced repetition
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.flashcards.insert_one(card_doc)
    
    return {"id": card_id, "message": "Flashcard created"}

@router.get("/flashcards")
async def get_flashcards(
    deck_name: Optional[str] = None,
    exam_type: Optional[str] = None,
    due_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get user's flashcards"""
    query = {"user_id": current_user["id"]}
    
    if deck_name:
        query["deck_name"] = deck_name
    if exam_type:
        query["exam_type"] = exam_type
    if due_only:
        query["next_review"] = {"$lte": datetime.now(timezone.utc).isoformat()}
    
    cards = await db.flashcards.find(query, {"_id": 0}).to_list(500)
    
    # Group by deck
    decks = {}
    for card in cards:
        deck = card.get("deck_name", "General")
        if deck not in decks:
            decks[deck] = []
        decks[deck].append(card)
    
    return {
        "flashcards": cards,
        "decks": decks,
        "total": len(cards),
        "due_count": len([c for c in cards if c.get("next_review", "") <= datetime.now(timezone.utc).isoformat()])
    }

@router.post("/flashcards/{card_id}/review")
async def review_flashcard(
    card_id: str,
    correct: bool,
    difficulty: int = 3,  # 1-5 scale
    current_user: dict = Depends(get_current_user)
):
    """Record a flashcard review using SM-2 algorithm"""
    card = await db.flashcards.find_one({"id": card_id, "user_id": current_user["id"]})
    
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # SM-2 algorithm for spaced repetition
    ef = card.get("difficulty_score", 2.5)
    review_count = card.get("review_count", 0) + 1
    correct_count = card.get("correct_count", 0) + (1 if correct else 0)
    
    if correct:
        if review_count == 1:
            interval = 1
        elif review_count == 2:
            interval = 6
        else:
            interval = int(card.get("interval", 1) * ef)
        
        ef = ef + (0.1 - (5 - difficulty) * (0.08 + (5 - difficulty) * 0.02))
    else:
        interval = 1
        ef = max(1.3, ef - 0.2)
    
    ef = max(1.3, ef)
    
    from datetime import timedelta
    next_review = datetime.now(timezone.utc) + timedelta(days=interval)
    
    await db.flashcards.update_one(
        {"id": card_id},
        {
            "$set": {
                "review_count": review_count,
                "correct_count": correct_count,
                "last_reviewed": datetime.now(timezone.utc).isoformat(),
                "next_review": next_review.isoformat(),
                "difficulty_score": ef,
                "interval": interval
            }
        }
    )
    
    return {
        "success": True,
        "next_review": next_review.isoformat(),
        "interval_days": interval,
        "difficulty_score": ef
    }

@router.post("/flashcards/generate")
async def generate_flashcards(
    topic: str,
    exam_type: str,
    count: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Generate flashcards using AI"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        prompt = f"""Generate {count} flashcards for {exam_type.upper()} exam preparation on the topic: {topic}
        
        Return as JSON array with format:
        [
            {{"front": "Question or term", "back": "Answer or definition"}},
            ...
        ]
        
        Make them educational and relevant to {exam_type.upper()} exam content."""
        
        chat = LlmChat(
            api_key=api_key,
            model="gpt-4o-mini",
            system_message="You are an educational content creator specializing in language exam preparation."
        )
        
        response = await chat.send_async(UserMessage(prompt))
        
        import json
        # Extract JSON from response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        cards_data = json.loads(content)
        
        # Save flashcards
        created_cards = []
        for card in cards_data[:count]:
            card_id = str(uuid.uuid4())
            card_doc = {
                "id": card_id,
                "user_id": current_user["id"],
                "institution_id": current_user.get("institution_id"),
                "front": card["front"],
                "back": card["back"],
                "deck_name": topic,
                "exam_type": exam_type,
                "tags": ["ai-generated", topic],
                "review_count": 0,
                "correct_count": 0,
                "next_review": datetime.now(timezone.utc).isoformat(),
                "difficulty_score": 2.5,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.flashcards.insert_one(card_doc)
            created_cards.append(card_doc)
        
        return {
            "success": True,
            "cards_created": len(created_cards),
            "flashcards": created_cards
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")

# ==================== VOCABULARY ====================
@router.get("/vocabularies")
async def get_vocabularies(
    exam_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's vocabulary list"""
    query = {"user_id": current_user["id"]}
    
    if exam_type:
        query["exam_type"] = exam_type
    if difficulty:
        query["difficulty"] = difficulty
    if search:
        query["$or"] = [
            {"word": {"$regex": search, "$options": "i"}},
            {"definition": {"$regex": search, "$options": "i"}}
        ]
    
    vocab = await db.vocabulary.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    
    return {
        "vocabulary": vocab,
        "total": len(vocab),
        "by_difficulty": {
            "easy": len([v for v in vocab if v.get("difficulty") == "easy"]),
            "medium": len([v for v in vocab if v.get("difficulty") == "medium"]),
            "hard": len([v for v in vocab if v.get("difficulty") == "hard"])
        }
    }

@router.post("/vocabularies")
async def create_vocabulary(
    vocab: VocabularyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new vocabulary word"""
    vocab_id = str(uuid.uuid4())
    
    vocab_doc = {
        "id": vocab_id,
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        **vocab.dict(),
        "mastery_level": 0,
        "review_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.vocabulary.insert_one(vocab_doc)
    
    return {"id": vocab_id, "message": "Vocabulary added"}

@router.post("/vocabularies/{vocab_id}/review")
async def review_vocabulary(
    vocab_id: str,
    knew_it: bool,
    current_user: dict = Depends(get_current_user)
):
    """Record a vocabulary review"""
    vocab = await db.vocabulary.find_one({"id": vocab_id, "user_id": current_user["id"]})
    
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    
    mastery = vocab.get("mastery_level", 0)
    if knew_it:
        mastery = min(mastery + 1, 5)
    else:
        mastery = max(mastery - 1, 0)
    
    await db.vocabulary.update_one(
        {"id": vocab_id},
        {
            "$set": {
                "mastery_level": mastery,
                "last_reviewed": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {"review_count": 1}
        }
    )
    
    return {"mastery_level": mastery, "message": "Review recorded"}

# ==================== MATERIALS UPLOAD ====================
@router.post("/upload")
async def upload_material(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    exam_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Upload a study material file"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Only institutions can upload materials")
    
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "audio/mpeg", "audio/wav"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {allowed_types}")
    
    # Save file (in production, use cloud storage)
    material_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
    file_path = f"/tmp/materials/{material_id}.{file_ext}"
    
    os.makedirs("/tmp/materials", exist_ok=True)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    material_doc = {
        "id": material_id,
        "institution_id": current_user["id"],
        "title": title or file.filename,
        "filename": file.filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "file_size": len(content),
        "exam_type": exam_type,
        "download_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.library_materials.insert_one(material_doc)
    
    return {
        "id": material_id,
        "message": "Material uploaded successfully",
        "filename": file.filename
    }

@router.get("/materials")
async def get_materials(
    exam_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get institution's uploaded materials"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    query = {"institution_id": institution_id}
    if exam_type:
        query["exam_type"] = exam_type
    
    materials = await db.library_materials.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    return {"materials": materials}

@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an uploaded material"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    material = await db.library_materials.find_one({
        "id": material_id,
        "institution_id": current_user["id"]
    })
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Delete file
    if os.path.exists(material.get("file_path", "")):
        os.remove(material["file_path"])
    
    await db.library_materials.delete_one({"id": material_id})
    
    return {"message": "Material deleted"}

@router.post("/materials/{material_id}/offline")
async def mark_for_offline(
    material_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a material for offline access"""
    await db.offline_materials.update_one(
        {"user_id": current_user["id"], "material_id": material_id},
        {
            "$set": {
                "user_id": current_user["id"],
                "material_id": material_id,
                "marked_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"message": "Marked for offline access"}
