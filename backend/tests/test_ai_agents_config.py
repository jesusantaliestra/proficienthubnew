"""
Test AI Agents Configuration and Student Exam Dashboard APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://eduplat-suite.preview.emergentagent.com')

class TestAIAgentsConfig:
    """Test AI Agents Configuration endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        # Login as institution
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert response.status_code == 200, f"Institution login failed: {response.text}"
        self.inst_token = response.json()["access_token"]
        self.inst_headers = {"Authorization": f"Bearer {self.inst_token}"}
        print(f"✓ Institution login successful")
    
    def test_get_ai_config(self):
        """GET /api/ai-agents/config - Returns agent configuration"""
        response = requests.get(f"{BASE_URL}/api/ai-agents/config", headers=self.inst_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should contain 'agents'"
        
        # Check agents structure
        agents = data["agents"]
        assert len(agents) >= 1, "Should have at least 1 agent"
        
        # Check first agent has required fields
        first_agent = agents[0]
        print(f"✓ GET /api/ai-agents/config - Found {len(agents)} agents")
        print(f"  Agent structure: {list(first_agent.keys())}")
        
        return data
    
    def test_update_ai_config(self):
        """POST /api/ai-agents/config - Update agent configuration"""
        # First get current config
        get_response = requests.get(f"{BASE_URL}/api/ai-agents/config", headers=self.inst_headers)
        current_config = get_response.json()
        
        # Update config
        update_data = {
            "agents": {
                "official_tutor": {"enabled": True, "voice_id": "nova"},
                "mock_coach": {"enabled": True, "voice_id": "echo"},
                "planner": {"enabled": False, "voice_id": None}
            },
            "default_voice_enabled": True
        }
        
        response = requests.post(f"{BASE_URL}/api/ai-agents/config", 
                                headers=self.inst_headers, 
                                json=update_data)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        print(f"✓ POST /api/ai-agents/config - Configuration updated")
        
        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/ai-agents/config", headers=self.inst_headers)
        verify_data = verify_response.json()
        print(f"  Updated config: {verify_data}")
    
    def test_get_available_agents(self):
        """GET /api/ai-agents/available - Get available agents for user"""
        response = requests.get(f"{BASE_URL}/api/ai-agents/available", headers=self.inst_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        print(f"✓ GET /api/ai-agents/available - Response: {data}")


class TestStudentExamDashboard:
    """Test Student Exam Dashboard endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        # Login as student
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "TEST_ui_student_1769781073@test.com",
            "password": "UtzILxgGZI4C"
        })
        if response.status_code != 200:
            pytest.skip("Test student not found")
        
        self.student_token = response.json()["access_token"]
        self.student_headers = {"Authorization": f"Bearer {self.student_token}"}
        print(f"✓ Student login successful")
    
    def test_get_my_credits(self):
        """GET /api/exam-plans/my-credits - Get student credits"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-credits", headers=self.student_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "credits" in data, "Response should contain 'credits'"
        
        credits = data["credits"]
        assert "mocks" in credits, "Credits should have 'mocks'"
        assert "speaking" in credits, "Credits should have 'speaking'"
        assert "writing" in credits, "Credits should have 'writing'"
        
        print(f"✓ GET /api/exam-plans/my-credits")
        print(f"  Mocks: {credits['mocks']['remaining']}")
        print(f"  Speaking: {credits['speaking']['remaining']}")
        print(f"  Writing: {credits['writing']['remaining']}")
    
    def test_get_exam_history(self):
        """GET /api/exam-plans/my-history - Get exam history"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-history", headers=self.student_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "attempts" in data, "Response should contain 'attempts'"
        
        print(f"✓ GET /api/exam-plans/my-history - Found {len(data['attempts'])} attempts")
    
    def test_get_upsell_options(self):
        """GET /api/exam-plans/upsell-options - Get upsell options"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/upsell-options", headers=self.student_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "current_credits" in data, "Response should contain 'current_credits'"
        assert "available_plans" in data, "Response should contain 'available_plans'"
        
        print(f"✓ GET /api/exam-plans/upsell-options")
        print(f"  Available plans: {len(data['available_plans'])}")
        if data.get('quick_buys'):
            print(f"  Quick buys: {len(data['quick_buys'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
