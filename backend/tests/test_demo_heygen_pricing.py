"""
Test Suite for Demo Premium, HeyGen Tutorials, Conversion Analytics, and Pricing Features
Tests: Demo 7-day system, HeyGen integration, Conversion funnel, Pricing with duration selector
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDemoPremiumSystem:
    """Demo Premium 7-day system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_demo_admin_config_returns_7_days_default(self):
        """GET /api/demo/admin/config - Returns config with 7 days default"""
        response = requests.get(f"{BASE_URL}/api/demo/admin/config", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify 7 days default
        assert data["default_duration_days"] == 7, f"Expected 7 days, got {data['default_duration_days']}"
        assert data["max_students_demo"] == 50
        assert "features_enabled" in data
        assert len(data["features_enabled"]) == 8  # 8 features
    
    def test_demo_request_creates_demo(self):
        """POST /api/demo/request - Creates demo with 7 days"""
        response = requests.post(f"{BASE_URL}/api/demo/request", json={
            "institution_name": "TEST_Demo Academy",
            "contact_email": "test_demo@example.com",
            "contact_name": "Test Contact",
            "phone": "+1234567890",
            "num_students": 30,
            "exam_types": ["toefl", "ielts"],
            "notes": "Test demo request"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["duration_days"] == 7
        assert "demo_id" in data
        assert "expires_at" in data
        assert "credentials" in data
        assert len(data["features"]) == 8
    
    def test_demo_admin_list(self):
        """GET /api/demo/admin/list - Lists all demos"""
        response = requests.get(f"{BASE_URL}/api/demo/admin/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "demos" in data
        assert "total" in data


class TestHeyGenIntegration:
    """HeyGen Tutorial integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_heygen_admin_config_api_key_configured(self):
        """GET /api/heygen/admin/config - Returns api_key_configured: true"""
        response = requests.get(f"{BASE_URL}/api/heygen/admin/config", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["api_key_configured"] == True, "HeyGen API key should be configured"
        assert data["enabled"] == True
        assert "tutorial_templates" in data
    
    def test_heygen_admin_avatars_returns_list(self):
        """GET /api/heygen/admin/avatars - Returns avatars list (1287 expected)"""
        response = requests.get(f"{BASE_URL}/api/heygen/admin/avatars", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "avatars" in data
        assert "total" in data
        # Should have 1287 avatars as per requirements
        assert data["total"] >= 1000, f"Expected ~1287 avatars, got {data['total']}"
    
    def test_heygen_templates(self):
        """GET /api/heygen/templates - Returns tutorial templates"""
        response = requests.get(f"{BASE_URL}/api/heygen/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert len(data["templates"]) >= 3  # At least 3 templates


class TestConversionAnalytics:
    """Conversion funnel tracking tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_conversion_funnel_returns_data(self):
        """GET /api/conversion-analytics/funnel - Returns funnel data"""
        response = requests.get(f"{BASE_URL}/api/conversion-analytics/funnel?days=30", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert data["period_days"] == 30
        assert "funnel" in data
        assert "total_visits" in data
        assert "overall_conversion" in data
        
        # Verify funnel stages
        stages = [f["stage"] for f in data["funnel"]]
        expected_stages = ["landing_visit", "chat_widget_opened", "demo_requested", "demo_activated"]
        for stage in expected_stages:
            assert stage in stages, f"Missing stage: {stage}"
    
    def test_conversion_track_event(self):
        """POST /api/conversion-analytics/track - Tracks funnel event"""
        response = requests.post(f"{BASE_URL}/api/conversion-analytics/track", json={
            "stage": "landing_visit",
            "session_id": "test_session_123",
            "metadata": {"source": "test"}
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "event_id" in data
    
    def test_demo_analytics(self):
        """GET /api/conversion-analytics/demo-analytics - Returns demo analytics"""
        response = requests.get(f"{BASE_URL}/api/conversion-analytics/demo-analytics?days=30", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total_demos" in data
        assert "active_demos" in data
        assert "conversion_rate" in data


class TestPricingWithDuration:
    """Pricing with duration selector tests"""
    
    def test_pricing_platform_plans(self):
        """GET /api/pricing/platform-plans - Returns pricing plans"""
        response = requests.get(f"{BASE_URL}/api/pricing/platform-plans")
        assert response.status_code == 200
        data = response.json()
        
        assert "exam_plans" in data
        assert "ai_tutor_options" in data
        assert "volume_pricing" in data
    
    def test_pricing_calculator(self):
        """GET /api/pricing/calculator - Calculates pricing"""
        response = requests.get(f"{BASE_URL}/api/pricing/calculator?exam_plan=plan_10&num_licenses=100&ai_tutor_option=none")
        assert response.status_code == 200
        data = response.json()
        
        assert "plan" in data
        assert "pricing" in data
        assert "price_per_license" in data["pricing"]
        assert "total_order_price" in data["pricing"]


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """GET /api/health - Backend health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_admin_login(self):
        """POST /api/auth/login - Admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "admin"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
