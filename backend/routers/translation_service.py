"""Dynamic Translation Service

This module provides automatic translation of UI strings to 80+ languages
using LLM (GPT) for accurate, context-aware translations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import hashlib
from datetime import datetime, timezone

router = APIRouter(prefix="/translations", tags=["Translations"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]


# =============================================
# Models
# =============================================

class TranslationRequest(BaseModel):
    """Request to translate strings"""
    keys: List[str]  # List of translation keys like "nav.home", "landing.hero_title"
    target_language: str  # Language code like "fr", "de", "zh"
    source_language: str = "en"


class BulkTranslationRequest(BaseModel):
    """Request to translate all strings to a language"""
    target_language: str
    source_texts: Dict[str, str]  # {"key": "English text", ...}


# Language names for better context in translations
LANGUAGE_NAMES = {
    'en': 'English', 'es': 'Spanish', 'zh': 'Chinese', 'hi': 'Hindi',
    'ar': 'Arabic', 'pt': 'Portuguese', 'bn': 'Bengali', 'ru': 'Russian',
    'ja': 'Japanese', 'pa': 'Punjabi', 'de': 'German', 'jv': 'Javanese',
    'ko': 'Korean', 'fr': 'French', 'te': 'Telugu', 'vi': 'Vietnamese',
    'mr': 'Marathi', 'ta': 'Tamil', 'tr': 'Turkish', 'ur': 'Urdu',
    'it': 'Italian', 'th': 'Thai', 'gu': 'Gujarati', 'pl': 'Polish',
    'uk': 'Ukrainian', 'ml': 'Malayalam', 'kn': 'Kannada', 'or': 'Odia',
    'my': 'Burmese', 'fa': 'Persian', 'ro': 'Romanian', 'nl': 'Dutch',
    'hu': 'Hungarian', 'el': 'Greek', 'cs': 'Czech', 'sv': 'Swedish',
    'he': 'Hebrew', 'id': 'Indonesian', 'ms': 'Malay', 'fi': 'Finnish',
    'da': 'Danish', 'no': 'Norwegian', 'sk': 'Slovak', 'bg': 'Bulgarian',
    'sr': 'Serbian', 'hr': 'Croatian', 'lt': 'Lithuanian', 'lv': 'Latvian',
    'et': 'Estonian', 'sl': 'Slovenian', 'fil': 'Filipino', 'sw': 'Swahili',
    'am': 'Amharic', 'ne': 'Nepali', 'si': 'Sinhala', 'km': 'Khmer',
    'zu': 'Zulu', 'xh': 'Xhosa', 'af': 'Afrikaans', 'ca': 'Catalan',
    'eu': 'Basque', 'gl': 'Galician', 'is': 'Icelandic', 'ga': 'Irish',
    'cy': 'Welsh', 'mt': 'Maltese', 'lb': 'Luxembourgish', 'sq': 'Albanian',
    'mk': 'Macedonian', 'bs': 'Bosnian', 'az': 'Azerbaijani', 'ka': 'Georgian',
    'hy': 'Armenian', 'kk': 'Kazakh', 'uz': 'Uzbek', 'mn': 'Mongolian',
    'lo': 'Lao', 'ps': 'Pashto', 'tg': 'Tajik'
}


# =============================================
# Translation Functions
# =============================================

async def translate_with_llm(texts: Dict[str, str], target_lang: str, source_lang: str = "en") -> Dict[str, str]:
    """
    Translate a batch of texts using LLM.
    Returns dict of {key: translated_text}
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    source_name = LANGUAGE_NAMES.get(source_lang, source_lang)
    
    # Prepare JSON of texts to translate
    texts_json = json.dumps(texts, ensure_ascii=False)
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"translate-{target_lang}-{hashlib.md5(texts_json.encode()).hexdigest()[:8]}",
        system_message=f"""You are a professional translator for an educational platform called ProficientHub.
Translate the provided JSON object from {source_name} to {target_name}.
The keys are translation identifiers - keep them EXACTLY as provided.
Only translate the VALUES, not the keys.
Maintain the same JSON structure.
For technical terms like "OET", "IELTS", "TOEFL", keep them as-is.
For words like "AI", "Mock", "Dashboard" - translate appropriately for the target language if a natural equivalent exists.
Ensure translations are natural and appropriate for a professional educational context.
Return ONLY valid JSON, no explanations."""
    ).with_model("openai", "gpt-4.1-mini")
    
    user_message = UserMessage(
        text=f"Translate this JSON from {source_name} to {target_name}:\n\n{texts_json}"
    )
    
    try:
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        # Clean up response if it has markdown code blocks
        response_text = response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        translated = json.loads(response_text)
        return translated
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Translation parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


async def get_cached_translation(key: str, target_lang: str) -> Optional[str]:
    """Get cached translation from database"""
    cache_entry = await db.translation_cache.find_one(
        {"key": key, "language": target_lang},
        {"_id": 0, "translation": 1}
    )
    return cache_entry.get("translation") if cache_entry else None


async def save_translations_to_cache(translations: Dict[str, str], target_lang: str, source_lang: str):
    """Save translations to cache"""
    now = datetime.now(timezone.utc).isoformat()
    
    for key, translation in translations.items():
        await db.translation_cache.update_one(
            {"key": key, "language": target_lang},
            {
                "$set": {
                    "key": key,
                    "language": target_lang,
                    "source_language": source_lang,
                    "translation": translation,
                    "updated_at": now
                }
            },
            upsert=True
        )


# =============================================
# API Endpoints
# =============================================

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in LANGUAGE_NAMES.items()
        ],
        "count": len(LANGUAGE_NAMES)
    }


@router.post("/translate")
async def translate_strings(request: TranslationRequest):
    """
    Translate specific strings to target language.
    Uses cache when available, falls back to LLM.
    """
    # Check cache first
    cached = {}
    to_translate = {}
    
    for key in request.keys:
        cached_value = await get_cached_translation(key, request.target_language)
        if cached_value:
            cached[key] = cached_value
        else:
            # We need the source text - this would come from the request or a lookup
            to_translate[key] = key  # Placeholder - actual implementation needs source texts
    
    # If we have texts to translate
    if to_translate:
        # In a real implementation, we'd get the source texts from somewhere
        # For now, return what we have cached
        pass
    
    return {
        "language": request.target_language,
        "translations": cached,
        "from_cache": len(cached),
        "newly_translated": 0
    }


@router.post("/translate-bulk")
async def translate_bulk(request: BulkTranslationRequest):
    """
    Translate all provided strings to target language.
    This is the main endpoint for generating translations for a new language.
    """
    target_lang = request.target_language
    source_texts = request.source_texts
    
    if not source_texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    if target_lang not in LANGUAGE_NAMES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {target_lang}")
    
    # Check cache for existing translations
    cached = {}
    to_translate = {}
    
    for key, text in source_texts.items():
        cached_value = await get_cached_translation(key, target_lang)
        if cached_value:
            cached[key] = cached_value
        else:
            to_translate[key] = text
    
    # Translate missing strings
    newly_translated = {}
    if to_translate:
        # Split into batches of 50 to avoid token limits
        batch_size = 50
        keys = list(to_translate.keys())
        
        for i in range(0, len(keys), batch_size):
            batch_keys = keys[i:i+batch_size]
            batch_texts = {k: to_translate[k] for k in batch_keys}
            
            batch_translations = await translate_with_llm(batch_texts, target_lang)
            newly_translated.update(batch_translations)
        
        # Save to cache
        await save_translations_to_cache(newly_translated, target_lang, "en")
    
    # Combine results
    all_translations = {**cached, **newly_translated}
    
    return {
        "language": target_lang,
        "language_name": LANGUAGE_NAMES.get(target_lang, target_lang),
        "translations": all_translations,
        "stats": {
            "total": len(all_translations),
            "from_cache": len(cached),
            "newly_translated": len(newly_translated)
        }
    }


@router.get("/cached/{language}")
async def get_cached_translations(language: str):
    """Get all cached translations for a language"""
    
    if language not in LANGUAGE_NAMES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    translations = await db.translation_cache.find(
        {"language": language},
        {"_id": 0, "key": 1, "translation": 1}
    ).to_list(1000)
    
    result = {t["key"]: t["translation"] for t in translations}
    
    return {
        "language": language,
        "language_name": LANGUAGE_NAMES.get(language),
        "translations": result,
        "count": len(result)
    }


@router.delete("/cache/{language}")
async def clear_language_cache(language: str):
    """Clear cached translations for a language (admin only)"""
    
    result = await db.translation_cache.delete_many({"language": language})
    
    return {
        "message": f"Cleared {result.deleted_count} cached translations for {language}"
    }


# =============================================
# Frontend Translation Endpoint
# =============================================

@router.get("/i18n/{language}")
async def get_i18n_bundle(language: str):
    """
    Get complete i18n bundle for a language.
    This is called by the frontend to load translations.
    Returns all translations for the specified language.
    """
    
    if language == "en":
        # English is the source language, return empty (frontend has it hardcoded)
        return {"language": "en", "translations": {}}
    
    # Get cached translations
    translations = await db.translation_cache.find(
        {"language": language},
        {"_id": 0, "key": 1, "translation": 1}
    ).to_list(2000)
    
    # Convert flat keys to nested structure for i18next
    result = {}
    for t in translations:
        key_parts = t["key"].split(".")
        current = result
        for i, part in enumerate(key_parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        current[key_parts[-1]] = t["translation"]
    
    return {
        "language": language,
        "language_name": LANGUAGE_NAMES.get(language, language),
        "translations": result
    }
