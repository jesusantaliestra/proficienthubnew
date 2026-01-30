"""
Test suite for Landing Agent and New Institution Routers
Tests: landing_agent, institution_students, institution_settings, institution_messaging
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "santaliestralimited@gmail.com"
ADMIN_PASSWORD = "Admin123!"
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope="module")
def institution_token(api_client):
    """Get institution authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": INSTITUTION_EMAIL,
        "password": INSTITUTION_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Institution authentication failed")


class TestLandingAgentPublicEndpoints:
    """Test Landing Agent public endpoints (no auth required)"""
    
    def test_get_landing_agent_config(self, api_client):
        """GET /api/landing-agent/config - Returns public config"""
        response = api_client.get(f"{BASE_URL}/api/landing-agent/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        assert "greeting_message" in data
        assert "max_messages" in data
        print(f"Landing agent config: enabled={data['enabled']}, max_messages={data['max_messages']}")
    
    def test_landing_agent_chat(self, api_client):
        """POST /api/landing-agent/chat - Chat with landing agent"""
        response = api_client.post(f"{BASE_URL}/api/landing-agent/chat", json={
            "message": "What is ProficientHub?"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "remaining_messages" in data
        assert "limit_reached" in data
        print(f"Chat response received, remaining_messages={data['remaining_messages']}")


class TestLandingAgentAdminEndpoints:
    """Test Landing Agent admin endpoints (auth required)"""
    
    def test_get_admin_config(self, api_client, admin_token):
        """GET /api/landing-agent/admin/config - Returns full config"""
        response = api_client.get(
            f"{BASE_URL}/api/landing-agent/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "llm_provider" in data
        assert "llm_model" in data
        assert "max_messages_per_session" in data
        print(f"Admin config: provider={data.get('llm_provider')}, model={data.get('llm_model')}")
    
    def test_update_admin_config(self, api_client, admin_token):
        """PUT /api/landing-agent/admin/config - Update config"""
        response = api_client.put(
            f"{BASE_URL}/api/landing-agent/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "enabled": True,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "max_messages_per_session": 5,
                "greeting_message": "¡Hola! Soy el asistente de ProficientHub."
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        print(f"Config update response: {data['message']}")
    
    def test_get_admin_stats(self, api_client, admin_token):
        """GET /api/landing-agent/admin/stats - Returns usage stats"""
        response = api_client.get(
            f"{BASE_URL}/api/landing-agent/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "active_sessions" in data
        assert "total_messages" in data
        assert "by_provider" in data
        print(f"Stats: sessions={data['active_sessions']}, messages={data['total_messages']}")


class TestInstitutionStudentsRouter:
    """Test Institution Students Router endpoints"""
    
    def test_get_institution_students(self, api_client, institution_token):
        """GET /api/institution/students - List students"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/students",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Response could be a list or object with students key
        if isinstance(data, list):
            print(f"Found {len(data)} students")
        elif isinstance(data, dict) and "students" in data:
            print(f"Found {len(data['students'])} students")
        else:
            print(f"Students response: {type(data)}")


class TestInstitutionSettingsRouter:
    """Test Institution Settings Router endpoints"""
    
    def test_get_institution_settings(self, api_client, institution_token):
        """GET /api/institution/settings - Get all settings"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/settings",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "institution_id" in data
        print(f"Settings retrieved for institution: {data.get('institution_id', 'N/A')[:20]}...")
    
    def test_get_placement_test_config(self, api_client, institution_token):
        """GET /api/institution/settings/placement-test - Get placement test config"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/settings/placement-test",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Field could be 'enabled' or 'placement_test_enabled'
        enabled = data.get("enabled") or data.get("placement_test_enabled")
        assert enabled is not None
        print(f"Placement test enabled: {enabled}")


class TestInstitutionMessagingRouter:
    """Test Institution Messaging Router endpoints"""
    
    def test_get_messaging_config(self, api_client, institution_token):
        """GET /api/institution/messaging/config - Get messaging config"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/messaging/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        print(f"Messaging enabled: {data.get('enabled')}, provider: {data.get('provider')}")
    
    def test_get_messaging_providers(self, api_client, institution_token):
        """GET /api/institution/messaging/providers - Get available providers"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/messaging/providers",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "providers" in data
        providers = data["providers"]
        assert len(providers) > 0
        print(f"Available providers: {[p['name'] for p in providers]}")
    
    def test_get_email_templates(self, api_client, institution_token):
        """GET /api/institution/email-templates - Get email templates"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/email-templates",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        print(f"Found {len(data['templates'])} email templates")
    
    def test_get_reports_config(self, api_client, institution_token):
        """GET /api/institution/reports/config - Get reports config"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/reports/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Field could be 'enabled' or 'weekly_enabled' or other report config fields
        assert isinstance(data, dict)
        print(f"Reports config retrieved: {list(data.keys())[:5]}")
    
    def test_generate_report(self, api_client, institution_token):
        """GET /api/institution/reports/generate - Generate a report"""
        response = api_client.get(
            f"{BASE_URL}/api/institution/reports/generate?report_type=overview",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Report could have different structures
        assert isinstance(data, dict)
        # Check for common report fields
        has_report_data = any(key in data for key in ["report_type", "summary", "exams", "engagement", "ai_usage"])
        assert has_report_data, f"Report should contain report data, got keys: {list(data.keys())}"
        print(f"Report generated with keys: {list(data.keys())[:5]}")


class TestHealthAndModulesLoaded:
    """Test that all modules are loaded correctly"""
    
    def test_health_check(self, api_client):
        """GET /api/health - Health check"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"
        print("Backend health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
