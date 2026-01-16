"""
ProficientHub - Speaking Practice Matching Service

Real-time matching of students for peer speaking practice.
Integrates with Zoom for video sessions.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import random

# Zoom SDK would be imported in production
# import zoom


@dataclass
class MatchResult:
    """Result of a matching attempt."""
    success: bool
    match_id: Optional[str]
    partner_user_id: Optional[str]
    partner_name: Optional[str]
    partner_level: Optional[str]
    exam_type: str
    meeting_url: Optional[str]
    meeting_id: Optional[str]
    meeting_password: Optional[str]
    scheduled_at: Optional[datetime]
    instructions: Dict[str, Any]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "match_id": self.match_id,
            "partner": {
                "user_id": self.partner_user_id,
                "name": self.partner_name,
                "level": self.partner_level,
            } if self.partner_user_id else None,
            "exam_type": self.exam_type,
            "meeting": {
                "url": self.meeting_url,
                "id": self.meeting_id,
                "password": self.meeting_password,
            } if self.meeting_url else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "instructions": self.instructions,
            "error_message": self.error_message,
        }


# =============================================================================
# ZOOM INTEGRATION
# =============================================================================

class ZoomConfig:
    """Zoom API configuration."""

    def __init__(self):
        self.api_key = os.environ.get("ZOOM_API_KEY", "")
        self.api_secret = os.environ.get("ZOOM_API_SECRET", "")
        self.account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
        self.sdk_key = os.environ.get("ZOOM_SDK_KEY", "")
        self.sdk_secret = os.environ.get("ZOOM_SDK_SECRET", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret)


class ZoomService:
    """
    Zoom integration for creating video meetings.
    """

    def __init__(self):
        self.config = ZoomConfig()

    async def create_meeting(
        self,
        topic: str,
        duration_minutes: int = 20,
        start_time: Optional[datetime] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Zoom meeting for speaking practice.
        """
        if not self.config.is_configured:
            # Return mock meeting for development
            meeting_id = hashlib.md5(
                f"{topic}{datetime.now(timezone.utc).timestamp()}".encode()
            ).hexdigest()[:10]
            password = hashlib.md5(meeting_id.encode()).hexdigest()[:6]

            return {
                "success": True,
                "meeting_id": meeting_id,
                "meeting_url": f"https://zoom.us/j/{meeting_id}?pwd={password}",
                "password": password,
                "host_key": hashlib.md5(f"host_{meeting_id}".encode()).hexdigest()[:6],
                "start_url": f"https://zoom.us/s/{meeting_id}?zak=mock_token",
                "join_url": f"https://zoom.us/j/{meeting_id}?pwd={password}",
            }

        # In production with Zoom API:
        # headers = self._get_auth_headers()
        # payload = {
        #     "topic": topic,
        #     "type": 2,  # Scheduled meeting
        #     "start_time": start_time.isoformat() if start_time else None,
        #     "duration": duration_minutes,
        #     "settings": {
        #         "host_video": True,
        #         "participant_video": True,
        #         "join_before_host": True,
        #         "waiting_room": False,
        #         "mute_upon_entry": False,
        #         "auto_recording": "none",
        #         **(settings or {})
        #     }
        # }
        # response = await http_client.post(
        #     f"https://api.zoom.us/v2/users/me/meetings",
        #     headers=headers,
        #     json=payload
        # )
        # return response.json()

        # Mock for development
        meeting_id = hashlib.md5(
            f"{topic}{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:10]
        password = hashlib.md5(meeting_id.encode()).hexdigest()[:6]

        return {
            "success": True,
            "meeting_id": meeting_id,
            "meeting_url": f"https://zoom.us/j/{meeting_id}?pwd={password}",
            "password": password,
            "host_key": hashlib.md5(f"host_{meeting_id}".encode()).hexdigest()[:6],
        }

    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete/cancel a Zoom meeting."""
        # In production:
        # response = await http_client.delete(
        #     f"https://api.zoom.us/v2/meetings/{meeting_id}",
        #     headers=self._get_auth_headers()
        # )
        # return response.status_code == 204
        return True

    async def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get list of participants in a meeting."""
        # In production, call Zoom API
        return []

    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers for Zoom API."""
        # In production: Generate JWT token
        import jwt
        import time

        token = jwt.encode(
            {
                "iss": self.config.api_key,
                "exp": time.time() + 3600,
            },
            self.config.api_secret,
            algorithm="HS256"
        )
        return {"Authorization": f"Bearer {token}"}


# =============================================================================
# MATCHING ALGORITHM
# =============================================================================

class MatchingCriteria:
    """Criteria for matching speaking practice partners."""

    def __init__(
        self,
        exam_type: str,
        current_level: str,
        target_score: Optional[float] = None,
        preferred_topics: Optional[List[str]] = None,
        same_academy_only: bool = False,
        similar_level_only: bool = True,
        max_level_difference: int = 1,
    ):
        self.exam_type = exam_type
        self.current_level = current_level
        self.target_score = target_score
        self.preferred_topics = preferred_topics or []
        self.same_academy_only = same_academy_only
        self.similar_level_only = similar_level_only
        self.max_level_difference = max_level_difference

    def matches(self, other: "MatchingCriteria") -> Tuple[bool, float]:
        """
        Check if two criteria match.
        Returns (is_match, score) where score is 0-1.
        """
        # Must match exam type
        if self.exam_type != other.exam_type:
            return False, 0.0

        score = 0.5  # Base score for matching exam type

        # Level matching
        levels = ["beginner", "intermediate", "advanced", "expert"]
        try:
            level_diff = abs(levels.index(self.current_level.lower()) -
                           levels.index(other.current_level.lower()))
        except (ValueError, AttributeError):
            level_diff = 0

        if self.similar_level_only and level_diff > self.max_level_difference:
            return False, 0.0

        # Add score based on level similarity
        score += (1 - level_diff / len(levels)) * 0.3

        # Target score similarity
        if self.target_score and other.target_score:
            score_diff = abs(self.target_score - other.target_score)
            if score_diff <= 0.5:
                score += 0.1
            elif score_diff <= 1.0:
                score += 0.05

        # Topic overlap
        if self.preferred_topics and other.preferred_topics:
            overlap = set(self.preferred_topics) & set(other.preferred_topics)
            if overlap:
                score += 0.1 * min(len(overlap), 3) / 3

        return True, min(score, 1.0)


class SpeakingPracticeService:
    """
    Main service for speaking practice matching and session management.
    """

    # Level definitions for matching
    LEVEL_MAP = {
        "beginner": {"min_score": 0, "max_score": 4.5},
        "intermediate": {"min_score": 4.5, "max_score": 6.5},
        "advanced": {"min_score": 6.5, "max_score": 8.0},
        "expert": {"min_score": 8.0, "max_score": 9.0},
    }

    def __init__(self, db_session=None):
        self.db = db_session
        self.zoom_service = ZoomService()
        # In-memory queue for real-time matching (in production: use Redis)
        self._waiting_queue: Dict[str, List[Dict[str, Any]]] = {}

    async def register_availability(
        self,
        user_id: str,
        academy_id: str,
        exam_type: str,
        current_level: str,
        target_score: Optional[float] = None,
        preferred_topics: Optional[List[str]] = None,
        available_minutes: int = 30,
        same_academy_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Register a student as available for speaking practice.
        Returns availability ID for tracking.
        """
        availability_id = hashlib.md5(
            f"{user_id}{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]

        available_until = datetime.now(timezone.utc) + timedelta(minutes=available_minutes)

        availability_entry = {
            "availability_id": availability_id,
            "user_id": user_id,
            "academy_id": academy_id,
            "exam_type": exam_type,
            "current_level": current_level,
            "target_score": target_score,
            "preferred_topics": preferred_topics or [],
            "same_academy_only": same_academy_only,
            "available_until": available_until,
            "registered_at": datetime.now(timezone.utc),
        }

        # Add to queue
        queue_key = exam_type
        if queue_key not in self._waiting_queue:
            self._waiting_queue[queue_key] = []
        self._waiting_queue[queue_key].append(availability_entry)

        # Try immediate matching
        match_result = await self._try_immediate_match(availability_entry)

        if match_result.success:
            return {
                "status": "matched",
                "availability_id": availability_id,
                "match": match_result.to_dict(),
            }

        return {
            "status": "waiting",
            "availability_id": availability_id,
            "position_in_queue": len(self._waiting_queue.get(queue_key, [])),
            "estimated_wait_minutes": self._estimate_wait_time(exam_type),
            "available_until": available_until.isoformat(),
        }

    async def cancel_availability(self, availability_id: str) -> bool:
        """Cancel availability registration."""
        for queue_key in self._waiting_queue:
            self._waiting_queue[queue_key] = [
                entry for entry in self._waiting_queue[queue_key]
                if entry.get("availability_id") != availability_id
            ]
        return True

    async def _try_immediate_match(
        self,
        new_entry: Dict[str, Any]
    ) -> MatchResult:
        """
        Try to find an immediate match for a new availability entry.
        """
        exam_type = new_entry["exam_type"]
        queue = self._waiting_queue.get(exam_type, [])

        new_criteria = MatchingCriteria(
            exam_type=new_entry["exam_type"],
            current_level=new_entry["current_level"],
            target_score=new_entry.get("target_score"),
            preferred_topics=new_entry.get("preferred_topics"),
            same_academy_only=new_entry.get("same_academy_only", False),
        )

        best_match = None
        best_score = 0

        for entry in queue:
            # Don't match with self
            if entry["user_id"] == new_entry["user_id"]:
                continue

            # Check if still available
            if entry["available_until"] < datetime.now(timezone.utc):
                continue

            # Check same academy constraint
            if (new_entry.get("same_academy_only") or entry.get("same_academy_only")):
                if new_entry["academy_id"] != entry["academy_id"]:
                    continue

            other_criteria = MatchingCriteria(
                exam_type=entry["exam_type"],
                current_level=entry["current_level"],
                target_score=entry.get("target_score"),
                preferred_topics=entry.get("preferred_topics"),
                same_academy_only=entry.get("same_academy_only", False),
            )

            is_match, score = new_criteria.matches(other_criteria)

            if is_match and score > best_score:
                best_match = entry
                best_score = score

        if best_match:
            # Create match and remove both from queue
            return await self._create_match(new_entry, best_match)

        return MatchResult(
            success=False,
            match_id=None,
            partner_user_id=None,
            partner_name=None,
            partner_level=None,
            exam_type=exam_type,
            meeting_url=None,
            meeting_id=None,
            meeting_password=None,
            scheduled_at=None,
            instructions={},
            error_message="No matching partner found. Added to waiting queue.",
        )

    async def _create_match(
        self,
        user1: Dict[str, Any],
        user2: Dict[str, Any]
    ) -> MatchResult:
        """
        Create a speaking practice match between two users.
        """
        from app.db.models_institutional import get_speaking_instructions

        match_id = hashlib.md5(
            f"{user1['user_id']}{user2['user_id']}{datetime.now(timezone.utc)}".encode()
        ).hexdigest()[:16]

        exam_type = user1["exam_type"]

        # Create Zoom meeting
        meeting = await self.zoom_service.create_meeting(
            topic=f"Speaking Practice - {exam_type.upper().replace('_', ' ')}",
            duration_minutes=20,
            start_time=datetime.now(timezone.utc),
        )

        # Get instructions for this exam type
        instructions = get_speaking_instructions(exam_type)

        # Remove both users from queue
        queue_key = exam_type
        if queue_key in self._waiting_queue:
            self._waiting_queue[queue_key] = [
                entry for entry in self._waiting_queue[queue_key]
                if entry["user_id"] not in [user1["user_id"], user2["user_id"]]
            ]

        # In production: save match to database
        # match_record = SpeakingPracticeMatch(...)

        return MatchResult(
            success=True,
            match_id=match_id,
            partner_user_id=user2["user_id"],
            partner_name=f"Student {user2['user_id'][:8]}",  # In production: get actual name
            partner_level=user2["current_level"],
            exam_type=exam_type,
            meeting_url=meeting.get("meeting_url") or meeting.get("join_url"),
            meeting_id=meeting.get("meeting_id"),
            meeting_password=meeting.get("password"),
            scheduled_at=datetime.now(timezone.utc),
            instructions=instructions,
        )

    def _estimate_wait_time(self, exam_type: str) -> int:
        """Estimate wait time based on queue status."""
        queue_size = len(self._waiting_queue.get(exam_type, []))
        if queue_size == 0:
            return 10  # Default estimate
        elif queue_size < 5:
            return 5
        elif queue_size < 10:
            return 2
        else:
            return 1

    async def get_queue_status(self, exam_type: Optional[str] = None) -> Dict[str, Any]:
        """Get current queue status."""
        if exam_type:
            queue = self._waiting_queue.get(exam_type, [])
            # Clean expired entries
            now = datetime.now(timezone.utc)
            active = [e for e in queue if e["available_until"] > now]
            return {
                "exam_type": exam_type,
                "waiting_count": len(active),
                "estimated_wait_minutes": self._estimate_wait_time(exam_type),
            }

        status = {}
        now = datetime.now(timezone.utc)
        for exam, queue in self._waiting_queue.items():
            active = [e for e in queue if e["available_until"] > now]
            status[exam] = {
                "waiting_count": len(active),
                "estimated_wait_minutes": self._estimate_wait_time(exam),
            }
        return status

    async def end_session(
        self,
        match_id: str,
        user_id: str,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        End a speaking practice session and optionally provide feedback.
        """
        # In production: update database
        return {
            "status": "completed",
            "match_id": match_id,
            "feedback_recorded": rating is not None,
        }

    async def get_user_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get user's speaking practice history."""
        # In production: query database
        return []

    async def get_available_partners_count(
        self,
        exam_type: str,
        level: Optional[str] = None,
    ) -> int:
        """Get count of available partners for matching."""
        queue = self._waiting_queue.get(exam_type, [])
        now = datetime.now(timezone.utc)
        active = [e for e in queue if e["available_until"] > now]

        if level:
            active = [e for e in active if e.get("current_level") == level]

        return len(active)


# =============================================================================
# TOPIC SELECTION FOR SPEAKING PRACTICE
# =============================================================================

SPEAKING_TOPICS = {
    "ielts_academic": {
        "part1": [
            {"topic": "Your hometown", "questions": ["Where is your hometown?", "What do you like about it?", "Has it changed much?"]},
            {"topic": "Your work or studies", "questions": ["What do you do?", "Why did you choose this field?", "What do you enjoy about it?"]},
            {"topic": "Free time", "questions": ["What do you do in your free time?", "Do you prefer indoor or outdoor activities?", "How has this changed over time?"]},
            {"topic": "Technology", "questions": ["Do you use technology often?", "What technology couldn't you live without?", "How has technology changed your life?"]},
            {"topic": "Reading", "questions": ["Do you like reading?", "What kind of books do you read?", "Did you read much as a child?"]},
        ],
        "part2": [
            {"topic": "Describe a memorable trip", "cue_card": ["where you went", "who you went with", "what you did", "why it was memorable"]},
            {"topic": "Describe a person who has influenced you", "cue_card": ["who this person is", "how you know them", "what they have done", "how they influenced you"]},
            {"topic": "Describe a skill you would like to learn", "cue_card": ["what the skill is", "why you want to learn it", "how you would learn it", "how difficult it would be"]},
            {"topic": "Describe a book you have read", "cue_card": ["what it was about", "why you read it", "what you learned", "whether you would recommend it"]},
            {"topic": "Describe a place you like to visit", "cue_card": ["where it is", "how often you go", "what you do there", "why you like it"]},
        ],
        "part3": [
            {"theme": "Travel", "questions": ["How has travel changed in recent years?", "Do you think travel will change in the future?", "What are the benefits and drawbacks of tourism?"]},
            {"theme": "Education", "questions": ["How important is education in your country?", "How has education changed?", "What skills are most important to learn?"]},
            {"theme": "Technology", "questions": ["How has technology affected society?", "Are there any negative effects of technology?", "What technologies will be important in the future?"]},
        ],
    },
    "toefl_ibt": {
        "independent": [
            {"prompt": "Do you agree or disagree: It is better to have a few close friends than many casual friends?", "prep_time": 15, "response_time": 45},
            {"prompt": "Talk about a teacher who has had a significant influence on you.", "prep_time": 15, "response_time": 45},
            {"prompt": "Do you prefer working alone or in a group?", "prep_time": 15, "response_time": 45},
            {"prompt": "Describe a place that is special to you and explain why.", "prep_time": 15, "response_time": 45},
        ],
    },
    "pte_academic": {
        "describe_image": [
            {"type": "line_graph", "description": "Economic growth over 10 years"},
            {"type": "bar_chart", "description": "Population by country"},
            {"type": "pie_chart", "description": "Budget allocation"},
            {"type": "process", "description": "Manufacturing process"},
        ],
    },
}


def get_random_speaking_topic(exam_type: str, part: str) -> Dict[str, Any]:
    """Get a random speaking topic for practice."""
    exam_base = exam_type.split("_")[0]
    topics = SPEAKING_TOPICS.get(exam_type) or SPEAKING_TOPICS.get(f"{exam_base}_academic", {})

    if part in topics:
        return random.choice(topics[part])

    # Return default topic
    return {
        "topic": "General conversation",
        "questions": ["Tell me about yourself", "What are your goals?", "What do you enjoy doing?"],
    }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_speaking_practice_service(db_session=None) -> SpeakingPracticeService:
    """Factory function to create speaking practice service."""
    return SpeakingPracticeService(db_session=db_session)


def create_zoom_service() -> ZoomService:
    """Factory function to create Zoom service."""
    return ZoomService()
