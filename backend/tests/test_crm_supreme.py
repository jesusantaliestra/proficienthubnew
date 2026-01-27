"""
CRM Supreme Feature Tests
Tests for email templates, automation rules, and tasks endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://whitlabel-app.preview.emergentagent.com').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestCRMSupremeAuth:
    """Test authentication for CRM Supreme features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestEmailTemplates(TestCRMSupremeAuth):
    """Email Templates CRUD tests"""
    
    def test_get_email_templates(self, auth_headers):
        """GET /api/crm/email-templates - Returns templates list"""
        response = requests.get(f"{BASE_URL}/api/crm/email-templates", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "templates" in data, "Response should contain 'templates' key"
        assert isinstance(data["templates"], list), "Templates should be a list"
        print(f"✓ GET /api/crm/email-templates - Found {len(data['templates'])} templates")
    
    def test_email_templates_have_required_fields(self, auth_headers):
        """Verify email templates have required fields"""
        response = requests.get(f"{BASE_URL}/api/crm/email-templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["templates"]:
            template = data["templates"][0]
            required_fields = ["id", "name", "subject", "body_html", "category"]
            for field in required_fields:
                assert field in template, f"Template missing required field: {field}"
            print(f"✓ Email templates have all required fields: {required_fields}")
    
    def test_create_email_template(self, auth_headers):
        """POST /api/crm/email-templates - Creates new template"""
        new_template = {
            "name": "TEST_CRM_Template",
            "subject": "Test Subject {{contact_name}}",
            "body_html": "<h1>Hello {{contact_name}}</h1><p>This is a test template.</p>",
            "category": "follow_up",
            "variables": ["contact_name"]
        }
        response = requests.post(f"{BASE_URL}/api/crm/email-templates", 
                                json=new_template, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create template: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain template id"
        print(f"✓ POST /api/crm/email-templates - Created template with id: {data['id']}")
        return data["id"]


class TestAutomationRules(TestCRMSupremeAuth):
    """Automation Rules CRUD tests"""
    
    def test_get_automation_rules(self, auth_headers):
        """GET /api/crm/automation-rules - Returns rules list"""
        response = requests.get(f"{BASE_URL}/api/crm/automation-rules", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "rules" in data, "Response should contain 'rules' key"
        assert isinstance(data["rules"], list), "Rules should be a list"
        print(f"✓ GET /api/crm/automation-rules - Found {len(data['rules'])} rules")
    
    def test_automation_rules_have_required_fields(self, auth_headers):
        """Verify automation rules have required fields"""
        response = requests.get(f"{BASE_URL}/api/crm/automation-rules", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["rules"]:
            rule = data["rules"][0]
            required_fields = ["id", "name", "trigger_type", "actions", "is_active"]
            for field in required_fields:
                assert field in rule, f"Rule missing required field: {field}"
            print(f"✓ Automation rules have all required fields: {required_fields}")
    
    def test_create_automation_rule(self, auth_headers):
        """POST /api/crm/automation-rules - Creates new rule"""
        new_rule = {
            "name": "TEST_CRM_Automation",
            "trigger_type": "lead_created",
            "trigger_config": {},
            "actions": [{"type": "send_email", "template": "welcome"}],
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/crm/automation-rules", 
                                json=new_rule, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create rule: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain rule id"
        print(f"✓ POST /api/crm/automation-rules - Created rule with id: {data['id']}")
        return data["id"]


class TestCRMTasks(TestCRMSupremeAuth):
    """CRM Tasks CRUD tests"""
    
    def test_get_tasks(self, auth_headers):
        """GET /api/crm/tasks - Returns tasks list"""
        response = requests.get(f"{BASE_URL}/api/crm/tasks", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "tasks" in data, "Response should contain 'tasks' key"
        assert isinstance(data["tasks"], list), "Tasks should be a list"
        print(f"✓ GET /api/crm/tasks - Found {len(data['tasks'])} tasks")
    
    def test_create_task(self, auth_headers):
        """POST /api/crm/tasks - Creates new task"""
        new_task = {
            "title": "TEST_CRM_Task",
            "description": "Test task description",
            "due_date": "2026-02-01",
            "priority": "high",
            "assigned_to": "",
            "lead_id": ""
        }
        response = requests.post(f"{BASE_URL}/api/crm/tasks", 
                                json=new_task, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain task id"
        print(f"✓ POST /api/crm/tasks - Created task with id: {data['id']}")
        return data["id"]


class TestCRMSupremeIntegration(TestCRMSupremeAuth):
    """Integration tests for CRM Supreme features"""
    
    def test_full_crm_workflow(self, auth_headers):
        """Test complete CRM workflow: templates -> rules -> tasks"""
        # 1. Get templates
        templates_res = requests.get(f"{BASE_URL}/api/crm/email-templates", headers=auth_headers)
        assert templates_res.status_code == 200
        templates = templates_res.json()["templates"]
        print(f"✓ Step 1: Retrieved {len(templates)} email templates")
        
        # 2. Get automation rules
        rules_res = requests.get(f"{BASE_URL}/api/crm/automation-rules", headers=auth_headers)
        assert rules_res.status_code == 200
        rules = rules_res.json()["rules"]
        print(f"✓ Step 2: Retrieved {len(rules)} automation rules")
        
        # 3. Get tasks
        tasks_res = requests.get(f"{BASE_URL}/api/crm/tasks", headers=auth_headers)
        assert tasks_res.status_code == 200
        tasks = tasks_res.json()["tasks"]
        print(f"✓ Step 3: Retrieved {len(tasks)} tasks")
        
        print("✓ Full CRM Supreme workflow completed successfully")


class TestCRMSupremeAccessControl(TestCRMSupremeAuth):
    """Test access control for CRM Supreme features"""
    
    def test_unauthenticated_access_denied(self):
        """Verify unauthenticated requests are denied"""
        endpoints = [
            "/api/crm/email-templates",
            "/api/crm/automation-rules",
            "/api/crm/tasks"
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code in [401, 403], f"Expected 401/403 for {endpoint}, got {response.status_code}"
        print("✓ All CRM Supreme endpoints require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
