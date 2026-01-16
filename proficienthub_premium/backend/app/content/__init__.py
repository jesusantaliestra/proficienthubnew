"""
ProficientHub - Content Module

Contains exam topics, question banks, and content generation utilities.
"""

from app.content.exam_topics import (
    IELTS_TOPICS,
    CAMBRIDGE_TOPICS,
    TOEFL_TOPICS,
    TopicFrequency,
    TopicDifficulty,
    get_topics_for_exam,
    get_writing_task2_topic,
    get_speaking_part2_topic,
)

__all__ = [
    "IELTS_TOPICS",
    "CAMBRIDGE_TOPICS",
    "TOEFL_TOPICS",
    "TopicFrequency",
    "TopicDifficulty",
    "get_topics_for_exam",
    "get_writing_task2_topic",
    "get_speaking_part2_topic",
]
