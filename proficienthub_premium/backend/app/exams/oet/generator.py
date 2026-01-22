"""
ProficientHub - OET Exam Generator
Complete exam generation service for OET (Occupational English Test)
"""

import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from uuid import uuid4
import structlog
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.exams.oet.models import (
    OETProfession, OETSection, OETGrade, ListeningPart, ReadingPart,
    QuestionType, WritingTaskType, SpeakingScenarioType,
    OETListeningQuestion, OETReadingQuestion, ReadingPassage,
    OETWritingTask, OETSpeakingRolePlay, PatientCaseNotes,
    OETExamSession, OETSectionResult, OETExam, OETContentItem,
    OET_SCORING_CONFIG, raw_to_scaled_score, scaled_score_to_grade
)
from app.exams.oet.content_bank import OETContentBank

logger = structlog.get_logger(__name__)


class OETExamGenerator:
    """
    Generator for OET exam content
    Supports both template-based and AI-generated content
    """

    def __init__(
        self,
        session: AsyncSession,
        ai_client: Optional[Any] = None  # Anthropic/OpenAI client
    ):
        self.session = session
        self.ai_client = ai_client
        self.content_bank = OETContentBank()

    # =========================================================================
    # MAIN GENERATION METHODS
    # =========================================================================

    async def generate_complete_exam(
        self,
        user_id: str,
        profession: OETProfession,
        sections: Optional[List[OETSection]] = None
    ) -> OETExamSession:
        """
        Generate a complete OET exam with all sections

        Args:
            user_id: User ID
            profession: OET profession (medicine, nursing, etc.)
            sections: Specific sections to generate (default: all)

        Returns:
            Complete OETExamSession with all content
        """
        if sections is None:
            sections = [OETSection.LISTENING, OETSection.READING,
                       OETSection.WRITING, OETSection.SPEAKING]

        exam_session = OETExamSession(
            id=str(uuid4()),
            user_id=user_id,
            profession=profession
        )

        logger.info(
            "generating_oet_exam",
            user_id=user_id,
            profession=profession.value,
            sections=[s.value for s in sections]
        )

        # Generate each section
        tasks = []
        for section in sections:
            if section == OETSection.LISTENING:
                tasks.append(self._generate_listening_section(profession))
            elif section == OETSection.READING:
                tasks.append(self._generate_reading_section(profession))
            elif section == OETSection.WRITING:
                tasks.append(self._generate_writing_section(profession))
            elif section == OETSection.SPEAKING:
                tasks.append(self._generate_speaking_section(profession))

        # Run generation in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, section in enumerate(sections):
            if isinstance(results[i], Exception):
                logger.error(f"Failed to generate {section.value}", error=str(results[i]))
                continue

            if section == OETSection.LISTENING:
                exam_session.listening = results[i]
            elif section == OETSection.READING:
                exam_session.reading = results[i]
            elif section == OETSection.WRITING:
                exam_session.writing = results[i]
            elif section == OETSection.SPEAKING:
                exam_session.speaking = results[i]

        exam_session.status = "created"

        # Persist to database
        await self._persist_exam_session(exam_session)

        logger.info(
            "oet_exam_generated",
            exam_id=exam_session.id,
            user_id=user_id
        )

        return exam_session

    async def generate_section(
        self,
        user_id: str,
        profession: OETProfession,
        section: OETSection
    ) -> Dict[str, Any]:
        """Generate a single OET section"""
        if section == OETSection.LISTENING:
            return await self._generate_listening_section(profession)
        elif section == OETSection.READING:
            return await self._generate_reading_section(profession)
        elif section == OETSection.WRITING:
            return await self._generate_writing_section(profession)
        elif section == OETSection.SPEAKING:
            return await self._generate_speaking_section(profession)
        else:
            raise ValueError(f"Invalid section: {section}")

    # =========================================================================
    # LISTENING SECTION GENERATION
    # =========================================================================

    async def _generate_listening_section(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """Generate complete Listening section (Parts A, B, C)"""
        listening_content = {
            "section": OETSection.LISTENING.value,
            "time_limit_minutes": OET_SCORING_CONFIG["listening"]["time_minutes"],
            "total_questions": OET_SCORING_CONFIG["listening"]["total_questions"],
            "parts": {}
        }

        # Part A - Consultation extracts (24 questions)
        part_a = await self._generate_listening_part_a(profession)
        listening_content["parts"]["part_a"] = part_a

        # Part B - Workplace extracts (6 questions)
        part_b = await self._generate_listening_part_b(profession)
        listening_content["parts"]["part_b"] = part_b

        # Part C - Presentation extracts (12 questions)
        part_c = await self._generate_listening_part_c(profession)
        listening_content["parts"]["part_c"] = part_c

        return listening_content

    async def _generate_listening_part_a(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part A - Two consultation extracts with note completion
        24 questions total (12 per consultation)
        """
        consultations = []

        # Generate 2 consultations
        scenarios = random.sample(
            self.content_bank.LISTENING_PART_A_TEMPLATE["example_scenarios"],
            min(2, len(self.content_bank.LISTENING_PART_A_TEMPLATE["example_scenarios"]))
        )

        for i, scenario in enumerate(scenarios):
            consultation = await self._generate_consultation_content(
                profession=profession,
                scenario=scenario,
                question_count=12,
                consultation_number=i + 1
            )
            consultations.append(consultation)

        return {
            "part": ListeningPart.PART_A.value,
            "instructions": self.content_bank.LISTENING_PART_A_TEMPLATE["instructions"],
            "question_count": 24,
            "consultations": consultations
        }

    async def _generate_consultation_content(
        self,
        profession: OETProfession,
        scenario: Dict[str, Any],
        question_count: int,
        consultation_number: int
    ) -> Dict[str, Any]:
        """Generate a single consultation with questions"""
        # Try AI generation first
        if self.ai_client:
            try:
                return await self._ai_generate_consultation(
                    profession, scenario, question_count
                )
            except Exception as e:
                logger.warning("AI generation failed, using template", error=str(e))

        # Fallback to template-based generation
        return self._template_generate_consultation(
            profession, scenario, question_count, consultation_number
        )

    def _template_generate_consultation(
        self,
        profession: OETProfession,
        scenario: Dict[str, Any],
        question_count: int,
        consultation_number: int
    ) -> Dict[str, Any]:
        """Template-based consultation generation"""
        # Get question stems
        question_stems = self.content_bank.LISTENING_PART_A_TEMPLATE["question_stems"]

        questions = []
        for i in range(question_count):
            q_num = (consultation_number - 1) * question_count + i + 1
            stem = question_stems[i % len(question_stems)]

            questions.append({
                "id": str(uuid4()),
                "question_number": q_num,
                "question_type": QuestionType.NOTE_COMPLETION.value,
                "question_text": stem,
                "max_words": 3,
                "correct_answer": "[ANSWER_PLACEHOLDER]",
                "points": 1
            })

        return {
            "consultation_number": consultation_number,
            "title": scenario["title"],
            "speakers": scenario["speakers"],
            "medical_context": scenario["medical_context"],
            "audio": {
                "id": str(uuid4()),
                "url": f"/audio/oet/listening/part_a/consultation_{consultation_number}.mp3",
                "duration_seconds": 300,  # 5 minutes
                "transcript": "[TRANSCRIPT_PLACEHOLDER]"
            },
            "questions": questions
        }

    async def _generate_listening_part_b(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part B - Six workplace extracts with MCQ
        6 questions total
        """
        extracts = []
        scenarios = self.content_bank.LISTENING_PART_B_TEMPLATE["example_scenarios"]

        for i, scenario in enumerate(scenarios[:6]):
            extract = {
                "extract_number": i + 1,
                "title": scenario["title"],
                "context": scenario["context"],
                "audio": {
                    "id": str(uuid4()),
                    "url": f"/audio/oet/listening/part_b/extract_{i+1}.mp3",
                    "duration_seconds": 45,
                    "transcript": "[TRANSCRIPT_PLACEHOLDER]"
                },
                "question": {
                    "id": str(uuid4()),
                    "question_number": 25 + i,
                    "question_type": QuestionType.MULTIPLE_CHOICE.value,
                    "question_text": f"What is the {scenario['question_focus']}?",
                    "options": ["Option A", "Option B", "Option C"],
                    "correct_answer": "A",
                    "points": 1
                }
            }
            extracts.append(extract)

        return {
            "part": ListeningPart.PART_B.value,
            "instructions": self.content_bank.LISTENING_PART_B_TEMPLATE["instructions"],
            "question_count": 6,
            "extracts": extracts
        }

    async def _generate_listening_part_c(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part C - Two presentations with MCQ
        12 questions total (6 per presentation)
        """
        presentations = []
        topics = random.sample(
            self.content_bank.LISTENING_PART_C_TEMPLATE["example_topics"],
            2
        )

        for i, topic in enumerate(topics):
            questions = []
            for j in range(6):
                q_num = 31 + (i * 6) + j
                questions.append({
                    "id": str(uuid4()),
                    "question_number": q_num,
                    "question_type": QuestionType.MULTIPLE_CHOICE.value,
                    "question_text": f"Question {q_num} about {topic}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": random.choice(["A", "B", "C", "D"]),
                    "points": 1
                })

            presentation = {
                "presentation_number": i + 1,
                "topic": topic,
                "audio": {
                    "id": str(uuid4()),
                    "url": f"/audio/oet/listening/part_c/presentation_{i+1}.mp3",
                    "duration_seconds": 300,
                    "transcript": "[TRANSCRIPT_PLACEHOLDER]"
                },
                "questions": questions
            }
            presentations.append(presentation)

        return {
            "part": ListeningPart.PART_C.value,
            "instructions": self.content_bank.LISTENING_PART_C_TEMPLATE["instructions"],
            "question_count": 12,
            "presentations": presentations
        }

    # =========================================================================
    # READING SECTION GENERATION
    # =========================================================================

    async def _generate_reading_section(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """Generate complete Reading section (Parts A, B, C)"""
        reading_content = {
            "section": OETSection.READING.value,
            "time_limit_minutes": OET_SCORING_CONFIG["reading"]["time_minutes"],
            "total_questions": OET_SCORING_CONFIG["reading"]["total_questions"],
            "parts": {}
        }

        # Part A - Expeditious reading (20 questions)
        part_a = await self._generate_reading_part_a(profession)
        reading_content["parts"]["part_a"] = part_a

        # Part B - Short texts (6 questions)
        part_b = await self._generate_reading_part_b(profession)
        reading_content["parts"]["part_b"] = part_b

        # Part C - Long texts (16 questions)
        part_c = await self._generate_reading_part_c(profession)
        reading_content["parts"]["part_c"] = part_c

        return reading_content

    async def _generate_reading_part_a(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part A - Four short texts with 20 questions
        Questions ask which text contains specific information
        """
        text_types = self.content_bank.READING_PART_A_TEMPLATE["text_types"]
        selected_types = random.sample(text_types, 4)

        texts = []
        for i, text_type in enumerate(selected_types):
            text = {
                "id": str(uuid4()),
                "label": chr(65 + i),  # A, B, C, D
                "type": text_type,
                "title": f"Text {chr(65 + i)}: {text_type}",
                "content": f"[CONTENT_PLACEHOLDER for {text_type}]",
                "word_count": 175
            }
            texts.append(text)

        # Generate 20 questions
        questions = []
        question_formats = self.content_bank.READING_PART_A_TEMPLATE["question_formats"]
        for i in range(20):
            questions.append({
                "id": str(uuid4()),
                "question_number": i + 1,
                "question_type": QuestionType.MATCHING.value,
                "question_text": random.choice(question_formats).replace(
                    "[specific information]", f"[INFO_{i+1}]"
                ).replace("[condition/treatment]", f"[TOPIC_{i+1}]").replace(
                    "[topic]", f"[SUBJECT_{i+1}]"
                ).replace("[statement]", f"[STATEMENT_{i+1}]"),
                "options": ["A", "B", "C", "D"],
                "correct_answer": random.choice(["A", "B", "C", "D"]),
                "points": 1
            })

        return {
            "part": ReadingPart.PART_A.value,
            "instructions": self.content_bank.READING_PART_A_TEMPLATE["instructions"],
            "question_count": 20,
            "texts": texts,
            "questions": questions
        }

    async def _generate_reading_part_b(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part B - Six short texts with MCQ
        """
        text_types = self.content_bank.READING_PART_B_TEMPLATE["text_types"]

        items = []
        for i in range(6):
            text_type = text_types[i % len(text_types)]
            item = {
                "id": str(uuid4()),
                "text_number": i + 1,
                "type": text_type,
                "content": f"[CONTENT_PLACEHOLDER for {text_type}]",
                "word_count": 125,
                "question": {
                    "id": str(uuid4()),
                    "question_number": 21 + i,
                    "question_type": QuestionType.MULTIPLE_CHOICE.value,
                    "question_text": f"What is the main purpose of this {text_type}?",
                    "options": [
                        "Option A - [PLACEHOLDER]",
                        "Option B - [PLACEHOLDER]",
                        "Option C - [PLACEHOLDER]",
                        "Option D - [PLACEHOLDER]"
                    ],
                    "correct_answer": "A",
                    "points": 1
                }
            }
            items.append(item)

        return {
            "part": ReadingPart.PART_B.value,
            "instructions": self.content_bank.READING_PART_B_TEMPLATE["instructions"],
            "question_count": 6,
            "items": items
        }

    async def _generate_reading_part_c(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate Part C - Two long texts with 8 questions each
        """
        texts = []
        question_types = self.content_bank.READING_PART_C_TEMPLATE["question_types"]

        for i in range(2):
            # Generate paragraphs A-G
            paragraphs = {}
            for j in range(7):
                para_label = chr(65 + j)  # A-G
                paragraphs[para_label] = f"[PARAGRAPH_{para_label}_CONTENT]"

            # Generate 8 questions per text
            questions = []
            for j in range(8):
                q_num = 27 + (i * 8) + j
                q_type = question_types[j % len(question_types)]
                questions.append({
                    "id": str(uuid4()),
                    "question_number": q_num,
                    "question_type": QuestionType.MULTIPLE_CHOICE.value,
                    "question_text": f"({q_type}) [QUESTION_PLACEHOLDER]",
                    "paragraph_reference": random.choice(list(paragraphs.keys())),
                    "options": [
                        "Option A", "Option B", "Option C", "Option D"
                    ],
                    "correct_answer": random.choice(["A", "B", "C", "D"]),
                    "points": 1
                })

            text = {
                "id": str(uuid4()),
                "text_number": i + 1,
                "title": f"[TEXT_{i+1}_TITLE]",
                "paragraphs": paragraphs,
                "word_count": 700,
                "questions": questions
            }
            texts.append(text)

        return {
            "part": ReadingPart.PART_C.value,
            "instructions": self.content_bank.READING_PART_C_TEMPLATE["instructions"],
            "question_count": 16,
            "texts": texts
        }

    # =========================================================================
    # WRITING SECTION GENERATION
    # =========================================================================

    async def _generate_writing_section(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """Generate Writing section - Referral/Discharge letter"""
        config = OET_SCORING_CONFIG["writing"]

        # Get template for profession
        task_type = random.choice([
            WritingTaskType.REFERRAL_LETTER,
            WritingTaskType.DISCHARGE_LETTER
        ])
        template = self.content_bank.get_writing_template(profession, task_type)

        # Generate or use template case notes
        case_notes = template["template"]

        # Randomize patient details
        patient_name = self._generate_patient_name()
        date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

        writing_content = {
            "section": OETSection.WRITING.value,
            "time_limit_minutes": config["time_minutes"],
            "word_limit": config["word_limit"],
            "task": {
                "id": str(uuid4()),
                "task_type": task_type.value,
                "profession": profession.value,
                "instructions": self._get_writing_instructions(task_type),
                "recipient": template["recipient"],
                "recipient_institution": template["recipient_institution"],
                "case_notes": {
                    "patient_name": patient_name,
                    "age": case_notes.age,
                    "gender": case_notes.gender,
                    "date": date_str,
                    "presenting_complaint": case_notes.presenting_complaint,
                    "history_of_present_illness": case_notes.history_of_present_illness,
                    "past_medical_history": case_notes.past_medical_history,
                    "medications": case_notes.medications,
                    "allergies": case_notes.allergies,
                    "social_history": case_notes.social_history,
                    "family_history": case_notes.family_history,
                    "examination_findings": case_notes.examination_findings,
                    "vital_signs": case_notes.vital_signs,
                    "investigations": case_notes.investigations,
                    "diagnosis": case_notes.diagnosis,
                    "treatment_plan": case_notes.treatment_plan,
                    "discharge_medications": case_notes.discharge_medications,
                    "follow_up_instructions": case_notes.follow_up_instructions,
                    "referral_reason": case_notes.referral_reason
                },
                "required_points": template["required_points"],
                "evaluation_criteria": config["criteria"]
            }
        }

        return writing_content

    def _get_writing_instructions(self, task_type: WritingTaskType) -> str:
        """Get instructions for writing task type"""
        instructions = {
            WritingTaskType.REFERRAL_LETTER: """
Read the case notes and complete the writing task which follows.

You are writing to a specialist to refer your patient for further assessment and management.

Using the information in the case notes, write a letter of referral to the specialist.
In your answer:
• Expand the relevant notes into complete sentences
• Do not use note form
• Use letter format

The body of the letter should be approximately 180-200 words.
            """.strip(),
            WritingTaskType.DISCHARGE_LETTER: """
Read the case notes and complete the writing task which follows.

You are writing to the patient's GP following their discharge from hospital.

Using the information in the case notes, write a letter to the GP.
In your answer:
• Expand the relevant notes into complete sentences
• Do not use note form
• Use letter format

The body of the letter should be approximately 180-200 words.
            """.strip()
        }
        return instructions.get(task_type, instructions[WritingTaskType.REFERRAL_LETTER])

    # =========================================================================
    # SPEAKING SECTION GENERATION
    # =========================================================================

    async def _generate_speaking_section(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """Generate Speaking section - Two role-plays"""
        config = OET_SCORING_CONFIG["speaking"]

        # Select two different scenario types
        scenario_types = list(SpeakingScenarioType)
        selected_types = random.sample(scenario_types, 2)

        role_plays = []
        for i, scenario_type in enumerate(selected_types):
            scenario = self.content_bank.get_speaking_scenario(profession, scenario_type)

            role_play = {
                "id": str(uuid4()),
                "role_play_number": i + 1,
                "scenario_type": scenario_type.value,
                "title": scenario["title"],
                "setting": scenario["setting"],
                "preparation_time_minutes": config["preparation_time_minutes"],
                "role_play_time_minutes": config["role_play_time_minutes"],
                "candidate_card": {
                    "role": scenario["candidate_card"].role,
                    "setting": scenario["candidate_card"].setting,
                    "context": scenario["candidate_card"].context,
                    "tasks": scenario["candidate_card"].tasks
                },
                "interlocutor_card": {
                    "role": scenario["interlocutor_card"].role,
                    "context": scenario["interlocutor_card"].context,
                    "emotional_state": scenario["interlocutor_card"].emotional_state,
                    "concerns": scenario["interlocutor_card"].concerns,
                    "information_to_provide": scenario["interlocutor_card"].information_to_provide
                },
                "interlocutor_prompts": scenario["interlocutor_prompts"],
                "evaluation_criteria": config["criteria"]
            }
            role_plays.append(role_play)

        speaking_content = {
            "section": OETSection.SPEAKING.value,
            "total_time_minutes": (
                config["preparation_time_minutes"] + config["role_play_time_minutes"]
            ) * 2,
            "role_plays": role_plays
        }

        return speaking_content

    # =========================================================================
    # AI GENERATION METHODS
    # =========================================================================

    async def _ai_generate_consultation(
        self,
        profession: OETProfession,
        scenario: Dict[str, Any],
        question_count: int
    ) -> Dict[str, Any]:
        """Generate consultation content using AI"""
        if not self.ai_client:
            raise ValueError("AI client not configured")

        prompt = self.content_bank.get_ai_prompt(
            "listening_consultation",
            profession=profession.value,
            scenario=scenario["title"],
            speakers=", ".join(scenario["speakers"])
        )

        # Call AI API
        response = await self._call_ai_api(prompt)

        # Parse response
        return self._parse_ai_consultation_response(response, scenario, question_count)

    async def _call_ai_api(self, prompt: str) -> str:
        """Call AI API (Anthropic Claude)"""
        if not self.ai_client:
            raise ValueError("AI client not configured")

        # For Anthropic Claude
        message = await self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def _parse_ai_consultation_response(
        self,
        response: str,
        scenario: Dict[str, Any],
        question_count: int
    ) -> Dict[str, Any]:
        """Parse AI response for consultation content"""
        # This would parse the AI's structured response
        # For now, return template structure
        return self._template_generate_consultation(
            OETProfession.MEDICINE, scenario, question_count, 1
        )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _generate_patient_name(self) -> str:
        """Generate a random patient name"""
        first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
            "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    async def _persist_exam_session(self, exam_session: OETExamSession) -> None:
        """Persist exam session to database"""
        for section_name in ["listening", "reading", "writing", "speaking"]:
            section_content = getattr(exam_session, section_name)
            if section_content:
                section_enum = OETSection(section_name)

                # Get time limit
                time_limit = OET_SCORING_CONFIG.get(
                    section_name, {}
                ).get("time_minutes", 60) * 60

                oet_exam = OETExam(
                    id=str(uuid4()),
                    user_id=exam_session.user_id,
                    profession=exam_session.profession.value,
                    section=section_enum.value,
                    content=section_content,
                    time_limit_seconds=time_limit,
                    status="created"
                )

                self.session.add(oet_exam)

        await self.session.commit()

    async def get_exam_by_id(self, exam_id: str) -> Optional[OETExam]:
        """Retrieve an exam by ID"""
        result = await self.session.execute(
            select(OETExam).where(OETExam.id == exam_id)
        )
        return result.scalar_one_or_none()

    async def get_user_exams(
        self,
        user_id: str,
        section: Optional[OETSection] = None,
        status: Optional[str] = None
    ) -> List[OETExam]:
        """Get all exams for a user"""
        query = select(OETExam).where(OETExam.user_id == user_id)

        if section:
            query = query.where(OETExam.section == section.value)
        if status:
            query = query.where(OETExam.status == status)

        query = query.order_by(OETExam.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())
