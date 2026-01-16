"""
ProficientHub - Exam Generator Service

Enterprise-grade exam generation with anti-hallucination validation system.
Generates authentic exam questions following official formats and guidelines.
"""

import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random

from app.content.exam_topics import (
    ALL_EXAM_TOPICS,
    get_all_topics_for_exam,
    get_writing_task2_topic,
    get_speaking_part2_topic,
    TopicFrequency,
    TopicDifficulty,
)


class QuestionType(str, Enum):
    """Supported question types across all exam formats."""
    # Reading
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE_NOT_GIVEN = "true_false_not_given"
    YES_NO_NOT_GIVEN = "yes_no_not_given"
    MATCHING_HEADINGS = "matching_headings"
    MATCHING_INFORMATION = "matching_information"
    MATCHING_FEATURES = "matching_features"
    SENTENCE_COMPLETION = "sentence_completion"
    SUMMARY_COMPLETION = "summary_completion"
    NOTE_COMPLETION = "note_completion"
    TABLE_COMPLETION = "table_completion"
    FLOW_CHART_COMPLETION = "flow_chart_completion"
    DIAGRAM_LABELING = "diagram_labeling"
    SHORT_ANSWER = "short_answer"

    # Listening
    FORM_COMPLETION = "form_completion"
    MAP_LABELING = "map_labeling"
    PLAN_LABELING = "plan_labeling"

    # Writing
    TASK1_REPORT = "task1_report"
    TASK1_LETTER = "task1_letter"
    TASK2_ESSAY = "task2_essay"
    INTEGRATED_WRITING = "integrated_writing"

    # Speaking
    INTERVIEW = "interview"
    CUE_CARD = "cue_card"
    DISCUSSION = "discussion"
    READ_ALOUD = "read_aloud"
    DESCRIBE_IMAGE = "describe_image"
    RETELL_LECTURE = "retell_lecture"


class ValidationStatus(str, Enum):
    """Validation status for generated content."""
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    REGENERATE = "regenerate"


@dataclass
class ValidationResult:
    """Result of content validation."""
    status: ValidationStatus
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedQuestion:
    """A generated exam question with metadata."""
    question_id: str
    exam_type: str
    section: str
    question_type: QuestionType
    content: Dict[str, Any]
    validation: ValidationResult
    difficulty: TopicDifficulty
    topic: str
    generated_at: datetime
    generation_model: str
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "exam_type": self.exam_type,
            "section": self.section,
            "question_type": self.question_type.value,
            "content": self.content,
            "validation": {
                "status": self.validation.status.value,
                "score": self.validation.score,
                "issues": self.validation.issues,
            },
            "difficulty": self.difficulty.value,
            "topic": self.topic,
            "generated_at": self.generated_at.isoformat(),
            "version": self.version,
        }


# ============================================================================
# EXAM FORMAT SPECIFICATIONS - Official Formats for Anti-Hallucination
# ============================================================================

EXAM_FORMAT_SPECS = {
    "ielts_academic": {
        "reading": {
            "num_passages": 3,
            "passage_length_range": (700, 900),  # words
            "questions_per_passage": (13, 14),
            "total_questions": 40,
            "time_minutes": 60,
            "question_types": [
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.TRUE_FALSE_NOT_GIVEN,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_INFORMATION,
                QuestionType.SENTENCE_COMPLETION,
                QuestionType.SUMMARY_COMPLETION,
                QuestionType.SHORT_ANSWER,
            ],
            "passage_sources": ["academic_journals", "magazines", "newspapers", "books"],
            "topics": ["science", "history", "sociology", "economics", "environment"],
        },
        "listening": {
            "num_sections": 4,
            "questions_per_section": 10,
            "total_questions": 40,
            "time_minutes": 30,
            "section_contexts": [
                "social_conversation",  # Section 1
                "social_monologue",     # Section 2
                "academic_discussion",  # Section 3
                "academic_lecture",     # Section 4
            ],
            "question_types": [
                QuestionType.FORM_COMPLETION,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MATCHING_FEATURES,
                QuestionType.MAP_LABELING,
                QuestionType.NOTE_COMPLETION,
                QuestionType.SENTENCE_COMPLETION,
            ],
        },
        "writing": {
            "task1": {
                "type": "report",
                "min_words": 150,
                "time_minutes": 20,
                "data_types": ["graph", "chart", "table", "diagram", "map", "process"],
            },
            "task2": {
                "type": "essay",
                "min_words": 250,
                "time_minutes": 40,
                "essay_types": ["opinion", "discussion", "problem_solution", "two_part"],
            },
        },
        "speaking": {
            "part1": {
                "type": "interview",
                "duration_minutes": (4, 5),
                "num_topics": 3,
                "questions_per_topic": (3, 4),
            },
            "part2": {
                "type": "cue_card",
                "preparation_seconds": 60,
                "speaking_minutes": (1, 2),
            },
            "part3": {
                "type": "discussion",
                "duration_minutes": (4, 5),
            },
        },
    },
    "ielts_general": {
        "reading": {
            "num_passages": 3,
            "sections": ["social_survival", "workplace", "general_interest"],
            "total_questions": 40,
            "time_minutes": 60,
        },
        "listening": "same_as_academic",
        "writing": {
            "task1": {
                "type": "letter",
                "min_words": 150,
                "time_minutes": 20,
                "letter_types": ["formal", "semi_formal", "informal"],
                "purposes": ["request", "complaint", "apology", "invitation", "application"],
            },
            "task2": "same_as_academic",
        },
        "speaking": "same_as_academic",
    },
    "cambridge_b2_first": {
        "reading_use_of_english": {
            "num_parts": 7,
            "total_questions": 52,
            "time_minutes": 75,
            "parts": {
                1: {"type": "multiple_choice_cloze", "questions": 8},
                2: {"type": "open_cloze", "questions": 8},
                3: {"type": "word_formation", "questions": 8},
                4: {"type": "key_word_transformations", "questions": 6},
                5: {"type": "multiple_choice", "questions": 6},
                6: {"type": "gapped_text", "questions": 6},
                7: {"type": "multiple_matching", "questions": 10},
            },
        },
        "writing": {
            "part1": {
                "type": "essay",
                "words": (140, 190),
                "required": True,
            },
            "part2": {
                "types": ["article", "email_letter", "report", "review"],
                "words": (140, 190),
                "choose_one_of": 3,
            },
            "time_minutes": 80,
        },
        "listening": {
            "num_parts": 4,
            "total_questions": 30,
            "time_minutes": 40,
        },
        "speaking": {
            "duration_minutes": 14,
            "num_parts": 4,
            "format": "paired",
        },
    },
    "cambridge_c1_advanced": {
        "reading_use_of_english": {
            "num_parts": 8,
            "total_questions": 56,
            "time_minutes": 90,
            "parts": {
                1: {"type": "multiple_choice_cloze", "questions": 8},
                2: {"type": "open_cloze", "questions": 8},
                3: {"type": "word_formation", "questions": 8},
                4: {"type": "key_word_transformations", "questions": 6},
                5: {"type": "multiple_choice", "questions": 6},
                6: {"type": "cross_text_multiple_matching", "questions": 4},
                7: {"type": "gapped_text", "questions": 6},
                8: {"type": "multiple_matching", "questions": 10},
            },
        },
        "writing": {
            "part1": {
                "type": "essay",
                "words": (220, 260),
                "required": True,
            },
            "part2": {
                "types": ["email_letter", "proposal", "report", "review"],
                "words": (220, 260),
                "choose_one_of": 3,
            },
            "time_minutes": 90,
        },
        "listening": {
            "num_parts": 4,
            "total_questions": 30,
            "time_minutes": 40,
        },
        "speaking": {
            "duration_minutes": 15,
            "num_parts": 4,
            "format": "paired",
        },
    },
    "toefl_ibt": {
        "reading": {
            "num_passages": 2,
            "passage_length": (700, 800),
            "questions_per_passage": 10,
            "total_questions": 20,
            "time_minutes": 35,
            "question_types": [
                "factual_information",
                "negative_factual",
                "inference",
                "rhetorical_purpose",
                "vocabulary",
                "reference",
                "sentence_simplification",
                "insert_text",
                "prose_summary",
                "fill_table",
            ],
        },
        "listening": {
            "num_lectures": 3,
            "num_conversations": 2,
            "questions_per_lecture": 6,
            "questions_per_conversation": 5,
            "total_questions": 28,
            "time_minutes": 36,
        },
        "speaking": {
            "num_tasks": 4,
            "time_minutes": 16,
            "tasks": {
                1: {"type": "independent", "prep_seconds": 15, "response_seconds": 45},
                2: {"type": "integrated_campus", "prep_seconds": 30, "response_seconds": 60},
                3: {"type": "integrated_academic", "prep_seconds": 30, "response_seconds": 60},
                4: {"type": "integrated_lecture", "prep_seconds": 20, "response_seconds": 60},
            },
        },
        "writing": {
            "integrated": {
                "reading_time_minutes": 3,
                "listening_time_minutes": 2,
                "writing_time_minutes": 20,
                "words": (150, 225),
            },
            "academic_discussion": {
                "time_minutes": 10,
                "words": (100, 150),
            },
        },
    },
    "pte_academic": {
        "speaking_writing": {
            "time_minutes": (54, 67),
            "tasks": [
                {"type": "read_aloud", "count": (6, 7)},
                {"type": "repeat_sentence", "count": (10, 12)},
                {"type": "describe_image", "count": (3, 4)},
                {"type": "retell_lecture", "count": (1, 2)},
                {"type": "answer_short_question", "count": (5, 6)},
                {"type": "summarize_written_text", "count": 1},
                {"type": "essay", "count": 1, "words": (200, 300), "time_minutes": 20},
            ],
        },
        "reading": {
            "time_minutes": (29, 30),
            "tasks": [
                {"type": "fill_blanks_reading_writing", "count": (5, 6)},
                {"type": "multiple_choice_multiple", "count": (1, 2)},
                {"type": "reorder_paragraphs", "count": (2, 3)},
                {"type": "fill_blanks_reading", "count": (4, 5)},
                {"type": "multiple_choice_single", "count": (1, 2)},
            ],
        },
        "listening": {
            "time_minutes": (30, 43),
            "tasks": [
                {"type": "summarize_spoken_text", "count": (1, 2)},
                {"type": "multiple_choice_multiple", "count": (1, 2)},
                {"type": "fill_blanks", "count": (2, 3)},
                {"type": "highlight_correct_summary", "count": (1, 2)},
                {"type": "multiple_choice_single", "count": (1, 2)},
                {"type": "select_missing_word", "count": (1, 2)},
                {"type": "highlight_incorrect_words", "count": (2, 3)},
                {"type": "write_from_dictation", "count": (3, 4)},
            ],
        },
    },
    "oet_medicine": {
        "listening": {
            "num_parts": 3,
            "total_questions": 42,
            "time_minutes": 40,
            "parts": {
                "A": {"type": "consultation_extracts", "questions": 24},
                "B": {"type": "workplace_presentations", "questions": 6},
                "C": {"type": "healthcare_presentations", "questions": 12},
            },
        },
        "reading": {
            "num_parts": 3,
            "total_questions": 42,
            "time_minutes": 60,
            "parts": {
                "A": {"type": "expeditious_reading", "questions": 20, "texts": 4},
                "B": {"type": "careful_reading_short", "questions": 6},
                "C": {"type": "careful_reading_long", "questions": 16, "texts": 2},
            },
        },
        "writing": {
            "type": "referral_letter",
            "time_minutes": 45,
            "words": (180, 200),
            "case_notes_provided": True,
        },
        "speaking": {
            "type": "role_play",
            "num_scenarios": 2,
            "time_per_scenario_minutes": 5,
            "preparation_minutes": 3,
        },
    },
    "duolingo": {
        "adaptive_test": {
            "time_minutes": 60,
            "sections": ["literacy", "conversation", "comprehension", "production"],
            "question_types": [
                "read_and_complete",
                "read_and_select",
                "listen_and_type",
                "read_aloud",
                "write_about_photo",
                "speak_about_photo",
                "read_then_write",
                "listen_then_speak",
                "interactive_reading",
                "interactive_listening",
            ],
        },
        "video_interview": {
            "speaking_prompts": 2,
            "writing_prompts": 1,
            "time_minutes": 10,
        },
    },
}


# ============================================================================
# ANTI-HALLUCINATION VALIDATION SYSTEM
# ============================================================================

class AntiHallucinationValidator:
    """
    Multi-layer validation system to ensure generated content is authentic,
    accurate, and follows official exam formats.
    """

    # Forbidden patterns that indicate hallucination
    HALLUCINATION_PATTERNS = [
        r"(?i)as an ai",
        r"(?i)i cannot",
        r"(?i)i'm sorry",
        r"(?i)i don't have",
        r"(?i)my training data",
        r"(?i)language model",
        r"(?i)artificial intelligence",
        r"(?i)openai|anthropic|claude|gpt",
        r"(?i)this is a fictional",
        r"(?i)for example purposes",
        r"(?i)placeholder",
        r"(?i)lorem ipsum",
        r"(?i)\[insert\s",
        r"(?i)\[your\s",
        r"(?i)xxx+",
        r"(?i)sample answer",
        r"(?i)example response",
    ]

    # Academic vocabulary expected in high-level exam content
    ACADEMIC_VOCABULARY = {
        "analyze", "concept", "theory", "hypothesis", "methodology",
        "significant", "impact", "factor", "aspect", "perspective",
        "evidence", "research", "study", "data", "findings",
        "conclusion", "implication", "correlation", "phenomenon",
        "framework", "paradigm", "critique", "synthesis", "evaluation",
    }

    # Medical vocabulary for OET validation
    MEDICAL_VOCABULARY = {
        "patient", "diagnosis", "treatment", "symptoms", "medication",
        "referral", "consultation", "examination", "history", "prognosis",
        "condition", "therapy", "dosage", "contraindication", "procedure",
        "assessment", "intervention", "monitoring", "discharge", "follow-up",
    }

    def __init__(self, exam_type: str):
        self.exam_type = exam_type
        self.format_spec = EXAM_FORMAT_SPECS.get(exam_type, {})

    async def validate_content(
        self,
        content: Dict[str, Any],
        content_type: str,
        section: str,
    ) -> ValidationResult:
        """
        Run all validation checks on generated content.
        """
        issues = []
        suggestions = []
        scores = []

        # 1. Check for hallucination patterns
        hall_result = self._check_hallucination_patterns(content)
        scores.append(hall_result[0])
        issues.extend(hall_result[1])

        # 2. Validate format compliance
        format_result = self._validate_format(content, content_type, section)
        scores.append(format_result[0])
        issues.extend(format_result[1])
        suggestions.extend(format_result[2])

        # 3. Check content quality
        quality_result = self._check_content_quality(content, content_type)
        scores.append(quality_result[0])
        issues.extend(quality_result[1])

        # 4. Validate answer consistency
        if content_type in ["multiple_choice", "true_false_not_given"]:
            answer_result = self._validate_answers(content)
            scores.append(answer_result[0])
            issues.extend(answer_result[1])

        # 5. Domain-specific validation
        domain_result = self._domain_specific_validation(content, section)
        scores.append(domain_result[0])
        issues.extend(domain_result[1])

        # Calculate final score
        final_score = sum(scores) / len(scores) if scores else 0.0

        # Determine status
        if issues and any("critical" in issue.lower() for issue in issues):
            status = ValidationStatus.REGENERATE
        elif final_score < 0.6:
            status = ValidationStatus.FAILED
        elif final_score < 0.8:
            status = ValidationStatus.NEEDS_REVIEW
        else:
            status = ValidationStatus.PASSED

        return ValidationResult(
            status=status,
            score=final_score,
            issues=issues,
            suggestions=suggestions,
            metadata={"scores_breakdown": dict(zip(
                ["hallucination", "format", "quality", "answers", "domain"],
                scores
            ))},
        )

    def _check_hallucination_patterns(
        self,
        content: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Check for AI hallucination indicators."""
        issues = []
        text = json.dumps(content, ensure_ascii=False)

        for pattern in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, text):
                issues.append(f"CRITICAL: Hallucination pattern detected: {pattern}")

        score = 1.0 if not issues else 0.0
        return score, issues

    def _validate_format(
        self,
        content: Dict[str, Any],
        content_type: str,
        section: str,
    ) -> Tuple[float, List[str], List[str]]:
        """Validate content follows official exam format."""
        issues = []
        suggestions = []
        score = 1.0

        # Get section spec
        section_spec = self.format_spec.get(section, {})

        # Check required fields based on content type
        if content_type == "multiple_choice":
            required = ["question", "options", "correct_answer"]
            for field in required:
                if field not in content:
                    issues.append(f"Missing required field: {field}")
                    score -= 0.2

            # Validate option count (usually 4 for most exams)
            if "options" in content:
                opt_count = len(content["options"])
                if opt_count < 3 or opt_count > 5:
                    issues.append(f"Invalid option count: {opt_count}")
                    score -= 0.1

        elif content_type == "passage":
            if "text" not in content:
                issues.append("Missing passage text")
                score -= 0.3
            else:
                word_count = len(content["text"].split())
                if section_spec.get("passage_length_range"):
                    min_words, max_words = section_spec["passage_length_range"]
                    if word_count < min_words:
                        suggestions.append(f"Passage too short ({word_count} words)")
                        score -= 0.1
                    elif word_count > max_words:
                        suggestions.append(f"Passage too long ({word_count} words)")
                        score -= 0.05

        elif content_type == "essay_prompt":
            if "topic" not in content or "task" not in content:
                issues.append("Missing topic or task description")
                score -= 0.2

        return max(0, score), issues, suggestions

    def _check_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str,
    ) -> Tuple[float, List[str]]:
        """Check overall content quality."""
        issues = []
        score = 1.0
        text = json.dumps(content, ensure_ascii=False)

        # Check for repetitive content
        words = text.lower().split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:
                issues.append("Content appears repetitive")
                score -= 0.2

        # Check for appropriate academic vocabulary in reading passages
        if content_type == "passage":
            academic_count = sum(1 for word in words if word in self.ACADEMIC_VOCABULARY)
            if academic_count < 3:
                issues.append("Insufficient academic vocabulary")
                score -= 0.1

        # Check grammar indicators (basic)
        text_check = content.get("text", "") or content.get("question", "")
        if text_check:
            # Check sentence structure
            sentences = text_check.split(".")
            short_sentences = sum(1 for s in sentences if len(s.split()) < 3 and s.strip())
            if short_sentences > len(sentences) * 0.5:
                issues.append("Too many incomplete sentences")
                score -= 0.15

        return max(0, score), issues

    def _validate_answers(
        self,
        content: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Validate answer consistency and correctness."""
        issues = []
        score = 1.0

        if "options" in content and "correct_answer" in content:
            correct = content["correct_answer"]
            options = content["options"]

            # Check correct answer exists in options
            if isinstance(correct, int):
                if correct < 0 or correct >= len(options):
                    issues.append("CRITICAL: Correct answer index out of range")
                    score = 0.0
            elif isinstance(correct, str):
                if correct not in options and correct.upper() not in ["A", "B", "C", "D", "E"]:
                    issues.append("CRITICAL: Correct answer not in options")
                    score = 0.0

            # Check for duplicate options
            if len(options) != len(set(str(o).lower() for o in options)):
                issues.append("Duplicate options detected")
                score -= 0.2

        return max(0, score), issues

    def _domain_specific_validation(
        self,
        content: Dict[str, Any],
        section: str,
    ) -> Tuple[float, List[str]]:
        """Domain-specific validation based on exam type."""
        issues = []
        score = 1.0
        text = json.dumps(content, ensure_ascii=False).lower()

        # OET-specific validation
        if "oet" in self.exam_type:
            medical_count = sum(1 for word in text.split() if word in self.MEDICAL_VOCABULARY)
            if medical_count < 2:
                issues.append("Insufficient medical terminology for OET")
                score -= 0.2

        # IELTS Academic vs General
        if self.exam_type == "ielts_general" and section == "writing":
            if "letter" not in text and "dear" not in text:
                issues.append("General Training Task 1 should be a letter format")
                score -= 0.15

        return max(0, score), issues


# ============================================================================
# EXAM GENERATOR SERVICE
# ============================================================================

class ExamGeneratorService:
    """
    Enterprise exam generation service with anti-hallucination validation.
    """

    def __init__(self, ai_client=None):
        """
        Initialize with optional AI client (OpenAI or Anthropic).
        If no client provided, uses template-based generation.
        """
        self.ai_client = ai_client
        self.question_cache: Dict[str, List[GeneratedQuestion]] = {}

    async def generate_full_mock_exam(
        self,
        exam_type: str,
        difficulty: TopicDifficulty = TopicDifficulty.INTERMEDIATE,
        topic_preferences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete mock exam for the specified exam type.
        """
        exam_spec = EXAM_FORMAT_SPECS.get(exam_type)
        if not exam_spec:
            raise ValueError(f"Unsupported exam type: {exam_type}")

        validator = AntiHallucinationValidator(exam_type)
        exam_sections = {}

        # Generate each section based on exam type
        if exam_type.startswith("ielts"):
            exam_sections = await self._generate_ielts_exam(
                exam_type, exam_spec, difficulty, validator
            )
        elif exam_type.startswith("cambridge"):
            exam_sections = await self._generate_cambridge_exam(
                exam_type, exam_spec, difficulty, validator
            )
        elif exam_type == "toefl_ibt":
            exam_sections = await self._generate_toefl_exam(
                exam_spec, difficulty, validator
            )
        elif exam_type == "pte_academic":
            exam_sections = await self._generate_pte_exam(
                exam_spec, difficulty, validator
            )
        elif exam_type == "oet_medicine":
            exam_sections = await self._generate_oet_exam(
                exam_spec, difficulty, validator
            )
        elif exam_type == "duolingo":
            exam_sections = await self._generate_duolingo_exam(
                exam_spec, difficulty, validator
            )

        return {
            "exam_type": exam_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "difficulty": difficulty.value,
            "sections": exam_sections,
            "metadata": {
                "version": "1.0",
                "generator": "ProficientHub ExamGenerator",
            },
        }

    async def _generate_ielts_exam(
        self,
        exam_type: str,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Academic or General Training exam."""
        sections = {}
        topics = get_all_topics_for_exam(exam_type)

        # Reading Section
        reading_spec = spec.get("reading", {})
        reading_questions = []
        for i in range(reading_spec.get("num_passages", 3)):
            passage_topic = self._select_topic(topics.get("reading", []), difficulty)
            passage = await self._generate_reading_passage(
                exam_type, passage_topic, difficulty, i + 1, validator
            )
            reading_questions.append(passage)
        sections["reading"] = {
            "passages": reading_questions,
            "time_minutes": reading_spec.get("time_minutes", 60),
            "total_questions": reading_spec.get("total_questions", 40),
        }

        # Listening Section
        listening_spec = spec.get("listening", {})
        listening_sections = []
        for i in range(listening_spec.get("num_sections", 4)):
            context = listening_spec.get("section_contexts", [])[i] if i < len(
                listening_spec.get("section_contexts", [])
            ) else "general"
            section = await self._generate_listening_section(
                exam_type, context, difficulty, i + 1, validator
            )
            listening_sections.append(section)
        sections["listening"] = {
            "sections": listening_sections,
            "time_minutes": listening_spec.get("time_minutes", 30),
            "total_questions": listening_spec.get("total_questions", 40),
        }

        # Writing Section
        writing_spec = spec.get("writing", {})
        writing_tasks = []

        # Task 1
        task1_spec = writing_spec.get("task1", {})
        if task1_spec.get("type") == "report":
            task1 = await self._generate_writing_task1_academic(
                exam_type, difficulty, validator
            )
        else:
            task1 = await self._generate_writing_task1_general(
                exam_type, difficulty, validator
            )
        writing_tasks.append(task1)

        # Task 2
        task2_topic = get_writing_task2_topic(exam_type)
        task2 = await self._generate_writing_task2(
            exam_type, task2_topic, difficulty, validator
        )
        writing_tasks.append(task2)
        sections["writing"] = {
            "tasks": writing_tasks,
            "total_time_minutes": 60,
        }

        # Speaking Section
        speaking_spec = spec.get("speaking", {})
        speaking_parts = []

        # Part 1 - Interview
        part1_topics = self._select_multiple_topics(
            topics.get("speaking", {}).get("part1", []),
            3,
            difficulty
        )
        part1 = await self._generate_speaking_part1(
            exam_type, part1_topics, validator
        )
        speaking_parts.append(part1)

        # Part 2 - Cue Card
        part2_topic = get_speaking_part2_topic(exam_type)
        part2 = await self._generate_speaking_part2(
            exam_type, part2_topic, validator
        )
        speaking_parts.append(part2)

        # Part 3 - Discussion
        part3 = await self._generate_speaking_part3(
            exam_type, part2_topic, validator
        )
        speaking_parts.append(part3)

        sections["speaking"] = {
            "parts": speaking_parts,
            "total_time_minutes": (11, 14),
        }

        return sections

    async def _generate_cambridge_exam(
        self,
        exam_type: str,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Cambridge B2 First or C1 Advanced exam."""
        sections = {}

        # Reading and Use of English
        rue_spec = spec.get("reading_use_of_english", {})
        rue_parts = []
        for part_num, part_spec in rue_spec.get("parts", {}).items():
            part = await self._generate_cambridge_rue_part(
                exam_type, part_num, part_spec, difficulty, validator
            )
            rue_parts.append(part)
        sections["reading_use_of_english"] = {
            "parts": rue_parts,
            "time_minutes": rue_spec.get("time_minutes", 75),
            "total_questions": rue_spec.get("total_questions", 52),
        }

        # Writing
        writing_spec = spec.get("writing", {})
        writing_parts = await self._generate_cambridge_writing(
            exam_type, writing_spec, difficulty, validator
        )
        sections["writing"] = writing_parts

        # Listening
        listening_spec = spec.get("listening", {})
        listening_parts = await self._generate_cambridge_listening(
            exam_type, listening_spec, difficulty, validator
        )
        sections["listening"] = listening_parts

        # Speaking
        speaking_spec = spec.get("speaking", {})
        speaking_parts = await self._generate_cambridge_speaking(
            exam_type, speaking_spec, difficulty, validator
        )
        sections["speaking"] = speaking_parts

        return sections

    async def _generate_toefl_exam(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate TOEFL iBT exam."""
        sections = {}

        # Reading
        reading_spec = spec.get("reading", {})
        reading_passages = []
        for i in range(reading_spec.get("num_passages", 2)):
            passage = await self._generate_toefl_reading_passage(
                i + 1, difficulty, validator
            )
            reading_passages.append(passage)
        sections["reading"] = {
            "passages": reading_passages,
            "time_minutes": reading_spec.get("time_minutes", 35),
            "total_questions": reading_spec.get("total_questions", 20),
        }

        # Listening
        listening_spec = spec.get("listening", {})
        listening_items = await self._generate_toefl_listening(
            listening_spec, difficulty, validator
        )
        sections["listening"] = listening_items

        # Speaking
        speaking_spec = spec.get("speaking", {})
        speaking_tasks = await self._generate_toefl_speaking(
            speaking_spec, difficulty, validator
        )
        sections["speaking"] = speaking_tasks

        # Writing
        writing_spec = spec.get("writing", {})
        writing_tasks = await self._generate_toefl_writing(
            writing_spec, difficulty, validator
        )
        sections["writing"] = writing_tasks

        return sections

    async def _generate_pte_exam(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate PTE Academic exam."""
        sections = {}

        # Speaking & Writing (combined in PTE)
        sw_spec = spec.get("speaking_writing", {})
        sw_tasks = await self._generate_pte_speaking_writing(
            sw_spec, difficulty, validator
        )
        sections["speaking_writing"] = sw_tasks

        # Reading
        reading_spec = spec.get("reading", {})
        reading_tasks = await self._generate_pte_reading(
            reading_spec, difficulty, validator
        )
        sections["reading"] = reading_tasks

        # Listening
        listening_spec = spec.get("listening", {})
        listening_tasks = await self._generate_pte_listening(
            listening_spec, difficulty, validator
        )
        sections["listening"] = listening_tasks

        return sections

    async def _generate_oet_exam(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate OET Medicine exam."""
        sections = {}

        # Listening
        listening_spec = spec.get("listening", {})
        listening_parts = await self._generate_oet_listening(
            listening_spec, difficulty, validator
        )
        sections["listening"] = listening_parts

        # Reading
        reading_spec = spec.get("reading", {})
        reading_parts = await self._generate_oet_reading(
            reading_spec, difficulty, validator
        )
        sections["reading"] = reading_parts

        # Writing
        writing_spec = spec.get("writing", {})
        writing_task = await self._generate_oet_writing(
            writing_spec, difficulty, validator
        )
        sections["writing"] = writing_task

        # Speaking
        speaking_spec = spec.get("speaking", {})
        speaking_tasks = await self._generate_oet_speaking(
            speaking_spec, difficulty, validator
        )
        sections["speaking"] = speaking_tasks

        return sections

    async def _generate_duolingo_exam(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Duolingo English Test."""
        sections = {}

        # Adaptive Test
        adaptive_spec = spec.get("adaptive_test", {})
        adaptive_questions = await self._generate_duolingo_adaptive(
            adaptive_spec, difficulty, validator
        )
        sections["adaptive_test"] = adaptive_questions

        # Video Interview
        interview_spec = spec.get("video_interview", {})
        interview_prompts = await self._generate_duolingo_interview(
            interview_spec, difficulty, validator
        )
        sections["video_interview"] = interview_prompts

        return sections

    # ========================================================================
    # HELPER METHODS FOR CONTENT GENERATION
    # ========================================================================

    def _select_topic(
        self,
        topics: List[Dict],
        difficulty: TopicDifficulty
    ) -> Dict[str, Any]:
        """Select a topic based on difficulty weighting."""
        if not topics:
            return {"name": "General", "subtopics": []}

        # Filter by difficulty if specified
        filtered = [t for t in topics if t.get("difficulty") == difficulty.value]
        if not filtered:
            filtered = topics

        # Weight by frequency
        weighted = []
        for topic in filtered:
            freq = topic.get("frequency", "common")
            weight = {"very_common": 5, "common": 3, "occasional": 1}.get(freq, 1)
            weighted.extend([topic] * weight)

        return random.choice(weighted) if weighted else topics[0]

    def _select_multiple_topics(
        self,
        topics: List[Dict],
        count: int,
        difficulty: TopicDifficulty
    ) -> List[Dict[str, Any]]:
        """Select multiple unique topics."""
        if not topics:
            return [{"name": "General"}] * count

        selected = []
        available = topics.copy()

        for _ in range(min(count, len(available))):
            topic = self._select_topic(available, difficulty)
            selected.append(topic)
            available = [t for t in available if t.get("name") != topic.get("name")]

        return selected

    def _generate_question_id(self, exam_type: str, section: str, index: int) -> str:
        """Generate unique question ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        content = f"{exam_type}_{section}_{index}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    # ========================================================================
    # READING PASSAGE GENERATION
    # ========================================================================

    async def _generate_reading_passage(
        self,
        exam_type: str,
        topic: Dict[str, Any],
        difficulty: TopicDifficulty,
        passage_num: int,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate a reading passage with questions."""

        # For now, use template-based generation
        # In production, this would call the AI client
        passage_content = await self._create_passage_template(
            exam_type, topic, difficulty, passage_num
        )

        # Generate questions for the passage
        questions = await self._generate_passage_questions(
            exam_type, passage_content, difficulty, passage_num, validator
        )

        # Validate the entire passage
        validation = await validator.validate_content(
            {**passage_content, "questions": questions},
            "passage",
            "reading"
        )

        return {
            "passage_number": passage_num,
            "topic": topic.get("name", "General"),
            "content": passage_content,
            "questions": questions,
            "validation": validation.status.value,
            "question_id": self._generate_question_id(exam_type, "reading", passage_num),
        }

    async def _create_passage_template(
        self,
        exam_type: str,
        topic: Dict[str, Any],
        difficulty: TopicDifficulty,
        passage_num: int,
    ) -> Dict[str, Any]:
        """Create passage structure (to be filled by AI or templates)."""
        topic_name = topic.get("name", "General Topic")
        subtopics = topic.get("subtopics", [])

        # Determine word count based on exam type and passage number
        if "ielts" in exam_type:
            base_words = 750 + (passage_num - 1) * 50  # Passages get longer
        elif "toefl" in exam_type:
            base_words = 700
        else:
            base_words = 600

        # Adjust for difficulty
        word_adjustment = {
            TopicDifficulty.BEGINNER: -100,
            TopicDifficulty.INTERMEDIATE: 0,
            TopicDifficulty.ADVANCED: 100,
            TopicDifficulty.EXPERT: 150,
        }
        target_words = base_words + word_adjustment.get(difficulty, 0)

        return {
            "title": f"Passage {passage_num}: {topic_name}",
            "text": f"[PASSAGE TEXT ABOUT {topic_name.upper()}]",  # Placeholder
            "target_word_count": target_words,
            "topic": topic_name,
            "subtopics": subtopics[:3] if subtopics else [],
            "source_type": "academic_journal" if passage_num == 3 else "magazine",
        }

    async def _generate_passage_questions(
        self,
        exam_type: str,
        passage: Dict[str, Any],
        difficulty: TopicDifficulty,
        passage_num: int,
        validator: AntiHallucinationValidator,
    ) -> List[Dict[str, Any]]:
        """Generate questions for a reading passage."""
        questions = []

        # Determine question types based on exam and passage number
        if "ielts" in exam_type:
            question_types = self._get_ielts_question_types(passage_num)
        elif "toefl" in exam_type:
            question_types = self._get_toefl_question_types()
        else:
            question_types = [QuestionType.MULTIPLE_CHOICE] * 5

        for i, q_type in enumerate(question_types):
            question = await self._generate_single_question(
                exam_type, q_type, passage, difficulty, i + 1, validator
            )
            questions.append(question)

        return questions

    def _get_ielts_question_types(self, passage_num: int) -> List[QuestionType]:
        """Get question types for IELTS passage based on position."""
        if passage_num == 1:
            return [
                QuestionType.TRUE_FALSE_NOT_GIVEN,
                QuestionType.TRUE_FALSE_NOT_GIVEN,
                QuestionType.TRUE_FALSE_NOT_GIVEN,
                QuestionType.TRUE_FALSE_NOT_GIVEN,
                QuestionType.SENTENCE_COMPLETION,
                QuestionType.SENTENCE_COMPLETION,
                QuestionType.SENTENCE_COMPLETION,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
            ]
        elif passage_num == 2:
            return [
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.MATCHING_HEADINGS,
                QuestionType.SUMMARY_COMPLETION,
                QuestionType.SUMMARY_COMPLETION,
                QuestionType.SUMMARY_COMPLETION,
                QuestionType.SUMMARY_COMPLETION,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
            ]
        else:  # passage 3
            return [
                QuestionType.MATCHING_INFORMATION,
                QuestionType.MATCHING_INFORMATION,
                QuestionType.MATCHING_INFORMATION,
                QuestionType.MATCHING_INFORMATION,
                QuestionType.YES_NO_NOT_GIVEN,
                QuestionType.YES_NO_NOT_GIVEN,
                QuestionType.YES_NO_NOT_GIVEN,
                QuestionType.YES_NO_NOT_GIVEN,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.SENTENCE_COMPLETION,
            ]

    def _get_toefl_question_types(self) -> List[QuestionType]:
        """Get question types for TOEFL passage."""
        return [
            QuestionType.MULTIPLE_CHOICE,  # Factual
            QuestionType.MULTIPLE_CHOICE,  # Negative factual
            QuestionType.MULTIPLE_CHOICE,  # Inference
            QuestionType.MULTIPLE_CHOICE,  # Rhetorical purpose
            QuestionType.MULTIPLE_CHOICE,  # Vocabulary
            QuestionType.MULTIPLE_CHOICE,  # Reference
            QuestionType.MULTIPLE_CHOICE,  # Sentence simplification
            QuestionType.MULTIPLE_CHOICE,  # Insert text
            QuestionType.MULTIPLE_CHOICE,  # Prose summary
            QuestionType.MULTIPLE_CHOICE,  # Fill table
        ]

    async def _generate_single_question(
        self,
        exam_type: str,
        q_type: QuestionType,
        context: Dict[str, Any],
        difficulty: TopicDifficulty,
        question_num: int,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate a single question of specified type."""
        question_id = self._generate_question_id(exam_type, q_type.value, question_num)

        # Template-based question structure
        question_content = {
            "question_number": question_num,
            "type": q_type.value,
            "question": f"[QUESTION {question_num} - {q_type.value}]",  # Placeholder
            "difficulty": difficulty.value,
        }

        # Add type-specific fields
        if q_type == QuestionType.MULTIPLE_CHOICE:
            question_content["options"] = ["A", "B", "C", "D"]
            question_content["correct_answer"] = "A"  # Placeholder
        elif q_type in [QuestionType.TRUE_FALSE_NOT_GIVEN, QuestionType.YES_NO_NOT_GIVEN]:
            question_content["options"] = ["TRUE", "FALSE", "NOT GIVEN"]
            question_content["correct_answer"] = "TRUE"  # Placeholder
        elif q_type == QuestionType.MATCHING_HEADINGS:
            question_content["paragraph"] = "A"
            question_content["correct_heading"] = "i"
        elif q_type in [QuestionType.SENTENCE_COMPLETION, QuestionType.SUMMARY_COMPLETION]:
            question_content["word_limit"] = "NO MORE THAN THREE WORDS"
            question_content["correct_answer"] = "[ANSWER]"

        # Validate the question
        validation = await validator.validate_content(
            question_content,
            q_type.value,
            "reading"
        )

        return {
            "question_id": question_id,
            **question_content,
            "validation_status": validation.status.value,
        }

    # ========================================================================
    # LISTENING SECTION GENERATION
    # ========================================================================

    async def _generate_listening_section(
        self,
        exam_type: str,
        context: str,
        difficulty: TopicDifficulty,
        section_num: int,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate a listening section."""
        return {
            "section_number": section_num,
            "context": context,
            "audio_script": f"[AUDIO SCRIPT FOR SECTION {section_num} - {context}]",
            "questions": [
                {
                    "question_number": i,
                    "type": "completion" if section_num <= 2 else "multiple_choice",
                    "question": f"[QUESTION {i}]",
                    "correct_answer": f"[ANSWER {i}]",
                }
                for i in range(1, 11)
            ],
            "duration_seconds": 300 + section_num * 60,
        }

    # ========================================================================
    # WRITING TASK GENERATION
    # ========================================================================

    async def _generate_writing_task1_academic(
        self,
        exam_type: str,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Academic Writing Task 1."""
        data_types = ["line_graph", "bar_chart", "pie_chart", "table", "process", "map"]
        selected_type = random.choice(data_types)

        return {
            "task_number": 1,
            "type": "report",
            "data_type": selected_type,
            "prompt": f"The {selected_type.replace('_', ' ')} below shows [DESCRIPTION]. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
            "visual_data": f"[{selected_type.upper()} DATA]",
            "word_requirement": {"minimum": 150},
            "time_minutes": 20,
        }

    async def _generate_writing_task1_general(
        self,
        exam_type: str,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS General Training Writing Task 1."""
        letter_types = ["formal", "semi_formal", "informal"]
        purposes = ["request", "complaint", "apology", "invitation", "application"]

        selected_type = random.choice(letter_types)
        selected_purpose = random.choice(purposes)

        return {
            "task_number": 1,
            "type": "letter",
            "letter_type": selected_type,
            "purpose": selected_purpose,
            "prompt": f"Write a {selected_type.replace('_', '-')} letter to [RECIPIENT] regarding [SITUATION]. In your letter:\n- [BULLET 1]\n- [BULLET 2]\n- [BULLET 3]",
            "word_requirement": {"minimum": 150},
            "time_minutes": 20,
        }

    async def _generate_writing_task2(
        self,
        exam_type: str,
        topic: Dict[str, Any],
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Writing Task 2 essay."""
        essay_types = ["opinion", "discussion", "problem_solution", "two_part"]
        selected_type = random.choice(essay_types)

        topic_name = topic.get("name", "General Topic")

        prompts = {
            "opinion": f"Some people believe that {topic_name.lower()} [STATEMENT]. To what extent do you agree or disagree?",
            "discussion": f"Some people think that {topic_name.lower()} [VIEWPOINT A]. Others believe that [VIEWPOINT B]. Discuss both views and give your own opinion.",
            "problem_solution": f"[PROBLEM RELATED TO {topic_name.upper()}] is becoming increasingly common. What are the causes of this problem and what measures can be taken to address it?",
            "two_part": f"[STATEMENT ABOUT {topic_name.upper()}]. Why do you think this is the case? What can be done to address this situation?",
        }

        return {
            "task_number": 2,
            "type": "essay",
            "essay_type": selected_type,
            "topic": topic_name,
            "prompt": prompts[selected_type],
            "word_requirement": {"minimum": 250},
            "time_minutes": 40,
        }

    # ========================================================================
    # SPEAKING PART GENERATION
    # ========================================================================

    async def _generate_speaking_part1(
        self,
        exam_type: str,
        topics: List[Dict[str, Any]],
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Speaking Part 1 questions."""
        questions = []

        for topic in topics:
            topic_name = topic.get("name", "General")
            subtopics = topic.get("subtopics", [])

            topic_questions = [
                f"Let's talk about {topic_name.lower()}. [QUESTION 1]",
                f"[QUESTION 2 ABOUT {topic_name.upper()}]",
                f"[QUESTION 3 ABOUT {topic_name.upper()}]",
            ]

            questions.append({
                "topic": topic_name,
                "questions": topic_questions,
            })

        return {
            "part_number": 1,
            "type": "interview",
            "duration_minutes": (4, 5),
            "topics": questions,
        }

    async def _generate_speaking_part2(
        self,
        exam_type: str,
        topic: Dict[str, Any],
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Speaking Part 2 cue card."""
        topic_name = topic.get("name", "General Topic")

        return {
            "part_number": 2,
            "type": "cue_card",
            "preparation_seconds": 60,
            "speaking_minutes": (1, 2),
            "topic": topic_name,
            "cue_card": {
                "main_prompt": f"Describe [TOPIC RELATED TO {topic_name.upper()}]",
                "bullet_points": [
                    "[BULLET 1 - WHAT/WHO/WHERE]",
                    "[BULLET 2 - WHEN/HOW]",
                    "[BULLET 3 - WHY/DETAILS]",
                    "[BULLET 4 - FEELINGS/THOUGHTS]",
                ],
            },
            "follow_up_question": f"[FOLLOW-UP ABOUT {topic_name.upper()}]",
        }

    async def _generate_speaking_part3(
        self,
        exam_type: str,
        part2_topic: Dict[str, Any],
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate IELTS Speaking Part 3 discussion questions."""
        topic_name = part2_topic.get("name", "General Topic")

        return {
            "part_number": 3,
            "type": "discussion",
            "duration_minutes": (4, 5),
            "topic": topic_name,
            "questions": [
                f"[ABSTRACT QUESTION 1 ABOUT {topic_name.upper()}]",
                f"[ABSTRACT QUESTION 2 - COMPARISON/CONTRAST]",
                f"[ABSTRACT QUESTION 3 - FUTURE/SPECULATION]",
                f"[ABSTRACT QUESTION 4 - OPINION/EVALUATION]",
                f"[ABSTRACT QUESTION 5 - SOCIETY/GLOBAL PERSPECTIVE]",
            ],
        }

    # ========================================================================
    # CAMBRIDGE, TOEFL, PTE, OET, DUOLINGO SPECIFIC GENERATORS
    # ========================================================================

    async def _generate_cambridge_rue_part(
        self,
        exam_type: str,
        part_num: int,
        part_spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Cambridge Reading and Use of English part."""
        return {
            "part_number": part_num,
            "type": part_spec.get("type", "unknown"),
            "num_questions": part_spec.get("questions", 0),
            "content": f"[PART {part_num} CONTENT - {part_spec.get('type', '').upper()}]",
            "questions": [
                {"question_number": i, "content": f"[Q{i}]", "answer": f"[A{i}]"}
                for i in range(1, part_spec.get("questions", 0) + 1)
            ],
        }

    async def _generate_cambridge_writing(
        self,
        exam_type: str,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Cambridge Writing section."""
        return {
            "time_minutes": spec.get("time_minutes", 80),
            "parts": [
                {
                    "part_number": 1,
                    "type": "essay",
                    "word_range": spec.get("part1", {}).get("words", (140, 190)),
                    "prompt": "[COMPULSORY ESSAY PROMPT]",
                },
                {
                    "part_number": 2,
                    "type": "choice",
                    "word_range": spec.get("part2", {}).get("words", (140, 190)),
                    "options": [
                        {"type": t, "prompt": f"[{t.upper()} PROMPT]"}
                        for t in spec.get("part2", {}).get("types", ["article", "email", "report"])
                    ],
                },
            ],
        }

    async def _generate_cambridge_listening(
        self,
        exam_type: str,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Cambridge Listening section."""
        return {
            "time_minutes": spec.get("time_minutes", 40),
            "total_questions": spec.get("total_questions", 30),
            "parts": [
                {
                    "part_number": i,
                    "audio_script": f"[AUDIO SCRIPT PART {i}]",
                    "questions": [{"q": j, "answer": f"[A{j}]"} for j in range(1, 8)],
                }
                for i in range(1, spec.get("num_parts", 4) + 1)
            ],
        }

    async def _generate_cambridge_speaking(
        self,
        exam_type: str,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Cambridge Speaking section."""
        return {
            "duration_minutes": spec.get("duration_minutes", 14),
            "format": spec.get("format", "paired"),
            "parts": [
                {"part_number": 1, "type": "interview", "content": "[INTERVIEW QUESTIONS]"},
                {"part_number": 2, "type": "long_turn", "content": "[VISUAL PROMPTS]"},
                {"part_number": 3, "type": "collaborative", "content": "[DISCUSSION TASK]"},
                {"part_number": 4, "type": "discussion", "content": "[DISCUSSION QUESTIONS]"},
            ],
        }

    async def _generate_toefl_reading_passage(
        self,
        passage_num: int,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate TOEFL reading passage."""
        return {
            "passage_number": passage_num,
            "content": f"[TOEFL READING PASSAGE {passage_num}]",
            "word_count": 700,
            "questions": [
                {"q": i, "type": self._get_toefl_question_types()[i-1].value, "answer": f"[A{i}]"}
                for i in range(1, 11)
            ],
        }

    async def _generate_toefl_listening(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate TOEFL Listening section."""
        items = []

        # Lectures
        for i in range(spec.get("num_lectures", 3)):
            items.append({
                "type": "lecture",
                "number": i + 1,
                "script": f"[LECTURE {i+1} SCRIPT]",
                "questions": [{"q": j, "answer": f"[A{j}]"} for j in range(1, 7)],
            })

        # Conversations
        for i in range(spec.get("num_conversations", 2)):
            items.append({
                "type": "conversation",
                "number": i + 1,
                "script": f"[CONVERSATION {i+1} SCRIPT]",
                "questions": [{"q": j, "answer": f"[A{j}]"} for j in range(1, 6)],
            })

        return {
            "time_minutes": spec.get("time_minutes", 36),
            "items": items,
        }

    async def _generate_toefl_speaking(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate TOEFL Speaking section."""
        tasks = []
        for task_num, task_spec in spec.get("tasks", {}).items():
            tasks.append({
                "task_number": task_num,
                "type": task_spec.get("type", "independent"),
                "prep_seconds": task_spec.get("prep_seconds", 15),
                "response_seconds": task_spec.get("response_seconds", 45),
                "prompt": f"[SPEAKING TASK {task_num} PROMPT]",
            })
        return {"time_minutes": spec.get("time_minutes", 16), "tasks": tasks}

    async def _generate_toefl_writing(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate TOEFL Writing section."""
        return {
            "tasks": [
                {
                    "type": "integrated",
                    "reading": "[READING PASSAGE]",
                    "listening": "[LECTURE SCRIPT]",
                    "prompt": "[INTEGRATED WRITING PROMPT]",
                    "time_minutes": 20,
                    "word_range": spec.get("integrated", {}).get("words", (150, 225)),
                },
                {
                    "type": "academic_discussion",
                    "prompt": "[ACADEMIC DISCUSSION PROMPT]",
                    "time_minutes": 10,
                    "word_range": spec.get("academic_discussion", {}).get("words", (100, 150)),
                },
            ],
        }

    async def _generate_pte_speaking_writing(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate PTE Speaking & Writing section."""
        tasks = []
        for task_spec in spec.get("tasks", []):
            task_type = task_spec.get("type", "unknown")
            count = task_spec.get("count", 1)
            if isinstance(count, tuple):
                count = count[0]

            for i in range(count):
                tasks.append({
                    "type": task_type,
                    "number": i + 1,
                    "content": f"[{task_type.upper()} CONTENT {i+1}]",
                })

        return {
            "time_minutes": spec.get("time_minutes", (54, 67)),
            "tasks": tasks,
        }

    async def _generate_pte_reading(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate PTE Reading section."""
        return {
            "time_minutes": spec.get("time_minutes", (29, 30)),
            "tasks": [
                {"type": t.get("type"), "count": t.get("count"), "content": f"[{t.get('type', '').upper()}]"}
                for t in spec.get("tasks", [])
            ],
        }

    async def _generate_pte_listening(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate PTE Listening section."""
        return {
            "time_minutes": spec.get("time_minutes", (30, 43)),
            "tasks": [
                {"type": t.get("type"), "count": t.get("count"), "content": f"[{t.get('type', '').upper()}]"}
                for t in spec.get("tasks", [])
            ],
        }

    async def _generate_oet_listening(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate OET Listening section."""
        parts = []
        for part_key, part_spec in spec.get("parts", {}).items():
            parts.append({
                "part": part_key,
                "type": part_spec.get("type", "unknown"),
                "questions": part_spec.get("questions", 0),
                "content": f"[OET LISTENING PART {part_key}]",
            })
        return {
            "time_minutes": spec.get("time_minutes", 40),
            "parts": parts,
        }

    async def _generate_oet_reading(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate OET Reading section."""
        parts = []
        for part_key, part_spec in spec.get("parts", {}).items():
            parts.append({
                "part": part_key,
                "type": part_spec.get("type", "unknown"),
                "questions": part_spec.get("questions", 0),
                "content": f"[OET READING PART {part_key}]",
            })
        return {
            "time_minutes": spec.get("time_minutes", 60),
            "parts": parts,
        }

    async def _generate_oet_writing(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate OET Writing section (referral letter)."""
        return {
            "type": "referral_letter",
            "time_minutes": spec.get("time_minutes", 45),
            "word_range": spec.get("words", (180, 200)),
            "case_notes": "[PATIENT CASE NOTES]",
            "recipient": "[SPECIALIST/HEALTHCARE PROVIDER]",
            "purpose": "[PURPOSE OF REFERRAL]",
        }

    async def _generate_oet_speaking(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate OET Speaking section (role-plays)."""
        scenarios = []
        for i in range(spec.get("num_scenarios", 2)):
            scenarios.append({
                "scenario_number": i + 1,
                "setting": "[HEALTHCARE SETTING]",
                "patient_card": "[PATIENT ROLE CARD]",
                "candidate_card": "[CANDIDATE ROLE CARD]",
                "preparation_minutes": spec.get("preparation_minutes", 3),
                "duration_minutes": spec.get("time_per_scenario_minutes", 5),
            })
        return {"scenarios": scenarios}

    async def _generate_duolingo_adaptive(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Duolingo adaptive test questions."""
        questions = []
        for q_type in spec.get("question_types", []):
            questions.append({
                "type": q_type,
                "content": f"[{q_type.upper()} QUESTION]",
                "adaptive_level": difficulty.value,
            })
        return {
            "time_minutes": spec.get("time_minutes", 60),
            "sections": spec.get("sections", []),
            "questions": questions,
        }

    async def _generate_duolingo_interview(
        self,
        spec: Dict,
        difficulty: TopicDifficulty,
        validator: AntiHallucinationValidator,
    ) -> Dict[str, Any]:
        """Generate Duolingo video interview prompts."""
        return {
            "time_minutes": spec.get("time_minutes", 10),
            "speaking_prompts": [
                {"prompt": "[SPEAKING PROMPT 1]"},
                {"prompt": "[SPEAKING PROMPT 2]"},
            ],
            "writing_prompt": {"prompt": "[WRITING PROMPT]"},
        }


# ============================================================================
# QUESTION BANK MANAGER
# ============================================================================

class QuestionBankManager:
    """
    Manages question bank storage, retrieval, and quality assurance.
    """

    def __init__(self, storage_backend=None):
        self.storage = storage_backend or {}  # In-memory default
        self.quality_threshold = 0.8

    async def store_question(self, question: GeneratedQuestion) -> bool:
        """Store a validated question in the bank."""
        if question.validation.score < self.quality_threshold:
            return False

        key = f"{question.exam_type}:{question.section}:{question.question_type.value}"
        if key not in self.storage:
            self.storage[key] = []
        self.storage[key].append(question)
        return True

    async def get_questions(
        self,
        exam_type: str,
        section: str,
        question_type: Optional[QuestionType] = None,
        count: int = 10,
        difficulty: Optional[TopicDifficulty] = None,
    ) -> List[GeneratedQuestion]:
        """Retrieve questions from the bank."""
        key_prefix = f"{exam_type}:{section}"

        if question_type:
            key = f"{key_prefix}:{question_type.value}"
            questions = self.storage.get(key, [])
        else:
            questions = []
            for key, qs in self.storage.items():
                if key.startswith(key_prefix):
                    questions.extend(qs)

        # Filter by difficulty if specified
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]

        # Random selection
        return random.sample(questions, min(count, len(questions)))

    async def get_bank_stats(self) -> Dict[str, Any]:
        """Get statistics about the question bank."""
        stats = {
            "total_questions": 0,
            "by_exam_type": {},
            "by_section": {},
            "by_difficulty": {},
            "average_quality_score": 0.0,
        }

        all_scores = []

        for key, questions in self.storage.items():
            exam_type, section, q_type = key.split(":")

            stats["total_questions"] += len(questions)

            if exam_type not in stats["by_exam_type"]:
                stats["by_exam_type"][exam_type] = 0
            stats["by_exam_type"][exam_type] += len(questions)

            if section not in stats["by_section"]:
                stats["by_section"][section] = 0
            stats["by_section"][section] += len(questions)

            for q in questions:
                diff = q.difficulty.value
                if diff not in stats["by_difficulty"]:
                    stats["by_difficulty"][diff] = 0
                stats["by_difficulty"][diff] += 1
                all_scores.append(q.validation.score)

        if all_scores:
            stats["average_quality_score"] = sum(all_scores) / len(all_scores)

        return stats


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_exam_generator(ai_client=None) -> ExamGeneratorService:
    """Factory function to create an exam generator instance."""
    return ExamGeneratorService(ai_client=ai_client)
