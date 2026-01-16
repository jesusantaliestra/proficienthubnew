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
# OET (Occupational English Test) TOPICS - MEDICINE
# =============================================================================

OET_TOPICS = {
    "professions": [
        "Medicine", "Nursing", "Dentistry", "Pharmacy",
        "Physiotherapy", "Occupational Therapy", "Dietetics",
        "Speech Pathology", "Podiatry", "Optometry",
        "Radiography", "Veterinary Science"
    ],

    "listening": {
        "part_a": {
            "name": "Consultation Extracts",
            "description": "Two recorded health professional-patient consultations",
            "duration": "5 minutes each",
            "question_types": ["note completion", "gap fill"],
            "common_scenarios": [
                {
                    "scenario": "Initial patient assessment",
                    "topics": ["presenting complaint", "medical history", "symptoms"]
                },
                {
                    "scenario": "Follow-up consultation",
                    "topics": ["treatment progress", "medication review", "test results"]
                },
                {
                    "scenario": "Specialist referral discussion",
                    "topics": ["diagnosis explanation", "treatment options", "prognosis"]
                },
                {
                    "scenario": "Discharge planning",
                    "topics": ["home care instructions", "medication schedule", "follow-up appointments"]
                }
            ]
        },
        "part_b": {
            "name": "Short Workplace Extracts",
            "description": "Six short recordings of healthcare workplace communications",
            "duration": "1 minute each",
            "question_types": ["multiple choice"],
            "communication_types": [
                "Team briefings",
                "Handover reports",
                "Phone conversations",
                "Patient instructions",
                "Colleague discussions",
                "Health presentations"
            ]
        },
        "part_c": {
            "name": "Presentation Extracts",
            "description": "Two longer recordings (interviews, presentations)",
            "duration": "5 minutes each",
            "question_types": ["multiple choice"],
            "content_types": [
                "Health policy discussions",
                "Medical research presentations",
                "Patient care guidelines",
                "Healthcare service updates"
            ]
        }
    },

    "reading": {
        "part_a": {
            "name": "Expeditious Reading",
            "description": "Quick reading to locate specific information",
            "time_limit": 15,
            "text_types": [
                "Patient information leaflets",
                "Hospital guidelines",
                "Medical device instructions",
                "Healthcare facility procedures"
            ],
            "question_types": ["matching", "sentence completion", "short answer"]
        },
        "part_b": {
            "name": "Careful Reading (Short Texts)",
            "description": "Detailed reading of healthcare workplace texts",
            "text_types": [
                "Hospital policy documents",
                "Clinical guidelines",
                "Patient safety protocols",
                "Professional development notices"
            ],
            "question_types": ["multiple choice", "matching headings"]
        },
        "part_c": {
            "name": "Careful Reading (Long Texts)",
            "description": "Two longer texts requiring detailed comprehension",
            "text_types": [
                "Medical journal articles",
                "Research summaries",
                "Healthcare editorials",
                "Clinical case studies"
            ],
            "question_types": ["multiple choice"],
            "skills_tested": [
                "Understanding main ideas",
                "Identifying supporting details",
                "Making inferences",
                "Understanding writer's opinion"
            ]
        }
    },

    "writing": {
        "description": "Write a referral letter based on case notes",
        "time_limit": 45,
        "word_count": "180-200",
        "letter_types": [
            {
                "type": "Referral letter",
                "purpose": "Referring patient to specialist",
                "common_scenarios": [
                    "GP to specialist referral",
                    "Hospital to community care",
                    "Specialist to rehabilitation"
                ]
            },
            {
                "type": "Discharge letter",
                "purpose": "Summarizing hospital stay and care plan",
                "common_scenarios": [
                    "Post-surgery discharge",
                    "Chronic condition management",
                    "Mental health care transfer"
                ]
            },
            {
                "type": "Transfer letter",
                "purpose": "Transferring care between facilities",
                "common_scenarios": [
                    "Nursing home admission",
                    "Rehabilitation facility transfer",
                    "Palliative care referral"
                ]
            }
        ],
        "assessment_criteria": [
            {
                "criterion": "Purpose",
                "weight": "high",
                "description": "Clear communication of referral reason"
            },
            {
                "criterion": "Content",
                "weight": "high",
                "description": "Relevant selection from case notes"
            },
            {
                "criterion": "Conciseness and clarity",
                "weight": "medium",
                "description": "Appropriate length and clear expression"
            },
            {
                "criterion": "Genre and style",
                "weight": "medium",
                "description": "Appropriate letter format and professional tone"
            },
            {
                "criterion": "Organization and layout",
                "weight": "medium",
                "description": "Logical structure and paragraphing"
            },
            {
                "criterion": "Language",
                "weight": "high",
                "description": "Grammar, vocabulary, spelling, punctuation"
            }
        ],
        "common_medical_topics": [
            {
                "condition": "Cardiovascular",
                "examples": ["Chest pain", "Hypertension", "Heart failure", "Arrhythmia"]
            },
            {
                "condition": "Respiratory",
                "examples": ["Asthma", "COPD", "Pneumonia", "Sleep apnea"]
            },
            {
                "condition": "Musculoskeletal",
                "examples": ["Back pain", "Arthritis", "Fractures", "Sports injuries"]
            },
            {
                "condition": "Neurological",
                "examples": ["Headaches", "Stroke", "Epilepsy", "Parkinson's"]
            },
            {
                "condition": "Mental Health",
                "examples": ["Depression", "Anxiety", "Dementia", "Substance abuse"]
            },
            {
                "condition": "Endocrine",
                "examples": ["Diabetes", "Thyroid disorders", "Obesity"]
            },
            {
                "condition": "Gastrointestinal",
                "examples": ["Abdominal pain", "IBD", "Liver disease", "Reflux"]
            },
            {
                "condition": "Oncology",
                "examples": ["Cancer screening", "Treatment planning", "Palliative care"]
            }
        ]
    },

    "speaking": {
        "description": "Role-play with an interlocutor (simulated patient/carer)",
        "time_limit": 20,
        "structure": {
            "warm_up": {
                "duration": "2-3 minutes",
                "purpose": "General conversation about profession and experience"
            },
            "role_plays": {
                "number": 2,
                "duration": "5 minutes each",
                "preparation": "2-3 minutes to read role card"
            }
        },
        "role_play_scenarios": [
            {
                "category": "Explaining diagnosis",
                "scenarios": [
                    "Breaking bad news sensitively",
                    "Explaining test results",
                    "Discussing treatment options"
                ]
            },
            {
                "category": "Gathering information",
                "scenarios": [
                    "Taking patient history",
                    "Assessing pain levels",
                    "Identifying symptoms"
                ]
            },
            {
                "category": "Providing instructions",
                "scenarios": [
                    "Medication instructions",
                    "Pre-procedure preparation",
                    "Post-operative care"
                ]
            },
            {
                "category": "Managing difficult situations",
                "scenarios": [
                    "Dealing with anxious patient",
                    "Addressing non-compliance",
                    "Handling complaints"
                ]
            },
            {
                "category": "Counseling and support",
                "scenarios": [
                    "Lifestyle advice",
                    "Smoking cessation",
                    "Mental health support"
                ]
            }
        ],
        "assessment_criteria": [
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
}


# =============================================================================
# DUOLINGO ENGLISH TEST (DET) TOPICS
# =============================================================================

DUOLINGO_TOPICS = {
    "adaptive_test": {
        "description": "Computer-adaptive test that adjusts difficulty based on performance",
        "duration": 60,
        "sections": [
            {
                "name": "Read and Complete",
                "description": "Fill in missing letters in words within sentences",
                "skills": ["vocabulary", "grammar", "spelling"]
            },
            {
                "name": "Read and Select",
                "description": "Identify real English words from a list",
                "skills": ["vocabulary recognition"]
            },
            {
                "name": "Listen and Type",
                "description": "Type what you hear",
                "skills": ["listening", "spelling"]
            },
            {
                "name": "Read Aloud",
                "description": "Read a sentence aloud",
                "skills": ["pronunciation", "fluency"]
            },
            {
                "name": "Write About the Photo",
                "description": "Describe an image in writing",
                "skills": ["writing", "vocabulary"]
            },
            {
                "name": "Speak About the Photo",
                "description": "Describe an image verbally",
                "skills": ["speaking", "vocabulary"]
            },
            {
                "name": "Read, Then Write",
                "description": "Read a prompt and write a response",
                "skills": ["reading comprehension", "writing"]
            },
            {
                "name": "Read, Then Speak",
                "description": "Read a question and respond verbally",
                "skills": ["reading", "speaking"]
            },
            {
                "name": "Listen, Then Speak",
                "description": "Listen to a question and respond",
                "skills": ["listening", "speaking"]
            },
            {
                "name": "Interactive Reading",
                "description": "Complete sentences in a passage",
                "skills": ["reading", "grammar"]
            },
            {
                "name": "Interactive Listening",
                "description": "Identify words and complete sentences from audio",
                "skills": ["listening", "vocabulary"]
            }
        ]
    },
    "writing_sample_topics": [
        "Describe an important tradition in your culture",
        "What qualities make a good leader?",
        "Should students have homework?",
        "Describe your favorite place to relax",
        "What is an important skill everyone should learn?"
    ],
    "speaking_sample_topics": [
        "Describe your hometown",
        "Talk about a person who has influenced you",
        "What do you like to do in your free time?",
        "Describe a challenging experience",
        "What are your future goals?"
    ]
}


# =============================================================================
# COMPLETE TOPIC REGISTRY
# =============================================================================

ALL_EXAM_TOPICS = {
    "ielts_academic": IELTS_TOPICS,
    "ielts_general": IELTS_TOPICS,  # Uses same topics with different reading texts
    "cambridge_b2_first": CAMBRIDGE_TOPICS["b2_first"],
    "cambridge_c1_advanced": CAMBRIDGE_TOPICS["c1_advanced"],
    "toefl_ibt": TOEFL_TOPICS,
    "pte_academic": PTE_TOPICS,
    "oet_medicine": OET_TOPICS,
    "duolingo": DUOLINGO_TOPICS,
}


def get_all_topics_for_exam(exam_type: str) -> Dict[str, Any]:
    """Obtiene todos los topics configurados para un tipo de examen"""
    return ALL_EXAM_TOPICS.get(exam_type, IELTS_TOPICS)
