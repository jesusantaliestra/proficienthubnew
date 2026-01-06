# exam_questions.py - Main exam question loader
# Imports from all exam banks and provides unified access

import os
import sys

# Add exam_banks directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from exam_banks.ielts_bank import IELTS_READING_PASSAGES, IELTS_ADDITIONAL_PASSAGES
    from exam_banks.toefl_bank import TOEFL_READING_PASSAGES, TOEFL_SPEAKING_PROMPTS, TOEFL_WRITING_TASKS
    from exam_banks.other_exams_bank import (
        CAMBRIDGE_READING_PASSAGES, CAMBRIDGE_SPEAKING_PROMPTS,
        PTE_READING_PASSAGES,
        OET_READING_PASSAGES, OET_WRITING_TASKS, OET_SPEAKING_PROMPTS
    )
except ImportError:
    # Fallback if modules not available
    IELTS_READING_PASSAGES = []
    IELTS_ADDITIONAL_PASSAGES = []
    TOEFL_READING_PASSAGES = []
    TOEFL_SPEAKING_PROMPTS = []
    TOEFL_WRITING_TASKS = []
    CAMBRIDGE_READING_PASSAGES = []
    CAMBRIDGE_SPEAKING_PROMPTS = []
    PTE_READING_PASSAGES = []
    OET_READING_PASSAGES = []
    OET_WRITING_TASKS = []
    OET_SPEAKING_PROMPTS = []

# Combine all IELTS passages
ALL_IELTS_PASSAGES = IELTS_READING_PASSAGES + IELTS_ADDITIONAL_PASSAGES

# Full mock test configurations
MOCK_TESTS = {
    "ielts_academic": {
        "name": "IELTS Academic Full Test",
        "total_exams": 20,
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
        "total_exams": 20,
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
        "total_exams": 20,
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
        "total_exams": 20,
        "duration_minutes": 180,
        "sections": [
            {"name": "Speaking & Writing", "duration": 77, "questions": 28},
            {"name": "Reading", "duration": 32, "questions": 20},
            {"name": "Listening", "duration": 45, "questions": 23}
        ]
    },
    "oet": {
        "name": "OET Full Test",
        "total_exams": 20,
        "duration_minutes": 170,
        "sections": [
            {"name": "Listening", "duration": 45, "questions": 42},
            {"name": "Reading", "duration": 60, "questions": 42},
            {"name": "Writing", "duration": 45, "tasks": 1},
            {"name": "Speaking", "duration": 20, "role_plays": 2}
        ]
    }
}

# Speaking prompts organized by exam type
SPEAKING_PROMPTS = {
    "ielts": {
        "part1": [
            {"id": f"ielts_s1_{i}", "topic": topic, "questions": questions, "time_per_question": 30}
            for i, (topic, questions) in enumerate([
                ("Home", ["Do you live in a house or an apartment?", "What's your favorite room?", "Would you like to move?", "How long have you lived there?"]),
                ("Work/Study", ["Do you work or study?", "What do you like about your job/studies?", "Would you change careers?", "Future plans?"]),
                ("Hometown", ["Where are you from?", "What do you like about it?", "Has it changed much?", "Would you recommend it to visitors?"]),
                ("Food", ["What's your favorite food?", "Do you cook?", "Are there any foods you dislike?", "Has your diet changed?"]),
                ("Technology", ["Do you use technology often?", "What device is most important to you?", "How has technology changed your life?", "Any technology you avoid?"]),
                ("Sports", ["Do you play any sports?", "What sports are popular in your country?", "Did you play sports as a child?", "Would you like to try a new sport?"]),
                ("Reading", ["Do you enjoy reading?", "What types of books?", "Do you prefer physical or digital books?", "Did you read more as a child?"]),
                ("Music", ["Do you listen to music?", "What genre do you prefer?", "Can you play any instruments?", "Has your taste in music changed?"]),
                ("Travel", ["Do you like to travel?", "Where have you been?", "Where would you like to go?", "Do you prefer traveling alone or with others?"]),
                ("Shopping", ["Do you like shopping?", "Online or in stores?", "What do you usually buy?", "Has the way you shop changed?"])
            ], start=1)
        ],
        "part2": [
            {
                "id": f"ielts_s2_{i}",
                "topic": topic,
                "cue_card": cue_card,
                "preparation_time": 60,
                "speaking_time": 120
            } for i, (topic, cue_card) in enumerate([
                ("Describe a book you have read recently", "You should say:\n- what the book was about\n- why you decided to read it\n- how long it took you to read\n- and explain if you would recommend it"),
                ("Describe a place you would like to visit", "You should say:\n- where the place is\n- how you learned about it\n- what you would do there\n- and explain why you want to visit"),
                ("Describe a person who has influenced you", "You should say:\n- who this person is\n- how you know them\n- what they have done\n- and explain how they influenced you"),
                ("Describe a skill you would like to learn", "You should say:\n- what the skill is\n- why you want to learn it\n- how you would learn it\n- and explain how it would help you"),
                ("Describe a memorable event from your life", "You should say:\n- what the event was\n- when it happened\n- who was involved\n- and explain why it was memorable"),
                ("Describe a piece of technology you use often", "You should say:\n- what it is\n- how often you use it\n- what you use it for\n- and explain why it is important to you"),
                ("Describe a time you helped someone", "You should say:\n- who you helped\n- what you helped them with\n- why you helped them\n- and explain how you felt afterward"),
                ("Describe a goal you hope to achieve", "You should say:\n- what the goal is\n- when you set this goal\n- what you need to do\n- and explain why this goal matters"),
                ("Describe a childhood memory", "You should say:\n- what the memory is\n- how old you were\n- who was involved\n- and explain why you remember it"),
                ("Describe something you do to stay healthy", "You should say:\n- what you do\n- how often you do it\n- when you started\n- and explain how it helps your health"),
                ("Describe a movie you enjoyed", "You should say:\n- what the movie was\n- when you watched it\n- who you watched it with\n- and explain why you enjoyed it"),
                ("Describe a teacher who influenced you", "You should say:\n- who the teacher was\n- what they taught\n- what made them special\n- and explain their influence on you"),
                ("Describe an outdoor activity you enjoy", "You should say:\n- what the activity is\n- where you do it\n- who you do it with\n- and explain why you enjoy it"),
                ("Describe a time you received good news", "You should say:\n- what the news was\n- when you received it\n- how you received it\n- and explain how you felt"),
                ("Describe a tradition in your culture", "You should say:\n- what the tradition is\n- when it occurs\n- what happens\n- and explain its significance"),
                ("Describe a time you were proud of yourself", "You should say:\n- what happened\n- when it happened\n- what you did\n- and explain why you felt proud"),
                ("Describe a place where you feel relaxed", "You should say:\n- where it is\n- how often you go there\n- what you do there\n- and explain why it relaxes you"),
                ("Describe something you bought that you're happy about", "You should say:\n- what you bought\n- when you bought it\n- why you bought it\n- and explain why you're happy about it"),
                ("Describe a difficult decision you made", "You should say:\n- what the decision was\n- why it was difficult\n- how you decided\n- and explain the outcome"),
                ("Describe a language you would like to learn", "You should say:\n- what language it is\n- why you want to learn it\n- how you would learn it\n- and explain how it would benefit you")
            ], start=1)
        ],
        "part3": [
            {
                "id": f"ielts_s3_{i}",
                "topic": topic,
                "questions": questions,
                "time_per_question": 60
            } for i, (topic, questions) in enumerate([
                ("Reading and Education", ["How has reading changed with technology?", "Should children be encouraged to read more?", "What are the benefits of reading fiction vs. non-fiction?", "Will physical books become obsolete?"]),
                ("Travel and Tourism", ["How has tourism changed your country?", "What are the negative effects of mass tourism?", "Should tourists respect local customs?", "How will travel change in the future?"]),
                ("Technology and Society", ["Has technology improved our quality of life?", "What are the risks of AI?", "Should children's technology use be limited?", "How will technology affect jobs?"]),
                ("Health and Lifestyle", ["Why are lifestyle diseases increasing?", "Should governments promote healthy living?", "What role should schools play in health education?", "Is traditional medicine effective?"]),
                ("Work and Career", ["How important is job satisfaction vs. salary?", "Is remote work the future?", "Should retirement ages be raised?", "How has work culture changed?"]),
                ("Environment", ["Who is responsible for environmental protection?", "Can individuals make a difference?", "Should developing countries prioritize economy or environment?", "What will happen if we don't act on climate change?"]),
                ("Education", ["Is traditional education still relevant?", "Should education be free?", "What skills should schools teach?", "How should teachers be trained?"]),
                ("Media and Communication", ["Has social media improved communication?", "Should news be regulated?", "How can we combat misinformation?", "What's the future of journalism?"]),
                ("Culture and Tradition", ["Are traditions becoming less important?", "Should cultures be preserved?", "How does globalization affect local cultures?", "Should children learn about their cultural heritage?"]),
                ("Cities and Development", ["Should cities continue to grow?", "How can cities become more livable?", "What's the future of urban planning?", "Should people live closer to nature?"])
            ], start=1)
        ]
    },
    "toefl": {
        "independent": [p["prompts"][0] for p in TOEFL_SPEAKING_PROMPTS] if TOEFL_SPEAKING_PROMPTS else [],
        "integrated": [
            {"id": f"toefl_sint_{i}", "reading": reading, "prompt": prompt, "preparation_time": 30, "speaking_time": 60}
            for i, (reading, prompt) in enumerate([
                ("The university plans to eliminate the bus service that currently transports students between campus and downtown.", "The student expresses her opinion. State her opinion and explain the reasons she gives."),
                ("The announcement states that the university library will reduce its operating hours.", "Summarize the student's opinion and explain the reasons he gives."),
                ("The notice indicates that the university will require all students to live on campus for their first year.", "Explain the student's position and the reasons she provides."),
                ("The proposal suggests converting the main parking lot into a green space.", "State the student's opinion about the proposal and explain his reasoning."),
                ("The department announces new requirements for the thesis submission process.", "Summarize the student's concerns and explain why she has them.")
            ], start=1)
        ]
    },
    "cambridge": [p["parts"] for p in CAMBRIDGE_SPEAKING_PROMPTS] if CAMBRIDGE_SPEAKING_PROMPTS else [],
    "pte": {
        "read_aloud": [
            {"id": f"pte_ra_{i}", "text": text, "time": 40}
            for i, text in enumerate([
                "Climate change is one of the most pressing challenges facing humanity today. Scientists agree that human activities, particularly the burning of fossil fuels, are contributing to global warming at an unprecedented rate.",
                "The development of artificial intelligence has accelerated rapidly in recent years, raising questions about the future of employment and the ethical implications of machine decision-making.",
                "Universities around the world are adapting to changing educational needs by offering more flexible learning options, including online courses and hybrid programs that combine digital and in-person instruction.",
                "Economic inequality has become a significant concern in many developed nations, with the gap between the wealthy and the poor continuing to widen despite overall economic growth.",
                "Biodiversity loss threatens the stability of ecosystems and the services they provide, from food production to climate regulation, making conservation efforts increasingly urgent."
            ], start=1)
        ],
        "describe_image": [
            {"id": f"pte_di_{i}", "description": desc, "time": 40}
            for i, desc in enumerate([
                "Line graph showing population growth trends over 50 years in different regions",
                "Bar chart comparing energy consumption by source across countries",
                "Pie chart illustrating market share of smartphone manufacturers",
                "Process diagram showing the water treatment cycle",
                "Map indicating migration patterns in Europe"
            ], start=1)
        ]
    },
    "oet": [p["role_plays"][0] for p in OET_SPEAKING_PROMPTS] if OET_SPEAKING_PROMPTS else []
}

# Writing tasks organized by exam type
WRITING_TASKS = {
    "ielts": {
        "task1": [
            {"id": f"ielts_w1_{i}", "type": "graph_description", "prompt": prompt, "min_words": 150, "time_minutes": 20}
            for i, prompt in enumerate([
                "The bar chart shows the percentage of households with internet access in five countries from 2000 to 2020. Summarize the information and make comparisons.",
                "The line graph shows changes in average temperatures in three cities over a 50-year period. Describe the main trends.",
                "The pie charts compare energy consumption by source in two countries. Summarize and compare the key features.",
                "The table shows unemployment rates by age group in four countries. Report the main features and make comparisons.",
                "The diagram illustrates the process of recycling plastic bottles. Summarize the information by describing the process.",
                "The maps show changes to a town center between 1980 and 2020. Summarize the key developments.",
                "The chart shows CO2 emissions per capita for different regions. Describe and compare the data.",
                "The graph shows birth rates and death rates in a country over 100 years. Describe the trends.",
                "The diagram shows the life cycle of a butterfly. Describe the stages.",
                "The chart compares water usage in different sectors across countries. Analyze the data."
            ], start=1)
        ],
        "task2": [
            {"id": f"ielts_w2_{i}", "type": "essay", "prompt": prompt, "min_words": 250, "time_minutes": 40}
            for i, prompt in enumerate([
                "Some people think that unpaid community service should be a compulsory part of high school programs. To what extent do you agree or disagree?",
                "In many countries, the proportion of older people is steadily increasing. Does this trend have more positive or negative effects on society?",
                "Some believe that children should be taught to compete. Others think they should be taught to cooperate. Discuss both views.",
                "The best way to reduce crime is to give longer prison sentences. To what extent do you agree?",
                "Some people believe that technological progress is the answer to world poverty. Others think technology makes problems worse. Discuss.",
                "International tourism has brought enormous benefits to many places. At the same time, it has caused problems. Discuss.",
                "Governments should spend money on railways rather than roads. To what extent do you agree?",
                "Some think famous people can help international aid organizations. Others believe celebrities make problems worse. Discuss.",
                "University students should pay full cost of their education. To what extent do you agree?",
                "Some believe art should be funded by governments. Others think artists should fund themselves. Discuss both views.",
                "Many buildings are protected by law because of their historical importance. Is this good for the cities?",
                "Some believe we should preserve old buildings. Others think they should be replaced with modern ones. Discuss.",
                "In the past, people were more dependent on each other. Now people are more independent. Is this a positive or negative development?",
                "Some countries have age restrictions for politicians. Others allow people of any age. Discuss.",
                "Team activities teach more important skills than individual activities. Do you agree?",
                "Many cities replace old buildings with new ones. Is this a positive or negative development?",
                "Some believe sports bring people together. Others think they create division. Discuss both views.",
                "Governments should control the amount of violence in films and TV. Do you agree?",
                "People are living longer. What problems will this cause? How can they be addressed?",
                "Some feel that education should prepare students for specific careers. Others think it should teach general knowledge. Discuss."
            ], start=1)
        ]
    },
    "toefl": {
        "integrated": [t["tasks"][0] for t in TOEFL_WRITING_TASKS] if TOEFL_WRITING_TASKS else [],
        "independent": [t["tasks"][0] for t in TOEFL_WRITING_TASKS] if TOEFL_WRITING_TASKS else []
    },
    "cambridge": {
        "part1": [
            {"id": f"cam_w1_{i}", "type": "essay", "prompt": prompt, "word_count": "220-260", "time_minutes": 45}
            for i, prompt in enumerate([
                "Your class has had a discussion about whether technology has improved education. Write an essay discussing both sides.",
                "Write an essay about whether governments should invest more in public transport or roads.",
                "Discuss whether schools should teach practical life skills alongside academic subjects.",
                "Write about whether social media has had a positive or negative effect on society.",
                "Discuss the advantages and disadvantages of working from home."
            ], start=1)
        ],
        "part2": [
            {"id": f"cam_w2_{i}", "type": type_, "prompt": prompt, "word_count": "220-260", "time_minutes": 45}
            for i, (type_, prompt) in enumerate([
                ("letter", "Write a letter to a local newspaper about environmental issues in your area."),
                ("report", "Write a report for your school principal suggesting improvements to sports facilities."),
                ("review", "Write a review of a book or film you have recently enjoyed."),
                ("proposal", "Write a proposal for an event to celebrate your town's anniversary."),
                ("article", "Write an article about how young people can contribute to their communities.")
            ], start=1)
        ]
    },
    "pte": {
        "summarize_written": [
            {"id": f"pte_sw_{i}", "prompt": prompt, "word_count": "5-75", "time_minutes": 10}
            for i, prompt in enumerate([
                "Summarize the passage about climate change and its effects on biodiversity.",
                "Summarize the text describing the evolution of digital communication.",
                "Write a summary of the passage about sustainable urban development.",
                "Summarize the article about the benefits and risks of artificial intelligence.",
                "Write a summary of the text discussing global economic trends."
            ], start=1)
        ],
        "essay": [
            {"id": f"pte_essay_{i}", "prompt": prompt, "word_count": "200-300", "time_minutes": 20}
            for i, prompt in enumerate([
                "Some people think that children should begin formal education at an early age. Others think they should not start school until they are older. Discuss.",
                "Climate change is a serious problem. What can individuals do to help address this issue?",
                "Technology has made it easier to work remotely. Discuss the advantages and disadvantages of working from home.",
                "Some believe that competitive sports teach children important lessons. Others think cooperation is more valuable. Discuss both views.",
                "Should governments invest more in space exploration or focus on solving Earth's problems? Discuss."
            ], start=1)
        ]
    },
    "oet": [t["task"] for t in OET_WRITING_TASKS] if OET_WRITING_TASKS else []
}

# Listening questions - sample structure for all exam types
LISTENING_QUESTIONS = {
    "ielts": [
        {
            "id": f"ielts_l_sec{section}_{i}",
            "section": section,
            "type": "form_completion" if section == 1 else "multiple_choice",
            "audio_id": f"ielts_audio_{section}_{i}",
            "title": title,
            "questions": questions
        }
        for section in range(1, 5)
        for i, (title, questions) in enumerate([
            ("University Accommodation Inquiry", [
                {"blank": "Name: ___", "answer": "Thompson"},
                {"blank": "Phone: ___", "answer": "07845123456"},
                {"blank": "Room type: ___", "answer": "single"},
            ]),
            ("Tour Guide Information", [
                {"question": "When does the tour start?", "options": ["9am", "10am", "11am"], "answer": "10am"},
                {"question": "How long is the tour?", "options": ["1 hour", "2 hours", "3 hours"], "answer": "2 hours"},
            ]),
            ("Academic Lecture: Marine Biology", [
                {"question": "What is the main topic?", "options": ["Fish migration", "Coral reefs", "Ocean currents"], "answer": "Coral reefs"},
            ]),
            ("Research Discussion", [
                {"question": "What methodology was used?", "options": ["Qualitative", "Quantitative", "Mixed"], "answer": "Mixed"},
            ]),
        ], start=1)
    ],
    "toefl": [
        {
            "id": f"toefl_l_{i}",
            "type": "lecture",
            "topic": topic,
            "questions": [
                {"question": q, "options": opts, "answer": ans}
                for q, opts, ans in questions
            ]
        }
        for i, (topic, questions) in enumerate([
            ("Art History: Renaissance", [
                ("What characterized Renaissance art?", ["Religious themes", "Abstract forms", "Humanism and perspective", "Minimalism"], "Humanism and perspective"),
                ("Which artist is mentioned?", ["Picasso", "Michelangelo", "Monet", "Van Gogh"], "Michelangelo"),
            ]),
            ("Biology: Cell Division", [
                ("What type of cell division is discussed?", ["Mitosis", "Meiosis", "Both", "Neither"], "Both"),
                ("How many daughter cells result from meiosis?", ["2", "4", "6", "8"], "4"),
            ]),
        ], start=1)
    ]
}


def get_exam_questions(exam_type: str, section: str, count: int = 5, exam_number: int = None):
    """Get questions for a specific exam type, section, and optionally a specific exam number"""
    questions = []
    
    if section == "reading":
        if exam_type == "ielts":
            passages = ALL_IELTS_PASSAGES if ALL_IELTS_PASSAGES else IELTS_READING_PASSAGES
        elif exam_type == "toefl":
            passages = TOEFL_READING_PASSAGES
        elif exam_type == "cambridge":
            passages = CAMBRIDGE_READING_PASSAGES
        elif exam_type == "pte":
            passages = PTE_READING_PASSAGES
        elif exam_type == "oet":
            passages = OET_READING_PASSAGES
        else:
            passages = IELTS_READING_PASSAGES
        
        # Filter by exam number if specified
        if exam_number and passages:
            passages = [p for p in passages if p.get("exam_id") == f"{exam_type}_exam_{exam_number}"]
        
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
        elif "essay" in writing:
            questions = writing["essay"][:count]
    
    elif section == "speaking":
        speaking = SPEAKING_PROMPTS.get(exam_type, SPEAKING_PROMPTS.get("ielts", {}))
        if "part2" in speaking:
            questions = speaking["part2"][:count]
        elif "independent" in speaking:
            questions = speaking["independent"][:count]
    
    return questions


def get_full_exam(exam_type: str, exam_number: int = 1):
    """Get a complete exam with all sections for a specific exam number (1-20)"""
    exam_id = f"{exam_type}_exam_{exam_number}"
    
    return {
        "exam_id": exam_id,
        "exam_number": exam_number,
        "exam_type": exam_type,
        "config": get_mock_test_config(exam_type),
        "sections": {
            "reading": get_exam_questions(exam_type, "reading", 3, exam_number),
            "listening": get_exam_questions(exam_type, "listening", 4, exam_number),
            "writing": get_exam_questions(exam_type, "writing", 2, exam_number),
            "speaking": get_exam_questions(exam_type, "speaking", 3, exam_number)
        }
    }


def get_available_exams(exam_type: str):
    """Get list of available exam numbers for an exam type"""
    return {
        "exam_type": exam_type,
        "total_exams": 20,
        "exam_numbers": list(range(1, 21)),
        "config": get_mock_test_config(exam_type)
    }


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
