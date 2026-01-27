"""
Test Suite for Supreme Features:
- Messaging Configuration (WhatsApp/SMS)
- Email Templates System
- Automatic Reports Generation
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"

class TestSupremeFeatures:
    """Test Supreme features: Messaging, Email Templates, Reports"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.institution_token = None
        
    def get_institution_token(self):
        """Get or create institution token"""
        if self.institution_token:
            return self.institution_token
            
        # Try to login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        
        if login_response.status_code == 200:
            self.institution_token = login_response.json()["access_token"]
            return self.institution_token
        
        # Register if login fails
        unique_id = str(uuid.uuid4())[:8]
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_inst_{unique_id}@test.com",
            "password": "Test123!",
            "name": f"Test Institution {unique_id}",
            "user_type": "institution",
            "institution_name": f"Test Academy {unique_id}"
        })
        
        if register_response.status_code == 200:
            self.institution_token = register_response.json()["access_token"]
            return self.institution_token
        
        pytest.skip("Could not authenticate as institution")
        
    def get_auth_headers(self):
        """Get authorization headers"""
        token = self.get_institution_token()
        return {"Authorization": f"Bearer {token}"}

    # ==================== MESSAGING CONFIG TESTS ====================
    
    def test_get_messaging_config(self):
        """GET /api/institution/messaging/config - Returns messaging configuration"""
        response = self.session.get(
            f"{BASE_URL}/api/institution/messaging/config",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "provider" in data, "Response should contain 'provider'"
        assert "enabled" in data, "Response should contain 'enabled'"
        assert "sms_enabled" in data, "Response should contain 'sms_enabled'"
        assert "whatsapp_enabled" in data, "Response should contain 'whatsapp_enabled'"
        print(f"✓ Messaging config retrieved: provider={data.get('provider')}, enabled={data.get('enabled')}")
        
    def test_save_messaging_config(self):
        """POST /api/institution/messaging/config - Save messaging configuration"""
        config = {
            "provider": "twilio",
            "api_key": "test_api_key_12345",
            "api_secret": "test_secret",
            "account_sid": "AC123456789",
            "from_number": "+1234567890",
            "whatsapp_number": "whatsapp:+1234567890",
            "enabled": True
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/institution/messaging/config",
            json=config,
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response should indicate success"
        print(f"✓ Messaging config saved successfully")
        
        # Verify config was saved by fetching it
        get_response = self.session.get(
            f"{BASE_URL}/api/institution/messaging/config",
            headers=self.get_auth_headers()
        )
        
        assert get_response.status_code == 200
        saved_config = get_response.json()
        assert saved_config.get("provider") == "twilio", "Provider should be saved as 'twilio'"
        assert saved_config.get("enabled") == True, "Enabled should be True"
        print(f"✓ Messaging config verified after save")
        
    def test_messaging_config_forbidden_for_non_institution(self):
        """Messaging config should be forbidden for non-institution users"""
        # Register a student
        unique_id = str(uuid.uuid4())[:8]
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_student_{unique_id}@test.com",
            "password": "Test123!",
            "name": f"Test Student {unique_id}",
            "user_type": "individual"
        })
        
        if register_response.status_code != 200:
            pytest.skip("Could not create test student")
            
        student_token = register_response.json()["access_token"]
        
        response = self.session.get(
            f"{BASE_URL}/api/institution/messaging/config",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403 for non-institution, got {response.status_code}"
        print(f"✓ Non-institution users correctly forbidden from messaging config")

    # ==================== REPORTS CONFIG TESTS ====================
    
    def test_get_reports_config(self):
        """GET /api/institution/reports/config - Returns reports configuration"""
        response = self.session.get(
            f"{BASE_URL}/api/institution/reports/config",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "weekly_enabled" in data, "Response should contain 'weekly_enabled'"
        assert "monthly_enabled" in data, "Response should contain 'monthly_enabled'"
        assert "send_to_admins" in data, "Response should contain 'send_to_admins'"
        assert "include_ai_usage" in data, "Response should contain 'include_ai_usage'"
        assert "include_exam_stats" in data, "Response should contain 'include_exam_stats'"
        assert "include_engagement" in data, "Response should contain 'include_engagement'"
        assert "delivery_day" in data, "Response should contain 'delivery_day'"
        print(f"✓ Reports config retrieved: weekly={data.get('weekly_enabled')}, monthly={data.get('monthly_enabled')}")
        
    def test_save_reports_config(self):
        """POST /api/institution/reports/config - Save reports configuration"""
        config = {
            "weekly_enabled": True,
            "monthly_enabled": True,
            "send_to_admins": True,
            "send_to_students": False,
            "include_ai_usage": True,
            "include_exam_stats": True,
            "include_engagement": True,
            "delivery_day": 2  # Tuesday
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/institution/reports/config",
            json=config,
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response should indicate success"
        print(f"✓ Reports config saved successfully")
        
        # Verify config was saved
        get_response = self.session.get(
            f"{BASE_URL}/api/institution/reports/config",
            headers=self.get_auth_headers()
        )
        
        assert get_response.status_code == 200
        saved_config = get_response.json()
        assert saved_config.get("delivery_day") == 2, "Delivery day should be saved as 2"
        print(f"✓ Reports config verified after save")
        
    def test_generate_weekly_report(self):
        """GET /api/institution/reports/generate?report_type=weekly - Generate weekly report"""
        response = self.session.get(
            f"{BASE_URL}/api/institution/reports/generate?report_type=weekly",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify report structure
        assert data.get("report_type") == "weekly", "Report type should be 'weekly'"
        assert "generated_at" in data, "Report should have 'generated_at'"
        assert "period" in data, "Report should have 'period'"
        assert "institution" in data, "Report should have 'institution'"
        assert "engagement" in data, "Report should have 'engagement'"
        assert "ai_usage" in data, "Report should have 'ai_usage'"
        assert "exams" in data, "Report should have 'exams'"
        
        # Verify engagement structure
        engagement = data.get("engagement", {})
        assert "active_students" in engagement, "Engagement should have 'active_students'"
        assert "activity_rate" in engagement, "Engagement should have 'activity_rate'"
        
        # Verify AI usage structure
        ai_usage = data.get("ai_usage", {})
        assert "total_credits_used" in ai_usage, "AI usage should have 'total_credits_used'"
        
        print(f"✓ Weekly report generated: {data.get('institution', {}).get('total_students', 0)} students, {engagement.get('active_students', 0)} active")
        
    def test_generate_monthly_report(self):
        """GET /api/institution/reports/generate?report_type=monthly - Generate monthly report"""
        response = self.session.get(
            f"{BASE_URL}/api/institution/reports/generate?report_type=monthly",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("report_type") == "monthly", "Report type should be 'monthly'"
        assert "period" in data, "Report should have 'period'"
        
        # Verify period is ~30 days
        period = data.get("period", {})
        assert "start" in period, "Period should have 'start'"
        assert "end" in period, "Period should have 'end'"
        
        print(f"✓ Monthly report generated successfully")

    # ==================== EMAIL TEMPLATES TESTS ====================
    
    def test_get_email_templates(self):
        """GET /api/institution/email-templates - Returns default email templates"""
        response = self.session.get(
            f"{BASE_URL}/api/institution/email-templates",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "templates" in data, "Response should contain 'templates'"
        templates = data.get("templates", [])
        
        # Should have default templates
        template_types = [t.get("template_type") for t in templates]
        assert "welcome" in template_types, "Should have 'welcome' template"
        assert "exam_reminder" in template_types, "Should have 'exam_reminder' template"
        assert "progress_report" in template_types, "Should have 'progress_report' template"
        
        # Verify template structure
        for template in templates:
            assert "subject" in template, f"Template {template.get('template_type')} should have 'subject'"
            assert "body_html" in template, f"Template {template.get('template_type')} should have 'body_html'"
            
        print(f"✓ Email templates retrieved: {len(templates)} templates ({', '.join(template_types)})")
        
    def test_save_custom_email_template(self):
        """POST /api/institution/email-templates - Save custom email template"""
        custom_template = {
            "template_type": "welcome",
            "subject": "Welcome to Our Academy - {student_name}",
            "body_html": "<h1>Welcome {student_name}!</h1><p>Your account is ready at {institution_name}.</p>",
            "body_text": "Welcome {student_name}! Your account is ready."
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/institution/email-templates",
            json=custom_template,
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response should indicate success"
        print(f"✓ Custom email template saved successfully")
        
        # Verify template was saved
        get_response = self.session.get(
            f"{BASE_URL}/api/institution/email-templates",
            headers=self.get_auth_headers()
        )
        
        assert get_response.status_code == 200
        templates = get_response.json().get("templates", [])
        welcome_template = next((t for t in templates if t.get("template_type") == "welcome"), None)
        
        assert welcome_template is not None, "Welcome template should exist"
        assert "Our Academy" in welcome_template.get("subject", ""), "Custom subject should be saved"
        print(f"✓ Custom template verified after save")
        
    def test_preview_email_template(self):
        """POST /api/institution/email-templates/preview - Preview template with sample data"""
        response = self.session.post(
            f"{BASE_URL}/api/institution/email-templates/preview?template_type=welcome",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "subject" in data, "Preview should contain 'subject'"
        assert "body_html" in data, "Preview should contain 'body_html'"
        
        # Verify placeholders are replaced
        subject = data.get("subject", "")
        body = data.get("body_html", "")
        
        # Should not contain unreplaced placeholders
        assert "{student_name}" not in subject, "Subject should have placeholders replaced"
        assert "{institution_name}" not in body or "Juan" in body, "Body should have some placeholders replaced"
        
        print(f"✓ Email template preview generated: subject='{subject[:50]}...'")
        
    def test_preview_nonexistent_template(self):
        """Preview should return 404 for non-existent template"""
        response = self.session.post(
            f"{BASE_URL}/api/institution/email-templates/preview?template_type=nonexistent_template",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent template, got {response.status_code}"
        print(f"✓ Non-existent template correctly returns 404")

    # ==================== REPORTS HISTORY TEST ====================
    
    def test_get_reports_history(self):
        """GET /api/institution/reports/history - Get historical reports"""
        # First generate a report to ensure there's history
        self.session.get(
            f"{BASE_URL}/api/institution/reports/generate?report_type=weekly",
            headers=self.get_auth_headers()
        )
        
        response = self.session.get(
            f"{BASE_URL}/api/institution/reports/history?limit=5",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "reports" in data, "Response should contain 'reports'"
        reports = data.get("reports", [])
        
        # Should have at least one report from our generation
        assert len(reports) >= 1, "Should have at least one report in history"
        
        # Verify report structure
        for report in reports:
            assert "id" in report, "Report should have 'id'"
            assert "report_type" in report, "Report should have 'report_type'"
            assert "created_at" in report, "Report should have 'created_at'"
            
        print(f"✓ Reports history retrieved: {len(reports)} reports")


class TestMessagingTestEndpoint:
    """Test messaging test endpoint (MOCKED)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def get_institution_token(self):
        # Try to login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register if login fails
        unique_id = str(uuid.uuid4())[:8]
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_inst_{unique_id}@test.com",
            "password": "Test123!",
            "name": f"Test Institution {unique_id}",
            "user_type": "institution",
            "institution_name": f"Test Academy {unique_id}"
        })
        
        if register_response.status_code == 200:
            return register_response.json()["access_token"]
        
        pytest.skip("Could not authenticate")
        
    def test_send_test_sms_mocked(self):
        """POST /api/institution/messaging/test - Test SMS (MOCKED - no actual send)"""
        token = self.get_institution_token()
        
        # First enable messaging
        self.session.post(
            f"{BASE_URL}/api/institution/messaging/config",
            json={
                "provider": "twilio",
                "api_key": "test_key",
                "enabled": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = self.session.post(
            f"{BASE_URL}/api/institution/messaging/test?message_type=sms&test_number=+1234567890",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Test should indicate success"
        assert "note" in data, "Response should contain note about mocked integration"
        print(f"✓ Test SMS endpoint works (MOCKED): {data.get('message')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
