"""
Test suite for Conversion Analytics endpoints
Tests funnel tracking, trends, demo analytics, and chat widget metrics
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestConversionAnalytics:
    """Conversion Analytics endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.admin_token = token
        else:
            pytest.skip("Admin login failed - skipping conversion analytics tests")
    
    def test_health_check(self):
        """Test backend health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_get_funnel_metrics(self):
        """Test GET /api/conversion-analytics/funnel returns funnel data"""
        response = self.session.get(f"{BASE_URL}/api/conversion-analytics/funnel?days=30")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert "period_days" in data
        assert "total_visits" in data
        assert "funnel" in data
        assert "overall_conversion" in data
        
        # Verify funnel has 10 stages
        assert len(data["funnel"]) == 10
        
        # Verify each stage has required fields
        expected_stages = [
            "landing_visit", "chat_widget_opened", "chat_interaction",
            "demo_requested", "demo_activated", "demo_engaged",
            "pricing_viewed", "checkout_started", "payment_completed",
            "converted_to_customer"
        ]
        
        for i, stage in enumerate(data["funnel"]):
            assert stage["stage"] == expected_stages[i]
            assert "count" in stage
            assert "conversion_rate" in stage
            assert "label" in stage
            assert "step_conversion" in stage
        
        print(f"✓ Funnel metrics returned with {len(data['funnel'])} stages")
        print(f"  Total visits: {data['total_visits']}")
        print(f"  Overall conversion: {data['overall_conversion']}%")
    
    def test_get_trends(self):
        """Test GET /api/conversion-analytics/trends returns daily trends"""
        response = self.session.get(f"{BASE_URL}/api/conversion-analytics/trends?days=30")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert "period_days" in data
        assert "trends" in data
        assert "stages" in data
        
        # Verify stages list
        assert len(data["stages"]) == 10
        
        # Verify trends data structure (if any data exists)
        if data["trends"]:
            trend = data["trends"][0]
            assert "date" in trend
            # Each trend should have all stage keys
            for stage in data["stages"]:
                assert stage in trend
        
        print(f"✓ Trends returned with {len(data['trends'])} days of data")
    
    def test_get_demo_analytics(self):
        """Test GET /api/conversion-analytics/demo-analytics returns demo stats"""
        response = self.session.get(f"{BASE_URL}/api/conversion-analytics/demo-analytics?days=30")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert "period_days" in data
        assert "total_demos" in data
        assert "active_demos" in data
        assert "converted_demos" in data
        assert "expired_demos" in data
        assert "conversion_rate" in data
        assert "avg_engagement_events" in data
        assert "metrics" in data
        
        # Verify metrics sub-structure
        assert "demo_to_conversion" in data["metrics"]
        assert "active_rate" in data["metrics"]
        
        print(f"✓ Demo analytics returned")
        print(f"  Total demos: {data['total_demos']}")
        print(f"  Active demos: {data['active_demos']}")
        print(f"  Conversion rate: {data['conversion_rate']}%")
    
    def test_get_chat_widget_metrics(self):
        """Test GET /api/conversion-analytics/chat-widget-metrics returns chat stats"""
        response = self.session.get(f"{BASE_URL}/api/conversion-analytics/chat-widget-metrics?days=30")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert "period_days" in data
        assert "chat_opened" in data
        assert "chat_interacted" in data
        assert "total_messages" in data
        assert "unique_sessions" in data
        assert "avg_messages_per_session" in data
        assert "engagement_rate" in data
        
        print(f"✓ Chat widget metrics returned")
        print(f"  Chat opened: {data['chat_opened']}")
        print(f"  Total messages: {data['total_messages']}")
        print(f"  Engagement rate: {data['engagement_rate']}%")
    
    def test_track_funnel_event(self):
        """Test POST /api/conversion-analytics/track creates funnel event"""
        # Track a landing visit event
        response = self.session.post(f"{BASE_URL}/api/conversion-analytics/track", json={
            "stage": "landing_visit",
            "session_id": "test_session_123",
            "metadata": {"source": "test"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "event_id" in data
        
        print(f"✓ Funnel event tracked with ID: {data['event_id']}")
    
    def test_track_invalid_stage(self):
        """Test POST /api/conversion-analytics/track rejects invalid stage"""
        response = self.session.post(f"{BASE_URL}/api/conversion-analytics/track", json={
            "stage": "invalid_stage",
            "session_id": "test_session_123"
        })
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        
        print("✓ Invalid stage correctly rejected")
    
    def test_funnel_requires_admin(self):
        """Test funnel endpoint requires admin user_type"""
        # Create a new session without auth
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Try to access funnel without auth
        response = session.get(f"{BASE_URL}/api/conversion-analytics/funnel?days=30")
        assert response.status_code in [401, 403]
        
        print("✓ Funnel endpoint correctly requires authentication")
    
    def test_funnel_different_periods(self):
        """Test funnel endpoint with different time periods"""
        for days in [7, 14, 30, 60, 90]:
            response = self.session.get(f"{BASE_URL}/api/conversion-analytics/funnel?days={days}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["period_days"] == days
        
        print("✓ Funnel endpoint works with different time periods (7, 14, 30, 60, 90 days)")


class TestI18nConfiguration:
    """Test i18n configuration and language support"""
    
    def test_i18n_file_exists(self):
        """Verify i18n configuration file exists"""
        import os
        i18n_path = "/app/frontend/src/i18n/index.js"
        assert os.path.exists(i18n_path)
        print("✓ i18n configuration file exists")
    
    def test_supported_languages(self):
        """Verify 6 main languages are configured"""
        with open("/app/frontend/src/i18n/index.js", "r") as f:
            content = f.read()
        
        # Check for main language translations
        main_languages = ["en:", "es:", "pt:", "zh:", "fr:", "de:"]
        for lang in main_languages:
            assert lang in content, f"Language {lang} not found in i18n config"
        
        print("✓ All 6 main languages (EN, ES, PT, ZH, FR, DE) are configured")
    
    def test_translation_namespaces(self):
        """Verify translation namespaces exist"""
        with open("/app/frontend/src/i18n/index.js", "r") as f:
            content = f.read()
        
        # Check for required namespaces
        namespaces = ["nav:", "landing:", "pricing:", "dashboard:", "exams:", "common:"]
        for ns in namespaces:
            assert ns in content, f"Namespace {ns} not found in i18n config"
        
        print("✓ All required translation namespaces exist (nav, landing, pricing, dashboard, exams, common)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
