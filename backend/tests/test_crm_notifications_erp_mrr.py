"""
Test CRM Notification Settings and ERP MRR Calculations
Tests for:
- CRM Notification Settings CRUD (POST, GET, PATCH, DELETE)
- Notification triggers on lead stage change
- ERP MRR metrics with real calculations
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


def get_auth_token():
    """Helper to get authentication token"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    login_response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "demo_academy@test.com",
        "password": "Demo123!"
    })
    
    if login_response.status_code == 200:
        return login_response.json().get("access_token")
    return None


class TestCRMNotificationSettings:
    """Test CRM Notification Settings CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.user_id = login_response.json().get("user", {}).get("id")
        else:
            pytest.skip("Authentication failed - skipping tests")
        
        yield
        
        # Cleanup: Delete test notification settings
        try:
            settings_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings")
            if settings_response.status_code == 200:
                settings = settings_response.json().get("settings", [])
                for setting in settings:
                    if setting.get("name", "").startswith("TEST_"):
                        self.session.delete(f"{BASE_URL}/api/crm-edu/notification-settings/{setting['id']}")
        except:
            pass
    
    def test_create_notification_setting(self):
        """Test POST /api/crm-edu/notification-settings creates rule"""
        payload = {
            "name": "TEST_Hot_Lead_Alert",
            "trigger_stage": "qualified",
            "notify_on_enter": True,
            "notify_on_exit": False,
            "notification_channels": ["in_app", "email"],
            "recipients": ["owner"],
            "include_lead_details": True,
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain id"
        assert data.get("message") == "Notification setting created"
        
        # Verify by GET
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{data['id']}")
        assert get_response.status_code == 200
        setting = get_response.json()
        assert setting["name"] == "TEST_Hot_Lead_Alert"
        assert setting["trigger_stage"] == "qualified"
        assert setting["notify_on_enter"] == True
        assert "in_app" in setting["notification_channels"]
        assert "email" in setting["notification_channels"]
    
    def test_list_notification_settings(self):
        """Test GET /api/crm-edu/notification-settings lists rules"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "settings" in data, "Response should contain settings array"
        assert "stages" in data, "Response should contain stages array"
        assert isinstance(data["settings"], list)
        assert isinstance(data["stages"], list)
        assert len(data["stages"]) > 0, "Should have pipeline stages"
    
    def test_update_notification_setting_toggle_active(self):
        """Test PATCH /api/crm-edu/notification-settings/{id} toggles active/inactive"""
        # First create a setting
        create_payload = {
            "name": "TEST_Toggle_Rule",
            "trigger_stage": "demo_scheduled",
            "notify_on_enter": True,
            "notification_channels": ["in_app"],
            "recipients": ["owner"],
            "is_active": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=create_payload)
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Toggle to inactive
        update_response = self.session.patch(
            f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}",
            json={"is_active": False}
        )
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        assert update_response.json().get("message") == "Setting updated"
        
        # Verify toggle worked
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] == False
        
        # Toggle back to active
        update_response2 = self.session.patch(
            f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}",
            json={"is_active": True}
        )
        assert update_response2.status_code == 200
        
        # Verify
        get_response2 = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response2.json()["is_active"] == True
    
    def test_delete_notification_setting(self):
        """Test DELETE /api/crm-edu/notification-settings/{id} deletes rule"""
        # First create a setting
        create_payload = {
            "name": "TEST_Delete_Rule",
            "trigger_stage": "trial",
            "notify_on_enter": True,
            "notification_channels": ["in_app"],
            "recipients": ["owner"],
            "is_active": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=create_payload)
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Delete the setting
        delete_response = self.session.delete(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        assert delete_response.json().get("message") == "Setting deleted"
        
        # Verify deletion - should return 404
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response.status_code == 404, "Deleted setting should return 404"
    
    def test_quick_presets_hot_lead_alert(self):
        """Test creating Hot Lead Alert preset"""
        payload = {
            "name": "TEST_Hot_Lead_Alert_Preset",
            "trigger_stage": "qualified",
            "notify_on_enter": True,
            "notify_on_exit": False,
            "notification_channels": ["in_app"],
            "recipients": ["owner"],
            "include_lead_details": True,
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=payload)
        assert response.status_code == 200
        
        # Verify
        setting_id = response.json()["id"]
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response.status_code == 200
        setting = get_response.json()
        assert setting["trigger_stage"] == "qualified"
    
    def test_quick_presets_demo_booked(self):
        """Test creating Demo Booked preset"""
        payload = {
            "name": "TEST_Demo_Booked_Preset",
            "trigger_stage": "demo_scheduled",
            "notify_on_enter": True,
            "notify_on_exit": False,
            "notification_channels": ["in_app"],
            "recipients": ["owner"],
            "include_lead_details": True,
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=payload)
        assert response.status_code == 200
        
        setting_id = response.json()["id"]
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response.status_code == 200
        assert get_response.json()["trigger_stage"] == "demo_scheduled"
    
    def test_quick_presets_new_customer(self):
        """Test creating New Customer preset"""
        payload = {
            "name": "TEST_New_Customer_Preset",
            "trigger_stage": "active",
            "notify_on_enter": True,
            "notify_on_exit": False,
            "notification_channels": ["in_app", "email"],
            "recipients": ["owner", "team"],
            "include_lead_details": True,
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=payload)
        assert response.status_code == 200
        
        setting_id = response.json()["id"]
        get_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings/{setting_id}")
        assert get_response.status_code == 200
        setting = get_response.json()
        assert setting["trigger_stage"] == "active"
        assert "team" in setting["recipients"]


class TestNotificationTriggerOnStageChange:
    """Test that notifications are created when lead stage changes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.user_id = login_response.json().get("user", {}).get("id")
        else:
            pytest.skip("Authentication failed - skipping tests")
        
        yield
        
        # Cleanup
        try:
            # Delete test notification settings
            settings_response = self.session.get(f"{BASE_URL}/api/crm-edu/notification-settings")
            if settings_response.status_code == 200:
                settings = settings_response.json().get("settings", [])
                for setting in settings:
                    if setting.get("name", "").startswith("TEST_"):
                        self.session.delete(f"{BASE_URL}/api/crm-edu/notification-settings/{setting['id']}")
        except:
            pass
    
    def test_notification_created_on_stage_change(self):
        """Test that notification is created when lead moves to a stage with notification rule"""
        # Step 1: Create a notification rule for 'qualified' stage
        rule_payload = {
            "name": "TEST_Qualified_Notification",
            "trigger_stage": "qualified",
            "notify_on_enter": True,
            "notify_on_exit": False,
            "notification_channels": ["in_app"],
            "recipients": ["owner"],
            "include_lead_details": True,
            "is_active": True
        }
        
        rule_response = self.session.post(f"{BASE_URL}/api/crm-edu/notification-settings", json=rule_payload)
        assert rule_response.status_code == 200, f"Failed to create notification rule: {rule_response.text}"
        
        # Step 2: Create a test lead in 'lead' stage
        lead_payload = {
            "institution_name": f"TEST_Notification_Academy_{uuid.uuid4().hex[:8]}",
            "contact_name": "Test Contact",
            "contact_email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "contact_phone": "+1234567890",
            "contact_role": "Director",
            "estimated_students": 100,
            "exam_types_interested": ["ielts"],
            "country": "USA",
            "source": "website"
        }
        
        lead_response = self.session.post(f"{BASE_URL}/api/crm-edu/leads", json=lead_payload)
        assert lead_response.status_code == 200, f"Failed to create lead: {lead_response.text}"
        lead_id = lead_response.json()["id"]
        
        # Step 3: Get initial notification count
        initial_notifications = self.session.get(f"{BASE_URL}/api/crm-edu/notifications")
        initial_count = initial_notifications.json().get("unread_count", 0) if initial_notifications.status_code == 200 else 0
        
        # Step 4: Update lead to 'qualified' stage (should trigger notification)
        update_response = self.session.patch(
            f"{BASE_URL}/api/crm-edu/leads/{lead_id}",
            json={"stage": "qualified"}
        )
        assert update_response.status_code == 200, f"Failed to update lead stage: {update_response.text}"
        
        # Step 5: Check that notification was created
        notifications_response = self.session.get(f"{BASE_URL}/api/crm-edu/notifications")
        assert notifications_response.status_code == 200, f"Failed to get notifications: {notifications_response.text}"
        
        notifications_data = notifications_response.json()
        notifications = notifications_data.get("notifications", [])
        
        # Find the notification for our lead
        lead_notification = None
        for notif in notifications:
            if notif.get("lead_id") == lead_id and notif.get("type") == "stage_change":
                lead_notification = notif
                break
        
        assert lead_notification is not None, "Notification should be created for stage change"
        assert "qualified" in lead_notification.get("new_stage", "").lower() or "qualified" in lead_notification.get("title", "").lower()


class TestERPMRRMetrics:
    """Test ERP MRR metrics with real calculations from subscription data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Authentication failed - skipping tests")
    
    def test_mrr_metrics_endpoint(self):
        """Test GET /api/erp/subscriptions/metrics/mrr returns MRR metrics"""
        response = self.session.get(f"{BASE_URL}/api/erp/subscriptions/metrics/mrr")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "current_mrr" in data, "Response should contain current_mrr"
        assert "current_arr" in data, "Response should contain current_arr"
        assert "active_subscriptions" in data, "Response should contain active_subscriptions"
        assert "avg_mrr_per_subscription" in data, "Response should contain avg_mrr_per_subscription"
        assert "mrr_by_plan" in data, "Response should contain mrr_by_plan"
        
        # Verify data types
        assert isinstance(data["current_mrr"], (int, float))
        assert isinstance(data["current_arr"], (int, float))
        assert isinstance(data["active_subscriptions"], int)
        
        # Verify ARR = MRR * 12
        if data["current_mrr"] > 0:
            expected_arr = data["current_mrr"] * 12
            assert abs(data["current_arr"] - expected_arr) < 1, f"ARR should be MRR * 12. Got ARR={data['current_arr']}, MRR={data['current_mrr']}"
    
    def test_mrr_by_plan_breakdown(self):
        """Test MRR by Plan breakdown is accurate"""
        response = self.session.get(f"{BASE_URL}/api/erp/subscriptions/metrics/mrr")
        
        assert response.status_code == 200
        data = response.json()
        
        mrr_by_plan = data.get("mrr_by_plan", {})
        
        # If there are plans, verify structure
        if mrr_by_plan:
            for plan_name, plan_data in mrr_by_plan.items():
                assert "count" in plan_data, f"Plan {plan_name} should have count"
                assert "mrr" in plan_data, f"Plan {plan_name} should have mrr"
                assert isinstance(plan_data["count"], int)
                assert isinstance(plan_data["mrr"], (int, float))
            
            # Verify total MRR equals sum of plan MRRs
            total_plan_mrr = sum(p["mrr"] for p in mrr_by_plan.values())
            assert abs(data["current_mrr"] - total_plan_mrr) < 1, \
                f"Total MRR ({data['current_mrr']}) should equal sum of plan MRRs ({total_plan_mrr})"
    
    def test_avg_mrr_per_customer(self):
        """Test Avg MRR/Customer calculation"""
        response = self.session.get(f"{BASE_URL}/api/erp/subscriptions/metrics/mrr")
        
        assert response.status_code == 200
        data = response.json()
        
        current_mrr = data.get("current_mrr", 0)
        active_subs = data.get("active_subscriptions", 0)
        avg_mrr = data.get("avg_mrr_per_subscription", 0)
        
        # Verify calculation
        if active_subs > 0:
            expected_avg = current_mrr / active_subs
            assert abs(avg_mrr - expected_avg) < 1, \
                f"Avg MRR ({avg_mrr}) should equal MRR/subs ({expected_avg})"
        else:
            assert avg_mrr == 0, "Avg MRR should be 0 when no subscriptions"


class TestERPDashboardMetrics:
    """Test ERP Dashboard shows correct metrics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Authentication failed - skipping tests")
    
    def test_invoice_stats_summary(self):
        """Test invoice stats summary endpoint"""
        response = self.session.get(f"{BASE_URL}/api/erp/invoices/stats/summary?period=month")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "totals" in data or "by_status" in data, "Response should contain totals or by_status"
    
    def test_subscriptions_list(self):
        """Test subscriptions list endpoint"""
        response = self.session.get(f"{BASE_URL}/api/erp/subscriptions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "subscriptions" in data, "Response should contain subscriptions"
        assert isinstance(data["subscriptions"], list)
    
    def test_chart_of_accounts(self):
        """Test chart of accounts endpoint"""
        response = self.session.get(f"{BASE_URL}/api/erp/accounting/chart-of-accounts")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
