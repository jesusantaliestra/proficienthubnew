"""
Test suite for Superadmin Alerts System
Tests: GET /api/superadmin/alerts, GET /api/superadmin/alerts/summary, 
       POST /api/superadmin/alerts/{id}/dismiss, DELETE /api/superadmin/alerts/dismissed
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAlertsSystem:
    """Tests for the Superadmin Alerts API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as superadmin"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Also get institution token for 403 tests
        inst_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if inst_login.status_code == 200:
            self.inst_token = inst_login.json().get("access_token")
            self.inst_headers = {"Authorization": f"Bearer {self.inst_token}"}
        else:
            self.inst_token = None
            self.inst_headers = None
    
    def test_get_alerts_success(self):
        """GET /api/superadmin/alerts - returns alerts with severity levels"""
        response = requests.get(f"{BASE_URL}/api/superadmin/alerts", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "alerts" in data
        assert "total" in data
        assert "summary" in data
        
        # Verify summary structure
        summary = data["summary"]
        assert "critical" in summary
        assert "warning" in summary
        assert "info" in summary
        assert "success" in summary
        
        # Verify alerts have required fields
        for alert in data["alerts"]:
            assert "id" in alert
            assert "alert_type" in alert
            assert "severity" in alert
            assert "title" in alert
            assert "description" in alert
            assert "created_at" in alert
            assert alert["severity"] in ["critical", "warning", "info", "success"]
            assert alert["alert_type"] in ["low_credits", "inactive_institution", "milestone", "revenue", "error_rate"]
    
    def test_get_alerts_summary(self):
        """GET /api/superadmin/alerts/summary - returns alert counts for badge"""
        response = requests.get(f"{BASE_URL}/api/superadmin/alerts/summary", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify summary structure
        assert "total_active" in data
        assert "critical" in data
        assert "warning" in data
        assert "has_critical" in data
        
        # Verify types
        assert isinstance(data["total_active"], int)
        assert isinstance(data["critical"], int)
        assert isinstance(data["warning"], int)
        assert isinstance(data["has_critical"], bool)
    
    def test_get_alerts_filter_by_severity(self):
        """GET /api/superadmin/alerts?severity=warning - filter by severity"""
        response = requests.get(
            f"{BASE_URL}/api/superadmin/alerts", 
            headers=self.headers,
            params={"severity": "warning"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned alerts should be warnings
        for alert in data["alerts"]:
            assert alert["severity"] == "warning"
    
    def test_get_alerts_filter_by_type(self):
        """GET /api/superadmin/alerts?alert_type=low_credits - filter by type"""
        response = requests.get(
            f"{BASE_URL}/api/superadmin/alerts", 
            headers=self.headers,
            params={"alert_type": "low_credits"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned alerts should be low_credits type
        for alert in data["alerts"]:
            assert alert["alert_type"] == "low_credits"
    
    def test_dismiss_alert(self):
        """POST /api/superadmin/alerts/{id}/dismiss - dismiss specific alert"""
        # First get alerts
        alerts_resp = requests.get(f"{BASE_URL}/api/superadmin/alerts", headers=self.headers)
        assert alerts_resp.status_code == 200
        alerts = alerts_resp.json().get("alerts", [])
        
        if len(alerts) == 0:
            pytest.skip("No alerts to dismiss")
        
        alert_id = alerts[0]["id"]
        
        # Dismiss the alert
        dismiss_resp = requests.post(
            f"{BASE_URL}/api/superadmin/alerts/{alert_id}/dismiss",
            headers=self.headers
        )
        
        assert dismiss_resp.status_code == 200
        data = dismiss_resp.json()
        assert data["success"] == True
        assert "message" in data
        
        # Verify alert is no longer in list
        verify_resp = requests.get(f"{BASE_URL}/api/superadmin/alerts", headers=self.headers)
        assert verify_resp.status_code == 200
        remaining_alerts = verify_resp.json().get("alerts", [])
        dismissed_ids = [a["id"] for a in remaining_alerts]
        assert alert_id not in dismissed_ids
    
    def test_clear_dismissed_alerts(self):
        """DELETE /api/superadmin/alerts/dismissed - clear all dismissed alerts"""
        response = requests.delete(
            f"{BASE_URL}/api/superadmin/alerts/dismissed",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "cleared" in data
        assert isinstance(data["cleared"], int)
    
    def test_alerts_forbidden_for_non_superadmin(self):
        """GET /api/superadmin/alerts - returns 403 for non-superadmin"""
        if not self.inst_headers:
            pytest.skip("Institution login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/superadmin/alerts",
            headers=self.inst_headers
        )
        
        assert response.status_code == 403
    
    def test_alerts_summary_forbidden_for_non_superadmin(self):
        """GET /api/superadmin/alerts/summary - returns 403 for non-superadmin"""
        if not self.inst_headers:
            pytest.skip("Institution login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/superadmin/alerts/summary",
            headers=self.inst_headers
        )
        
        assert response.status_code == 403
    
    def test_dismiss_forbidden_for_non_superadmin(self):
        """POST /api/superadmin/alerts/{id}/dismiss - returns 403 for non-superadmin"""
        if not self.inst_headers:
            pytest.skip("Institution login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/superadmin/alerts/test_alert_id/dismiss",
            headers=self.inst_headers
        )
        
        assert response.status_code == 403


class TestLowCreditsAlert:
    """Tests for low credits alert generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as superadmin"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_low_credits_alert_exists(self):
        """Verify low credits alert is generated for 'Academia con Créditos Bajos'"""
        response = requests.get(
            f"{BASE_URL}/api/superadmin/alerts",
            headers=self.headers,
            params={"alert_type": "low_credits"}
        )
        
        assert response.status_code == 200
        alerts = response.json().get("alerts", [])
        
        # Should have at least one low credits alert
        assert len(alerts) >= 1, "Expected at least one low credits alert"
        
        # Find the alert for 'Academia con Créditos Bajos'
        low_credits_alert = None
        for alert in alerts:
            if "Academia con Créditos Bajos" in alert.get("institution_name", ""):
                low_credits_alert = alert
                break
        
        assert low_credits_alert is not None, "Expected low credits alert for 'Academia con Créditos Bajos'"
        
        # Verify alert details
        assert low_credits_alert["severity"] in ["critical", "warning"]
        assert "10" in low_credits_alert["description"]  # Should mention 10 credits
        assert low_credits_alert["data"]["remaining"] == 10
