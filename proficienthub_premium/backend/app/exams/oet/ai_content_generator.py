"""
ProficientHub - OET AI Content Generator
High-quality AI-powered content generation for OET exams
Uses Claude for generating authentic medical scenarios and content
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
import asyncio

from app.exams.oet.models import (
    OETProfession, OETSection, ListeningPart, ReadingPart,
    QuestionType, WritingTaskType, SpeakingScenarioType
)
from app.exams.oet.content_bank import OETContentBank

logger = structlog.get_logger(__name__)


class OETAIContentGenerator:
    """
    AI-powered content generator for OET exams
    Produces high-quality, authentic medical content
    """

    def __init__(self, ai_client: Any):
        """
        Initialize with AI client (Anthropic Claude)

        Args:
            ai_client: Anthropic client instance
        """
        self.ai_client = ai_client
        self.content_bank = OETContentBank()
        self.model = "claude-sonnet-4-20250514"

    # =========================================================================
    # LISTENING CONTENT GENERATION
    # =========================================================================

    async def generate_listening_consultation(
        self,
        profession: OETProfession,
        scenario_type: str,
        consultation_number: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a complete consultation for Listening Part A

        Returns:
            Complete consultation with transcript, audio markers, and questions
        """
        prompt = f"""
You are an expert in creating OET (Occupational English Test) Listening content.

Generate a realistic medical consultation transcript for OET Listening Part A.

PROFESSION: {profession.value}
SCENARIO TYPE: {scenario_type}
CONSULTATION NUMBER: {consultation_number}

Requirements:
1. Two speakers: Healthcare professional (Doctor/Nurse) and Patient
2. Duration: 4-5 minutes when read at natural pace (approximately 600-800 words)
3. Include realistic medical terminology appropriate to {profession.value}
4. Include natural speech patterns:
   - Some hesitations ("um", "er")
   - Clarifications ("What I mean is...")
   - Interruptions
   - Back-channeling ("I see", "Right", "Okay")
5. Cover these elements:
   - Initial greeting and establishing rapport
   - Presenting complaint exploration
   - History taking (systematic approach)
   - Examination discussion
   - Diagnosis/Assessment discussion
   - Management plan
   - Closing

Generate 12 note-completion questions based on the transcript.
Questions should:
- Test comprehension of key medical information
- Require answers of 1-3 words
- Be answerable from a single listening
- Cover different parts of the consultation

Respond in this exact JSON format:
{{
    "title": "Consultation title",
    "medical_context": "Brief context",
    "speakers": {{
        "speaker_1": "Doctor/Nurse Name",
        "speaker_2": "Patient Name"
    }},
    "transcript": [
        {{"speaker": "speaker_1", "text": "dialogue line", "timestamp": "0:00"}},
        {{"speaker": "speaker_2", "text": "dialogue line", "timestamp": "0:05"}}
    ],
    "duration_seconds": 280,
    "key_vocabulary": ["term1", "term2"],
    "questions": [
        {{
            "question_number": 1,
            "question_text": "Patient's main complaint: ___",
            "correct_answer": "chest pain",
            "answer_location": "0:30-0:45",
            "max_words": 3
        }}
    ]
}}
        """

        response = await self._call_ai(prompt, max_tokens=4096)
        return self._parse_json_response(response)

    async def generate_listening_workplace_extract(
        self,
        profession: OETProfession,
        context: str,
        extract_number: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a workplace extract for Listening Part B

        Returns:
            Short workplace dialogue with MCQ question
        """
        prompt = f"""
You are an expert in creating OET Listening content.

Generate a short workplace extract for OET Listening Part B.

PROFESSION: {profession.value}
CONTEXT: {context}
EXTRACT NUMBER: {extract_number}

Requirements:
1. Duration: 30-45 seconds (100-150 words)
2. Natural workplace communication between healthcare professionals
3. One clear main point that forms the basis of the MCQ
4. Realistic workplace setting (handover, meeting, phone call, etc.)

The MCQ should:
- Have 3 options (A, B, C)
- Test the main point or outcome of the conversation
- Have only one clearly correct answer

Respond in this exact JSON format:
{{
    "title": "Extract title",
    "setting": "Where this takes place",
    "speakers": ["Speaker 1 role", "Speaker 2 role"],
    "transcript": [
        {{"speaker": 0, "text": "dialogue line"}},
        {{"speaker": 1, "text": "dialogue line"}}
    ],
    "duration_seconds": 40,
    "question": {{
        "question_text": "What is the main outcome of this conversation?",
        "options": ["Option A", "Option B", "Option C"],
        "correct_answer": "A",
        "explanation": "Why A is correct"
    }}
}}
        """

        response = await self._call_ai(prompt, max_tokens=1500)
        return self._parse_json_response(response)

    async def generate_listening_presentation(
        self,
        profession: OETProfession,
        topic: str,
        presentation_number: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a presentation extract for Listening Part C

        Returns:
            Academic presentation with MCQ questions
        """
        prompt = f"""
You are an expert in creating OET Listening content.

Generate an academic/professional presentation for OET Listening Part C.

PROFESSION: {profession.value}
TOPIC: {topic}
PRESENTATION NUMBER: {presentation_number}

Requirements:
1. Duration: 4-5 minutes (500-700 words)
2. Academic/professional register
3. Evidence-based content with:
   - Statistics and research findings
   - Clinical guidelines references
   - Real-world applications
4. Clear structure:
   - Introduction
   - Main points (3-4)
   - Conclusion/recommendations
5. Single speaker (lecturer/presenter)

Generate 6 MCQ questions testing:
- Main ideas
- Specific details
- Statistics/numbers
- Recommendations
- Inferences

Respond in this exact JSON format:
{{
    "title": "Presentation title",
    "presenter": "Dr./Prof. Name, Institution",
    "topic_area": "Speciality area",
    "transcript": "Full presentation text with natural speech markers...",
    "duration_seconds": 280,
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "questions": [
        {{
            "question_number": 1,
            "question_text": "According to the presenter, what is the main...",
            "options": ["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
            "correct_answer": "B",
            "explanation": "The presenter states that..."
        }}
    ]
}}
        """

        response = await self._call_ai(prompt, max_tokens=3000)
        return self._parse_json_response(response)

    # =========================================================================
    # READING CONTENT GENERATION
    # =========================================================================

    async def generate_reading_part_a_texts(
        self,
        profession: OETProfession,
        topic: str
    ) -> Dict[str, Any]:
        """
        Generate four short texts for Reading Part A

        Returns:
            Four related texts with 20 questions
        """
        prompt = f"""
You are an expert in creating OET Reading content.

Generate four short healthcare texts for OET Reading Part A (Expeditious Reading).

PROFESSION: {profession.value}
TOPIC: {topic}

Requirements for the texts:
1. Each text: 150-200 words
2. Four different text types:
   - Text A: Clinical guideline or protocol
   - Text B: Patient information leaflet
   - Text C: Research summary or abstract
   - Text D: Professional policy or advisory
3. All texts relate to the same topic but from different perspectives
4. Professional healthcare language appropriate to {profession.value}

Generate 20 questions asking "In which text..." or "Which text mentions..."
Questions should:
- Require scanning/skimming skills
- Have clear, unambiguous answers
- Cover all four texts relatively equally

Respond in this exact JSON format:
{{
    "topic": "{topic}",
    "texts": [
        {{
            "label": "A",
            "type": "Clinical guideline",
            "title": "Text A title",
            "content": "Full text content...",
            "word_count": 175
        }},
        {{
            "label": "B",
            "type": "Patient information",
            "title": "Text B title",
            "content": "Full text content...",
            "word_count": 180
        }},
        {{
            "label": "C",
            "type": "Research summary",
            "title": "Text C title",
            "content": "Full text content...",
            "word_count": 170
        }},
        {{
            "label": "D",
            "type": "Professional advisory",
            "title": "Text D title",
            "content": "Full text content...",
            "word_count": 185
        }}
    ],
    "questions": [
        {{
            "question_number": 1,
            "question_text": "Which text mentions the importance of...",
            "correct_answer": "C",
            "evidence": "Text C states: '...'"
        }}
    ]
}}
        """

        response = await self._call_ai(prompt, max_tokens=4096)
        return self._parse_json_response(response)

    async def generate_reading_part_c_text(
        self,
        profession: OETProfession,
        topic: str,
        text_number: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a long text for Reading Part C

        Returns:
            Academic text with 8 comprehension questions
        """
        prompt = f"""
You are an expert in creating OET Reading content.

Generate a long academic text for OET Reading Part C.

PROFESSION: {profession.value}
TOPIC: {topic}
TEXT NUMBER: {text_number}

Requirements:
1. Length: 600-800 words
2. Style: Journal article or editorial
3. Structure with labeled paragraphs (A through G)
4. Content should include:
   - Introduction with context
   - Discussion of current evidence
   - Different perspectives or approaches
   - Implications for practice
   - Conclusion or recommendations
5. Sophisticated vocabulary appropriate for healthcare professionals
6. Complex sentence structures

Generate 8 MCQ questions covering:
- Main idea identification (1-2 questions)
- Specific detail comprehension (2-3 questions)
- Inference and implication (1-2 questions)
- Author's purpose or tone (1 question)
- Vocabulary in context (1 question)

Respond in this exact JSON format:
{{
    "title": "Article title",
    "source": "Adapted from [Journal Name], [Year]",
    "paragraphs": {{
        "A": "First paragraph content...",
        "B": "Second paragraph content...",
        "C": "Third paragraph content...",
        "D": "Fourth paragraph content...",
        "E": "Fifth paragraph content...",
        "F": "Sixth paragraph content...",
        "G": "Seventh paragraph content..."
    }},
    "word_count": 720,
    "questions": [
        {{
            "question_number": 27,
            "question_type": "main_idea",
            "question_text": "The main purpose of this article is to...",
            "paragraph_reference": null,
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": "B",
            "explanation": "The author's main purpose is..."
        }}
    ]
}}
        """

        response = await self._call_ai(prompt, max_tokens=4096)
        return self._parse_json_response(response)

    # =========================================================================
    # WRITING CONTENT GENERATION
    # =========================================================================

    async def generate_writing_case_notes(
        self,
        profession: OETProfession,
        task_type: WritingTaskType,
        scenario: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate authentic patient case notes for Writing task

        Returns:
            Complete case notes with task instructions and model answer
        """
        task_desc = {
            WritingTaskType.REFERRAL_LETTER: "referral to a specialist",
            WritingTaskType.DISCHARGE_LETTER: "discharge summary to GP",
            WritingTaskType.TRANSFER_LETTER: "transfer to another facility",
            WritingTaskType.ADVICE_LETTER: "advice letter to patient"
        }

        prompt = f"""
You are an expert in creating OET Writing content for {profession.value}.

Generate authentic patient case notes for an OET Writing task.

PROFESSION: {profession.value}
TASK TYPE: {task_type.value} - {task_desc.get(task_type, 'referral letter')}
SCENARIO: {scenario or 'Generate an appropriate medical scenario'}

Requirements:
1. Realistic patient presentation
2. Complete medical information in note form:
   - Patient demographics
   - Presenting complaint
   - History of present illness
   - Past medical history
   - Medications
   - Allergies
   - Social history
   - Examination findings
   - Vital signs
   - Investigation results
   - Diagnosis
   - Management plan
3. Appropriate complexity for 45-minute task
4. Include some information that should NOT be included in the letter (tests candidate's selection skills)

Also provide:
- Clear task instructions
- Required content points (5-7 key points)
- Model answer (180-200 words)

Respond in this exact JSON format:
{{
    "task_type": "{task_type.value}",
    "recipient": "Dr./Specialist Name, Specialty",
    "recipient_institution": "Hospital/Clinic Name",
    "instructions": "Full task instructions...",
    "case_notes": {{
        "patient_name": "First Last",
        "age": 55,
        "gender": "Male/Female",
        "date": "Today's date",
        "presenting_complaint": "...",
        "history_of_present_illness": "...",
        "past_medical_history": ["condition1", "condition2"],
        "medications": [
            {{"name": "Drug", "dose": "dose", "frequency": "frequency"}}
        ],
        "allergies": ["allergy1"],
        "social_history": {{
            "occupation": "...",
            "smoking": "...",
            "alcohol": "...",
            "living_situation": "..."
        }},
        "family_history": ["..."],
        "examination_findings": {{
            "general": "...",
            "specific_system": "..."
        }},
        "vital_signs": {{
            "BP": "...",
            "HR": "...",
            "RR": "...",
            "Temp": "...",
            "SpO2": "..."
        }},
        "investigations": [
            {{"test": "Test name", "result": "Result"}}
        ],
        "diagnosis": "...",
        "management_plan": ["point1", "point2"]
    }},
    "required_points": [
        "Point that must be covered",
        "Another required point"
    ],
    "model_answer": "Dear Dr...\\n\\nFull model letter here (180-200 words)...\\n\\nYours sincerely"
}}
        """

        response = await self._call_ai(prompt, max_tokens=3000)
        return self._parse_json_response(response)

    # =========================================================================
    # SPEAKING CONTENT GENERATION
    # =========================================================================

    async def generate_speaking_roleplay(
        self,
        profession: OETProfession,
        scenario_type: SpeakingScenarioType,
        roleplay_number: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a complete role-play scenario for Speaking

        Returns:
            Complete role-play with candidate card, interlocutor script
        """
        scenario_desc = {
            SpeakingScenarioType.HISTORY_TAKING: "taking a patient history",
            SpeakingScenarioType.EXPLANATION: "explaining a diagnosis or procedure",
            SpeakingScenarioType.COUNSELING: "counseling about lifestyle or treatment",
            SpeakingScenarioType.PATIENT_EDUCATION: "educating about condition management",
            SpeakingScenarioType.BREAKING_BAD_NEWS: "delivering difficult news",
            SpeakingScenarioType.REASSURANCE: "reassuring an anxious patient"
        }

        prompt = f"""
You are an expert in creating OET Speaking content.

Generate a complete role-play scenario for OET Speaking.

PROFESSION: {profession.value}
SCENARIO TYPE: {scenario_type.value} - {scenario_desc.get(scenario_type, '')}
ROLE-PLAY NUMBER: {roleplay_number}

Requirements:
1. Realistic clinical scenario appropriate for {profession.value}
2. Clear candidate tasks (4-5 tasks)
3. Interlocutor (patient/relative) with:
   - Specific emotional state
   - 3-4 concerns to raise
   - Background information to provide
4. Appropriate complexity (5 minutes of interaction)

Create interlocutor prompts that:
- Provide natural conversation flow
- Test clinical communication skills
- Allow demonstration of empathy and professionalism

Respond in this exact JSON format:
{{
    "title": "Scenario title",
    "setting": "Where this takes place",
    "scenario_type": "{scenario_type.value}",
    "preparation_time_minutes": 3,
    "interaction_time_minutes": 5,
    "candidate_card": {{
        "role": "Healthcare Professional Role",
        "setting": "Clinical setting",
        "context": "Situation context for candidate...",
        "tasks": [
            "First task",
            "Second task",
            "Third task",
            "Fourth task"
        ]
    }},
    "interlocutor_card": {{
        "role": "Patient/Relative role",
        "name": "Patient name",
        "age": 45,
        "context": "Patient's situation...",
        "emotional_state": "Anxious/Worried/Calm/Upset",
        "concerns": [
            "First concern to raise",
            "Second concern",
            "Third concern"
        ],
        "information_to_provide": {{
            "symptom_detail": "...",
            "relevant_history": "...",
            "social_context": "..."
        }}
    }},
    "interlocutor_script": [
        {{
            "cue": "After candidate introduces themselves",
            "response": "Patient's opening response..."
        }},
        {{
            "cue": "When asked about symptoms",
            "response": "Description of symptoms..."
        }},
        {{
            "cue": "When diagnosis/plan explained",
            "response": "Reaction and concern..."
        }},
        {{
            "cue": "Near the end",
            "response": "Final question or concern..."
        }}
    ],
    "evaluation_focus": [
        "Key communication skill to assess",
        "Another skill focus"
    ]
}}
        """

        response = await self._call_ai(prompt, max_tokens=2500)
        return self._parse_json_response(response)

    # =========================================================================
    # BATCH GENERATION
    # =========================================================================

    async def generate_complete_exam_content(
        self,
        profession: OETProfession
    ) -> Dict[str, Any]:
        """
        Generate complete content for all OET sections

        Runs generation for all sections in parallel.
        """
        logger.info("generating_complete_oet_content", profession=profession.value)

        tasks = [
            self._generate_full_listening(profession),
            self._generate_full_reading(profession),
            self._generate_full_writing(profession),
            self._generate_full_speaking(profession)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        content = {}
        sections = ["listening", "reading", "writing", "speaking"]

        for i, section in enumerate(sections):
            if isinstance(results[i], Exception):
                logger.error(f"Failed to generate {section}", error=str(results[i]))
                content[section] = {"error": str(results[i])}
            else:
                content[section] = results[i]

        return content

    async def _generate_full_listening(self, profession: OETProfession) -> Dict[str, Any]:
        """Generate all listening content"""
        part_a_1 = await self.generate_listening_consultation(
            profession, "Initial assessment", 1
        )
        part_a_2 = await self.generate_listening_consultation(
            profession, "Follow-up consultation", 2
        )

        part_b_extracts = []
        contexts = ["Handover", "Team meeting", "Phone call", "Staff briefing", "Family meeting", "Peer discussion"]
        for i, ctx in enumerate(contexts):
            extract = await self.generate_listening_workplace_extract(profession, ctx, i+1)
            part_b_extracts.append(extract)

        part_c_1 = await self.generate_listening_presentation(
            profession, "Recent clinical advances", 1
        )
        part_c_2 = await self.generate_listening_presentation(
            profession, "Healthcare policy update", 2
        )

        return {
            "part_a": {"consultations": [part_a_1, part_a_2]},
            "part_b": {"extracts": part_b_extracts},
            "part_c": {"presentations": [part_c_1, part_c_2]}
        }

    async def _generate_full_reading(self, profession: OETProfession) -> Dict[str, Any]:
        """Generate all reading content"""
        part_a = await self.generate_reading_part_a_texts(
            profession, "Management of chronic condition"
        )

        part_b_items = []
        for i in range(6):
            item = await self._generate_reading_part_b_item(profession, i+1)
            part_b_items.append(item)

        part_c_1 = await self.generate_reading_part_c_text(profession, "Clinical research findings", 1)
        part_c_2 = await self.generate_reading_part_c_text(profession, "Healthcare policy debate", 2)

        return {
            "part_a": part_a,
            "part_b": {"items": part_b_items},
            "part_c": {"texts": [part_c_1, part_c_2]}
        }

    async def _generate_reading_part_b_item(self, profession: OETProfession, item_num: int) -> Dict[str, Any]:
        """Generate a single Part B item"""
        text_types = ["memo", "policy", "notice", "email", "protocol", "announcement"]
        text_type = text_types[(item_num - 1) % len(text_types)]

        prompt = f"""
Generate a short workplace text for OET Reading Part B.

TEXT TYPE: {text_type}
PROFESSION: {profession.value}

Requirements:
- 100-150 words
- Professional workplace communication
- One clear MCQ question about the main message

Respond in JSON:
{{
    "type": "{text_type}",
    "content": "Full text...",
    "word_count": 125,
    "question": {{
        "question_text": "What is the main purpose of this {text_type}?",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "correct_answer": "B"
    }}
}}
        """

        response = await self._call_ai(prompt, max_tokens=1000)
        return self._parse_json_response(response)

    async def _generate_full_writing(self, profession: OETProfession) -> Dict[str, Any]:
        """Generate writing content"""
        task_type = WritingTaskType.REFERRAL_LETTER
        return await self.generate_writing_case_notes(profession, task_type)

    async def _generate_full_speaking(self, profession: OETProfession) -> Dict[str, Any]:
        """Generate all speaking content"""
        roleplay_1 = await self.generate_speaking_roleplay(
            profession, SpeakingScenarioType.EXPLANATION, 1
        )
        roleplay_2 = await self.generate_speaking_roleplay(
            profession, SpeakingScenarioType.COUNSELING, 2
        )

        return {"role_plays": [roleplay_1, roleplay_2]}

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _call_ai(self, prompt: str, max_tokens: int = 2048) -> str:
        """Call AI API"""
        message = await self.ai_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        # Find JSON in response
        try:
            # Try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            else:
                # Try to find JSON object
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)

            raise ValueError(f"Could not parse JSON from response: {response[:200]}...")
