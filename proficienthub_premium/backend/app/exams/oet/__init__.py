"""
ProficientHub - OET Exam Module
Complete implementation for OET (Occupational English Test) exam generation and evaluation

OET STRUCTURE:
- Listening (45 min): 3 parts, 42 questions
- Reading (60 min): 3 parts, 42 questions
- Writing (45 min): 1 referral letter
- Speaking (20 min): 2 role-plays

PROFESSIONS SUPPORTED:
- Medicine
- Nursing
- Dentistry
- Pharmacy
- Physiotherapy
- Radiography
- Occupational Therapy
- Dietetics
- Podiatry
- Speech Pathology
- Optometry
- Veterinary Science
"""

from app.exams.oet.models import (
    OETProfession,
    OETSection,
    OETGrade,
    ListeningPart,
    ReadingPart,
    OETListeningQuestion,
    OETReadingQuestion,
    OETWritingTask,
    OETSpeakingRolePlay,
    OETExamSession,
    OETSectionResult
)

from app.exams.oet.generator import OETExamGenerator
from app.exams.oet.evaluator import OETEvaluator
from app.exams.oet.content_bank import OETContentBank

__all__ = [
    "OETProfession",
    "OETSection",
    "OETGrade",
    "ListeningPart",
    "ReadingPart",
    "OETListeningQuestion",
    "OETReadingQuestion",
    "OETWritingTask",
    "OETSpeakingRolePlay",
    "OETExamSession",
    "OETSectionResult",
    "OETExamGenerator",
    "OETEvaluator",
    "OETContentBank"
]
