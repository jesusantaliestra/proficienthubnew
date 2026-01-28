"""
Test suite for Messaging Router (SMS/WhatsApp multi-provider integration)
Tests: GET /api/institution/messaging/providers, GET/POST /api/institution/messaging/config,
       POST /api/institution/messaging/test, GET /api/institution/messaging/logs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMessagingRouter:
    """Tests for the Institution Messaging API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as institution"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Also get admin token for 403 tests
        admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        if admin_login.status_code == 200:
            self.admin_token = admin_login.json().get("access_token")
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        else:
            self.admin_token = None
            self.admin_headers = None
    
    def test_get_messaging_providers(self):
        """GET /api/institution/messaging/providers - returns list of supported providers"""
        response = requests.get(f"{BASE_URL}/api/institution/messaging/providers", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "providers" in data
        providers = data["providers"]
        
        # Should have multiple providers
        assert len(providers) >= 10, f"Expected at least 10 providers, got {len(providers)}"
        
        # Verify provider structure
        for provider in providers:
            assert "id" in provider
            assert "name" in provider
            assert "regions" in provider
            assert "features" in provider
        
        # Verify known providers exist
        provider_ids = [p["id"] for p in providers]
        assert "twilio" in provider_ids
        assert "vonage" in provider_ids
        assert "messagebird" in provider_ids
    
    def test_get_messaging_config(self):
        """GET /api/institution/messaging/config - returns current config"""
        response = requests.get(f"{BASE_URL}/api/institution/messaging/config", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify config structure (should not expose secrets)
        assert "provider" in data or data.get("provider") is None
        assert "enabled" in data
        assert "sms_enabled" in data
        assert "whatsapp_enabled" in data
        assert "has_credentials" in data
        
        # Should not expose actual credentials
        assert "api_key" not in data
        assert "api_secret" not in data
        assert "auth_token" not in data
    
    def test_update_messaging_config(self):
        """POST /api/institution/messaging/config - updates configuration"""
        config = {
            "provider": "twilio",
            "enabled": True,
            "sms_enabled": True,
            "whatsapp_enabled": False,
            "from_number": "+1234567890"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution/messaging/config",
            headers=self.headers,
            json=config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        # Verify config was updated
        verify_resp = requests.get(f"{BASE_URL}/api/institution/messaging/config", headers=self.headers)
        assert verify_resp.status_code == 200
        updated_config = verify_resp.json()
        assert updated_config["provider"] == "twilio"
        assert updated_config["enabled"] == True
    
    def test_get_messaging_logs(self):
        """GET /api/institution/messaging/logs - returns message logs"""
        response = requests.get(f"{BASE_URL}/api/institution/messaging/logs", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        assert isinstance(data["total"], int)
    
    def test_messaging_logs_with_limit(self):
        """GET /api/institution/messaging/logs?limit=10 - respects limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/institution/messaging/logs",
            headers=self.headers,
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) <= 10


class TestMessagingProviderDetails:
    """Tests for specific provider configurations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as institution"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_providers_have_correct_features(self):
        """Verify providers have correct feature flags"""
        response = requests.get(f"{BASE_URL}/api/institution/messaging/providers", headers=self.headers)
        assert response.status_code == 200
        
        providers = {p["id"]: p for p in response.json()["providers"]}
        
        # Twilio should support both SMS and WhatsApp
        assert "twilio" in providers
        twilio = providers["twilio"]
        assert "SMS" in twilio["features"] or "sms" in [f.lower() for f in twilio["features"]]
        
        # Vonage should support SMS
        assert "vonage" in providers
    
    def test_providers_have_regions(self):
        """Verify providers have region information"""
        response = requests.get(f"{BASE_URL}/api/institution/messaging/providers", headers=self.headers)
        assert response.status_code == 200
        
        for provider in response.json()["providers"]:
            assert len(provider["regions"]) > 0, f"Provider {provider['id']} has no regions"
