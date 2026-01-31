"""
Test P0 (AI Agents Config) and P1 (Student Exam Dashboard) features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://oet-learning.preview.emergentagent.com').rstrip('/')

class TestAIAgentsConfig:
    """P0: AI Agents Configuration Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as institution and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_ai_agents_config(self):
        """GET /api/ai-agents/config returns 3 agents"""
        response = requests.get(f"{BASE_URL}/api/ai-agents/config", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should contain 'agents'"
        assert len(data["agents"]) == 3, f"Expected 3 agents, got {len(data['agents'])}"
        
        # Verify agent structure
        agent_ids = [a["id"] for a in data["agents"]]
        assert "official_tutor" in agent_ids, "Missing official_tutor agent"
        assert "mock_coach" in agent_ids, "Missing mock_coach agent"
        assert "planner" in agent_ids, "Missing planner agent"
        
        # Verify each agent has required fields
        for agent in data["agents"]:
            assert "id" in agent, "Agent missing 'id'"
            assert "name" in agent, "Agent missing 'name'"
            assert "enabled" in agent, "Agent missing 'enabled'"
            assert "credits_per_message" in agent, "Agent missing 'credits_per_message'"
        
        print(f"SUCCESS: GET /api/ai-agents/config returned {len(data['agents'])} agents")
    
    def test_save_ai_agents_config(self):
        """POST /api/ai-agents/config saves configuration"""
        payload = {
            "agents": {
                "official_tutor": {"enabled": True, "voice_id": "nova"},
                "mock_coach": {"enabled": True, "voice_id": "echo"},
                "planner": {"enabled": True, "voice_id": None}
            },
            "default_voice_enabled": True
        }
        
        response = requests.post(f"{BASE_URL}/api/ai-agents/config", 
                                headers=self.headers, json=payload)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True or "message" in data, "Save should return success"
        
        print("SUCCESS: POST /api/ai-agents/config saved configuration")
    
    def test_get_available_agents(self):
        """GET /api/ai-agents/available returns available agents"""
        response = requests.get(f"{BASE_URL}/api/ai-agents/available", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should contain 'agents'"
        
        print(f"SUCCESS: GET /api/ai-agents/available returned agents")


class TestStudentExamDashboard:
    """P1: Student Exam Dashboard Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as student and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "TEST_ui_student_1769781073@test.com",
            "password": "UtzILxgGZI4C"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_student_credits(self):
        """GET /api/exam-plans/my-credits returns student credits"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-credits", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "credits" in data, "Response should contain 'credits'"
        
        # Verify credit structure
        credits = data["credits"]
        assert "mocks" in credits, "Credits should have 'mocks'"
        assert "speaking" in credits, "Credits should have 'speaking'"
        assert "writing" in credits, "Credits should have 'writing'"
        
        print(f"SUCCESS: GET /api/exam-plans/my-credits returned credits")
    
    def test_get_exam_history(self):
        """GET /api/exam-plans/my-history returns exam history"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-history?exam_type=oet&limit=10", 
                               headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "attempts" in data, "Response should contain 'attempts'"
        
        print(f"SUCCESS: GET /api/exam-plans/my-history returned {len(data.get('attempts', []))} attempts")
    
    def test_get_upsell_options(self):
        """GET /api/exam-plans/upsell-options returns upsell options"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/upsell-options", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Upsell options should have available plans or quick buys
        assert "available_plans" in data or "quick_buys" in data, "Response should contain plans"
        
        print(f"SUCCESS: GET /api/exam-plans/upsell-options returned options")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
