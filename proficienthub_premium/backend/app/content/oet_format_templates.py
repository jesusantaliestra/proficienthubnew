"""
OET Format Templates for Visual Consistency
===========================================
HTML/Markdown templates for rendering OET exam content
with authentic OET visual styling.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .oet_specifications import OETHealthcareProfession, OETSection


# ============================================================
# CSS STYLES FOR OET EXAM RENDERING
# ============================================================

OET_CSS_STYLES = """
<style>
/* OET Brand Colors */
:root {
    --oet-blue: #003366;
    --oet-light-blue: #0066CC;
    --oet-accent: #FF6600;
    --oet-gray: #666666;
    --oet-light-gray: #F5F5F5;
    --oet-border: #DDDDDD;
    --oet-success: #28a745;
    --oet-warning: #ffc107;
    --oet-danger: #dc3545;
}

/* Base Exam Container */
.oet-exam-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background: #ffffff;
    color: #333333;
    line-height: 1.6;
}

/* Section Headers */
.oet-section-header {
    background: var(--oet-blue);
    color: white;
    padding: 15px 20px;
    margin-bottom: 20px;
    border-radius: 4px;
}

.oet-section-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
}

.oet-section-header .section-time {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-top: 5px;
}

/* Part Headers */
.oet-part-header {
    background: var(--oet-light-gray);
    border-left: 4px solid var(--oet-light-blue);
    padding: 12px 15px;
    margin: 20px 0 15px 0;
    font-weight: 600;
    color: var(--oet-blue);
}

/* Question Containers */
.oet-question-block {
    margin-bottom: 20px;
    padding: 15px;
    border: 1px solid var(--oet-border);
    border-radius: 4px;
    background: #ffffff;
}

.oet-question-number {
    display: inline-block;
    background: var(--oet-blue);
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-right: 10px;
}

.oet-question-text {
    display: inline;
    font-size: 1rem;
}

/* Multiple Choice Options */
.oet-options {
    margin-top: 12px;
    padding-left: 38px;
}

.oet-option {
    display: block;
    padding: 8px 12px;
    margin-bottom: 8px;
    border: 1px solid var(--oet-border);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.oet-option:hover {
    background: var(--oet-light-gray);
    border-color: var(--oet-light-blue);
}

.oet-option.selected {
    background: #e6f0ff;
    border-color: var(--oet-light-blue);
}

.oet-option-label {
    font-weight: 600;
    margin-right: 8px;
    color: var(--oet-blue);
}

/* Note Completion Input */
.oet-note-input {
    display: inline-block;
    min-width: 150px;
    padding: 6px 10px;
    border: none;
    border-bottom: 2px solid var(--oet-blue);
    font-size: 1rem;
    background: var(--oet-light-gray);
    margin: 0 5px;
}

.oet-note-input:focus {
    outline: none;
    border-bottom-color: var(--oet-accent);
    background: #fff;
}

/* Reading Text Container */
.oet-reading-text {
    background: var(--oet-light-gray);
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-size: 0.95rem;
    line-height: 1.8;
}

.oet-reading-text h3 {
    color: var(--oet-blue);
    margin-top: 0;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--oet-border);
}

/* Writing Task Container */
.oet-writing-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.oet-case-notes {
    background: #fffef0;
    border: 1px solid #e6e5d0;
    padding: 20px;
    border-radius: 4px;
    font-size: 0.9rem;
}

.oet-case-notes h3 {
    color: var(--oet-blue);
    margin-top: 0;
    font-size: 1rem;
}

.oet-case-notes-section {
    margin-bottom: 15px;
}

.oet-case-notes-section h4 {
    font-size: 0.85rem;
    color: var(--oet-gray);
    text-transform: uppercase;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
}

.oet-writing-area {
    background: white;
    border: 1px solid var(--oet-border);
    padding: 20px;
    border-radius: 4px;
}

.oet-writing-task {
    background: var(--oet-light-blue);
    color: white;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 0.95rem;
}

.oet-text-editor {
    width: 100%;
    min-height: 400px;
    padding: 15px;
    border: 1px solid var(--oet-border);
    border-radius: 4px;
    font-family: inherit;
    font-size: 1rem;
    line-height: 1.6;
    resize: vertical;
}

.oet-word-count {
    text-align: right;
    font-size: 0.85rem;
    color: var(--oet-gray);
    margin-top: 8px;
}

/* Speaking Role Cards */
.oet-roleplay-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 20px;
}

.oet-role-card {
    border: 2px solid var(--oet-border);
    border-radius: 8px;
    overflow: hidden;
}

.oet-role-card-header {
    padding: 12px 15px;
    font-weight: 600;
    font-size: 1rem;
}

.oet-role-card.candidate .oet-role-card-header {
    background: var(--oet-blue);
    color: white;
}

.oet-role-card.patient .oet-role-card-header {
    background: var(--oet-accent);
    color: white;
}

.oet-role-card-body {
    padding: 15px;
    font-size: 0.9rem;
}

.oet-role-card-body h4 {
    color: var(--oet-blue);
    font-size: 0.85rem;
    text-transform: uppercase;
    margin: 15px 0 8px 0;
    letter-spacing: 0.5px;
}

.oet-role-card-body ul {
    margin: 0;
    padding-left: 20px;
}

.oet-role-card-body li {
    margin-bottom: 6px;
}

/* Timer Display */
.oet-timer {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--oet-blue);
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 1.2rem;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.oet-timer.warning {
    background: var(--oet-warning);
    color: #333;
}

.oet-timer.danger {
    background: var(--oet-danger);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Progress Indicator */
.oet-progress {
    background: var(--oet-light-gray);
    height: 8px;
    border-radius: 4px;
    margin: 20px 0;
    overflow: hidden;
}

.oet-progress-bar {
    background: var(--oet-light-blue);
    height: 100%;
    transition: width 0.3s;
}

/* Audio Player Styling */
.oet-audio-player {
    background: var(--oet-light-gray);
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.oet-audio-player audio {
    width: 100%;
}

.oet-audio-info {
    font-size: 0.85rem;
    color: var(--oet-gray);
    margin-top: 8px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .oet-writing-container,
    .oet-roleplay-container {
        grid-template-columns: 1fr;
    }

    .oet-timer {
        position: static;
        margin-bottom: 20px;
    }
}

/* Print Styles */
@media print {
    .oet-timer,
    .oet-audio-player {
        display: none;
    }

    .oet-exam-container {
        max-width: 100%;
        padding: 0;
    }

    .oet-question-block {
        page-break-inside: avoid;
    }
}
</style>
"""


# ============================================================
# HTML TEMPLATES
# ============================================================

@dataclass
class OETTemplate:
    """Base template class"""
    name: str
    html: str


class OETTemplateRenderer:
    """Render OET exam content using templates"""

    @staticmethod
    def render_exam_header(
        section: OETSection,
        profession: OETHealthcareProfession,
        time_minutes: int
    ) -> str:
        """Render section header"""
        section_names = {
            OETSection.LISTENING: "Listening",
            OETSection.READING: "Reading",
            OETSection.WRITING: "Writing",
            OETSection.SPEAKING: "Speaking",
        }

        return f"""
<div class="oet-section-header">
    <h2>OET {section_names[section]} Sub-test</h2>
    <div class="section-time">
        Time allowed: {time_minutes} minutes |
        Profession: {profession.value.replace('_', ' ').title()}
    </div>
</div>
        """

    @staticmethod
    def render_part_header(part_name: str, description: str) -> str:
        """Render part header within section"""
        return f"""
<div class="oet-part-header">
    <strong>{part_name}</strong> - {description}
</div>
        """

    @staticmethod
    def render_note_completion_question(
        question_number: int,
        question_text: str,
        blank_position: str = "end"
    ) -> str:
        """Render a note completion question"""
        if blank_position == "end":
            return f"""
<div class="oet-question-block">
    <span class="oet-question-number">{question_number}</span>
    <span class="oet-question-text">{question_text}</span>
    <input type="text" class="oet-note-input" maxlength="50"
           data-question="{question_number}" placeholder="Answer">
</div>
            """
        else:
            parts = question_text.split("___")
            return f"""
<div class="oet-question-block">
    <span class="oet-question-number">{question_number}</span>
    <span class="oet-question-text">
        {parts[0]}
        <input type="text" class="oet-note-input" maxlength="50"
               data-question="{question_number}" placeholder="">
        {parts[1] if len(parts) > 1 else ''}
    </span>
</div>
            """

    @staticmethod
    def render_multiple_choice_question(
        question_number: int,
        question_text: str,
        options: List[str]
    ) -> str:
        """Render a multiple choice question"""
        options_html = ""
        for i, option in enumerate(options):
            label = chr(65 + i)  # A, B, C, D
            options_html += f"""
<label class="oet-option" data-option="{label}">
    <span class="oet-option-label">{label}.</span>
    <span>{option}</span>
</label>
            """

        return f"""
<div class="oet-question-block">
    <span class="oet-question-number">{question_number}</span>
    <span class="oet-question-text">{question_text}</span>
    <div class="oet-options">
        {options_html}
    </div>
</div>
        """

    @staticmethod
    def render_reading_text(
        text_label: str,
        title: str,
        content: str
    ) -> str:
        """Render a reading passage"""
        return f"""
<div class="oet-reading-text" id="text-{text_label.lower()}">
    <h3>Text {text_label}: {title}</h3>
    <div class="text-content">
        {content}
    </div>
</div>
        """

    @staticmethod
    def render_writing_task(
        case_notes: str,
        writing_task: str,
        word_limit: Dict[str, int]
    ) -> str:
        """Render writing task with case notes"""
        # Format case notes with sections
        formatted_notes = case_notes.replace("\n\n", "</div><div class='oet-case-notes-section'>")

        return f"""
<div class="oet-writing-container">
    <div class="oet-case-notes">
        <h3>Case Notes</h3>
        <div class="oet-case-notes-section">
            {formatted_notes}
        </div>
    </div>
    <div class="oet-writing-area">
        <div class="oet-writing-task">
            <strong>Writing Task:</strong><br>
            {writing_task}
        </div>
        <textarea class="oet-text-editor"
                  placeholder="Write your letter here..."
                  data-min-words="{word_limit['minimum']}"
                  data-max-words="{word_limit['maximum']}"></textarea>
        <div class="oet-word-count">
            Word count: <span id="word-count">0</span> / {word_limit['minimum']}-{word_limit['maximum']} words
        </div>
    </div>
</div>
        """

    @staticmethod
    def render_speaking_roleplay(
        setting: str,
        candidate_card: str,
        patient_card: str,
        prep_time_minutes: int
    ) -> str:
        """Render speaking roleplay cards"""
        # Format card content
        def format_card(content: str) -> str:
            lines = content.strip().split("\n")
            formatted = []
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.endswith(":"):
                    current_section = line[:-1]
                    formatted.append(f"<h4>{current_section}</h4>")
                elif line.startswith("•") or line.startswith("-"):
                    formatted.append(f"<li>{line[1:].strip()}</li>")
                else:
                    formatted.append(f"<p>{line}</p>")

            return "\n".join(formatted)

        return f"""
<div class="oet-speaking-section">
    <div class="oet-part-header">
        <strong>Setting:</strong> {setting}
    </div>
    <div class="oet-prep-notice" style="background: #fff3cd; padding: 10px; border-radius: 4px; margin: 15px 0;">
        <strong>Preparation time:</strong> {prep_time_minutes} minutes to read your card before the roleplay begins.
    </div>
    <div class="oet-roleplay-container">
        <div class="oet-role-card candidate">
            <div class="oet-role-card-header">CANDIDATE CARD</div>
            <div class="oet-role-card-body">
                {format_card(candidate_card)}
            </div>
        </div>
        <div class="oet-role-card patient">
            <div class="oet-role-card-header">PATIENT/CARER CARD</div>
            <div class="oet-role-card-body">
                {format_card(patient_card)}
            </div>
        </div>
    </div>
</div>
        """

    @staticmethod
    def render_timer(minutes: int) -> str:
        """Render countdown timer"""
        return f"""
<div class="oet-timer" id="exam-timer" data-minutes="{minutes}">
    {minutes}:00
</div>
        """

    @staticmethod
    def render_progress_bar(current: int, total: int) -> str:
        """Render progress indicator"""
        percentage = (current / total) * 100 if total > 0 else 0
        return f"""
<div class="oet-progress">
    <div class="oet-progress-bar" style="width: {percentage}%"></div>
</div>
<div style="text-align: center; font-size: 0.9rem; color: #666;">
    Question {current} of {total}
</div>
        """

    @staticmethod
    def render_audio_player(audio_url: str, plays_remaining: int = 1) -> str:
        """Render audio player for listening"""
        return f"""
<div class="oet-audio-player">
    <audio controls id="listening-audio">
        <source src="{audio_url}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    <div class="oet-audio-info">
        <strong>Note:</strong> You will hear the recording {'only once' if plays_remaining == 1 else f'{plays_remaining} times'}.
    </div>
</div>
        """


# ============================================================
# COMPLETE PAGE TEMPLATES
# ============================================================

LISTENING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OET Listening Sub-test</title>
    {styles}
</head>
<body>
    <div class="oet-exam-container">
        {header}
        {timer}

        <div class="oet-instructions" style="background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <strong>Instructions:</strong>
            <ul>
                <li>This test has three parts: Part A, Part B, and Part C</li>
                <li>You will hear each recording ONCE only</li>
                <li>Write your answers as you listen</li>
                <li>Check your answers when instructed</li>
            </ul>
        </div>

        {content}

        <div class="oet-navigation" style="margin-top: 30px; text-align: center;">
            <button onclick="submitSection()" style="background: var(--oet-blue); color: white; padding: 12px 30px; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;">
                Submit Answers
            </button>
        </div>
    </div>

    <script>
        // Timer functionality
        let timeLeft = {time_seconds};
        const timerEl = document.getElementById('exam-timer');

        const timer = setInterval(() => {{
            timeLeft--;
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerEl.textContent = `${{mins}}:${{secs.toString().padStart(2, '0')}}`;

            if (timeLeft <= 300) timerEl.classList.add('warning');
            if (timeLeft <= 60) timerEl.classList.add('danger');
            if (timeLeft <= 0) {{
                clearInterval(timer);
                submitSection();
            }}
        }}, 1000);

        function submitSection() {{
            // Collect answers
            const answers = {{}};
            document.querySelectorAll('.oet-note-input').forEach(input => {{
                answers[input.dataset.question] = input.value;
            }});
            document.querySelectorAll('.oet-option.selected').forEach(option => {{
                const block = option.closest('.oet-question-block');
                const qNum = block.querySelector('.oet-question-number').textContent;
                answers[qNum] = option.dataset.option;
            }});
            console.log('Submitted:', answers);
            // Send to backend
        }}

        // Option selection
        document.querySelectorAll('.oet-option').forEach(option => {{
            option.addEventListener('click', () => {{
                option.parentElement.querySelectorAll('.oet-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
            }});
        }});
    </script>
</body>
</html>
"""

READING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OET Reading Sub-test</title>
    {styles}
</head>
<body>
    <div class="oet-exam-container">
        {header}
        {timer}

        <div class="oet-instructions" style="background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <strong>Instructions:</strong>
            <ul>
                <li>Part A: 15 minutes - Read quickly to find specific information</li>
                <li>Part B: 45 minutes - Read carefully and answer comprehension questions</li>
                <li>You may write on the question paper</li>
            </ul>
        </div>

        {content}

        <div class="oet-navigation" style="margin-top: 30px; text-align: center;">
            <button onclick="submitSection()" style="background: var(--oet-blue); color: white; padding: 12px 30px; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;">
                Submit Answers
            </button>
        </div>
    </div>

    <script>
        let timeLeft = {time_seconds};
        const timerEl = document.getElementById('exam-timer');

        const timer = setInterval(() => {{
            timeLeft--;
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerEl.textContent = `${{mins}}:${{secs.toString().padStart(2, '0')}}`;

            if (timeLeft <= 300) timerEl.classList.add('warning');
            if (timeLeft <= 60) timerEl.classList.add('danger');
            if (timeLeft <= 0) {{
                clearInterval(timer);
                submitSection();
            }}
        }}, 1000);

        function submitSection() {{
            console.log('Submitting reading answers...');
        }}

        document.querySelectorAll('.oet-option').forEach(option => {{
            option.addEventListener('click', () => {{
                option.parentElement.querySelectorAll('.oet-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
            }});
        }});
    </script>
</body>
</html>
"""

WRITING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OET Writing Sub-test</title>
    {styles}
</head>
<body>
    <div class="oet-exam-container">
        {header}
        {timer}

        <div class="oet-instructions" style="background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <strong>Instructions:</strong>
            <ul>
                <li>Read the case notes carefully</li>
                <li>Write a letter of approximately 180-200 words</li>
                <li>Use an appropriate letter format</li>
                <li>You have 45 minutes for this task</li>
            </ul>
        </div>

        {content}

        <div class="oet-navigation" style="margin-top: 30px; text-align: center;">
            <button onclick="submitWriting()" style="background: var(--oet-blue); color: white; padding: 12px 30px; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;">
                Submit Letter
            </button>
        </div>
    </div>

    <script>
        let timeLeft = {time_seconds};
        const timerEl = document.getElementById('exam-timer');
        const editor = document.querySelector('.oet-text-editor');
        const wordCountEl = document.getElementById('word-count');

        const timer = setInterval(() => {{
            timeLeft--;
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerEl.textContent = `${{mins}}:${{secs.toString().padStart(2, '0')}}`;

            if (timeLeft <= 300) timerEl.classList.add('warning');
            if (timeLeft <= 60) timerEl.classList.add('danger');
            if (timeLeft <= 0) {{
                clearInterval(timer);
                submitWriting();
            }}
        }}, 1000);

        // Word count
        editor.addEventListener('input', () => {{
            const words = editor.value.trim().split(/\s+/).filter(w => w.length > 0).length;
            wordCountEl.textContent = words;

            const min = parseInt(editor.dataset.minWords);
            const max = parseInt(editor.dataset.maxWords);

            if (words < min) {{
                wordCountEl.style.color = '#dc3545';
            }} else if (words > max) {{
                wordCountEl.style.color = '#ffc107';
            }} else {{
                wordCountEl.style.color = '#28a745';
            }}
        }});

        function submitWriting() {{
            const letter = editor.value;
            console.log('Submitting letter:', letter);
        }}
    </script>
</body>
</html>
"""

SPEAKING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OET Speaking Sub-test</title>
    {styles}
</head>
<body>
    <div class="oet-exam-container">
        {header}

        <div class="oet-instructions" style="background: #e8f4f8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <strong>Instructions:</strong>
            <ul>
                <li>You will complete 2 role-plays</li>
                <li>You have 3 minutes to prepare for each role-play</li>
                <li>Each role-play lasts approximately 5 minutes</li>
                <li>Read only the CANDIDATE card - the interlocutor has different information</li>
            </ul>
        </div>

        {content}

        <div class="oet-navigation" style="margin-top: 30px; text-align: center;">
            <button id="start-prep" onclick="startPreparation()" style="background: var(--oet-accent); color: white; padding: 12px 30px; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;">
                Start Preparation Time
            </button>
            <button id="start-roleplay" onclick="startRoleplay()" style="display: none; background: var(--oet-blue); color: white; padding: 12px 30px; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;">
                Begin Role-play
            </button>
        </div>
    </div>

    <script>
        let prepTime = 180; // 3 minutes
        let roleplayTime = 300; // 5 minutes

        function startPreparation() {{
            document.getElementById('start-prep').style.display = 'none';
            const timerDiv = document.createElement('div');
            timerDiv.className = 'oet-timer';
            timerDiv.id = 'prep-timer';
            document.body.appendChild(timerDiv);

            const countdown = setInterval(() => {{
                prepTime--;
                const mins = Math.floor(prepTime / 60);
                const secs = prepTime % 60;
                timerDiv.textContent = `Prep: ${{mins}}:${{secs.toString().padStart(2, '0')}}`;

                if (prepTime <= 0) {{
                    clearInterval(countdown);
                    timerDiv.remove();
                    document.getElementById('start-roleplay').style.display = 'inline-block';
                }}
            }}, 1000);
        }}

        function startRoleplay() {{
            document.getElementById('start-roleplay').style.display = 'none';
            const timerDiv = document.createElement('div');
            timerDiv.className = 'oet-timer';
            timerDiv.id = 'roleplay-timer';
            document.body.appendChild(timerDiv);

            const countdown = setInterval(() => {{
                roleplayTime--;
                const mins = Math.floor(roleplayTime / 60);
                const secs = roleplayTime % 60;
                timerDiv.textContent = `${{mins}}:${{secs.toString().padStart(2, '0')}}`;

                if (roleplayTime <= 60) timerDiv.classList.add('warning');
                if (roleplayTime <= 0) {{
                    clearInterval(countdown);
                    alert('Role-play time is up!');
                }}
            }}, 1000);
        }}
    </script>
</body>
</html>
"""


# ============================================================
# TEMPLATE ASSEMBLY FUNCTIONS
# ============================================================

def render_listening_exam(
    profession: OETHealthcareProfession,
    content: Dict[str, Any]
) -> str:
    """Render complete listening exam page"""
    renderer = OETTemplateRenderer()

    header = renderer.render_exam_header(
        OETSection.LISTENING,
        profession,
        time_minutes=45
    )
    timer = renderer.render_timer(45)

    # Build content sections
    content_html = ""

    # Part A
    content_html += renderer.render_part_header(
        "Part A",
        "Consultation extracts (Questions 1-24)"
    )
    # Add questions for Part A...

    # Part B
    content_html += renderer.render_part_header(
        "Part B",
        "Short workplace extracts (Questions 25-30)"
    )
    # Add questions for Part B...

    # Part C
    content_html += renderer.render_part_header(
        "Part C",
        "Presentation extracts (Questions 31-42)"
    )
    # Add questions for Part C...

    return LISTENING_PAGE_TEMPLATE.format(
        styles=OET_CSS_STYLES,
        header=header,
        timer=timer,
        content=content_html,
        time_seconds=45 * 60
    )


def render_writing_exam(
    profession: OETHealthcareProfession,
    case_notes: str,
    writing_task: str
) -> str:
    """Render complete writing exam page"""
    renderer = OETTemplateRenderer()

    header = renderer.render_exam_header(
        OETSection.WRITING,
        profession,
        time_minutes=45
    )
    timer = renderer.render_timer(45)

    content = renderer.render_writing_task(
        case_notes=case_notes,
        writing_task=writing_task,
        word_limit={"minimum": 180, "maximum": 200}
    )

    return WRITING_PAGE_TEMPLATE.format(
        styles=OET_CSS_STYLES,
        header=header,
        timer=timer,
        content=content,
        time_seconds=45 * 60
    )


def render_speaking_exam(
    profession: OETHealthcareProfession,
    roleplay_data: Dict[str, Any]
) -> str:
    """Render speaking exam page"""
    renderer = OETTemplateRenderer()

    header = renderer.render_exam_header(
        OETSection.SPEAKING,
        profession,
        time_minutes=20
    )

    content = renderer.render_speaking_roleplay(
        setting=roleplay_data.get("setting", "Healthcare setting"),
        candidate_card=roleplay_data.get("candidate_card", ""),
        patient_card=roleplay_data.get("patient_card", ""),
        prep_time_minutes=3
    )

    return SPEAKING_PAGE_TEMPLATE.format(
        styles=OET_CSS_STYLES,
        header=header,
        content=content,
        time_seconds=20 * 60
    )
