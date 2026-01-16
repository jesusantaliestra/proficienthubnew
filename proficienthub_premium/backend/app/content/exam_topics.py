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
