# exam_questions.py - Comprehensive exam question bank
# Contains real-style questions for TOEFL, IELTS, Cambridge, PTE, OET

READING_PASSAGES = {
    "toefl": [
        {
            "id": "toefl_r1",
            "title": "The Evolution of Urban Planning",
            "passage": """Urban planning has undergone significant transformations since its inception in the late 19th century. Initially focused on addressing the unsanitary conditions of rapidly industrializing cities, early planners like Ebenezer Howard envisioned "garden cities" that would combine the best aspects of urban and rural living. These planned communities featured green spaces, residential areas, and industrial zones carefully separated to promote health and well-being.

The modernist movement of the mid-20th century brought a radical shift in urban planning philosophy. Architects like Le Corbusier advocated for high-rise buildings surrounded by open spaces, believing that vertical construction could solve urban crowding while preserving land for parks and recreation. This "towers in the park" concept influenced countless housing projects worldwide, though many later proved socially problematic.

Contemporary urban planning has embraced sustainability and mixed-use development. The New Urbanism movement promotes walkable neighborhoods with diverse housing types, local shops, and accessible public transportation. Smart city initiatives leverage technology to optimize traffic flow, reduce energy consumption, and improve public services. Today's planners recognize that successful cities must balance economic growth, environmental protection, and social equity.""",
            "questions": [
                {
                    "id": "toefl_r1_q1",
                    "type": "multiple_choice",
                    "question": "According to the passage, what was the primary focus of early urban planners?",
                    "options": [
                        "A) Creating beautiful architectural designs",
                        "B) Addressing unsanitary conditions in industrial cities",
                        "C) Maximizing economic productivity",
                        "D) Building high-rise apartments"
                    ],
                    "correct_answer": "B"
                },
                {
                    "id": "toefl_r1_q2",
                    "type": "multiple_choice",
                    "question": "What can be inferred about Le Corbusier's 'towers in the park' concept?",
                    "options": [
                        "A) It was universally successful",
                        "B) It completely solved urban crowding",
                        "C) It had unintended social consequences",
                        "D) It was never implemented"
                    ],
                    "correct_answer": "C"
                },
                {
                    "id": "toefl_r1_q3",
                    "type": "vocabulary",
                    "question": "The word 'leverage' in paragraph 3 is closest in meaning to:",
                    "options": [
                        "A) avoid",
                        "B) utilize",
                        "C) destroy",
                        "D) simplify"
                    ],
                    "correct_answer": "B"
                }
            ]
        },
        {
            "id": "toefl_r2",
            "title": "Photosynthesis and Climate Change",
            "passage": """Photosynthesis, the process by which plants convert sunlight into chemical energy, plays a crucial role in regulating Earth's climate. Through this process, plants absorb carbon dioxide from the atmosphere and release oxygen, effectively acting as carbon sinks that mitigate the greenhouse effect. Scientists estimate that terrestrial plants absorb approximately 25% of human-generated carbon dioxide emissions annually.

However, rising global temperatures are affecting photosynthetic efficiency in complex ways. While increased CO2 levels can initially boost plant growth—a phenomenon known as CO2 fertilization—extreme heat can damage the cellular machinery responsible for photosynthesis. Studies show that when temperatures exceed optimal ranges, plants may actually release more carbon than they absorb, potentially accelerating climate change.

Researchers are exploring various strategies to enhance photosynthetic efficiency. Genetic engineering approaches aim to modify the Rubisco enzyme, which plays a central role in carbon fixation but operates inefficiently in warm conditions. Other scientists are developing artificial photosynthesis systems that could capture carbon dioxide more effectively than natural plants, potentially offering a technological solution to climate change.""",
            "questions": [
                {
                    "id": "toefl_r2_q1",
                    "type": "multiple_choice",
                    "question": "What percentage of human carbon dioxide emissions do terrestrial plants absorb?",
                    "options": [
                        "A) About 10%",
                        "B) About 25%",
                        "C) About 50%",
                        "D) About 75%"
                    ],
                    "correct_answer": "B"
                },
                {
                    "id": "toefl_r2_q2",
                    "type": "inference",
                    "question": "The passage suggests that CO2 fertilization:",
                    "options": [
                        "A) Always benefits plant growth",
                        "B) Has only negative effects",
                        "C) Has limited benefits in extreme conditions",
                        "D) Is the main cause of climate change"
                    ],
                    "correct_answer": "C"
                }
            ]
        }
    ],
    "ielts": [
        {
            "id": "ielts_r1",
            "title": "The Psychology of Consumer Behavior",
            "passage": """Understanding why consumers make particular purchasing decisions has become increasingly important in today's competitive marketplace. Researchers have identified several psychological factors that influence buying behavior, ranging from emotional triggers to cognitive biases that shape our perception of value.

One significant factor is social proof—the tendency to look at others' behavior when making decisions. Reviews, testimonials, and popularity indicators strongly influence purchase choices, particularly for unfamiliar products. Scarcity also plays a powerful role; limited availability creates urgency and increases perceived value. Marketers frequently employ countdown timers and "only X left in stock" messages to trigger this response.

The anchoring effect demonstrates how initial information disproportionately influences subsequent judgments. When consumers see an original price crossed out next to a sale price, they perceive greater value even if the "original" price was artificially inflated. Similarly, the paradox of choice suggests that while consumers appreciate options, too many alternatives can lead to decision paralysis and reduced satisfaction with eventual purchases.""",
            "questions": [
                {
                    "id": "ielts_r1_q1",
                    "type": "true_false_not_given",
                    "question": "Social proof is most effective for products consumers are already familiar with.",
                    "options": ["True", "False", "Not Given"],
                    "correct_answer": "False"
                },
                {
                    "id": "ielts_r1_q2",
                    "type": "true_false_not_given",
                    "question": "The anchoring effect can be manipulated by setting artificial original prices.",
                    "options": ["True", "False", "Not Given"],
                    "correct_answer": "True"
                },
                {
                    "id": "ielts_r1_q3",
                    "type": "matching",
                    "question": "Which psychological principle explains why 'limited time offers' are effective?",
                    "options": [
                        "A) Social proof",
                        "B) Scarcity",
                        "C) Anchoring effect",
                        "D) Paradox of choice"
                    ],
                    "correct_answer": "B"
                }
            ]
        }
    ]
}

LISTENING_QUESTIONS = {
    "ielts": [
        {
            "id": "ielts_l1",
            "type": "form_completion",
            "title": "University Library Registration",
            "instructions": "Complete the form below. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
            "audio_transcript": "Good morning, I'd like to register for a library card please. My name is Sarah Mitchell, that's M-I-T-C-H-E-L-L. I'm a new student in the Environmental Science department. My student ID is ES2024-0847. I live at 15 Oak Street, apartment 3B. My phone number is 555-0173. I'd like to borrow mainly science journals and textbooks.",
            "questions": [
                {"id": "l1_q1", "blank": "Name: Sarah _____", "answer": "Mitchell"},
                {"id": "l1_q2", "blank": "Department: _____ Science", "answer": "Environmental"},
                {"id": "l1_q3", "blank": "Student ID: _____", "answer": "ES2024-0847"},
                {"id": "l1_q4", "blank": "Address: 15 _____ Street", "answer": "Oak"}
            ]
        }
    ],
    "toefl": [
        {
            "id": "toefl_l1",
            "type": "lecture",
            "title": "Marine Biology: Coral Reef Ecosystems",
            "audio_transcript": "Today we'll examine coral reef ecosystems, often called the rainforests of the sea due to their incredible biodiversity. Coral reefs cover less than one percent of the ocean floor, yet they support approximately 25 percent of all marine species. The foundation of these ecosystems is the coral polyp, a tiny animal that forms a symbiotic relationship with photosynthetic algae called zooxanthellae. This partnership is remarkably sensitive to temperature changes—a rise of just one to two degrees Celsius can cause coral bleaching, where the coral expels its algae partner.",
            "questions": [
                {
                    "id": "toefl_l1_q1",
                    "type": "multiple_choice",
                    "question": "Why does the professor compare coral reefs to rainforests?",
                    "options": [
                        "A) They have similar temperatures",
                        "B) They both have high biodiversity",
                        "C) They cover similar areas",
                        "D) They face the same threats"
                    ],
                    "correct_answer": "B"
                },
                {
                    "id": "toefl_l1_q2",
                    "type": "multiple_choice",
                    "question": "What percentage of the ocean floor do coral reefs cover?",
                    "options": [
                        "A) Less than 1%",
                        "B) About 10%",
                        "C) About 25%",
                        "D) More than 50%"
                    ],
                    "correct_answer": "A"
                }
            ]
        }
    ]
}

WRITING_TASKS = {
    "ielts": {
        "task1": [
            {
                "id": "ielts_w1_1",
                "type": "graph_description",
                "prompt": "The bar chart below shows the percentage of households with internet access in five different countries between 2000 and 2020. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "graph_data": {
                    "countries": ["USA", "UK", "Japan", "Brazil", "India"],
                    "2000": [42, 26, 29, 3, 0.5],
                    "2010": [71, 77, 78, 41, 7.5],
                    "2020": [90, 94, 93, 81, 50]
                },
                "min_words": 150,
                "time_minutes": 20
            }
        ],
        "task2": [
            {
                "id": "ielts_w2_1",
                "type": "essay",
                "prompt": "Some people believe that unpaid community service should be a compulsory part of high school programs. To what extent do you agree or disagree?",
                "min_words": 250,
                "time_minutes": 40,
                "criteria": ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            },
            {
                "id": "ielts_w2_2",
                "type": "essay",
                "prompt": "In many countries, the proportion of older people is steadily increasing. Does this trend have more positive or negative effects on society?",
                "min_words": 250,
                "time_minutes": 40,
                "criteria": ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            }
        ]
    },
    "toefl": {
        "integrated": [
            {
                "id": "toefl_wi_1",
                "type": "integrated",
                "reading": "Recent studies have suggested that homework has limited educational benefits for elementary school students. Research indicates that young children learn more effectively through play-based activities and hands-on experiences. Furthermore, excessive homework can lead to stress and burnout, potentially creating negative attitudes toward learning.",
                "prompt": "Summarize the points made in the lecture, explaining how they cast doubt on specific points made in the reading passage.",
                "min_words": 150,
                "max_words": 225,
                "time_minutes": 20
            }
        ],
        "independent": [
            {
                "id": "toefl_wi_1",
                "type": "independent",
                "prompt": "Do you agree or disagree with the following statement? Students should be required to take classes in subjects outside their major field of study. Use specific reasons and examples to support your answer.",
                "min_words": 300,
                "time_minutes": 30
            }
        ]
    }
}

SPEAKING_PROMPTS = {
    "ielts": {
        "part1": [
            {
                "id": "ielts_s1_1",
                "topic": "Home",
                "questions": [
                    "Let's talk about your home. Do you live in a house or an apartment?",
                    "What's your favorite room in your home? Why?",
                    "Would you like to move to a different home in the future?",
                    "How long have you lived in your current home?"
                ],
                "time_per_question": 30
            },
            {
                "id": "ielts_s1_2",
                "topic": "Work/Study",
                "questions": [
                    "Do you work or are you a student?",
                    "What do you like most about your job/studies?",
                    "Would you like to change your job/field of study?",
                    "What are your future career plans?"
                ],
                "time_per_question": 30
            }
        ],
        "part2": [
            {
                "id": "ielts_s2_1",
                "topic": "Describe a book that you have read recently",
                "cue_card": "You should say:\n- what the book was about\n- why you decided to read it\n- how long it took you to read it\n- and explain whether you would recommend this book to others",
                "preparation_time": 60,
                "speaking_time": 120
            },
            {
                "id": "ielts_s2_2",
                "topic": "Describe a place you would like to visit",
                "cue_card": "You should say:\n- where the place is\n- how you know about this place\n- what you would do there\n- and explain why you want to visit this place",
                "preparation_time": 60,
                "speaking_time": 120
            }
        ],
        "part3": [
            {
                "id": "ielts_s3_1",
                "topic": "Reading and Books",
                "questions": [
                    "Do you think reading habits have changed over time?",
                    "Why do some people prefer e-books while others prefer printed books?",
                    "How important is it for children to develop reading habits?",
                    "Do you think books will eventually be replaced by digital media?"
                ],
                "time_per_question": 60
            }
        ]
    },
    "toefl": {
        "independent": [
            {
                "id": "toefl_si_1",
                "prompt": "Some people prefer to work for a large company, while others prefer to work for a small company. Which do you prefer and why?",
                "preparation_time": 15,
                "speaking_time": 45
            },
            {
                "id": "toefl_si_2",
                "prompt": "Describe a person who has had a significant influence on your life. Explain why this person is important to you.",
                "preparation_time": 15,
                "speaking_time": 45
            }
        ],
        "integrated": [
            {
                "id": "toefl_sint_1",
                "reading": "The university is planning to convert a large portion of the student parking lot into a green space with gardens and walking paths.",
                "prompt": "The student expresses her opinion about the university's plan. State her opinion and explain the reasons she gives for holding that opinion.",
                "preparation_time": 30,
                "speaking_time": 60
            }
        ]
    }
}

# Full mock test configurations
MOCK_TESTS = {
    "ielts_academic": {
        "name": "IELTS Academic Full Test",
        "duration_minutes": 175,
        "sections": [
            {"name": "Listening", "duration": 30, "questions": 40},
            {"name": "Reading", "duration": 60, "questions": 40},
            {"name": "Writing", "duration": 60, "tasks": 2},
            {"name": "Speaking", "duration": 15, "parts": 3}
        ]
    },
    "toefl_ibt": {
        "name": "TOEFL iBT Full Test",
        "duration_minutes": 180,
        "sections": [
            {"name": "Reading", "duration": 54, "questions": 30},
            {"name": "Listening", "duration": 41, "questions": 28},
            {"name": "Speaking", "duration": 17, "tasks": 4},
            {"name": "Writing", "duration": 50, "tasks": 2}
        ]
    },
    "cambridge_cae": {
        "name": "Cambridge C1 Advanced (CAE)",
        "duration_minutes": 235,
        "sections": [
            {"name": "Reading and Use of English", "duration": 90, "questions": 56},
            {"name": "Writing", "duration": 90, "tasks": 2},
            {"name": "Listening", "duration": 40, "questions": 30},
            {"name": "Speaking", "duration": 15, "parts": 4}
        ]
    },
    "pte_academic": {
        "name": "PTE Academic Full Test",
        "duration_minutes": 180,
        "sections": [
            {"name": "Speaking & Writing", "duration": 77, "questions": 28},
            {"name": "Reading", "duration": 32, "questions": 20},
            {"name": "Listening", "duration": 45, "questions": 23}
        ]
    },
    "oet": {
        "name": "OET Full Test",
        "duration_minutes": 170,
        "sections": [
            {"name": "Listening", "duration": 45, "questions": 42},
            {"name": "Reading", "duration": 60, "questions": 42},
            {"name": "Writing", "duration": 45, "tasks": 1},
            {"name": "Speaking", "duration": 20, "role_plays": 2}
        ]
    }
}

def get_exam_questions(exam_type: str, section: str, count: int = 5):
    """Get questions for a specific exam type and section"""
    questions = []
    
    if section == "reading":
        passages = READING_PASSAGES.get(exam_type, READING_PASSAGES.get("ielts", []))
        for passage in passages[:count]:
            questions.append({
                "passage": passage,
                "questions": passage.get("questions", [])
            })
    
    elif section == "listening":
        listening = LISTENING_QUESTIONS.get(exam_type, LISTENING_QUESTIONS.get("ielts", []))
        questions = listening[:count]
    
    elif section == "writing":
        writing = WRITING_TASKS.get(exam_type, WRITING_TASKS.get("ielts", {}))
        if "task2" in writing:
            questions = writing["task2"][:count]
        elif "independent" in writing:
            questions = writing["independent"][:count]
    
    elif section == "speaking":
        speaking = SPEAKING_PROMPTS.get(exam_type, SPEAKING_PROMPTS.get("ielts", {}))
        if "part2" in speaking:
            questions = speaking["part2"][:count]
        elif "independent" in speaking:
            questions = speaking["independent"][:count]
    
    return questions

def get_mock_test_config(exam_type: str):
    """Get full mock test configuration"""
    configs = {
        "ielts": MOCK_TESTS["ielts_academic"],
        "toefl": MOCK_TESTS["toefl_ibt"],
        "cambridge": MOCK_TESTS["cambridge_cae"],
        "pte": MOCK_TESTS["pte_academic"],
        "oet": MOCK_TESTS["oet"]
    }
    return configs.get(exam_type, configs["ielts"])
