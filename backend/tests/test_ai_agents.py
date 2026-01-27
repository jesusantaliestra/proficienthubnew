"""
Test suite for Multi-Agent AI Tutor System
Tests: AI Agents endpoints, Credits management, Mock Coach functionality
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"
STUDENT_EMAIL = "maria@demo.com"
STUDENT_PASSWORD = "Demo123!"


class TestAIAgentsBackend:
    """Test AI Agents backend endpoints"""
    
    @pytest.fixture(scope="class")
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Institution login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def student_token(self):
        """Get student auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Student login failed: {response.status_code} - {response.text}")
    
    # ==================== GET /api/ai-agents/available ====================
    
    def test_get_available_agents_returns_3_agents(self, student_token):
        """GET /api/ai-agents/available - Returns list of 3 agents with correct properties"""
        response = requests.get(
            f"{BASE_URL}/api/ai-agents/available",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should contain 'agents' key"
        
        agents = data["agents"]
        assert len(agents) >= 3, f"Expected at least 3 agents, got {len(agents)}"
        
        # Verify agent properties
        agent_ids = [a["id"] for a in agents]
        assert "official_tutor" in agent_ids, "official_tutor agent should be available"
        assert "mock_coach" in agent_ids, "mock_coach agent should be available"
        assert "planner" in agent_ids, "planner agent should be available"
        
        # Verify each agent has required properties
        for agent in agents:
            assert "id" in agent, "Agent should have 'id'"
            assert "name" in agent, "Agent should have 'name'"
            assert "name_es" in agent, "Agent should have 'name_es'"
            assert "description" in agent, "Agent should have 'description'"
            assert "credits_per_message" in agent, "Agent should have 'credits_per_message'"
            assert "voice_enabled" in agent, "Agent should have 'voice_enabled'"
        
        print(f"✓ Found {len(agents)} agents: {agent_ids}")
    
    # ==================== GET /api/ai-agents/credits ====================
    
    def test_get_credits_returns_balance(self, student_token):
        """GET /api/ai-agents/credits - Returns credit balance with total, used, remaining"""
        response = requests.get(
            f"{BASE_URL}/api/ai-agents/credits",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_credits" in data, "Response should contain 'total_credits'"
        assert "used_credits" in data, "Response should contain 'used_credits'"
        assert "remaining_credits" in data, "Response should contain 'remaining_credits'"
        
        # Verify remaining = total - used
        expected_remaining = data["total_credits"] - data["used_credits"]
        assert data["remaining_credits"] == expected_remaining, \
            f"remaining_credits should be {expected_remaining}, got {data['remaining_credits']}"
        
        print(f"✓ Credits: {data['remaining_credits']} remaining of {data['total_credits']} total")
    
    def test_get_credits_institution(self, institution_token):
        """GET /api/ai-agents/credits - Institution gets credit balance"""
        response = requests.get(
            f"{BASE_URL}/api/ai-agents/credits",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_credits" in data
        assert "remaining_credits" in data
        
        # Institutions should have at least 100 free starter credits
        assert data["total_credits"] >= 100, f"Institution should have at least 100 credits, got {data['total_credits']}"
        
        print(f"✓ Institution credits: {data['remaining_credits']} remaining")
    
    # ==================== GET /api/ai-agents/config ====================
    
    def test_get_agent_config(self, institution_token):
        """GET /api/ai-agents/config - Returns agent configuration for institution"""
        response = requests.get(
            f"{BASE_URL}/api/ai-agents/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should contain 'agents'"
        
        agents = data["agents"]
        assert len(agents) >= 3, f"Expected at least 3 agents in config, got {len(agents)}"
        
        # Verify each agent has enabled status
        for agent in agents:
            assert "id" in agent
            assert "enabled" in agent, f"Agent {agent.get('id')} should have 'enabled' field"
        
        print(f"✓ Agent config returned with {len(agents)} agents")
    
    # ==================== POST /api/ai-agents/config ====================
    
    def test_update_agent_config(self, institution_token):
        """POST /api/ai-agents/config - Update agent configuration (enable/disable agents)"""
        # First get current config
        get_response = requests.get(
            f"{BASE_URL}/api/ai-agents/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert get_response.status_code == 200
        
        # Update config - disable planner temporarily
        update_data = {
            "agents": {
                "official_tutor": {"enabled": True, "voice_id": "nova"},
                "mock_coach": {"enabled": True, "voice_id": "echo"},
                "planner": {"enabled": False}  # Disable planner
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/config",
            json=update_data,
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Update should return success=True"
        
        # Re-enable planner for other tests
        update_data["agents"]["planner"]["enabled"] = True
        requests.post(
            f"{BASE_URL}/api/ai-agents/config",
            json=update_data,
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        print("✓ Agent configuration updated successfully")
    
    def test_update_agent_config_student_forbidden(self, student_token):
        """POST /api/ai-agents/config - Students cannot update config"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/config",
            json={"agents": {}},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403 for student, got {response.status_code}"
        print("✓ Students correctly forbidden from updating config")
    
    # ==================== POST /api/ai-agents/interact ====================
    
    def test_interact_with_official_tutor(self, student_token):
        """POST /api/ai-agents/interact - Interact with Official Tutor agent"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/interact",
            json={
                "agent_type": "official_tutor",
                "message": "What are the main sections of the IELTS exam?",
                "exam_type": "ielts",
                "voice_enabled": False
            },
            headers={"Authorization": f"Bearer {student_token}"},
            timeout=30  # AI responses can take time
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check for success or insufficient credits
        if data.get("success") == False and data.get("error") == "insufficient_credits":
            print("⚠ Insufficient credits - skipping AI interaction test")
            pytest.skip("Insufficient credits for AI interaction")
        
        assert data.get("success") == True, f"Interaction should succeed: {data}"
        assert "response" in data, "Response should contain AI response text"
        assert "session_id" in data, "Response should contain session_id"
        assert "credits_consumed" in data, "Response should show credits consumed"
        
        # Verify response is meaningful
        assert len(data["response"]) > 50, "AI response should be substantial"
        
        print(f"✓ Official Tutor responded ({len(data['response'])} chars), {data['credits_consumed']} credit(s) used")
    
    def test_interact_with_planner(self, student_token):
        """POST /api/ai-agents/interact - Interact with Planner agent"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/interact",
            json={
                "agent_type": "planner",
                "message": "I have my IELTS exam in 2 months. I can study 2 hours per day.",
                "exam_type": "ielts",
                "voice_enabled": False
            },
            headers={"Authorization": f"Bearer {student_token}"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        if data.get("success") == False and data.get("error") == "insufficient_credits":
            print("⚠ Insufficient credits - skipping planner test")
            pytest.skip("Insufficient credits for AI interaction")
        
        assert data.get("success") == True, f"Planner interaction should succeed: {data}"
        assert "response" in data
        
        print(f"✓ Planner responded ({len(data['response'])} chars)")
    
    def test_interact_invalid_agent_type(self, student_token):
        """POST /api/ai-agents/interact - Invalid agent type returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/interact",
            json={
                "agent_type": "invalid_agent",
                "message": "Hello",
                "exam_type": "ielts"
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid agent, got {response.status_code}"
        print("✓ Invalid agent type correctly rejected")
    
    # ==================== Mock Coach Endpoints ====================
    
    def test_mock_coach_start_question(self, student_token):
        """POST /api/ai-agents/mock-coach/start-question - Start practice question session"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/mock-coach/start-question?exam_type=ielts&section=reading",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "session_id" in data, "Response should contain session_id"
        assert "question" in data, "Response should contain question"
        assert "max_attempts" in data, "Response should contain max_attempts"
        assert data["max_attempts"] == 5, "Max attempts should be 5"
        
        print(f"✓ Mock Coach question started: {data['question'][:50]}...")
        return data["session_id"]
    
    def test_mock_coach_check_wrong_answer_gives_hint(self, student_token):
        """POST /api/ai-agents/mock-coach/check-answer - Wrong answer gives hint"""
        # First start a question
        start_response = requests.post(
            f"{BASE_URL}/api/ai-agents/mock-coach/start-question?exam_type=ielts&section=reading",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        
        # Submit wrong answer
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/mock-coach/check-answer?session_id={session_id}&answer=wrong_answer",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("correct") == False, "Wrong answer should be marked incorrect"
        assert "hint" in data, "Wrong answer should provide a hint"
        assert "attempts_remaining" in data, "Should show attempts remaining"
        assert data["attempts_remaining"] == 4, "Should have 4 attempts remaining after 1 wrong"
        
        print(f"✓ Wrong answer gave hint: {data['hint']}")
    
    def test_mock_coach_correct_answer_revealed_after_5_attempts(self, student_token):
        """POST /api/ai-agents/mock-coach/check-answer - Correct answer revealed after 5 attempts"""
        # Start a question
        start_response = requests.post(
            f"{BASE_URL}/api/ai-agents/mock-coach/start-question?exam_type=ielts&section=grammar",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        
        # Submit 5 wrong answers
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/ai-agents/mock-coach/check-answer?session_id={session_id}&answer=wrong_{i}",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            
            if i < 4:
                # First 4 attempts should give hints
                assert data.get("correct") == False
                assert "hint" in data, f"Attempt {i+1} should give hint"
            else:
                # 5th attempt should reveal answer
                assert data.get("max_attempts_reached") == True, "5th attempt should trigger max_attempts_reached"
                assert "correct_answer" in data, "Should reveal correct answer after 5 attempts"
                print(f"✓ Correct answer revealed after 5 attempts: {data['correct_answer']}")
    
    # ==================== POST /api/ai-agents/credits/purchase ====================
    
    def test_purchase_credits(self, institution_token):
        """POST /api/ai-agents/credits/purchase - Purchase credits"""
        # Get initial credits
        initial_response = requests.get(
            f"{BASE_URL}/api/ai-agents/credits",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        initial_credits = initial_response.json().get("total_credits", 0)
        
        # Purchase 100 credits
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/credits/purchase",
            json={"credits": 100, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Purchase should succeed"
        assert data.get("credits_added") == 100, "Should add 100 credits"
        
        # Verify credits increased
        final_response = requests.get(
            f"{BASE_URL}/api/ai-agents/credits",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        final_credits = final_response.json().get("total_credits", 0)
        
        assert final_credits == initial_credits + 100, \
            f"Credits should increase by 100: {initial_credits} -> {final_credits}"
        
        print(f"✓ Purchased 100 credits: {initial_credits} -> {final_credits}")
    
    def test_purchase_credits_invalid_amount(self, institution_token):
        """POST /api/ai-agents/credits/purchase - Invalid credit amount rejected"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/credits/purchase",
            json={"credits": 50, "payment_method": "stripe"},  # 50 is not a valid tier
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid amount, got {response.status_code}"
        print("✓ Invalid credit amount correctly rejected")
    
    def test_purchase_credits_student_forbidden(self, student_token):
        """POST /api/ai-agents/credits/purchase - Students cannot purchase credits"""
        response = requests.post(
            f"{BASE_URL}/api/ai-agents/credits/purchase",
            json={"credits": 100, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403 for student, got {response.status_code}"
        print("✓ Students correctly forbidden from purchasing credits")
    
    # ==================== GET /api/ai-agents/sessions ====================
    
    def test_get_sessions(self, student_token):
        """GET /api/ai-agents/sessions - Get user's chat sessions"""
        response = requests.get(
            f"{BASE_URL}/api/ai-agents/sessions",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "sessions" in data, "Response should contain 'sessions'"
        
        # Sessions is a list (may be empty if no prior interactions)
        assert isinstance(data["sessions"], list), "Sessions should be a list"
        
        print(f"✓ Found {len(data['sessions'])} chat sessions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
