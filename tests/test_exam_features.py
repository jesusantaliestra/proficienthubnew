"""
Test suite for Exam Simulator and AI Tutor features
Tests: Exam types, practice questions, speaking prompts, writing tasks, voice features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://proficient-hub-1.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "santaliestralimited@gmail.com"
TEST_PASSWORD = "Admin123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestExamTypes:
    """Test GET /api/exams/types endpoint"""
    
    def test_get_exam_types_returns_all_types(self):
        """Test that exam types endpoint returns all 5 exam types"""
        response = requests.get(f"{BASE_URL}/api/exams/types")
        assert response.status_code == 200
        
        data = response.json()
        assert "exam_types" in data
        assert set(data["exam_types"]) == {"toefl", "ielts", "cambridge", "pte", "oet"}
    
    def test_get_exam_types_returns_sections(self):
        """Test that exam types endpoint returns sections for each exam"""
        response = requests.get(f"{BASE_URL}/api/exams/types")
        assert response.status_code == 200
        
        data = response.json()
        assert "sections" in data
        
        # Verify IELTS sections
        assert "ielts" in data["sections"]
        assert set(data["sections"]["ielts"]) == {"reading", "listening", "speaking", "writing"}
        
        # Verify TOEFL sections
        assert "toefl" in data["sections"]
        assert set(data["sections"]["toefl"]) == {"reading", "listening", "speaking", "writing"}
    
    def test_get_exam_types_returns_mock_test_configs(self):
        """Test that exam types endpoint returns mock test configurations"""
        response = requests.get(f"{BASE_URL}/api/exams/types")
        assert response.status_code == 200
        
        data = response.json()
        assert "mock_tests" in data
        
        # Verify IELTS mock test config
        ielts_config = data["mock_tests"]["ielts"]
        assert "name" in ielts_config
        assert "duration_minutes" in ielts_config
        assert "sections" in ielts_config
        assert ielts_config["duration_minutes"] == 175


class TestPracticeQuestions:
    """Test GET /api/exams/{examType}/practice endpoint"""
    
    def test_get_ielts_reading_practice(self, auth_headers):
        """Test getting IELTS reading practice questions"""
        response = requests.get(
            f"{BASE_URL}/api/exams/ielts/practice?section=reading",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "ielts"
        assert data["section"] == "reading"
        assert "questions" in data
        assert len(data["questions"]) > 0
        assert "time_limit" in data
        assert "instructions" in data
    
    def test_get_toefl_reading_practice(self, auth_headers):
        """Test getting TOEFL reading practice questions"""
        response = requests.get(
            f"{BASE_URL}/api/exams/toefl/practice?section=reading",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "toefl"
        assert data["section"] == "reading"
        assert "questions" in data
    
    def test_get_practice_with_passage_and_questions(self, auth_headers):
        """Test that reading practice includes passage and questions"""
        response = requests.get(
            f"{BASE_URL}/api/exams/ielts/practice?section=reading",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        question = data["questions"][0]
        
        # Verify passage structure
        assert "passage" in question
        assert "title" in question["passage"] or "passage" in question["passage"]
        
        # Verify questions structure
        assert "questions" in question
        assert len(question["questions"]) > 0
        
        # Verify question has required fields
        q = question["questions"][0]
        assert "id" in q
        assert "type" in q
        assert "question" in q
        assert "options" in q
        assert "correct_answer" in q
    
    def test_invalid_exam_type_returns_400(self, auth_headers):
        """Test that invalid exam type returns 400"""
        response = requests.get(
            f"{BASE_URL}/api/exams/invalid_exam/practice?section=reading",
            headers=auth_headers
        )
        assert response.status_code == 400


class TestSpeakingPrompts:
    """Test GET /api/exams/{examType}/speaking-prompts endpoint"""
    
    def test_get_ielts_speaking_prompts(self, auth_headers):
        """Test getting IELTS speaking prompts"""
        response = requests.get(
            f"{BASE_URL}/api/exams/ielts/speaking-prompts",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "ielts"
        assert "prompts" in data
    
    def test_get_toefl_speaking_prompts(self, auth_headers):
        """Test getting TOEFL speaking prompts"""
        response = requests.get(
            f"{BASE_URL}/api/exams/toefl/speaking-prompts",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "toefl"
        assert "prompts" in data
        
        # Verify TOEFL has independent and integrated prompts
        prompts = data["prompts"]
        assert "independent" in prompts or "integrated" in prompts
    
    def test_speaking_prompts_have_timing_info(self, auth_headers):
        """Test that speaking prompts include timing information"""
        response = requests.get(
            f"{BASE_URL}/api/exams/toefl/speaking-prompts",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        prompts = data["prompts"]
        
        # Check independent prompts have timing
        if "independent" in prompts and len(prompts["independent"]) > 0:
            prompt = prompts["independent"][0]
            assert "preparation_time" in prompt
            assert "speaking_time" in prompt


class TestWritingTasks:
    """Test GET /api/exams/{examType}/writing-tasks endpoint"""
    
    def test_get_ielts_writing_tasks(self, auth_headers):
        """Test getting IELTS writing tasks"""
        response = requests.get(
            f"{BASE_URL}/api/exams/ielts/writing-tasks",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "ielts"
        assert "tasks" in data
        
        # IELTS has task1 and task2
        tasks = data["tasks"]
        assert "task1" in tasks or "task2" in tasks
    
    def test_get_toefl_writing_tasks(self, auth_headers):
        """Test getting TOEFL writing tasks"""
        response = requests.get(
            f"{BASE_URL}/api/exams/toefl/writing-tasks",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["exam_type"] == "toefl"
        assert "tasks" in data
    
    def test_writing_tasks_have_requirements(self, auth_headers):
        """Test that writing tasks include word count requirements"""
        response = requests.get(
            f"{BASE_URL}/api/exams/ielts/writing-tasks",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        tasks = data["tasks"]
        
        # Check task2 has requirements
        if "task2" in tasks and len(tasks["task2"]) > 0:
            task = tasks["task2"][0]
            assert "prompt" in task
            assert "min_words" in task
            assert task["min_words"] >= 250


class TestVoiceFeatures:
    """Test voice-related endpoints"""
    
    def test_get_available_voices(self):
        """Test GET /api/voice/available-voices returns voice list"""
        response = requests.get(f"{BASE_URL}/api/voice/available-voices")
        assert response.status_code == 200
        
        data = response.json()
        assert "voices" in data
        assert "default" in data
        assert len(data["voices"]) >= 9  # Should have 9 voices
        
        # Verify voice structure
        voice = data["voices"][0]
        assert "id" in voice
        assert "name" in voice
        assert "description" in voice
    
    def test_voice_list_includes_nova(self):
        """Test that voice list includes nova (default voice)"""
        response = requests.get(f"{BASE_URL}/api/voice/available-voices")
        assert response.status_code == 200
        
        data = response.json()
        voice_ids = [v["id"] for v in data["voices"]]
        assert "nova" in voice_ids
        assert data["default"] == "nova"


class TestAITutorVoiceChat:
    """Test POST /api/ai-tutor/voice-chat endpoint"""
    
    def test_voice_chat_returns_text_and_audio(self, auth_headers):
        """Test that voice chat returns both text response and audio"""
        response = requests.post(
            f"{BASE_URL}/api/ai-tutor/voice-chat",
            headers=auth_headers,
            json={
                "message": "What is the best strategy for IELTS reading?",
                "exam_type": "ielts",
                "voice": "nova"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "text_response" in data
        assert len(data["text_response"]) > 0
        assert "audio_base64" in data
        assert len(data["audio_base64"]) > 0
        assert "voice" in data
    
    def test_voice_chat_with_different_voice(self, auth_headers):
        """Test voice chat with different voice selection"""
        response = requests.post(
            f"{BASE_URL}/api/ai-tutor/voice-chat",
            headers=auth_headers,
            json={
                "message": "Give me a quick tip for TOEFL speaking",
                "exam_type": "toefl",
                "voice": "alloy"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "text_response" in data
        assert "audio_base64" in data


class TestAITutorTextChat:
    """Test POST /api/ai-tutor/chat endpoint"""
    
    def test_text_chat_returns_response(self, auth_headers):
        """Test that text chat returns AI response"""
        response = requests.post(
            f"{BASE_URL}/api/ai-tutor/chat",
            headers=auth_headers,
            json={
                "message": "What are the main sections of IELTS?",
                "exam_type": "ielts"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0


class TestExamSubmission:
    """Test POST /api/exams/submit endpoint"""
    
    def test_submit_exam_attempt(self, auth_headers):
        """Test submitting an exam attempt"""
        response = requests.post(
            f"{BASE_URL}/api/exams/submit",
            headers=auth_headers,
            json={
                "exam_type": "ielts",
                "section": "reading",
                "answers": [
                    {"question_id": "q1", "answer": "B", "is_correct": True},
                    {"question_id": "q2", "answer": "A", "is_correct": False}
                ],
                "time_spent": 1200
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "score" in data
        assert "feedback" in data


class TestExamHistory:
    """Test GET /api/exams/history endpoint"""
    
    def test_get_exam_history(self, auth_headers):
        """Test getting exam history"""
        response = requests.get(
            f"{BASE_URL}/api/exams/history",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "attempts" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
