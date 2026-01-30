"""
Test suite for Alerts Automation Feature - Monetizable Alert System
Tests all 13+ endpoints for the alerts automation feature with 4 pricing tiers:
- Free ($0): 10 alerts/month, email only
- Starter ($29): 100 alerts/month, email + webhook
- Professional ($79): 500 alerts/month, all channels including SMS/WhatsApp
- Enterprise ($199): Unlimited alerts, all channels + Slack/Teams
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAlertsAutomationPricing:
    """Tests for GET /api/alerts-automation/pricing - Public endpoint"""
    
    def test_get_pricing_returns_4_tiers(self):
        """GET /api/alerts-automation/pricing - Returns 4 pricing tiers"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/pricing")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "tiers" in data
        assert "currency" in data
        assert "billing_cycle" in data
        
        # Verify 4 tiers exist
        tiers = data["tiers"]
        assert "free" in tiers
        assert "starter" in tiers
        assert "professional" in tiers
        assert "enterprise" in tiers
        
        # Verify Free tier
        assert tiers["free"]["price_monthly"] == 0
        assert tiers["free"]["alerts_per_month"] == 10
        assert "email" in tiers["free"]["channels"]
        
        # Verify Starter tier
        assert tiers["starter"]["price_monthly"] == 29
        assert tiers["starter"]["alerts_per_month"] == 100
        assert "webhook" in tiers["starter"]["channels"]
        
        # Verify Professional tier
        assert tiers["professional"]["price_monthly"] == 79
        assert tiers["professional"]["alerts_per_month"] == 500
        assert "sms" in tiers["professional"]["channels"]
        assert "whatsapp" in tiers["professional"]["channels"]
        
        # Verify Enterprise tier
        assert tiers["enterprise"]["price_monthly"] == 199
        assert tiers["enterprise"]["alerts_per_month"] == -1  # Unlimited
        assert "slack" in tiers["enterprise"]["channels"]
        assert "teams" in tiers["enterprise"]["channels"]


class TestAlertsAutomationAuthenticated:
    """Tests for authenticated alerts automation endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Register and login as institution"""
        # Create unique test institution
        self.test_email = f"test_alerts_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "TestPass123!"
        
        # Register institution
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Alerts Institution",
            "user_type": "institution"
        })
        
        if register_resp.status_code not in [200, 201]:
            # Try login if already exists
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.test_email,
                "password": self.test_password
            })
            if login_resp.status_code != 200:
                pytest.skip(f"Could not register or login: {register_resp.text}")
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Store created rule IDs for cleanup
        self.created_rule_ids = []
    
    def teardown_method(self, method):
        """Cleanup created rules"""
        for rule_id in self.created_rule_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
                    headers=self.headers
                )
            except:
                pass
    
    # ==================== SUBSCRIPTION TESTS ====================
    
    def test_get_subscription_default_free(self):
        """GET /api/alerts-automation/subscription - Returns default free tier"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify subscription structure
        assert "tier" in data
        assert "tier_details" in data or "alerts_remaining" in data
        assert data["tier"] == "free"  # Default tier
    
    def test_upgrade_subscription_to_starter(self):
        """PUT /api/alerts-automation/subscription - Upgrade to Starter tier"""
        response = requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "starter"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["tier"] == "starter"
        assert data["price"] == 29
        
        # Verify subscription was updated
        verify_resp = requests.get(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["tier"] == "starter"
    
    def test_upgrade_subscription_to_professional(self):
        """PUT /api/alerts-automation/subscription - Upgrade to Professional tier"""
        response = requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "professional"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tier"] == "professional"
        assert data["price"] == 79
    
    def test_upgrade_subscription_to_enterprise(self):
        """PUT /api/alerts-automation/subscription - Upgrade to Enterprise tier"""
        response = requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "enterprise"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tier"] == "enterprise"
        assert data["price"] == 199
    
    def test_upgrade_subscription_invalid_tier(self):
        """PUT /api/alerts-automation/subscription - Invalid tier rejected"""
        response = requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "invalid_tier"}
        )
        
        assert response.status_code == 400
    
    # ==================== CHANNELS TESTS ====================
    
    def test_get_channels(self):
        """GET /api/alerts-automation/channels - Returns available channels"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/channels",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "available_channels" in data
        assert "channel_info" in data
        
        # Verify channel info has all channels
        channel_info = data["channel_info"]
        assert "email" in channel_info
        assert "sms" in channel_info
        assert "whatsapp" in channel_info
        assert "webhook" in channel_info
        assert "slack" in channel_info
        assert "teams" in channel_info
    
    # ==================== RULES CRUD TESTS ====================
    
    def test_create_alert_rule(self):
        """POST /api/alerts-automation/rules - Create alert rule"""
        rule_data = {
            "name": f"TEST_Stale Lead Alert {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["email"],
            "recipient_type": "assigned_user",
            "is_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "message" in data
        assert "rule" in data
        
        # Store for cleanup
        self.created_rule_ids.append(data["id"])
        
        # Verify rule data
        rule = data["rule"]
        assert rule["name"] == rule_data["name"]
        assert rule["alert_type"] == "stale_lead"
        assert rule["trigger_days"] == 7
    
    def test_get_alert_rules(self):
        """GET /api/alerts-automation/rules - List alert rules"""
        # First create a rule
        rule_data = {
            "name": f"TEST_List Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 5,
            "channels": ["email"],
            "is_enabled": True
        }
        
        create_resp = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        assert create_resp.status_code == 200
        rule_id = create_resp.json()["id"]
        self.created_rule_ids.append(rule_id)
        
        # Get rules
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "rules" in data
        assert isinstance(data["rules"], list)
        
        # Verify created rule is in list
        rule_ids = [r["id"] for r in data["rules"]]
        assert rule_id in rule_ids
    
    def test_update_alert_rule_enable_disable(self):
        """PUT /api/alerts-automation/rules/{id} - Enable/disable rule"""
        # Create rule
        rule_data = {
            "name": f"TEST_Toggle Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["email"],
            "is_enabled": True
        }
        
        create_resp = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        assert create_resp.status_code == 200
        rule_id = create_resp.json()["id"]
        self.created_rule_ids.append(rule_id)
        
        # Disable rule
        update_resp = requests.put(
            f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
            headers=self.headers,
            json={"is_enabled": False}
        )
        
        assert update_resp.status_code == 200
        
        # Verify rule is disabled
        get_resp = requests.get(
            f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
            headers=self.headers
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["is_enabled"] == False
    
    def test_delete_alert_rule(self):
        """DELETE /api/alerts-automation/rules/{id} - Delete rule"""
        # Create rule
        rule_data = {
            "name": f"TEST_Delete Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["email"],
            "is_enabled": True
        }
        
        create_resp = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        assert create_resp.status_code == 200
        rule_id = create_resp.json()["id"]
        
        # Delete rule
        delete_resp = requests.delete(
            f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
            headers=self.headers
        )
        
        assert delete_resp.status_code == 200
        
        # Verify rule is deleted
        get_resp = requests.get(
            f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
            headers=self.headers
        )
        assert get_resp.status_code == 404
    
    def test_delete_nonexistent_rule(self):
        """DELETE /api/alerts-automation/rules/{id} - 404 for nonexistent rule"""
        response = requests.delete(
            f"{BASE_URL}/api/alerts-automation/rules/nonexistent_rule_id",
            headers=self.headers
        )
        
        assert response.status_code == 404
    
    # ==================== MANUAL TRIGGER TESTS ====================
    
    def test_manual_trigger_rule(self):
        """POST /api/alerts-automation/rules/{id}/trigger - Manual trigger"""
        # Create rule
        rule_data = {
            "name": f"TEST_Trigger Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["email"],
            "is_enabled": True
        }
        
        create_resp = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        assert create_resp.status_code == 200
        rule_id = create_resp.json()["id"]
        self.created_rule_ids.append(rule_id)
        
        # Trigger rule
        trigger_resp = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules/{rule_id}/trigger",
            headers=self.headers
        )
        
        assert trigger_resp.status_code == 200
        data = trigger_resp.json()
        
        assert "message" in data
        assert "alert_id" in data
        assert "channels" in data
    
    def test_manual_trigger_nonexistent_rule(self):
        """POST /api/alerts-automation/rules/{id}/trigger - 404 for nonexistent"""
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules/nonexistent_rule_id/trigger",
            headers=self.headers
        )
        
        assert response.status_code == 404
    
    # ==================== LOGS TESTS ====================
    
    def test_get_alert_logs(self):
        """GET /api/alerts-automation/logs - Get alert history"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/logs",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert isinstance(data["logs"], list)
    
    def test_get_alert_logs_with_limit(self):
        """GET /api/alerts-automation/logs?limit=5 - Get limited logs"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/logs",
            headers=self.headers,
            params={"limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert len(data["logs"]) <= 5
    
    # ==================== ANALYTICS TESTS ====================
    
    def test_get_analytics(self):
        """GET /api/alerts-automation/analytics - Usage analytics"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/analytics",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "subscription" in data
        assert "stats" in data
        
        # Verify subscription info
        sub = data["subscription"]
        assert "tier" in sub
        assert "alerts_used" in sub
        assert "alerts_limit" in sub
        
        # Verify stats
        stats = data["stats"]
        assert "total_alerts_sent" in stats
        assert "active_rules" in stats
    
    # ==================== STALE LEADS CHECK ====================
    
    def test_check_stale_leads(self):
        """GET /api/alerts-automation/check-stale-leads - Check stale leads"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/check-stale-leads",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "rules_active" in data or "message" in data
        assert "stale_leads" in data or "stale_leads_count" in data
    
    # ==================== TEMPLATES TESTS ====================
    
    def test_get_templates(self):
        """GET /api/alerts-automation/templates - Get message templates"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/templates",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        
        # Verify template types exist
        assert "stale_lead" in templates
        assert "student_inactive" in templates
        assert "payment_due" in templates
        
        # Verify template structure
        stale_lead = templates["stale_lead"]
        assert "email_subject" in stale_lead
        assert "email_body" in stale_lead
        assert "sms_message" in stale_lead
        assert "variables" in stale_lead


class TestAlertsAutomationTierRestrictions:
    """Tests for tier-based feature restrictions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Register and login as institution with free tier"""
        self.test_email = f"test_tier_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "TestPass123!"
        
        # Register institution
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Tier Institution",
            "user_type": "institution"
        })
        
        if register_resp.status_code not in [200, 201]:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.test_email,
                "password": self.test_password
            })
            if login_resp.status_code != 200:
                pytest.skip(f"Could not register or login")
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        self.created_rule_ids = []
    
    def teardown_method(self, method):
        """Cleanup"""
        for rule_id in self.created_rule_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/alerts-automation/rules/{rule_id}",
                    headers=self.headers
                )
            except:
                pass
    
    def test_free_tier_cannot_use_sms_channel(self):
        """Free tier cannot create rule with SMS channel"""
        # Ensure on free tier
        requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "free"}
        )
        
        rule_data = {
            "name": f"TEST_SMS Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["sms"],  # SMS not available in free tier
            "is_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        
        assert response.status_code == 403
        assert "upgrade" in response.json().get("detail", "").lower() or "not available" in response.json().get("detail", "").lower()
    
    def test_free_tier_cannot_use_student_inactive_type(self):
        """Free tier cannot create student_inactive alert type"""
        # Ensure on free tier
        requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "free"}
        )
        
        rule_data = {
            "name": f"TEST_Student Inactive {uuid.uuid4().hex[:6]}",
            "alert_type": "student_inactive",  # Not available in free tier
            "trigger_days": 7,
            "channels": ["email"],
            "is_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        
        assert response.status_code == 403
    
    def test_professional_tier_can_use_sms(self):
        """Professional tier can create rule with SMS channel"""
        # Upgrade to professional
        upgrade_resp = requests.put(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers,
            json={"tier": "professional"}
        )
        assert upgrade_resp.status_code == 200
        
        rule_data = {
            "name": f"TEST_SMS Pro Rule {uuid.uuid4().hex[:6]}",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["sms"],
            "is_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        
        assert response.status_code == 200
        self.created_rule_ids.append(response.json()["id"])


class TestAlertsAutomationUnauthorized:
    """Tests for unauthorized access"""
    
    def test_subscription_requires_auth(self):
        """GET /api/alerts-automation/subscription - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/subscription")
        
        assert response.status_code == 401
    
    def test_rules_requires_auth(self):
        """GET /api/alerts-automation/rules - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/rules")
        
        assert response.status_code == 401
    
    def test_channels_requires_auth(self):
        """GET /api/alerts-automation/channels - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/channels")
        
        assert response.status_code == 401
    
    def test_logs_requires_auth(self):
        """GET /api/alerts-automation/logs - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/logs")
        
        assert response.status_code == 401
    
    def test_analytics_requires_auth(self):
        """GET /api/alerts-automation/analytics - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts-automation/analytics")
        
        assert response.status_code == 401


class TestAlertsAutomationStudentAccess:
    """Tests for student access restrictions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Register and login as student"""
        self.test_email = f"test_student_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "TestPass123!"
        
        # Register student
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Student",
            "user_type": "student"
        })
        
        if register_resp.status_code not in [200, 201]:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.test_email,
                "password": self.test_password
            })
            if login_resp.status_code != 200:
                pytest.skip(f"Could not register or login as student")
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_student_cannot_access_subscription(self):
        """Students cannot access subscription endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/subscription",
            headers=self.headers
        )
        
        assert response.status_code == 403
    
    def test_student_cannot_create_rules(self):
        """Students cannot create alert rules"""
        rule_data = {
            "name": "Student Rule",
            "alert_type": "stale_lead",
            "trigger_days": 7,
            "channels": ["email"],
            "is_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/alerts-automation/rules",
            headers=self.headers,
            json=rule_data
        )
        
        assert response.status_code == 403
    
    def test_student_cannot_access_analytics(self):
        """Students cannot access analytics"""
        response = requests.get(
            f"{BASE_URL}/api/alerts-automation/analytics",
            headers=self.headers
        )
        
        assert response.status_code == 403
