"""
ProficientHub - OET Evaluator
Complete evaluation and scoring service for OET exams
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from uuid import uuid4
import structlog
from difflib import SequenceMatcher

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.exams.oet.models import (
    OETProfession, OETSection, OETGrade, ListeningPart, ReadingPart,
    OETSectionResult, OETExam,
    OET_SCORING_CONFIG, raw_to_scaled_score, scaled_score_to_grade,
    get_grade_description
)

logger = structlog.get_logger(__name__)


class OETEvaluator:
    """
    Evaluator for OET exam responses
    Handles automatic scoring for Listening/Reading
    AI-assisted scoring for Writing/Speaking
    """

    def __init__(
        self,
        session: AsyncSession,
        ai_client: Optional[Any] = None
    ):
        self.session = session
        self.ai_client = ai_client

    # =========================================================================
    # MAIN EVALUATION METHODS
    # =========================================================================

    async def evaluate_section(
        self,
        exam_id: str,
        answers: Dict[str, Any],
        time_elapsed_seconds: int
    ) -> OETSectionResult:
        """
        Evaluate a completed section

        Args:
            exam_id: OET exam ID
            answers: User's answers
            time_elapsed_seconds: Time taken

        Returns:
            OETSectionResult with scores and feedback
        """
        # Get exam from database
        exam = await self._get_exam(exam_id)
        if not exam:
            raise ValueError(f"Exam not found: {exam_id}")

        section = OETSection(exam.section)

        logger.info(
            "evaluating_oet_section",
            exam_id=exam_id,
            section=section.value,
            time_elapsed=time_elapsed_seconds
        )

        # Evaluate based on section type
        if section == OETSection.LISTENING:
            result = await self._evaluate_listening(exam, answers, time_elapsed_seconds)
        elif section == OETSection.READING:
            result = await self._evaluate_reading(exam, answers, time_elapsed_seconds)
        elif section == OETSection.WRITING:
            result = await self._evaluate_writing(exam, answers, time_elapsed_seconds)
        elif section == OETSection.SPEAKING:
            result = await self._evaluate_speaking(exam, answers, time_elapsed_seconds)
        else:
            raise ValueError(f"Invalid section: {section}")

        # Update exam record
        await self._update_exam_result(exam_id, result, answers)

        logger.info(
            "oet_section_evaluated",
            exam_id=exam_id,
            section=section.value,
            grade=result.grade.value,
            scaled_score=result.scaled_score
        )

        return result

    # =========================================================================
    # LISTENING EVALUATION
    # =========================================================================

    async def _evaluate_listening(
        self,
        exam: OETExam,
        answers: Dict[str, Any],
        time_elapsed: int
    ) -> OETSectionResult:
        """Evaluate Listening section"""
        content = exam.content
        config = OET_SCORING_CONFIG["listening"]

        total_correct = 0
        max_score = config["total_questions"]
        part_scores = {}

        # Evaluate Part A
        part_a_score = self._evaluate_listening_part_a(
            content["parts"]["part_a"],
            answers.get("part_a", {})
        )
        part_scores["part_a"] = part_a_score
        total_correct += part_a_score["correct"]

        # Evaluate Part B
        part_b_score = self._evaluate_listening_part_b(
            content["parts"]["part_b"],
            answers.get("part_b", {})
        )
        part_scores["part_b"] = part_b_score
        total_correct += part_b_score["correct"]

        # Evaluate Part C
        part_c_score = self._evaluate_listening_part_c(
            content["parts"]["part_c"],
            answers.get("part_c", {})
        )
        part_scores["part_c"] = part_c_score
        total_correct += part_c_score["correct"]

        # Calculate final scores
        scaled_score = raw_to_scaled_score(total_correct, max_score)
        grade = scaled_score_to_grade(scaled_score)

        return OETSectionResult(
            section=OETSection.LISTENING,
            raw_score=total_correct,
            max_score=max_score,
            scaled_score=scaled_score,
            grade=grade,
            part_scores=part_scores,
            time_taken_seconds=time_elapsed,
            time_limit_seconds=config["time_minutes"] * 60,
            feedback=self._generate_listening_feedback(part_scores, grade)
        )

    def _evaluate_listening_part_a(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part A - Note completion"""
        correct = 0
        total = 0
        details = []

        for consultation in part_content.get("consultations", []):
            for question in consultation.get("questions", []):
                total += 1
                q_id = question["id"]
                q_num = question["question_number"]
                correct_answer = question["correct_answer"]
                user_answer = answers.get(str(q_num), answers.get(q_id, ""))

                is_correct = self._check_gap_fill_answer(
                    user_answer,
                    correct_answer,
                    max_words=question.get("max_words", 3)
                )

                if is_correct:
                    correct += 1

                details.append({
                    "question_number": q_num,
                    "correct": is_correct,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer
                })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    def _evaluate_listening_part_b(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part B - Multiple choice"""
        correct = 0
        total = 0
        details = []

        for extract in part_content.get("extracts", []):
            question = extract.get("question", {})
            total += 1
            q_id = question["id"]
            q_num = question["question_number"]
            correct_answer = question["correct_answer"]
            user_answer = answers.get(str(q_num), answers.get(q_id, "")).upper()

            is_correct = user_answer == correct_answer.upper()

            if is_correct:
                correct += 1

            details.append({
                "question_number": q_num,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    def _evaluate_listening_part_c(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part C - Multiple choice"""
        correct = 0
        total = 0
        details = []

        for presentation in part_content.get("presentations", []):
            for question in presentation.get("questions", []):
                total += 1
                q_id = question["id"]
                q_num = question["question_number"]
                correct_answer = question["correct_answer"]
                user_answer = answers.get(str(q_num), answers.get(q_id, "")).upper()

                is_correct = user_answer == correct_answer.upper()

                if is_correct:
                    correct += 1

                details.append({
                    "question_number": q_num,
                    "correct": is_correct,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer
                })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    def _check_gap_fill_answer(
        self,
        user_answer: str,
        correct_answer: str,
        max_words: int = 3
    ) -> bool:
        """Check if gap fill answer is correct"""
        if not user_answer:
            return False

        # Normalize answers
        user_normalized = self._normalize_answer(user_answer)
        correct_normalized = self._normalize_answer(correct_answer)

        # Check word count
        word_count = len(user_normalized.split())
        if word_count > max_words:
            return False

        # Exact match
        if user_normalized == correct_normalized:
            return True

        # Similarity check (for minor spelling variations)
        similarity = SequenceMatcher(
            None, user_normalized, correct_normalized
        ).ratio()

        return similarity >= 0.85

    def _normalize_answer(self, answer: str) -> str:
        """Normalize answer for comparison"""
        # Lowercase
        answer = answer.lower()
        # Remove extra whitespace
        answer = " ".join(answer.split())
        # Remove punctuation except hyphens
        answer = re.sub(r'[^\w\s-]', '', answer)
        return answer.strip()

    # =========================================================================
    # READING EVALUATION
    # =========================================================================

    async def _evaluate_reading(
        self,
        exam: OETExam,
        answers: Dict[str, Any],
        time_elapsed: int
    ) -> OETSectionResult:
        """Evaluate Reading section"""
        content = exam.content
        config = OET_SCORING_CONFIG["reading"]

        total_correct = 0
        max_score = config["total_questions"]
        part_scores = {}

        # Evaluate Part A
        part_a_score = self._evaluate_reading_part_a(
            content["parts"]["part_a"],
            answers.get("part_a", {})
        )
        part_scores["part_a"] = part_a_score
        total_correct += part_a_score["correct"]

        # Evaluate Part B
        part_b_score = self._evaluate_reading_part_b(
            content["parts"]["part_b"],
            answers.get("part_b", {})
        )
        part_scores["part_b"] = part_b_score
        total_correct += part_b_score["correct"]

        # Evaluate Part C
        part_c_score = self._evaluate_reading_part_c(
            content["parts"]["part_c"],
            answers.get("part_c", {})
        )
        part_scores["part_c"] = part_c_score
        total_correct += part_c_score["correct"]

        scaled_score = raw_to_scaled_score(total_correct, max_score)
        grade = scaled_score_to_grade(scaled_score)

        return OETSectionResult(
            section=OETSection.READING,
            raw_score=total_correct,
            max_score=max_score,
            scaled_score=scaled_score,
            grade=grade,
            part_scores=part_scores,
            time_taken_seconds=time_elapsed,
            time_limit_seconds=config["time_minutes"] * 60,
            feedback=self._generate_reading_feedback(part_scores, grade)
        )

    def _evaluate_reading_part_a(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part A - Text matching"""
        correct = 0
        total = 0
        details = []

        for question in part_content.get("questions", []):
            total += 1
            q_id = question["id"]
            q_num = question["question_number"]
            correct_answer = question["correct_answer"]
            user_answer = answers.get(str(q_num), answers.get(q_id, "")).upper()

            is_correct = user_answer == correct_answer.upper()

            if is_correct:
                correct += 1

            details.append({
                "question_number": q_num,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    def _evaluate_reading_part_b(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part B - MCQ"""
        correct = 0
        total = 0
        details = []

        for item in part_content.get("items", []):
            question = item.get("question", {})
            total += 1
            q_id = question["id"]
            q_num = question["question_number"]
            correct_answer = question["correct_answer"]
            user_answer = answers.get(str(q_num), answers.get(q_id, "")).upper()

            is_correct = user_answer == correct_answer.upper()

            if is_correct:
                correct += 1

            details.append({
                "question_number": q_num,
                "correct": is_correct
            })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    def _evaluate_reading_part_c(
        self,
        part_content: Dict[str, Any],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Evaluate Part C - Long text MCQ"""
        correct = 0
        total = 0
        details = []

        for text in part_content.get("texts", []):
            for question in text.get("questions", []):
                total += 1
                q_id = question["id"]
                q_num = question["question_number"]
                correct_answer = question["correct_answer"]
                user_answer = answers.get(str(q_num), answers.get(q_id, "")).upper()

                is_correct = user_answer == correct_answer.upper()

                if is_correct:
                    correct += 1

                details.append({
                    "question_number": q_num,
                    "correct": is_correct
                })

        return {
            "correct": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0,
            "details": details
        }

    # =========================================================================
    # WRITING EVALUATION
    # =========================================================================

    async def _evaluate_writing(
        self,
        exam: OETExam,
        answers: Dict[str, Any],
        time_elapsed: int
    ) -> OETSectionResult:
        """Evaluate Writing section using AI"""
        content = exam.content
        config = OET_SCORING_CONFIG["writing"]

        letter_text = answers.get("letter", answers.get("response", ""))

        if not letter_text:
            return OETSectionResult(
                section=OETSection.WRITING,
                raw_score=0,
                max_score=42,  # Sum of all criteria max scores
                scaled_score=0,
                grade=OETGrade.E,
                criteria_scores={},
                time_taken_seconds=time_elapsed,
                time_limit_seconds=config["time_minutes"] * 60,
                feedback={"error": "No response provided"}
            )

        # AI evaluation
        if self.ai_client:
            criteria_scores, feedback = await self._ai_evaluate_writing(
                content["task"],
                letter_text
            )
        else:
            # Basic evaluation without AI
            criteria_scores, feedback = self._basic_evaluate_writing(
                content["task"],
                letter_text
            )

        # Calculate total score
        total_score = sum(criteria_scores.values())
        max_score = sum(c["max_score"] for c in config["criteria"].values())

        scaled_score = raw_to_scaled_score(total_score, max_score)
        grade = scaled_score_to_grade(scaled_score)

        return OETSectionResult(
            section=OETSection.WRITING,
            raw_score=total_score,
            max_score=max_score,
            scaled_score=scaled_score,
            grade=grade,
            criteria_scores=criteria_scores,
            time_taken_seconds=time_elapsed,
            time_limit_seconds=config["time_minutes"] * 60,
            feedback=feedback
        )

    async def _ai_evaluate_writing(
        self,
        task: Dict[str, Any],
        response: str
    ) -> Tuple[Dict[str, int], Dict[str, str]]:
        """Evaluate writing using AI"""
        prompt = f"""
You are an expert OET (Occupational English Test) Writing examiner.

TASK TYPE: {task['task_type']}
RECIPIENT: {task['recipient']}
CASE NOTES SUMMARY: Patient presenting with {task['case_notes']['presenting_complaint']}

CANDIDATE'S LETTER:
{response}

REQUIRED POINTS TO COVER:
{', '.join(task['required_points'])}

Evaluate the letter according to OET Writing criteria. For each criterion, provide:
1. A score from 0-7
2. Brief feedback

CRITERIA:
1. PURPOSE (0-7): Does the letter clearly state its purpose? Is the register appropriate?
2. CONTENT (0-7): Has relevant information been selected from the case notes? Is all necessary information included?
3. CONCISENESS & CLARITY (0-7): Is the letter free of unnecessary information? Is it clear and easy to follow?
4. GENRE & STYLE (0-7): Does it follow appropriate letter conventions? Is the tone professional?
5. ORGANISATION (0-7): Is there a logical structure? Are paragraphs well organized?
6. LANGUAGE (0-7): Is grammar accurate? Is medical vocabulary used appropriately?

Respond in JSON format:
{{
    "scores": {{
        "purpose": <0-7>,
        "content": <0-7>,
        "conciseness_clarity": <0-7>,
        "genre_style": <0-7>,
        "organization": <0-7>,
        "language": <0-7>
    }},
    "feedback": {{
        "purpose": "<feedback>",
        "content": "<feedback>",
        "conciseness_clarity": "<feedback>",
        "genre_style": "<feedback>",
        "organization": "<feedback>",
        "language": "<feedback>",
        "overall": "<overall feedback and suggestions>"
    }}
}}
        """

        response_text = await self._call_ai(prompt)

        try:
            import json
            result = json.loads(response_text)
            return result["scores"], result["feedback"]
        except Exception as e:
            logger.error("Failed to parse AI writing evaluation", error=str(e))
            return self._basic_evaluate_writing(task, response)

    def _basic_evaluate_writing(
        self,
        task: Dict[str, Any],
        response: str
    ) -> Tuple[Dict[str, int], Dict[str, str]]:
        """Basic writing evaluation without AI"""
        word_count = len(response.split())
        word_limit = task.get("word_limit", {"min": 180, "max": 200})

        scores = {}
        feedback = {}

        # Basic checks
        has_salutation = any(
            greeting in response.lower()
            for greeting in ["dear dr", "dear doctor", "dear mr", "dear ms"]
        )
        has_closing = any(
            closing in response.lower()
            for closing in ["yours sincerely", "yours faithfully", "kind regards"]
        )

        # Score each criterion based on basic heuristics
        scores["purpose"] = 4 if len(response) > 50 else 2
        feedback["purpose"] = "Consider ensuring the purpose is stated clearly in the opening."

        scores["content"] = 4 if word_count >= 100 else 2
        feedback["content"] = f"Word count: {word_count}. Ensure all required points are covered."

        if word_limit["min"] <= word_count <= word_limit["max"]:
            scores["conciseness_clarity"] = 5
            feedback["conciseness_clarity"] = "Word count is within the recommended range."
        elif word_count < word_limit["min"]:
            scores["conciseness_clarity"] = 3
            feedback["conciseness_clarity"] = f"Response is too short ({word_count} words). Aim for {word_limit['min']}-{word_limit['max']} words."
        else:
            scores["conciseness_clarity"] = 3
            feedback["conciseness_clarity"] = f"Response exceeds word limit ({word_count} words)."

        scores["genre_style"] = 5 if has_salutation and has_closing else 3
        feedback["genre_style"] = "Ensure proper letter format with salutation and closing."

        scores["organization"] = 4
        feedback["organization"] = "Consider organizing content into clear paragraphs."

        scores["language"] = 4
        feedback["language"] = "Review for grammar and appropriate medical terminology."

        feedback["overall"] = "This is a basic automated evaluation. For detailed feedback, AI-assisted evaluation is recommended."

        return scores, feedback

    # =========================================================================
    # SPEAKING EVALUATION
    # =========================================================================

    async def _evaluate_speaking(
        self,
        exam: OETExam,
        answers: Dict[str, Any],
        time_elapsed: int
    ) -> OETSectionResult:
        """Evaluate Speaking section"""
        content = exam.content
        config = OET_SCORING_CONFIG["speaking"]

        # Speaking evaluation requires audio/transcript
        # This would typically be done by a human examiner or AI with audio processing

        role_play_scores = []

        for rp in content.get("role_plays", []):
            rp_num = rp["role_play_number"]
            rp_answers = answers.get(f"role_play_{rp_num}", {})

            if self.ai_client and rp_answers.get("transcript"):
                scores, feedback = await self._ai_evaluate_speaking(
                    rp, rp_answers["transcript"]
                )
            else:
                # Placeholder scores for manual evaluation
                scores = {
                    "intelligibility": 4,
                    "fluency": 4,
                    "appropriateness": 4,
                    "resources": 4,
                    "relationship_building": 4,
                    "understanding": 4,
                    "information_gathering_giving": 4,
                    "providing_structure": 4
                }
                feedback = {"note": "Awaiting examiner evaluation"}

            role_play_scores.append({
                "role_play_number": rp_num,
                "scores": scores,
                "feedback": feedback
            })

        # Calculate overall speaking score
        all_scores = []
        for rp_score in role_play_scores:
            all_scores.extend(rp_score["scores"].values())

        if all_scores:
            total_score = sum(all_scores)
            max_score = len(all_scores) * 6  # Max 6 per criterion
        else:
            total_score = 0
            max_score = 48  # 8 criteria * 6 max

        scaled_score = raw_to_scaled_score(total_score, max_score)
        grade = scaled_score_to_grade(scaled_score)

        total_time = (
            config["preparation_time_minutes"] + config["role_play_time_minutes"]
        ) * 2 * 60

        return OETSectionResult(
            section=OETSection.SPEAKING,
            raw_score=total_score,
            max_score=max_score,
            scaled_score=scaled_score,
            grade=grade,
            criteria_scores={"role_plays": role_play_scores},
            time_taken_seconds=time_elapsed,
            time_limit_seconds=total_time,
            feedback=self._generate_speaking_feedback(role_play_scores, grade)
        )

    async def _ai_evaluate_speaking(
        self,
        role_play: Dict[str, Any],
        transcript: str
    ) -> Tuple[Dict[str, int], Dict[str, str]]:
        """Evaluate speaking using AI with transcript"""
        prompt = f"""
You are an expert OET Speaking examiner.

SCENARIO: {role_play['title']}
SETTING: {role_play['setting']}
CANDIDATE TASKS: {', '.join(role_play['candidate_card']['tasks'])}

CANDIDATE'S TRANSCRIPT:
{transcript}

Evaluate according to OET Speaking criteria. For each criterion, provide a score (0-6) and feedback.

LINGUISTIC CRITERIA:
1. Intelligibility (0-6): Pronunciation, stress, intonation
2. Fluency (0-6): Pace, hesitation, flow
3. Appropriateness (0-6): Register, professional language
4. Resources (0-6): Vocabulary range, grammatical accuracy

CLINICAL COMMUNICATION CRITERIA:
5. Relationship building (0-6): Empathy, active listening
6. Understanding patient needs (0-6): Checking understanding, clarification
7. Information gathering/giving (0-6): Systematic approach, clear explanations
8. Providing structure (0-6): Organization of consultation

Respond in JSON format:
{{
    "scores": {{
        "intelligibility": <0-6>,
        "fluency": <0-6>,
        "appropriateness": <0-6>,
        "resources": <0-6>,
        "relationship_building": <0-6>,
        "understanding": <0-6>,
        "information_gathering_giving": <0-6>,
        "providing_structure": <0-6>
    }},
    "feedback": {{
        "linguistic": "<feedback on language skills>",
        "clinical_communication": "<feedback on clinical communication>",
        "overall": "<overall feedback>"
    }}
}}
        """

        response = await self._call_ai(prompt)

        try:
            import json
            result = json.loads(response)
            return result["scores"], result["feedback"]
        except Exception:
            return {
                "intelligibility": 4, "fluency": 4, "appropriateness": 4, "resources": 4,
                "relationship_building": 4, "understanding": 4,
                "information_gathering_giving": 4, "providing_structure": 4
            }, {"error": "Failed to parse AI evaluation"}

    # =========================================================================
    # FEEDBACK GENERATION
    # =========================================================================

    def _generate_listening_feedback(
        self,
        part_scores: Dict[str, Any],
        grade: OETGrade
    ) -> Dict[str, str]:
        """Generate feedback for Listening section"""
        feedback = {
            "grade_description": get_grade_description(grade)["description"]
        }

        # Part-specific feedback
        for part, scores in part_scores.items():
            percentage = scores["percentage"]
            if percentage >= 80:
                feedback[part] = "Excellent performance. You demonstrated strong listening comprehension."
            elif percentage >= 60:
                feedback[part] = "Good performance. Continue practicing to improve accuracy."
            elif percentage >= 40:
                feedback[part] = "Satisfactory performance. Focus on note-taking strategies and medical vocabulary."
            else:
                feedback[part] = "Needs improvement. Practice listening to medical consultations and presentations regularly."

        return feedback

    def _generate_reading_feedback(
        self,
        part_scores: Dict[str, Any],
        grade: OETGrade
    ) -> Dict[str, str]:
        """Generate feedback for Reading section"""
        feedback = {
            "grade_description": get_grade_description(grade)["description"]
        }

        for part, scores in part_scores.items():
            percentage = scores["percentage"]
            if part == "part_a":
                if percentage >= 80:
                    feedback[part] = "Excellent scanning and skimming skills."
                else:
                    feedback[part] = "Practice expeditious reading techniques for locating specific information quickly."
            elif part == "part_b":
                if percentage >= 80:
                    feedback[part] = "Good understanding of short workplace texts."
                else:
                    feedback[part] = "Focus on understanding the main message in short professional communications."
            else:  # part_c
                if percentage >= 80:
                    feedback[part] = "Strong comprehension of complex medical texts."
                else:
                    feedback[part] = "Practice reading longer medical articles and identifying main ideas, details, and author's purpose."

        return feedback

    def _generate_speaking_feedback(
        self,
        role_play_scores: List[Dict],
        grade: OETGrade
    ) -> Dict[str, str]:
        """Generate feedback for Speaking section"""
        feedback = {
            "grade_description": get_grade_description(grade)["description"],
            "general": "Speaking performance is evaluated on both linguistic and clinical communication criteria."
        }

        for rp in role_play_scores:
            rp_num = rp["role_play_number"]
            scores = rp["scores"]

            # Calculate averages
            linguistic_avg = sum([
                scores.get("intelligibility", 0),
                scores.get("fluency", 0),
                scores.get("appropriateness", 0),
                scores.get("resources", 0)
            ]) / 4

            clinical_avg = sum([
                scores.get("relationship_building", 0),
                scores.get("understanding", 0),
                scores.get("information_gathering_giving", 0),
                scores.get("providing_structure", 0)
            ]) / 4

            feedback[f"role_play_{rp_num}"] = {
                "linguistic": f"Linguistic skills: {linguistic_avg:.1f}/6",
                "clinical": f"Clinical communication: {clinical_avg:.1f}/6"
            }

        return feedback

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _get_exam(self, exam_id: str) -> Optional[OETExam]:
        """Get exam from database"""
        result = await self.session.execute(
            select(OETExam).where(OETExam.id == exam_id)
        )
        return result.scalar_one_or_none()

    async def _update_exam_result(
        self,
        exam_id: str,
        result: OETSectionResult,
        answers: Dict[str, Any]
    ) -> None:
        """Update exam record with results"""
        await self.session.execute(
            update(OETExam)
            .where(OETExam.id == exam_id)
            .values(
                answers=answers,
                raw_score=result.raw_score,
                max_score=result.max_score,
                scaled_score=result.scaled_score,
                grade=result.grade.value,
                detailed_results={
                    "part_scores": result.part_scores,
                    "criteria_scores": result.criteria_scores
                },
                feedback=result.feedback,
                completed_at=datetime.now(timezone.utc),
                status="completed"
            )
        )
        await self.session.commit()

    async def _call_ai(self, prompt: str) -> str:
        """Call AI API"""
        if not self.ai_client:
            raise ValueError("AI client not configured")

        message = await self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    # =========================================================================
    # RESULT SUMMARY
    # =========================================================================

    async def get_complete_results(
        self,
        user_id: str,
        exam_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get complete results for all sections"""
        query = select(OETExam).where(
            OETExam.user_id == user_id,
            OETExam.status == "completed"
        )

        if exam_session_id:
            query = query.where(OETExam.mock_exam_section_id == exam_session_id)

        result = await self.session.execute(query)
        exams = list(result.scalars().all())

        section_results = {}
        for exam in exams:
            section_results[exam.section] = {
                "raw_score": exam.raw_score,
                "max_score": exam.max_score,
                "scaled_score": exam.scaled_score,
                "grade": exam.grade,
                "feedback": exam.feedback,
                "time_taken": exam.time_elapsed_seconds
            }

        # Calculate overall grade
        if section_results:
            avg_scaled = sum(
                r["scaled_score"] for r in section_results.values()
            ) / len(section_results)
            overall_grade = scaled_score_to_grade(int(avg_scaled))
        else:
            overall_grade = None

        return {
            "user_id": user_id,
            "sections": section_results,
            "overall_grade": overall_grade.value if overall_grade else None,
            "overall_description": get_grade_description(overall_grade) if overall_grade else None
        }
