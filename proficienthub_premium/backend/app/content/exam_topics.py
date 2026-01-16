"""
ProficientHub - Official Exam Topics Bank

Topics basados en los exámenes oficiales más recientes.
Categorizados por:
- Tipo de examen
- Sección
- Dificultad
- Frecuencia de aparición

FUENTES:
- Cambridge Assessment English official materials
- IELTS official practice tests
- TOEFL official guides
- Análisis de exámenes 2020-2025
"""

from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass


class TopicFrequency(str, Enum):
    """Frecuencia de aparición en exámenes oficiales"""
    VERY_COMMON = "very_common"      # >20% de exámenes
    COMMON = "common"                 # 10-20% de exámenes
    OCCASIONAL = "occasional"         # 5-10% de exámenes
    RARE = "rare"                     # <5% de exámenes


class TopicDifficulty(str, Enum):
    """Nivel de dificultad del topic"""
    BASIC = "basic"           # B1-B2
    INTERMEDIATE = "intermediate"  # B2-C1
    ADVANCED = "advanced"     # C1-C2


@dataclass
class ExamTopic:
    """Estructura de un topic de examen"""
    id: str
    name: str
    name_es: str
    category: str
    subcategories: List[str]
    frequency: TopicFrequency
    difficulty: TopicDifficulty
    sections: List[str]  # reading, writing, listening, speaking
    keywords: List[str]
    sample_questions: List[str]


# =============================================================================
# IELTS ACADEMIC & GENERAL TOPICS
# =============================================================================

IELTS_TOPICS = {
    "categories": [
        "Education", "Environment", "Technology", "Health", "Society",
        "Work", "Culture", "Science", "Travel", "Media"
    ],

    "reading": {
        "academic": [
            {
                "id": "ielts_read_001",
                "name": "Climate Change & Global Warming",
                "name_es": "Cambio Climático y Calentamiento Global",
                "category": "Environment",
                "frequency": TopicFrequency.VERY_COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Greenhouse effect mechanisms",
                    "Impact on ecosystems",
                    "Renewable energy solutions",
                    "International climate agreements",
                    "Carbon footprint reduction"
                ],
                "text_types": ["scientific article", "research summary", "opinion piece"]
            },
            {
                "id": "ielts_read_002",
                "name": "Technological Innovation",
                "name_es": "Innovación Tecnológica",
                "category": "Technology",
                "frequency": TopicFrequency.VERY_COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Artificial Intelligence",
                    "Automation and employment",
                    "Digital transformation",
                    "Cybersecurity",
                    "Social media impact"
                ],
                "text_types": ["research paper", "news article", "academic essay"]
            },
            {
                "id": "ielts_read_003",
                "name": "Urban Development & Architecture",
                "name_es": "Desarrollo Urbano y Arquitectura",
                "category": "Society",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Smart cities",
                    "Sustainable architecture",
                    "Urban planning challenges",
                    "Historic preservation",
                    "Public transportation"
                ],
                "text_types": ["case study", "descriptive text", "comparative analysis"]
            },
            {
                "id": "ielts_read_004",
                "name": "Health & Medicine",
                "name_es": "Salud y Medicina",
                "category": "Health",
                "frequency": TopicFrequency.VERY_COMMON,
                "difficulty": TopicDifficulty.ADVANCED,
                "subtopics": [
                    "Medical breakthroughs",
                    "Public health policies",
                    "Mental health awareness",
                    "Nutrition and diet",
                    "Healthcare systems comparison"
                ],
                "text_types": ["medical journal extract", "health report", "research findings"]
            },
            {
                "id": "ielts_read_005",
                "name": "Education Systems",
                "name_es": "Sistemas Educativos",
                "category": "Education",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Online learning evolution",
                    "Educational inequality",
                    "Teaching methodologies",
                    "University ranking systems",
                    "Vocational vs academic education"
                ],
                "text_types": ["educational research", "policy document", "comparative study"]
            },
            {
                "id": "ielts_read_006",
                "name": "Animal Behavior & Biology",
                "name_es": "Comportamiento Animal y Biología",
                "category": "Science",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Migration patterns",
                    "Endangered species",
                    "Marine life",
                    "Animal cognition",
                    "Ecosystems and biodiversity"
                ],
                "text_types": ["scientific article", "nature documentary transcript", "research paper"]
            },
            {
                "id": "ielts_read_007",
                "name": "History of Civilizations",
                "name_es": "Historia de las Civilizaciones",
                "category": "Culture",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.ADVANCED,
                "subtopics": [
                    "Ancient civilizations",
                    "Archaeological discoveries",
                    "Cultural evolution",
                    "Historical trade routes",
                    "Language development"
                ],
                "text_types": ["historical account", "archaeological report", "academic essay"]
            },
            {
                "id": "ielts_read_008",
                "name": "Psychology & Human Behavior",
                "name_es": "Psicología y Comportamiento Humano",
                "category": "Science",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.ADVANCED,
                "subtopics": [
                    "Memory and learning",
                    "Decision making",
                    "Social psychology",
                    "Child development",
                    "Emotional intelligence"
                ],
                "text_types": ["psychology journal", "experiment description", "theoretical analysis"]
            },
            {
                "id": "ielts_read_009",
                "name": "Economics & Business",
                "name_es": "Economía y Negocios",
                "category": "Work",
                "frequency": TopicFrequency.COMMON,
                "difficulty": TopicDifficulty.INTERMEDIATE,
                "subtopics": [
                    "Global economy trends",
                    "Startup ecosystems",
                    "Consumer behavior",
                    "International trade",
                    "Corporate sustainability"
                ],
                "text_types": ["business report", "economic analysis", "case study"]
            },
            {
                "id": "ielts_read_010",
                "name": "Space Exploration",
                "name_es": "Exploración Espacial",
                "category": "Science",
                "frequency": TopicFrequency.OCCASIONAL,
                "difficulty": TopicDifficulty.ADVANCED,
                "subtopics": [
                    "Mars colonization",
                    "Satellite technology",
                    "Space tourism",
                    "Astronomical discoveries",
                    "International space cooperation"
                ],
                "text_types": ["scientific article", "NASA/ESA report summary", "feature article"]
            }
        ],
        "general": [
            {
                "id": "ielts_gen_read_001",
                "name": "Workplace & Employment",
                "name_es": "Lugar de Trabajo y Empleo",
                "category": "Work",
                "frequency": TopicFrequency.VERY_COMMON,
                "difficulty": TopicDifficulty.BASIC,
                "subtopics": [
                    "Job advertisements",
                    "Workplace policies",
                    "Employee handbooks",
                    "Training programs",
                    "Work-life balance"
                ],
                "text_types": ["job listing", "company policy", "instruction manual"]
            },
            {
                "id": "ielts_gen_read_002",
                "name": "Consumer Information",
                "name_es": "Información al Consumidor",
                "category": "Society",
                "frequency": TopicFrequency.VERY_COMMON,
                "difficulty": TopicDifficulty.BASIC,
                "subtopics": [
                    "Product warranties",
                    "Terms and conditions",
                    "Consumer rights",
                    "Product reviews",
                    "Service comparisons"
                ],
                "text_types": ["product manual", "warranty document", "comparison guide"]
            }
        ]
    },

    "writing": {
        "task1": {
            "academic": [
                {
                    "id": "ielts_write_t1_001",
                    "name": "Line Graphs - Trends Over Time",
                    "name_es": "Gráficos de Líneas - Tendencias",
                    "frequency": TopicFrequency.VERY_COMMON,
                    "data_types": ["population growth", "economic indicators", "temperature changes"],
                    "key_vocabulary": ["increase", "decrease", "fluctuate", "peak", "plateau", "dramatic rise"]
                },
                {
                    "id": "ielts_write_t1_002",
                    "name": "Bar Charts - Comparisons",
                    "name_es": "Gráficos de Barras - Comparaciones",
                    "frequency": TopicFrequency.VERY_COMMON,
                    "data_types": ["survey results", "country comparisons", "industry statistics"],
                    "key_vocabulary": ["highest", "lowest", "significant difference", "comparable", "marginally"]
                },
                {
                    "id": "ielts_write_t1_003",
                    "name": "Pie Charts - Proportions",
                    "name_es": "Gráficos Circulares - Proporciones",
                    "frequency": TopicFrequency.COMMON,
                    "data_types": ["budget allocation", "market share", "demographic breakdown"],
                    "key_vocabulary": ["majority", "minority", "proportion", "segment", "accounts for"]
                },
                {
                    "id": "ielts_write_t1_004",
                    "name": "Process Diagrams",
                    "name_es": "Diagramas de Proceso",
                    "frequency": TopicFrequency.COMMON,
                    "data_types": ["manufacturing process", "natural cycle", "procedural steps"],
                    "key_vocabulary": ["firstly", "subsequently", "following this", "finally", "meanwhile"]
                },
                {
                    "id": "ielts_write_t1_005",
                    "name": "Maps - Changes Over Time",
                    "name_es": "Mapas - Cambios en el Tiempo",
                    "frequency": TopicFrequency.OCCASIONAL,
                    "data_types": ["urban development", "land use changes", "before/after comparisons"],
                    "key_vocabulary": ["transformed", "replaced", "expanded", "relocated", "demolished"]
                }
            ],
            "general": [
                {
                    "id": "ielts_gen_write_t1_001",
                    "name": "Formal Letters - Complaints",
                    "name_es": "Cartas Formales - Quejas",
                    "frequency": TopicFrequency.VERY_COMMON,
                    "scenarios": ["product defect", "poor service", "billing error"],
                    "tone": "formal"
                },
                {
                    "id": "ielts_gen_write_t1_002",
                    "name": "Semi-formal Letters - Requests",
                    "name_es": "Cartas Semi-formales - Solicitudes",
                    "frequency": TopicFrequency.COMMON,
                    "scenarios": ["job application", "information request", "permission request"],
                    "tone": "semi-formal"
                },
                {
                    "id": "ielts_gen_write_t1_003",
                    "name": "Informal Letters - Personal",
                    "name_es": "Cartas Informales - Personales",
                    "frequency": TopicFrequency.COMMON,
                    "scenarios": ["invitation", "advice to friend", "congratulations"],
                    "tone": "informal"
                }
            ]
        },
        "task2": [
            {
                "id": "ielts_write_t2_001",
                "name": "Technology & Society",
                "name_es": "Tecnología y Sociedad",
                "frequency": TopicFrequency.VERY_COMMON,
                "question_types": ["advantages/disadvantages", "opinion", "discussion"],
                "sample_topics": [
                    "Impact of smartphones on communication",
                    "Artificial intelligence replacing human jobs",
                    "Social media's influence on young people",
                    "Privacy concerns in the digital age"
                ]
            },
            {
                "id": "ielts_write_t2_002",
                "name": "Education",
                "name_es": "Educación",
                "frequency": TopicFrequency.VERY_COMMON,
                "question_types": ["opinion", "problem/solution", "discussion"],
                "sample_topics": [
                    "Online vs traditional education",
                    "Importance of university education",
                    "Gap year before university",
                    "Single-sex vs co-educational schools"
                ]
            },
            {
                "id": "ielts_write_t2_003",
                "name": "Environment",
                "name_es": "Medio Ambiente",
                "frequency": TopicFrequency.VERY_COMMON,
                "question_types": ["problem/solution", "causes/effects", "opinion"],
                "sample_topics": [
                    "Individual vs government responsibility for environment",
                    "Plastic pollution solutions",
                    "Urban vs rural environmental impact",
                    "Climate change mitigation strategies"
                ]
            },
            {
                "id": "ielts_write_t2_004",
                "name": "Health & Lifestyle",
                "name_es": "Salud y Estilo de Vida",
                "frequency": TopicFrequency.COMMON,
                "question_types": ["causes/effects", "problem/solution", "opinion"],
                "sample_topics": [
                    "Obesity causes and solutions",
                    "Mental health in modern society",
                    "Exercise and healthy diet importance",
                    "Healthcare: public vs private systems"
                ]
            },
            {
                "id": "ielts_write_t2_005",
                "name": "Work & Career",
                "name_es": "Trabajo y Carrera",
                "frequency": TopicFrequency.COMMON,
                "question_types": ["advantages/disadvantages", "opinion", "discussion"],
                "sample_topics": [
                    "Remote work vs office work",
                    "Job satisfaction vs high salary",
                    "Retirement age changes",
                    "Automation impact on employment"
                ]
            },
            {
                "id": "ielts_write_t2_006",
                "name": "Globalization & Culture",
                "name_es": "Globalización y Cultura",
                "frequency": TopicFrequency.COMMON,
                "question_types": ["discussion", "opinion", "advantages/disadvantages"],
                "sample_topics": [
                    "Cultural homogenization",
                    "International tourism effects",
                    "Preservation of local traditions",
                    "Global language dominance"
                ]
            },
            {
                "id": "ielts_write_t2_007",
                "name": "Crime & Punishment",
                "name_es": "Crimen y Castigo",
                "frequency": TopicFrequency.OCCASIONAL,
                "question_types": ["opinion", "problem/solution", "discussion"],
                "sample_topics": [
                    "Prison vs rehabilitation",
                    "Youth crime causes",
                    "Capital punishment debate",
                    "Crime prevention methods"
                ]
            },
            {
                "id": "ielts_write_t2_008",
                "name": "Government & Society",
                "name_es": "Gobierno y Sociedad",
                "frequency": TopicFrequency.COMMON,
                "question_types": ["opinion", "discussion", "problem/solution"],
                "sample_topics": [
                    "Government spending priorities",
                    "Wealth inequality",
                    "Censorship and free speech",
                    "Voting age changes"
                ]
            }
        ]
    },

    "listening": {
        "sections": [
            {
                "section": 1,
                "name": "Social/Everyday Contexts",
                "name_es": "Contextos Sociales/Cotidianos",
                "format": "conversation",
                "speakers": 2,
                "common_scenarios": [
                    "Hotel/accommodation booking",
                    "Travel arrangements",
                    "Club membership",
                    "Course enrollment",
                    "Service complaints"
                ]
            },
            {
                "section": 2,
                "name": "Social/General Interest Monologue",
                "name_es": "Monólogo de Interés General",
                "format": "monologue",
                "speakers": 1,
                "common_scenarios": [
                    "Tour guide information",
                    "Public announcement",
                    "Local facility description",
                    "Event information",
                    "Company/organization introduction"
                ]
            },
            {
                "section": 3,
                "name": "Academic Discussion",
                "name_es": "Discusión Académica",
                "format": "conversation",
                "speakers": "2-4",
                "common_scenarios": [
                    "Tutorial discussion",
                    "Research project planning",
                    "Assignment feedback",
                    "Study group discussion",
                    "Academic presentation preparation"
                ]
            },
            {
                "section": 4,
                "name": "Academic Lecture",
                "name_es": "Conferencia Académica",
                "format": "monologue",
                "speakers": 1,
                "common_topics": [
                    "Biology/Environment",
                    "History/Archaeology",
                    "Psychology",
                    "Business/Economics",
                    "Technology/Science"
                ]
            }
        ]
    },

    "speaking": {
        "part1": {
            "name": "Introduction & Interview",
            "duration_minutes": 5,
            "topics": [
                {
                    "category": "Personal",
                    "questions": [
                        "Work/Studies", "Hometown", "Home/Accommodation",
                        "Family", "Daily routine", "Free time"
                    ]
                },
                {
                    "category": "General Interest",
                    "questions": [
                        "Reading", "Music", "Sports", "Food", "Weather",
                        "Transport", "Technology", "Social media", "Shopping"
                    ]
                }
            ]
        },
        "part2": {
            "name": "Long Turn (Cue Card)",
            "duration_minutes": 4,
            "preparation_time": 60,
            "speaking_time": "1-2 minutes",
            "common_topics": [
                {
                    "category": "People",
                    "examples": [
                        "Describe a person who has influenced you",
                        "Describe a famous person you admire",
                        "Describe a family member you spend time with"
                    ]
                },
                {
                    "category": "Places",
                    "examples": [
                        "Describe a place you want to visit",
                        "Describe a city you have been to",
                        "Describe your favorite room"
                    ]
                },
                {
                    "category": "Objects",
                    "examples": [
                        "Describe a gift you received",
                        "Describe something you bought recently",
                        "Describe a piece of technology you use"
                    ]
                },
                {
                    "category": "Events/Experiences",
                    "examples": [
                        "Describe a memorable journey",
                        "Describe an important decision you made",
                        "Describe a time you helped someone"
                    ]
                },
                {
                    "category": "Abstract",
                    "examples": [
                        "Describe a skill you learned",
                        "Describe a goal you want to achieve",
                        "Describe something you do to stay healthy"
                    ]
                }
            ]
        },
        "part3": {
            "name": "Discussion",
            "duration_minutes": 5,
            "description": "Two-way discussion on abstract topics related to Part 2",
            "question_types": [
                "Comparison questions",
                "Speculation questions",
                "Opinion questions",
                "Explanation questions"
            ]
        }
    }
}


# =============================================================================
# CAMBRIDGE B2 FIRST & C1 ADVANCED TOPICS
# =============================================================================

CAMBRIDGE_TOPICS = {
    "b2_first": {
        "reading": {
            "text_types": [
                "Newspaper/magazine articles",
                "Fiction extracts",
                "Advertisements",
                "Reports",
                "Reviews"
            ],
            "common_topics": [
                "Lifestyle and relationships",
                "Education and learning",
                "Entertainment and media",
                "Health and fitness",
                "Environment and nature",
                "Technology and science",
                "Travel and tourism",
                "Work and careers"
            ]
        },
        "writing": {
            "part1": {
                "type": "Essay",
                "word_count": 140-190,
                "common_topics": [
                    "Should school uniforms be mandatory?",
                    "Advantages and disadvantages of living abroad",
                    "Technology in education",
                    "Environmental responsibility"
                ]
            },
            "part2": {
                "types": ["Article", "Email/Letter", "Report", "Review"],
                "word_count": 140-190
            }
        },
        "speaking": {
            "part1": "Interview (2 minutes)",
            "part2": "Long turn with photos (4 minutes)",
            "part3": "Collaborative task (4 minutes)",
            "part4": "Discussion (4 minutes)"
        }
    },
    "c1_advanced": {
        "reading": {
            "text_types": [
                "Academic texts",
                "Literary fiction",
                "Journalistic texts",
                "Professional/business texts"
            ],
            "common_topics": [
                "Scientific developments",
                "Social issues",
                "Cultural phenomena",
                "Economic trends",
                "Historical events",
                "Philosophical concepts"
            ]
        },
        "writing": {
            "part1": {
                "type": "Essay",
                "word_count": 220-260,
                "based_on": "Two texts with contrasting opinions"
            },
            "part2": {
                "types": ["Letter", "Proposal", "Report", "Review"],
                "word_count": 220-260
            }
        }
    }
}


# =============================================================================
# TOEFL iBT TOPICS
# =============================================================================

TOEFL_TOPICS = {
    "reading": {
        "passage_types": [
            "Exposition (explaining a topic)",
            "Argumentation (presenting a point of view)",
            "Historical narrative"
        ],
        "academic_subjects": [
            "Arts", "Life science", "Physical science", "Social science"
        ],
        "common_topics": [
            "Evolutionary biology",
            "Geology and earth science",
            "American history",
            "Psychology experiments",
            "Art history",
            "Astronomy",
            "Archaeology",
            "Economics"
        ]
    },
    "listening": {
        "conversation_contexts": [
            "Office hours with professor",
            "Service encounter (library, registrar)",
            "Student discussions"
        ],
        "lecture_topics": [
            "Biology", "Art history", "Astronomy",
            "Psychology", "Geology", "Architecture",
            "Literature", "History", "Environmental science"
        ]
    },
    "speaking": {
        "tasks": [
            {
                "task": 1,
                "type": "Independent",
                "description": "Express opinion on familiar topic",
                "preparation": 15,
                "response": 45
            },
            {
                "task": 2,
                "type": "Integrated (Reading + Listening + Speaking)",
                "description": "Campus situation",
                "preparation": 30,
                "response": 60
            },
            {
                "task": 3,
                "type": "Integrated (Reading + Listening + Speaking)",
                "description": "Academic topic",
                "preparation": 30,
                "response": 60
            },
            {
                "task": 4,
                "type": "Integrated (Listening + Speaking)",
                "description": "Academic lecture summary",
                "preparation": 20,
                "response": 60
            }
        ]
    },
    "writing": {
        "task1": {
            "type": "Integrated",
            "description": "Summarize points from reading and lecture",
            "word_count": 150-225,
            "time": 20
        },
        "task2": {
            "type": "Independent (Academic Discussion)",
            "description": "Contribute to academic discussion",
            "word_count": 100,
            "time": 10
        }
    }
}


# =============================================================================
# TOPIC SELECTION ENGINE
# =============================================================================

def get_topics_for_exam(
    exam_type: str,
    section: str,
    count: int = 3,
    difficulty: TopicDifficulty = None,
    exclude_ids: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene topics para generar un examen

    Args:
        exam_type: Tipo de examen (ielts_academic, cambridge_b2_first, etc.)
        section: Sección del examen (reading, writing, listening, speaking)
        count: Número de topics a retornar
        difficulty: Filtrar por dificultad
        exclude_ids: IDs de topics a excluir (ya usados por el estudiante)

    Returns:
        Lista de topics seleccionados
    """
    exclude_ids = exclude_ids or []

    # Seleccionar banco de topics según tipo de examen
    if exam_type.startswith("ielts"):
        topic_bank = IELTS_TOPICS
    elif exam_type.startswith("cambridge"):
        topic_bank = CAMBRIDGE_TOPICS
    elif exam_type.startswith("toefl"):
        topic_bank = TOEFL_TOPICS
    else:
        topic_bank = IELTS_TOPICS  # Default

    # Obtener topics de la sección
    section_topics = topic_bank.get(section, {})

    # Filtrar y seleccionar
    # (Implementación simplificada - en producción usar algoritmo más sofisticado)
    available_topics = []

    if isinstance(section_topics, dict):
        for key, topics in section_topics.items():
            if isinstance(topics, list):
                available_topics.extend(topics)

    # Filtrar excluidos
    available_topics = [t for t in available_topics if t.get("id") not in exclude_ids]

    # Filtrar por dificultad
    if difficulty:
        available_topics = [
            t for t in available_topics
            if t.get("difficulty") == difficulty
        ]

    # Seleccionar prioritizando frecuencia
    import random
    weighted_topics = []
    for topic in available_topics:
        freq = topic.get("frequency", TopicFrequency.COMMON)
        weight = {
            TopicFrequency.VERY_COMMON: 4,
            TopicFrequency.COMMON: 3,
            TopicFrequency.OCCASIONAL: 2,
            TopicFrequency.RARE: 1
        }.get(freq, 2)
        weighted_topics.extend([topic] * weight)

    if len(weighted_topics) < count:
        return weighted_topics[:count] if weighted_topics else []

    return random.sample(weighted_topics, min(count, len(weighted_topics)))


def get_writing_task2_topic(exam_type: str, exclude_recent: List[str] = None) -> Dict[str, Any]:
    """
    Obtiene un topic para Writing Task 2 (ensayo)
    Prioriza topics muy comunes y evita repeticiones recientes
    """
    exclude_recent = exclude_recent or []

    if exam_type.startswith("ielts"):
        topics = IELTS_TOPICS["writing"]["task2"]
    else:
        topics = IELTS_TOPICS["writing"]["task2"]  # Default to IELTS

    # Filtrar recientes
    available = [t for t in topics if t["id"] not in exclude_recent]

    if not available:
        available = topics  # Reset si todos han sido usados

    # Seleccionar con peso por frecuencia
    import random
    return random.choice(available)


def get_speaking_part2_topic(exam_type: str) -> Dict[str, Any]:
    """Obtiene un topic para Speaking Part 2 (cue card)"""
    import random

    if exam_type.startswith("ielts"):
        categories = IELTS_TOPICS["speaking"]["part2"]["common_topics"]
        category = random.choice(categories)
        topic = random.choice(category["examples"])
        return {
            "category": category["category"],
            "topic": topic,
            "preparation_time": IELTS_TOPICS["speaking"]["part2"]["preparation_time"],
            "speaking_time": IELTS_TOPICS["speaking"]["part2"]["speaking_time"]
        }

    return {"topic": "Describe a memorable experience", "preparation_time": 60}


# =============================================================================
# PTE ACADEMIC TOPICS
# =============================================================================

PTE_TOPICS = {
    "speaking_writing": {
        "read_aloud": {
            "description": "Read a text aloud with correct pronunciation and intonation",
            "common_topics": [
                "Scientific discoveries",
                "Historical events",
                "Business and economics",
                "Environmental issues",
                "Social phenomena",
                "Technology advancement",
                "Cultural studies",
                "Educational theories"
            ],
            "scoring_criteria": ["content", "oral_fluency", "pronunciation"]
        },
        "repeat_sentence": {
            "description": "Listen and repeat the sentence exactly",
            "sentence_types": [
                "Academic statements",
                "Scientific facts",
                "Historical information",
                "Statistical data",
                "Opinion statements"
            ],
            "scoring_criteria": ["content", "oral_fluency", "pronunciation"]
        },
        "describe_image": {
            "description": "Describe an image in detail",
            "image_types": [
                {
                    "type": "Line graph",
                    "common_topics": ["Economic trends", "Population changes", "Temperature variations"]
                },
                {
                    "type": "Bar chart",
                    "common_topics": ["Comparisons between countries", "Survey results", "Sales data"]
                },
                {
                    "type": "Pie chart",
                    "common_topics": ["Budget allocation", "Market share", "Demographics"]
                },
                {
                    "type": "Process diagram",
                    "common_topics": ["Manufacturing", "Natural cycles", "Scientific processes"]
                },
                {
                    "type": "Map",
                    "common_topics": ["City development", "Migration patterns", "Geographic features"]
                },
                {
                    "type": "Picture/Photo",
                    "common_topics": ["Daily life", "Events", "Landscapes", "People"]
                }
            ],
            "time_limit": 40,
            "scoring_criteria": ["content", "oral_fluency", "pronunciation"]
        },
        "retell_lecture": {
            "description": "Listen to a lecture and retell the main points",
            "lecture_topics": [
                "Biology and life sciences",
                "Psychology and behavior",
                "History and archaeology",
                "Business and management",
                "Environmental science",
                "Technology and innovation",
                "Arts and literature",
                "Sociology and culture"
            ],
            "time_limit": 40,
            "scoring_criteria": ["content", "oral_fluency", "pronunciation"]
        },
        "answer_short_question": {
            "description": "Answer a question with one or a few words",
            "question_categories": [
                "General knowledge",
                "Academic vocabulary",
                "Scientific terms",
                "Mathematical concepts",
                "Geographic facts"
            ]
        },
        "summarize_written_text": {
            "description": "Write a one-sentence summary of the passage",
            "text_topics": [
                "Scientific research findings",
                "Social studies",
                "Economic theories",
                "Historical events",
                "Environmental issues",
                "Technological developments"
            ],
            "word_limit": "5-75 words",
            "time_limit": 10,
            "scoring_criteria": ["content", "form", "grammar", "vocabulary"]
        },
        "essay": {
            "description": "Write an argumentative essay",
            "common_topics": [
                {
                    "category": "Education",
                    "examples": [
                        "Should university education be free?",
                        "Is online learning as effective as traditional classroom?",
                        "Should students be allowed to use calculators in exams?"
                    ]
                },
                {
                    "category": "Technology",
                    "examples": [
                        "Do the advantages of technology outweigh the disadvantages?",
                        "Should children be limited in their use of social media?",
                        "Will robots replace human workers?"
                    ]
                },
                {
                    "category": "Environment",
                    "examples": [
                        "Should governments impose taxes on carbon emissions?",
                        "Is individual action effective in fighting climate change?",
                        "Should plastic bags be banned completely?"
                    ]
                },
                {
                    "category": "Society",
                    "examples": [
                        "Should voting be compulsory?",
                        "Is globalization beneficial for developing countries?",
                        "Should there be a universal basic income?"
                    ]
                },
                {
                    "category": "Health",
                    "examples": [
                        "Should junk food advertising be banned?",
                        "Is healthcare a right or a privilege?",
                        "Should smoking be banned in all public places?"
                    ]
                }
            ],
            "word_limit": "200-300 words",
            "time_limit": 20,
            "scoring_criteria": ["content", "development_structure", "form", "grammar", "vocabulary", "spelling"]
        }
    },
    "reading": {
        "reading_writing_fill_blanks": {
            "description": "Fill in the blanks by selecting words from a dropdown",
            "text_topics": [
                "Academic articles",
                "Scientific papers",
                "News reports",
                "Historical texts",
                "Business documents"
            ],
            "skills_tested": ["vocabulary", "grammar", "reading comprehension"]
        },
        "multiple_choice_single": {
            "description": "Choose one correct answer",
            "question_types": [
                "Main idea",
                "Supporting details",
                "Inference",
                "Author's purpose",
                "Vocabulary in context"
            ]
        },
        "multiple_choice_multiple": {
            "description": "Choose multiple correct answers",
            "question_types": [
                "Supporting statements",
                "Multiple facts",
                "Different perspectives"
            ]
        },
        "reorder_paragraphs": {
            "description": "Arrange paragraphs in correct order",
            "text_types": [
                "Chronological narratives",
                "Logical arguments",
                "Process descriptions",
                "Cause and effect texts"
            ]
        },
        "reading_fill_blanks": {
            "description": "Drag words into blanks",
            "focus_areas": ["collocations", "grammar", "vocabulary"]
        }
    },
    "listening": {
        "summarize_spoken_text": {
            "description": "Write a summary of the lecture",
            "lecture_topics": [
                "Academic lectures",
                "Scientific presentations",
                "Historical narratives",
                "Business case studies"
            ],
            "word_limit": "50-70 words",
            "time_limit": 10
        },
        "multiple_choice_single": {
            "description": "Choose the correct answer based on the recording"
        },
        "multiple_choice_multiple": {
            "description": "Choose multiple correct answers"
        },
        "fill_blanks": {
            "description": "Fill in the blanks while listening"
        },
        "highlight_correct_summary": {
            "description": "Choose the paragraph that best summarizes the recording"
        },
        "select_missing_word": {
            "description": "Predict the missing word at the end of a recording"
        },
        "highlight_incorrect_words": {
            "description": "Identify words that differ from the recording"
        },
        "write_from_dictation": {
            "description": "Write exactly what you hear",
            "sentence_types": [
                "Academic statements",
                "Factual information",
                "Instructions",
                "Definitions"
            ]
        }
    }
}


# =============================================================================
# OET (Occupational English Test) - 12 HEALTHCARE PROFESSIONS
# Listening & Reading: IDENTICAL for all professions
# Speaking & Writing: SPECIFIC to each profession
# =============================================================================

# List of all 12 OET professions
OET_PROFESSIONS = [
    "medicine",
    "nursing",
    "dentistry",
    "pharmacy",
    "physiotherapy",
    "occupational_therapy",
    "dietetics",
    "speech_pathology",
    "podiatry",
    "optometry",
    "radiography",
    "veterinary_science"
]

# Listening and Reading are IDENTICAL for all professions
OET_LISTENING_READING = {
    "listening": {
        "description": "Same for all 12 professions",
        "time_limit": 40,
        "total_questions": 42,
        "part_a": {
            "name": "Consultation Extracts",
            "description": "Two recorded health professional-patient consultations",
            "duration_each": "5 minutes",
            "questions": 24,
            "question_types": ["note completion", "gap fill"],
            "common_scenarios": [
                {
                    "scenario": "Initial patient assessment",
                    "topics": ["presenting complaint", "medical history", "symptoms", "allergies"]
                },
                {
                    "scenario": "Follow-up consultation",
                    "topics": ["treatment progress", "medication review", "test results", "side effects"]
                },
                {
                    "scenario": "Specialist referral discussion",
                    "topics": ["diagnosis explanation", "treatment options", "prognosis", "risks"]
                },
                {
                    "scenario": "Discharge planning",
                    "topics": ["home care instructions", "medication schedule", "follow-up appointments", "warning signs"]
                }
            ]
        },
        "part_b": {
            "name": "Short Workplace Extracts",
            "description": "Six short recordings of healthcare workplace communications",
            "duration_each": "1 minute",
            "questions": 6,
            "question_types": ["multiple choice"],
            "communication_types": [
                "Team briefings",
                "Handover reports",
                "Phone conversations with colleagues",
                "Patient instructions",
                "Inter-departmental discussions",
                "Health education presentations"
            ]
        },
        "part_c": {
            "name": "Presentation Extracts",
            "description": "Two longer recordings (interviews, lectures, presentations)",
            "duration_each": "5 minutes",
            "questions": 12,
            "question_types": ["multiple choice"],
            "content_types": [
                "Health policy discussions",
                "Medical research presentations",
                "Patient care guidelines",
                "Healthcare service updates",
                "Public health announcements",
                "Professional development lectures"
            ]
        }
    },

    "reading": {
        "description": "Same for all 12 professions",
        "time_limit": 60,
        "total_questions": 42,
        "part_a": {
            "name": "Expeditious Reading",
            "description": "Quick reading to locate specific information from 4 short texts",
            "time_limit": 15,
            "questions": 20,
            "text_types": [
                "Patient information leaflets",
                "Hospital guidelines and protocols",
                "Medical device instructions",
                "Healthcare facility procedures",
                "Drug information sheets",
                "Safety notices"
            ],
            "question_types": ["matching", "sentence completion", "short answer"]
        },
        "part_b": {
            "name": "Careful Reading (Short Texts)",
            "description": "Detailed reading of healthcare workplace texts",
            "questions": 6,
            "text_types": [
                "Hospital policy documents",
                "Clinical guidelines",
                "Patient safety protocols",
                "Professional development notices",
                "Staff memos",
                "Healthcare regulations"
            ],
            "question_types": ["multiple choice", "matching headings"]
        },
        "part_c": {
            "name": "Careful Reading (Long Texts)",
            "description": "Two longer texts requiring detailed comprehension",
            "questions": 16,
            "text_types": [
                "Medical journal articles",
                "Research summaries",
                "Healthcare editorials",
                "Clinical case studies",
                "Health policy papers"
            ],
            "question_types": ["multiple choice"],
            "skills_tested": [
                "Understanding main ideas",
                "Identifying supporting details",
                "Making inferences",
                "Understanding writer's opinion",
                "Identifying purpose"
            ]
        }
    }
}

# Writing and Speaking SPECIFIC to each profession
OET_PROFESSION_SPECIFIC = {
    "medicine": {
        "code": "oet_medicine",
        "name": "Medicine (Doctors)",
        "writing": {
            "description": "Write a referral/discharge letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Discharge summary", "Transfer letter"],
            "common_scenarios": [
                {
                    "type": "Referral to specialist",
                    "examples": ["Cardiology referral for chest pain", "Neurology for recurrent headaches", "Oncology for suspicious mass"]
                },
                {
                    "type": "Discharge summary",
                    "examples": ["Post-MI discharge", "Post-surgical discharge", "Pneumonia treatment completion"]
                },
                {
                    "type": "GP update letter",
                    "examples": ["Outpatient follow-up summary", "Test results communication", "Treatment plan update"]
                }
            ],
            "common_conditions": [
                "Cardiovascular: MI, heart failure, hypertension, arrhythmia",
                "Respiratory: COPD, asthma, pneumonia, lung cancer",
                "Neurological: stroke, epilepsy, Parkinson's, MS",
                "Gastrointestinal: IBD, liver cirrhosis, peptic ulcer",
                "Endocrine: diabetes, thyroid disorders, Addison's",
                "Oncology: various cancers, palliative care",
                "Mental health: depression, anxiety, schizophrenia"
            ]
        },
        "speaking": {
            "description": "Role-play consultations with simulated patients",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Breaking bad news", "example": "Informing patient of cancer diagnosis"},
                {"scenario": "Explaining treatment options", "example": "Discussing surgery vs medication"},
                {"scenario": "Taking medical history", "example": "New patient with chest pain"},
                {"scenario": "Discussing test results", "example": "Explaining abnormal blood tests"},
                {"scenario": "Managing non-compliance", "example": "Patient not taking medication"},
                {"scenario": "Lifestyle counseling", "example": "Advising on smoking cessation"}
            ]
        }
    },
    "nursing": {
        "code": "oet_nursing",
        "name": "Nursing",
        "writing": {
            "description": "Write a referral/handover letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Handover letter", "Discharge letter"],
            "common_scenarios": [
                {
                    "type": "Community nurse referral",
                    "examples": ["Post-operative wound care", "Diabetes management at home", "Palliative care at home"]
                },
                {
                    "type": "Shift handover",
                    "examples": ["ICU patient status", "Post-surgical patient care", "Mental health patient monitoring"]
                },
                {
                    "type": "Discharge planning",
                    "examples": ["Home care instructions", "Medication management", "Follow-up appointments"]
                }
            ],
            "common_conditions": [
                "Post-operative care and wound management",
                "Medication administration and monitoring",
                "Patient education and self-care",
                "Pain management",
                "Fall prevention and mobility",
                "Nutrition and hydration",
                "Mental health observations"
            ]
        },
        "speaking": {
            "description": "Role-play nurse-patient/carer interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Patient education", "example": "Teaching insulin injection technique"},
                {"scenario": "Pre-procedure preparation", "example": "Preparing patient for surgery"},
                {"scenario": "Pain assessment", "example": "Assessing post-operative pain"},
                {"scenario": "Medication counseling", "example": "Explaining new medications"},
                {"scenario": "Wound care instructions", "example": "Teaching wound dressing change"},
                {"scenario": "Dealing with anxious patient", "example": "Calming pre-surgery anxiety"}
            ]
        }
    },
    "dentistry": {
        "code": "oet_dentistry",
        "name": "Dentistry",
        "writing": {
            "description": "Write a referral letter based on dental case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Specialist referral", "Treatment summary"],
            "common_scenarios": [
                {
                    "type": "Oral surgery referral",
                    "examples": ["Impacted wisdom teeth", "Jaw cyst removal", "TMJ dysfunction"]
                },
                {
                    "type": "Periodontal specialist",
                    "examples": ["Advanced periodontal disease", "Gum recession treatment", "Implant assessment"]
                },
                {
                    "type": "Orthodontic referral",
                    "examples": ["Malocclusion assessment", "Child orthodontic evaluation"]
                }
            ],
            "common_conditions": [
                "Caries and restorative dentistry",
                "Periodontal disease",
                "Endodontic problems (root canal)",
                "Oral pathology",
                "TMJ disorders",
                "Dental trauma",
                "Oral cancer screening"
            ]
        },
        "speaking": {
            "description": "Role-play dentist-patient interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Treatment explanation", "example": "Explaining root canal procedure"},
                {"scenario": "Addressing dental anxiety", "example": "Calming nervous patient"},
                {"scenario": "Post-extraction care", "example": "Instructions after tooth removal"},
                {"scenario": "Oral hygiene education", "example": "Teaching proper brushing technique"},
                {"scenario": "Treatment options", "example": "Crown vs extraction discussion"},
                {"scenario": "Child patient communication", "example": "First dental visit for child"}
            ]
        }
    },
    "pharmacy": {
        "code": "oet_pharmacy",
        "name": "Pharmacy",
        "writing": {
            "description": "Write a letter to healthcare provider based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["GP letter", "Medication review letter", "Intervention letter"],
            "common_scenarios": [
                {
                    "type": "Medication interaction alert",
                    "examples": ["Drug-drug interaction identified", "Contraindication discovered"]
                },
                {
                    "type": "Medication review outcome",
                    "examples": ["Polypharmacy review", "Compliance issues identified"]
                },
                {
                    "type": "Dosage adjustment recommendation",
                    "examples": ["Renal impairment dose adjustment", "Age-related dosing"]
                }
            ],
            "common_conditions": [
                "Drug interactions and contraindications",
                "Medication compliance issues",
                "Adverse drug reactions",
                "Dosage adjustments",
                "Medication reviews for elderly",
                "Anticoagulation management",
                "Pain medication management"
            ]
        },
        "speaking": {
            "description": "Role-play pharmacist-patient consultations",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "New medication counseling", "example": "Explaining new prescription"},
                {"scenario": "OTC advice", "example": "Recommending cold/flu treatment"},
                {"scenario": "Side effect discussion", "example": "Addressing medication concerns"},
                {"scenario": "Compliance counseling", "example": "Motivating medication adherence"},
                {"scenario": "Drug interaction warning", "example": "Explaining interaction risks"},
                {"scenario": "Inhaler technique", "example": "Teaching correct inhaler use"}
            ]
        }
    },
    "physiotherapy": {
        "code": "oet_physiotherapy",
        "name": "Physiotherapy",
        "writing": {
            "description": "Write a referral/progress letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Progress report", "Discharge summary"],
            "common_scenarios": [
                {
                    "type": "Orthopaedic specialist referral",
                    "examples": ["Suspected ACL tear", "Chronic back pain investigation"]
                },
                {
                    "type": "Progress report to GP",
                    "examples": ["Post-stroke rehabilitation", "Post-surgical recovery"]
                },
                {
                    "type": "Discharge summary",
                    "examples": ["Completed rehabilitation program", "Return to work assessment"]
                }
            ],
            "common_conditions": [
                "Musculoskeletal injuries",
                "Post-surgical rehabilitation",
                "Stroke rehabilitation",
                "Sports injuries",
                "Chronic pain management",
                "Respiratory physiotherapy",
                "Neurological conditions"
            ]
        },
        "speaking": {
            "description": "Role-play physiotherapist-patient interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Exercise instruction", "example": "Teaching home exercise program"},
                {"scenario": "Pain management", "example": "Discussing pain during treatment"},
                {"scenario": "Treatment explanation", "example": "Explaining manual therapy approach"},
                {"scenario": "Goal setting", "example": "Discussing rehabilitation goals"},
                {"scenario": "Progress review", "example": "Reviewing treatment outcomes"},
                {"scenario": "Return to activity", "example": "Advising return to sport/work"}
            ]
        }
    },
    "occupational_therapy": {
        "code": "oet_occupational_therapy",
        "name": "Occupational Therapy",
        "writing": {
            "description": "Write a referral/assessment letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Assessment report", "Equipment recommendation"],
            "common_scenarios": [
                {
                    "type": "Home modification assessment",
                    "examples": ["Bathroom adaptation needs", "Stair lift recommendation"]
                },
                {
                    "type": "Return to work assessment",
                    "examples": ["Workplace modification needs", "Graduated return plan"]
                },
                {
                    "type": "Equipment recommendation",
                    "examples": ["Wheelchair assessment", "Assistive technology needs"]
                }
            ],
            "common_conditions": [
                "Stroke rehabilitation",
                "Hand injuries",
                "Cognitive impairment",
                "Mental health conditions",
                "Developmental disorders",
                "Ageing-related decline",
                "Workplace injuries"
            ]
        },
        "speaking": {
            "description": "Role-play OT-patient/carer interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Activity assessment", "example": "Assessing daily living skills"},
                {"scenario": "Equipment training", "example": "Teaching use of adaptive equipment"},
                {"scenario": "Home safety discussion", "example": "Discussing home modifications"},
                {"scenario": "Carer education", "example": "Training family member in transfers"},
                {"scenario": "Goal setting", "example": "Establishing independence goals"},
                {"scenario": "Discharge planning", "example": "Planning home discharge"}
            ]
        }
    },
    "dietetics": {
        "code": "oet_dietetics",
        "name": "Dietetics",
        "writing": {
            "description": "Write a referral/consultation letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Nutrition assessment", "Diet plan letter"],
            "common_scenarios": [
                {
                    "type": "Specialist nutrition referral",
                    "examples": ["Enteral feeding assessment", "Eating disorder specialist"]
                },
                {
                    "type": "GP update letter",
                    "examples": ["Diabetes nutrition management", "Weight management progress"]
                },
                {
                    "type": "Hospital discharge nutrition plan",
                    "examples": ["Post-bariatric surgery diet", "Renal diet at home"]
                }
            ],
            "common_conditions": [
                "Diabetes mellitus nutrition",
                "Obesity and weight management",
                "Eating disorders",
                "Renal disease diet",
                "Malnutrition assessment",
                "Gastrointestinal conditions",
                "Food allergies and intolerances"
            ]
        },
        "speaking": {
            "description": "Role-play dietitian-patient consultations",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Diet education", "example": "Explaining diabetic diet"},
                {"scenario": "Weight management", "example": "Discussing weight loss strategies"},
                {"scenario": "Allergy counseling", "example": "Managing food allergies"},
                {"scenario": "Meal planning", "example": "Creating personalized meal plan"},
                {"scenario": "Motivation counseling", "example": "Addressing diet non-compliance"},
                {"scenario": "Cultural diet adaptation", "example": "Adapting diet to cultural preferences"}
            ]
        }
    },
    "speech_pathology": {
        "code": "oet_speech_pathology",
        "name": "Speech Pathology",
        "writing": {
            "description": "Write a referral/assessment letter based on case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Assessment report", "Progress report"],
            "common_scenarios": [
                {
                    "type": "ENT referral",
                    "examples": ["Voice disorder investigation", "Swallowing assessment"]
                },
                {
                    "type": "Neurologist update",
                    "examples": ["Post-stroke communication progress", "Parkinson's speech changes"]
                },
                {
                    "type": "School/GP report",
                    "examples": ["Child language assessment", "Stuttering therapy progress"]
                }
            ],
            "common_conditions": [
                "Dysphagia (swallowing disorders)",
                "Aphasia (language disorders)",
                "Voice disorders",
                "Stuttering/fluency disorders",
                "Child speech/language delay",
                "Cognitive-communication disorders",
                "Hearing impairment support"
            ]
        },
        "speaking": {
            "description": "Role-play speech pathologist-patient/carer interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Swallowing assessment", "example": "Explaining dysphagia risks"},
                {"scenario": "Communication strategies", "example": "Teaching aphasia strategies to carer"},
                {"scenario": "Voice therapy", "example": "Explaining vocal hygiene"},
                {"scenario": "Child therapy", "example": "Discussing speech exercises with parent"},
                {"scenario": "Modified diet", "example": "Explaining thickened fluids"},
                {"scenario": "AAC device", "example": "Introducing communication device"}
            ]
        }
    },
    "podiatry": {
        "code": "oet_podiatry",
        "name": "Podiatry",
        "writing": {
            "description": "Write a referral letter based on podiatry case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Assessment report", "Treatment summary"],
            "common_scenarios": [
                {
                    "type": "Vascular surgeon referral",
                    "examples": ["Peripheral vascular disease", "Non-healing ulcer"]
                },
                {
                    "type": "Diabetes team referral",
                    "examples": ["High-risk diabetic foot", "Charcot foot suspected"]
                },
                {
                    "type": "Orthopaedic referral",
                    "examples": ["Surgical opinion for bunion", "Hammer toe correction"]
                }
            ],
            "common_conditions": [
                "Diabetic foot complications",
                "Peripheral vascular disease",
                "Foot ulcers and wounds",
                "Nail conditions (ingrown, fungal)",
                "Biomechanical problems",
                "Sports injuries",
                "Arthritis-related foot problems"
            ]
        },
        "speaking": {
            "description": "Role-play podiatrist-patient interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Diabetic foot care", "example": "Teaching foot self-examination"},
                {"scenario": "Wound care education", "example": "Explaining ulcer dressing"},
                {"scenario": "Footwear advice", "example": "Recommending appropriate shoes"},
                {"scenario": "Treatment explanation", "example": "Explaining ingrown nail surgery"},
                {"scenario": "Orthotic fitting", "example": "Discussing custom insoles"},
                {"scenario": "Fall prevention", "example": "Addressing balance concerns"}
            ]
        }
    },
    "optometry": {
        "code": "oet_optometry",
        "name": "Optometry",
        "writing": {
            "description": "Write a referral letter based on optometry case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Examination report", "Co-management letter"],
            "common_scenarios": [
                {
                    "type": "Ophthalmologist referral",
                    "examples": ["Suspected glaucoma", "Macular degeneration", "Cataract assessment"]
                },
                {
                    "type": "GP referral",
                    "examples": ["Diabetic retinopathy findings", "Hypertensive retinopathy"]
                },
                {
                    "type": "Co-management update",
                    "examples": ["Post-cataract monitoring", "Glaucoma follow-up"]
                }
            ],
            "common_conditions": [
                "Glaucoma",
                "Cataracts",
                "Macular degeneration",
                "Diabetic retinopathy",
                "Refractive errors",
                "Dry eye syndrome",
                "Contact lens complications"
            ]
        },
        "speaking": {
            "description": "Role-play optometrist-patient interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Diagnosis explanation", "example": "Explaining glaucoma diagnosis"},
                {"scenario": "Contact lens education", "example": "Teaching lens care"},
                {"scenario": "Vision changes", "example": "Discussing presbyopia options"},
                {"scenario": "Referral discussion", "example": "Explaining need for specialist"},
                {"scenario": "Eye drop instruction", "example": "Teaching eye drop technique"},
                {"scenario": "Lifestyle advice", "example": "Computer vision syndrome management"}
            ]
        }
    },
    "radiography": {
        "code": "oet_radiography",
        "name": "Radiography",
        "writing": {
            "description": "Write a letter based on radiography case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Examination report", "Follow-up letter"],
            "common_scenarios": [
                {
                    "type": "Radiologist consultation",
                    "examples": ["Complex imaging protocol", "Contrast reaction history"]
                },
                {
                    "type": "Referring clinician update",
                    "examples": ["Procedure completion", "Additional imaging recommendation"]
                },
                {
                    "type": "Patient safety concern",
                    "examples": ["Incidental finding", "Urgent finding communication"]
                }
            ],
            "common_conditions": [
                "Pre-procedure patient preparation",
                "Contrast media protocols",
                "Radiation safety",
                "Patient positioning",
                "Image quality optimization",
                "Emergency imaging protocols",
                "Interventional procedures"
            ]
        },
        "speaking": {
            "description": "Role-play radiographer-patient interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Procedure explanation", "example": "Explaining MRI procedure"},
                {"scenario": "Anxiety management", "example": "Calming claustrophobic patient"},
                {"scenario": "Contrast information", "example": "Explaining contrast injection"},
                {"scenario": "Pregnancy screening", "example": "Discussing radiation risks"},
                {"scenario": "Positioning instruction", "example": "Guiding patient positioning"},
                {"scenario": "Post-procedure care", "example": "After interventional procedure"}
            ]
        }
    },
    "veterinary_science": {
        "code": "oet_veterinary_science",
        "name": "Veterinary Science",
        "writing": {
            "description": "Write a referral letter based on veterinary case notes",
            "time_limit": 45,
            "word_count": "180-200",
            "letter_types": ["Referral letter", "Case summary", "Follow-up letter"],
            "common_scenarios": [
                {
                    "type": "Specialist referral",
                    "examples": ["Orthopaedic surgery referral", "Oncology consultation"]
                },
                {
                    "type": "Case transfer",
                    "examples": ["Emergency transfer", "After-hours handover"]
                },
                {
                    "type": "Owner communication",
                    "examples": ["Treatment summary for owner", "Ongoing care instructions"]
                }
            ],
            "common_conditions": [
                "Musculoskeletal injuries",
                "Internal medicine cases",
                "Dermatological conditions",
                "Oncology",
                "Emergency and critical care",
                "Dental conditions",
                "Behavioural issues"
            ]
        },
        "speaking": {
            "description": "Role-play veterinarian-pet owner interactions",
            "time_limit": 20,
            "role_play_scenarios": [
                {"scenario": "Diagnosis explanation", "example": "Explaining cancer diagnosis"},
                {"scenario": "Treatment discussion", "example": "Discussing surgery options"},
                {"scenario": "Euthanasia discussion", "example": "End-of-life conversation"},
                {"scenario": "Post-operative care", "example": "Home care instructions"},
                {"scenario": "Preventive care", "example": "Vaccination schedule"},
                {"scenario": "Cost discussion", "example": "Discussing treatment costs"}
            ]
        }
    }
}

# Assessment criteria (same for all professions)
OET_ASSESSMENT_CRITERIA = {
    "writing": [
        {"criterion": "Purpose", "weight": "high", "description": "Clear communication of referral/letter purpose"},
        {"criterion": "Content", "weight": "high", "description": "Relevant selection and organization from case notes"},
        {"criterion": "Conciseness and clarity", "weight": "medium", "description": "Appropriate length and clear expression"},
        {"criterion": "Genre and style", "weight": "medium", "description": "Appropriate letter format and professional tone"},
        {"criterion": "Organization and layout", "weight": "medium", "description": "Logical structure and paragraphing"},
        {"criterion": "Language", "weight": "high", "description": "Grammar, vocabulary, spelling, punctuation"}
    ],
    "speaking": [
        "Intelligibility",
        "Fluency",
        "Appropriateness of language",
        "Resources of grammar and expression",
        "Relationship building",
        "Understanding and incorporating patient's perspective",
        "Providing structure",
        "Information gathering",
        "Information giving"
    ]
}

def get_oet_topics(profession: str) -> Dict[str, Any]:
    """
    Get OET topics for a specific profession.
    Returns listening/reading (same for all) + profession-specific writing/speaking.
    """
    profession = profession.lower().replace(" ", "_")
    if profession not in OET_PROFESSIONS:
        profession = "medicine"  # Default to medicine

    profession_specific = OET_PROFESSION_SPECIFIC.get(profession, OET_PROFESSION_SPECIFIC["medicine"])

    return {
        "profession": profession,
        "profession_name": profession_specific["name"],
        "code": profession_specific["code"],
        "listening": OET_LISTENING_READING["listening"],
        "reading": OET_LISTENING_READING["reading"],
        "writing": profession_specific["writing"],
        "speaking": profession_specific["speaking"],
        "assessment_criteria": OET_ASSESSMENT_CRITERIA
    }


# =============================================================================
# TOEIC (Test of English for International Communication)
# =============================================================================

TOEIC_TOPICS = {
    "description": "Business and workplace English proficiency test",
    "versions": ["TOEIC Listening & Reading", "TOEIC Speaking & Writing"],

    "listening_reading": {
        "total_time": 120,
        "total_questions": 200,

        "listening": {
            "time_limit": 45,
            "questions": 100,
            "parts": {
                "part1": {
                    "name": "Photographs",
                    "questions": 6,
                    "description": "Listen to statements about a photograph",
                    "photo_types": [
                        "Office scenes",
                        "Business meetings",
                        "Manufacturing/industrial",
                        "Transportation",
                        "Retail/service",
                        "Outdoor work scenes"
                    ]
                },
                "part2": {
                    "name": "Question-Response",
                    "questions": 25,
                    "description": "Listen to a question and select best response",
                    "question_types": [
                        "Yes/No questions",
                        "Wh- questions (who, what, where, when, why, how)",
                        "Choice questions",
                        "Tag questions",
                        "Statements requiring response"
                    ]
                },
                "part3": {
                    "name": "Conversations",
                    "questions": 39,
                    "description": "Listen to conversations between 2-3 people",
                    "conversation_contexts": [
                        "Office discussions",
                        "Customer service",
                        "Business meetings",
                        "Phone conversations",
                        "Travel arrangements",
                        "Project planning"
                    ],
                    "question_types": ["main idea", "detail", "inference", "speaker intent"]
                },
                "part4": {
                    "name": "Talks",
                    "questions": 30,
                    "description": "Listen to short monologues",
                    "talk_types": [
                        "Announcements",
                        "Voicemail messages",
                        "News reports",
                        "Advertisements",
                        "Introductions/speeches",
                        "Instructions/directions"
                    ]
                }
            }
        },

        "reading": {
            "time_limit": 75,
            "questions": 100,
            "parts": {
                "part5": {
                    "name": "Incomplete Sentences",
                    "questions": 30,
                    "description": "Choose word/phrase to complete sentence",
                    "grammar_focus": [
                        "Verb tenses",
                        "Parts of speech",
                        "Prepositions",
                        "Conjunctions",
                        "Word forms",
                        "Subject-verb agreement"
                    ]
                },
                "part6": {
                    "name": "Text Completion",
                    "questions": 16,
                    "description": "Complete texts with missing sentences/words",
                    "text_types": [
                        "Emails",
                        "Letters",
                        "Notices",
                        "Articles",
                        "Advertisements"
                    ]
                },
                "part7": {
                    "name": "Reading Comprehension",
                    "questions": 54,
                    "description": "Read passages and answer questions",
                    "passage_types": {
                        "single_passages": [
                            "Emails and letters",
                            "Memos",
                            "Advertisements",
                            "Notices and announcements",
                            "Articles",
                            "Schedules and forms"
                        ],
                        "multiple_passages": [
                            "Related emails",
                            "Article with comments",
                            "Advertisement with review",
                            "Form with correspondence"
                        ]
                    }
                }
            }
        }
    },

    "speaking_writing": {
        "speaking": {
            "time_limit": 20,
            "questions": 11,
            "tasks": {
                "q1_2": {
                    "name": "Read a text aloud",
                    "count": 2,
                    "prep_time": 45,
                    "response_time": 45,
                    "text_types": ["advertisement", "announcement", "instruction"]
                },
                "q3": {
                    "name": "Describe a picture",
                    "count": 1,
                    "prep_time": 45,
                    "response_time": 30,
                    "picture_types": ["workplace scene", "business event", "daily activity"]
                },
                "q4_6": {
                    "name": "Respond to questions",
                    "count": 3,
                    "prep_time": 0,
                    "response_time": "15-30 each",
                    "topics": ["daily life", "personal experience", "business situations"]
                },
                "q7_9": {
                    "name": "Respond to questions using provided information",
                    "count": 3,
                    "prep_time": 45,
                    "response_time": "15-30 each",
                    "info_types": ["schedule", "agenda", "itinerary", "table"]
                },
                "q10": {
                    "name": "Propose a solution",
                    "count": 1,
                    "prep_time": 45,
                    "response_time": 60,
                    "scenario_types": ["customer complaint", "workplace problem", "scheduling conflict"]
                },
                "q11": {
                    "name": "Express an opinion",
                    "count": 1,
                    "prep_time": 45,
                    "response_time": 60,
                    "topics": ["business decisions", "workplace policies", "professional practices"]
                }
            }
        },

        "writing": {
            "time_limit": 60,
            "questions": 8,
            "tasks": {
                "q1_5": {
                    "name": "Write a sentence based on a picture",
                    "count": 5,
                    "time_per_question": "8 minutes total",
                    "description": "Write one sentence using two given words"
                },
                "q6_7": {
                    "name": "Respond to a written request",
                    "count": 2,
                    "time_per_question": 10,
                    "word_count": "minimum 50",
                    "request_types": ["email", "message", "inquiry"]
                },
                "q8": {
                    "name": "Write an opinion essay",
                    "count": 1,
                    "time_limit": 30,
                    "word_count": "minimum 300",
                    "topics": [
                        "Business decisions and practices",
                        "Workplace policies",
                        "Professional development",
                        "Work-life balance",
                        "Technology in workplace"
                    ]
                }
            }
        }
    },

    "common_business_topics": [
        {
            "category": "Corporate Development",
            "topics": ["mergers", "acquisitions", "company restructuring", "expansion"]
        },
        {
            "category": "Personnel",
            "topics": ["hiring", "training", "promotions", "benefits", "retirement"]
        },
        {
            "category": "Finance",
            "topics": ["budgets", "investments", "banking", "accounting", "taxes"]
        },
        {
            "category": "Marketing",
            "topics": ["advertising", "sales", "market research", "product launches"]
        },
        {
            "category": "Travel",
            "topics": ["business trips", "conferences", "hotels", "transportation"]
        },
        {
            "category": "Office Operations",
            "topics": ["meetings", "scheduling", "supplies", "equipment", "facilities"]
        },
        {
            "category": "Manufacturing",
            "topics": ["production", "quality control", "assembly", "shipping"]
        },
        {
            "category": "Technology",
            "topics": ["computers", "software", "electronics", "technical support"]
        }
    ],

    "scoring": {
        "listening_reading": {
            "scale": "10-990",
            "listening_max": 495,
            "reading_max": 495
        },
        "speaking_writing": {
            "speaking_scale": "0-200",
            "writing_scale": "0-200"
        }
    }
}


# =============================================================================
# COMPLETE TOPIC REGISTRY
# =============================================================================

ALL_EXAM_TOPICS = {
    # IELTS
    "ielts_academic": IELTS_TOPICS,
    "ielts_general": IELTS_TOPICS,

    # Cambridge
    "cambridge_b2_first": CAMBRIDGE_TOPICS["b2_first"],
    "cambridge_c1_advanced": CAMBRIDGE_TOPICS["c1_advanced"],

    # TOEFL
    "toefl_ibt": TOEFL_TOPICS,

    # PTE
    "pte_academic": PTE_TOPICS,

    # TOEIC
    "toeic": TOEIC_TOPICS,

    # OET - All 12 professions
    "oet_medicine": get_oet_topics("medicine"),
    "oet_nursing": get_oet_topics("nursing"),
    "oet_dentistry": get_oet_topics("dentistry"),
    "oet_pharmacy": get_oet_topics("pharmacy"),
    "oet_physiotherapy": get_oet_topics("physiotherapy"),
    "oet_occupational_therapy": get_oet_topics("occupational_therapy"),
    "oet_dietetics": get_oet_topics("dietetics"),
    "oet_speech_pathology": get_oet_topics("speech_pathology"),
    "oet_podiatry": get_oet_topics("podiatry"),
    "oet_optometry": get_oet_topics("optometry"),
    "oet_radiography": get_oet_topics("radiography"),
    "oet_veterinary_science": get_oet_topics("veterinary_science"),
}

# Available exams for institutional selection
AVAILABLE_EXAMS = {
    "ielts": {
        "name": "IELTS",
        "variants": ["ielts_academic", "ielts_general"],
        "description": "International English Language Testing System"
    },
    "toefl": {
        "name": "TOEFL",
        "variants": ["toefl_ibt"],
        "description": "Test of English as a Foreign Language"
    },
    "cambridge": {
        "name": "Cambridge",
        "variants": ["cambridge_b2_first", "cambridge_c1_advanced"],
        "description": "Cambridge English Qualifications"
    },
    "pte": {
        "name": "PTE Academic",
        "variants": ["pte_academic"],
        "description": "Pearson Test of English Academic"
    },
    "toeic": {
        "name": "TOEIC",
        "variants": ["toeic"],
        "description": "Test of English for International Communication"
    },
    "oet": {
        "name": "OET",
        "variants": [f"oet_{p}" for p in OET_PROFESSIONS],
        "description": "Occupational English Test (12 healthcare professions)",
        "professions": OET_PROFESSIONS
    }
}


def get_all_topics_for_exam(exam_type: str) -> Dict[str, Any]:
    """Get all topics configured for an exam type."""
    return ALL_EXAM_TOPICS.get(exam_type, IELTS_TOPICS)


def get_available_exams() -> Dict[str, Any]:
    """Get list of all available exams for institutional selection."""
    return AVAILABLE_EXAMS


def get_oet_professions() -> List[str]:
    """Get list of all OET professions."""
    return OET_PROFESSIONS
