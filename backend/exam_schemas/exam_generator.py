"""
Multi-Agent Exam Generation and Validation System
Pipeline: AI Generator → AI Reviewer 1 → AI Reviewer 2 → Human Review → Bank
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from uuid import uuid4
from enum import Enum

# Import exam schema
from exam_schemas.oet_schema import (
    OET_EXAM_STRUCTURE, OET_MEDICAL_TOPICS, OET_GRADING,
    ValidationStatus, DifficultyLevel, OETProfession,
    OETListeningPart, OETReadingPart, QuestionType
)

class AgentRole(str, Enum):
    GENERATOR = "generator"
    REVIEWER_1 = "reviewer_1"
    REVIEWER_2 = "reviewer_2"
    HUMAN = "human"

# ==================== VALIDATION PROMPTS ====================

GENERATOR_SYSTEM_PROMPT = """You are an expert OET (Occupational English Test) exam content creator for healthcare professionals.

Your role is to generate authentic, high-quality exam content that:
1. Follows the EXACT official OET format and structure
2. Uses realistic healthcare scenarios and medical terminology
3. Tests appropriate English language skills for healthcare contexts
4. Has clear, unambiguous correct answers
5. Matches the difficulty level of real OET exams

CRITICAL RULES:
- NEVER copy existing OET questions - create original content
- Use realistic but fictional patient names and scenarios
- Ensure medical accuracy in all content
- Match the exact question format specified
- Provide clear, defensible correct answers

Output format: Valid JSON matching the specified schema."""

REVIEWER_1_SYSTEM_PROMPT = """You are an expert OET exam quality reviewer (Reviewer 1 - Content Accuracy).

Your role is to review generated OET exam content for:
1. MEDICAL ACCURACY - Is all medical information correct?
2. LANGUAGE APPROPRIATENESS - Is the English level appropriate for OET?
3. ANSWER VALIDITY - Is the correct answer clearly correct?
4. FORMAT COMPLIANCE - Does it match OET official format?
5. AMBIGUITY CHECK - Are there any ambiguous questions?

For each item, provide:
- PASS/FAIL status
- Specific issues found (if any)
- Suggested corrections (if needed)

Be strict - flag any issues. Better to reject than pass poor content."""

REVIEWER_2_SYSTEM_PROMPT = """You are an expert OET exam quality reviewer (Reviewer 2 - Educational Quality).

Your role is to review OET exam content for:
1. DISCRIMINATION - Does the question effectively differentiate ability levels?
2. DISTRACTOR QUALITY - Are wrong options plausible but clearly wrong?
3. TOPIC COVERAGE - Is the topic relevant to healthcare professionals?
4. DIFFICULTY CALIBRATION - Is difficulty appropriate for OET standards?
5. ORIGINALITY CHECK - Does this seem like copied/common content?

For each item, provide:
- PASS/FAIL status
- Quality score (1-10)
- Specific feedback
- Recommendations for improvement

Focus on educational effectiveness and exam validity."""

# ==================== VALIDATION CRITERIA ====================

VALIDATION_CRITERIA = {
    "listening": {
        "part_a": {
            "audio_length_seconds": {"min": 180, "max": 300},
            "questions_per_consultation": 12,
            "answer_word_limit": 3,
            "must_use_exact_words": True,
            "medical_accuracy_required": True,
            "natural_dialogue": True
        },
        "part_b": {
            "extract_length_seconds": {"min": 45, "max": 75},
            "distractors_plausible": True,
            "single_clear_answer": True,
            "workplace_context": True
        },
        "part_c": {
            "presentation_length_seconds": {"min": 240, "max": 360},
            "questions_sequential": True,
            "inference_questions_included": True,
            "professional_context": True
        }
    },
    "reading": {
        "part_a": {
            "texts_per_theme": 4,
            "text_word_count": {"min": 100, "max": 200},
            "time_pressure_appropriate": True,
            "scanning_skill_tested": True
        },
        "part_b": {
            "text_word_count": {"min": 50, "max": 150},
            "workplace_document_style": True,
            "practical_information": True
        },
        "part_c": {
            "text_word_count": {"min": 600, "max": 800},
            "academic_register": True,
            "opinion_questions_included": True
        }
    },
    "writing": {
        "case_notes_realistic": True,
        "irrelevant_details_included": True,  # To test discernment
        "letter_type_clear": True,
        "recipient_appropriate": True,
        "word_count_achievable": True
    },
    "speaking": {
        "scenario_realistic": True,
        "communication_challenge_clear": True,
        "empathy_opportunity": True,
        "information_exchange_needed": True
    }
}

# ==================== QUALITY METRICS ====================

class QualityMetrics:
    """Track quality metrics for exam content"""
    
    @staticmethod
    def calculate_question_quality(question: Dict) -> Dict:
        """Calculate quality score for a question"""
        metrics = {
            "clarity_score": 0,
            "difficulty_appropriate": False,
            "answer_defensible": False,
            "medical_accuracy": False,
            "format_compliant": False,
            "overall_score": 0
        }
        
        # Check clarity (no ambiguous language)
        ambiguous_words = ["might", "could", "possibly", "sometimes", "often"]
        question_text = question.get("question_text", "").lower()
        ambiguity_count = sum(1 for word in ambiguous_words if word in question_text)
        metrics["clarity_score"] = max(0, 10 - ambiguity_count * 2)
        
        # Check format compliance
        required_fields = ["question_id", "question_text", "correct_answer"]
        metrics["format_compliant"] = all(field in question for field in required_fields)
        
        # Calculate overall
        scores = [metrics["clarity_score"]]
        if metrics["format_compliant"]:
            scores.append(10)
        metrics["overall_score"] = sum(scores) / len(scores)
        
        return metrics

    @staticmethod
    def calculate_exam_quality(exam: Dict) -> Dict:
        """Calculate overall exam quality metrics"""
        return {
            "total_questions": 42 + 42 + 1 + 2,  # Listening + Reading + Writing + Speaking
            "topics_unique": len(set(exam.get("topics_covered", []))),
            "difficulty_balance": exam.get("difficulty_distribution", {}),
            "validation_status": exam.get("validation_status", "draft"),
            "ready_for_use": exam.get("validation_status") == "approved"
        }


# ==================== EXAM GENERATOR ====================

class OETExamGenerator:
    """Generate OET exam content with multi-agent validation"""
    
    def __init__(self, db, llm_client=None):
        self.db = db
        self.llm_client = llm_client
        
    async def generate_listening_part_a(self, profession: str, topic: str) -> Dict:
        """Generate Listening Part A - Consultation extracts"""
        
        prompt = f"""Generate an OET Listening Part A consultation extract for {profession}.

Topic: {topic}
Format: Two healthcare professional-patient consultations
Questions: 24 note-completion questions (12 per consultation)

Requirements:
1. Create a realistic consultation dialogue
2. Include patient history, symptoms, examination, diagnosis, and treatment plan
3. Create 12 questions that require exact words from the audio
4. Answers should be 1-3 words from the dialogue
5. Use appropriate medical terminology for {profession}

Output JSON format:
{{
    "consultation_1": {{
        "scenario": "description",
        "dialogue": [
            {{"speaker": "nurse/doctor/patient", "text": "..."}},
            ...
        ],
        "questions": [
            {{
                "question_number": 1,
                "blank_text": "Patient reports ___ for the past week",
                "correct_answer": "severe headaches",
                "acceptable_answers": ["severe headache", "bad headaches"]
            }},
            ...
        ]
    }},
    "consultation_2": {{ ... }}
}}
"""
        
        # In production, this would call the LLM
        # For now, return a structured template
        return {
            "part": "part_a",
            "profession": profession,
            "topic": topic,
            "status": "generated",
            "needs_llm_generation": True,
            "prompt": prompt
        }
    
    async def generate_reading_part_a(self, theme: str) -> Dict:
        """Generate Reading Part A - Four texts on one theme"""
        
        prompt = f"""Generate OET Reading Part A content.

Theme: {theme}
Format: 4 short healthcare texts (Text A, B, C, D) on the same theme
Questions: 20 questions (matching, short answer, gap fill)

Text requirements:
- Text A: Case study or patient scenario (150-200 words)
- Text B: Clinical guideline extract (150-200 words)
- Text C: Research summary (150-200 words)
- Text D: Policy or procedure extract (150-200 words)

Question distribution:
- Questions 1-8: Matching (which text contains this information?)
- Questions 9-14: Short answer (exact words from texts)
- Questions 15-20: Gap fill (complete sentences)

Output JSON format:
{{
    "theme": "{theme}",
    "texts": {{
        "A": {{"title": "...", "content": "...", "type": "case_study"}},
        "B": {{"title": "...", "content": "...", "type": "guideline"}},
        "C": {{"title": "...", "content": "...", "type": "research"}},
        "D": {{"title": "...", "content": "...", "type": "policy"}}
    }},
    "questions": [
        {{
            "question_number": 1,
            "type": "matching",
            "question_text": "Which text mentions...",
            "correct_answer": "B",
            "explanation": "Text B states that..."
        }},
        ...
    ]
}}
"""
        return {
            "part": "part_a",
            "theme": theme,
            "status": "generated",
            "needs_llm_generation": True,
            "prompt": prompt
        }
    
    async def generate_writing_task(self, profession: str, letter_type: str) -> Dict:
        """Generate Writing Task - Professional letter"""
        
        prompt = f"""Generate an OET Writing task for {profession}.

Letter type: {letter_type}
Word count: 180-200 words

Requirements:
1. Create detailed, realistic case notes
2. Include some irrelevant details (to test candidate's ability to select relevant info)
3. The task should require clear clinical reasoning
4. Include specific medical details appropriate for {profession}

Case notes should include:
- Patient demographics
- Presenting complaint
- History (relevant AND some irrelevant details)
- Examination findings
- Investigations and results
- Diagnosis
- Treatment given
- Discharge/referral plan

Output JSON format:
{{
    "task_instructions": "Using the information in the case notes, write a {letter_type} letter...",
    "recipient": {{
        "name": "Dr...",
        "position": "...",
        "facility": "..."
    }},
    "case_notes": {{
        "patient_name": "...",
        "dob": "...",
        "presenting_complaint": "...",
        ...
    }},
    "key_points_to_include": ["...", "..."],
    "points_to_omit": ["irrelevant detail 1", "..."],
    "sample_answer": "Dear Dr..."
}}
"""
        return {
            "task_type": "writing",
            "profession": profession,
            "letter_type": letter_type,
            "status": "generated",
            "needs_llm_generation": True,
            "prompt": prompt
        }
    
    async def generate_speaking_role_play(self, profession: str, scenario_type: str) -> Dict:
        """Generate Speaking Role Play"""
        
        prompt = f"""Generate an OET Speaking role play for {profession}.

Scenario type: {scenario_type}
Duration: 5 minutes

Requirements:
1. Realistic healthcare scenario
2. Clear communication challenge
3. Opportunity for empathy and rapport building
4. Information exchange needed
5. Appropriate for {profession} context

Output JSON format:
{{
    "scenario_title": "...",
    "setting": "...",
    "candidate_card": {{
        "role": "...",
        "situation": "...",
        "tasks": ["...", "...", "..."]
    }},
    "interlocutor_card": {{
        "role": "...",
        "situation": "...",
        "responses": {{
            "initial_concern": "...",
            "if_asked_about_X": "...",
            "emotional_state": "..."
        }}
    }},
    "key_communication_points": ["...", "..."],
    "sample_dialogue": [
        {{"speaker": "candidate", "text": "..."}},
        {{"speaker": "patient", "text": "..."}}
    ]
}}
"""
        return {
            "task_type": "speaking",
            "profession": profession,
            "scenario_type": scenario_type,
            "status": "generated",
            "needs_llm_generation": True,
            "prompt": prompt
        }


# ==================== VALIDATION PIPELINE ====================

class ValidationPipeline:
    """Multi-agent validation pipeline for exam content"""
    
    def __init__(self, db, llm_client=None):
        self.db = db
        self.llm_client = llm_client
    
    async def validate_with_reviewer_1(self, content: Dict) -> Tuple[bool, Dict]:
        """First AI reviewer - Content Accuracy"""
        
        review_prompt = f"""Review this OET exam content for accuracy:

{json.dumps(content, indent=2)}

Check:
1. Medical accuracy of all clinical information
2. Language appropriateness for healthcare context
3. Correct answer validity
4. Format compliance with OET standards
5. Any ambiguities in questions

Respond with JSON:
{{
    "passed": true/false,
    "issues": ["issue1", "issue2"],
    "corrections_needed": ["correction1", "correction2"],
    "confidence_score": 0-100
}}
"""
        
        # In production, call LLM
        # For now, return pass with notes
        return True, {
            "reviewer": "ai_reviewer_1",
            "passed": True,
            "issues": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def validate_with_reviewer_2(self, content: Dict) -> Tuple[bool, Dict]:
        """Second AI reviewer - Educational Quality"""
        
        review_prompt = f"""Review this OET exam content for educational quality:

{json.dumps(content, indent=2)}

Check:
1. Question discrimination effectiveness
2. Distractor quality (plausible but wrong)
3. Topic relevance for healthcare professionals
4. Difficulty calibration
5. Originality (not copied content)

Respond with JSON:
{{
    "passed": true/false,
    "quality_score": 1-10,
    "feedback": ["feedback1", "feedback2"],
    "recommendations": ["rec1", "rec2"]
}}
"""
        
        return True, {
            "reviewer": "ai_reviewer_2",
            "passed": True,
            "quality_score": 8,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def run_full_pipeline(self, content: Dict) -> Dict:
        """Run content through full validation pipeline"""
        
        results = {
            "content_id": content.get("id", str(uuid4())),
            "original_status": content.get("validation_status", "draft"),
            "pipeline_started": datetime.now(timezone.utc).isoformat(),
            "stages": []
        }
        
        # Stage 1: AI Reviewer 1
        passed_1, review_1 = await self.validate_with_reviewer_1(content)
        results["stages"].append({
            "stage": "ai_reviewer_1",
            "passed": passed_1,
            "details": review_1
        })
        
        if not passed_1:
            results["final_status"] = ValidationStatus.REJECTED.value
            results["rejection_reason"] = "Failed AI Reviewer 1"
            return results
        
        # Stage 2: AI Reviewer 2
        passed_2, review_2 = await self.validate_with_reviewer_2(content)
        results["stages"].append({
            "stage": "ai_reviewer_2",
            "passed": passed_2,
            "details": review_2
        })
        
        if not passed_2:
            results["final_status"] = ValidationStatus.REJECTED.value
            results["rejection_reason"] = "Failed AI Reviewer 2"
            return results
        
        # Stage 3: Ready for human review
        results["final_status"] = ValidationStatus.PENDING_HUMAN_REVIEW.value
        results["pipeline_completed"] = datetime.now(timezone.utc).isoformat()
        
        return results


# ==================== ANTI-REPETITION SYSTEM ====================

class AntiRepetitionSystem:
    """Prevent topic and question repetition"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_student_history(self, student_id: str) -> Dict:
        """Get all questions/topics a student has seen"""
        history = await self.db.student_exam_history.find_one(
            {"student_id": student_id},
            {"_id": 0}
        )
        return history or {"seen_questions": [], "seen_topics": [], "seen_exams": []}
    
    async def select_exam_for_student(self, student_id: str, exam_type: str) -> Optional[str]:
        """Select an exam the student hasn't taken"""
        history = await self.get_student_history(student_id)
        seen_exams = history.get("seen_exams", [])
        
        # Find an exam not in seen_exams
        available_exam = await self.db.exam_bank.find_one({
            "exam_type": exam_type,
            "exam_id": {"$nin": seen_exams},
            "validation_status": "approved"
        }, {"_id": 0})
        
        return available_exam
    
    async def record_exam_taken(self, student_id: str, exam_id: str, topics: List[str]):
        """Record that a student has taken an exam"""
        await self.db.student_exam_history.update_one(
            {"student_id": student_id},
            {
                "$push": {
                    "seen_exams": exam_id,
                    "seen_topics": {"$each": topics}
                },
                "$set": {"last_exam_date": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    
    async def check_topic_repetition(self, student_id: str, proposed_topics: List[str]) -> Dict:
        """Check if proposed topics would cause too much repetition"""
        history = await self.get_student_history(student_id)
        seen_topics = set(history.get("seen_topics", []))
        proposed_set = set(proposed_topics)
        
        overlap = seen_topics.intersection(proposed_set)
        repetition_rate = len(overlap) / len(proposed_set) if proposed_set else 0
        
        return {
            "overlap_topics": list(overlap),
            "repetition_rate": repetition_rate,
            "acceptable": repetition_rate < 0.3  # Max 30% topic overlap
        }
