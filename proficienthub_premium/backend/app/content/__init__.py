"""
OET Content Module
==================
Contains specifications, samples, and templates for OET exam generation.
"""

from .oet_specifications import (
    OETHealthcareProfession,
    OETSection,
    OETBandScore,
    OETListeningSpec,
    OETReadingSpec,
    OETWritingSpec,
    OETSpeakingSpec,
    OETProfessionContext,
    OETExamSpecification,
    OET_EXAM_SPEC,
    OET_PROFESSION_CONTEXTS,
    get_profession_context,
    get_writing_letter_types,
)

from .oet_sample_references import (
    OETWritingSample,
    OETListeningSample,
    OETReadingSample,
    OETSpeakingSample,
    OET_WRITING_SAMPLES,
    OET_LISTENING_SAMPLES,
    OET_READING_SAMPLES,
    OET_SPEAKING_SAMPLES,
    OET_TOPICS_BY_PROFESSION,
    get_writing_sample,
    get_speaking_sample,
    get_topics_for_profession,
)

from .oet_format_templates import (
    OET_CSS_STYLES,
    OETTemplateRenderer,
    render_listening_exam,
    render_writing_exam,
    render_speaking_exam,
)

__all__ = [
    # Specifications
    "OETHealthcareProfession",
    "OETSection",
    "OETBandScore",
    "OETListeningSpec",
    "OETReadingSpec",
    "OETWritingSpec",
    "OETSpeakingSpec",
    "OETProfessionContext",
    "OETExamSpecification",
    "OET_EXAM_SPEC",
    "OET_PROFESSION_CONTEXTS",
    "get_profession_context",
    "get_writing_letter_types",
    # Samples
    "OETWritingSample",
    "OETListeningSample",
    "OETReadingSample",
    "OETSpeakingSample",
    "OET_WRITING_SAMPLES",
    "OET_LISTENING_SAMPLES",
    "OET_READING_SAMPLES",
    "OET_SPEAKING_SAMPLES",
    "OET_TOPICS_BY_PROFESSION",
    "get_writing_sample",
    "get_speaking_sample",
    "get_topics_for_profession",
    # Templates
    "OET_CSS_STYLES",
    "OETTemplateRenderer",
    "render_listening_exam",
    "render_writing_exam",
    "render_speaking_exam",
]
