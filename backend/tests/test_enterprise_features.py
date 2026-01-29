"""
Enterprise Features Test Suite
Tests for API Keys, Integrations Hub, ERP Dashboard, and CRM Education
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"
ADMIN_EMAIL = "santaliestralimited@gmail.com"
ADMIN_PASSWORD = "Admin123!"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_institution_login(self):
        """Test institution login with demo credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "institution"
        print(f"✓ Institution login successful: {data['user']['email']}")
        return data["access_token"]


class TestAPIKeysManager:
    """Tests for API Keys Management - /api/api-keys"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_api_keys(self):
        """Test GET /api/api-keys - list all API keys"""
        response = requests.get(f"{BASE_URL}/api/api-keys", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List API keys: {len(data)} keys found")
    
    def test_create_api_key(self):
        """Test POST /api/api-keys - create new API key"""
        response = requests.post(f"{BASE_URL}/api/api-keys", 
            headers=self.headers,
            json={
                "name": "TEST_Integration_Key",
                "description": "Test key for automated testing",
                "scopes": ["read", "write"],
                "rate_limit": 500,
                "expires_in_days": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["name"] == "TEST_Integration_Key"
        assert "ph_live_" in data["api_key"]
        print(f"✓ Created API key: {data['key_prefix']}...")
        return data
    
    def test_create_and_revoke_api_key(self):
        """Test creating and revoking an API key"""
        # Create
        create_response = requests.post(f"{BASE_URL}/api/api-keys", 
            headers=self.headers,
            json={
                "name": "TEST_Revoke_Key",
                "scopes": ["read"],
                "rate_limit": 100,
                "expires_in_days": 7
            }
        )
        assert create_response.status_code == 200
        key_data = create_response.json()
        key_id = key_data["id"]
        
        # Revoke
        revoke_response = requests.delete(f"{BASE_URL}/api/api-keys/{key_id}", headers=self.headers)
        assert revoke_response.status_code == 200
        print(f"✓ Created and revoked API key: {key_id}")


class TestIntegrationsHub:
    """Tests for External Integrations - /api/integrations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_available_integrations(self):
        """Test GET /api/integrations/available - list all available integrations"""
        response = requests.get(f"{BASE_URL}/api/integrations/available", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        assert "categories" in data
        
        # Verify CRM integrations exist
        integrations = data["integrations"]
        assert "salesforce" in integrations
        assert "hubspot" in integrations
        assert "zoho_crm" in integrations
        
        # Verify ERP integrations exist
        assert "quickbooks" in integrations
        assert "xero" in integrations
        
        # Verify categories
        assert "crm" in data["categories"]
        assert "erp" in data["categories"]
        
        print(f"✓ Available integrations: {len(integrations)} total")
        print(f"  - CRM: {len(data['categories']['crm'])} integrations")
        print(f"  - ERP: {len(data['categories']['erp'])} integrations")
    
    def test_list_connected_integrations(self):
        """Test GET /api/integrations - list connected integrations"""
        response = requests.get(f"{BASE_URL}/api/integrations", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        print(f"✓ Connected integrations: {len(data['integrations'])} active")
    
    def test_connect_integration_simulated(self):
        """Test POST /api/integrations/connect - connect an integration (simulated)"""
        response = requests.post(f"{BASE_URL}/api/integrations/connect",
            headers=self.headers,
            json={
                "integration_type": "pipedrive",
                "credentials": {"api_key": "test_api_key_12345"},
                "settings": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending_verification"
        print(f"✓ Connected integration (simulated): {data['id']}")
        
        # Clean up - disconnect
        requests.delete(f"{BASE_URL}/api/integrations/{data['id']}", headers=self.headers)


class TestERPDashboard:
    """Tests for ERP Dashboard - /api/erp/*"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_invoices(self):
        """Test GET /api/erp/invoices - list invoices"""
        response = requests.get(f"{BASE_URL}/api/erp/invoices?page=1&per_page=10", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data
        assert "total" in data
        assert "page" in data
        print(f"✓ Invoices list: {data['total']} total invoices")
    
    def test_invoice_stats_summary(self):
        """Test GET /api/erp/invoices/stats/summary - get invoice statistics"""
        response = requests.get(f"{BASE_URL}/api/erp/invoices/stats/summary?period=month", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "totals" in data
        print(f"✓ Invoice stats: {data}")
    
    def test_subscription_mrr_metrics(self):
        """Test GET /api/erp/subscriptions/metrics/mrr - get MRR metrics"""
        response = requests.get(f"{BASE_URL}/api/erp/subscriptions/metrics/mrr", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ MRR metrics: {data}")
    
    def test_chart_of_accounts(self):
        """Test GET /api/erp/accounting/chart-of-accounts - get chart of accounts"""
        response = requests.get(f"{BASE_URL}/api/erp/accounting/chart-of-accounts", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Chart of accounts: {data}")


class TestCRMEducation:
    """Tests for CRM Education - /api/crm-edu/*"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_pipeline_stages(self):
        """Test GET /api/crm-edu/pipeline-stages - get education pipeline stages"""
        response = requests.get(f"{BASE_URL}/api/crm-edu/pipeline-stages", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "stages" in data
        stages = data["stages"]
        
        # Verify education-specific stages exist
        stage_ids = [s["id"] for s in stages]
        assert "lead" in stage_ids
        assert "qualified" in stage_ids
        assert "demo_scheduled" in stage_ids
        assert "trial" in stage_ids
        assert "active" in stage_ids
        
        print(f"✓ Pipeline stages: {len(stages)} stages")
        for stage in stages[:5]:
            print(f"  - {stage['name']} ({stage['id']})")
    
    def test_list_leads(self):
        """Test GET /api/crm-edu/leads - list education leads"""
        response = requests.get(f"{BASE_URL}/api/crm-edu/leads?per_page=100", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "total" in data
        print(f"✓ CRM leads: {data['total']} total leads")
    
    def test_list_tasks(self):
        """Test GET /api/crm-edu/tasks - list CRM tasks"""
        response = requests.get(f"{BASE_URL}/api/crm-edu/tasks?status=pending", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        print(f"✓ CRM tasks: {len(data['tasks'])} pending tasks")
    
    def test_pipeline_analytics(self):
        """Test GET /api/crm-edu/analytics/pipeline - get pipeline analytics"""
        response = requests.get(f"{BASE_URL}/api/crm-edu/analytics/pipeline", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "conversion_rate" in data
        assert "by_stage" in data
        print(f"✓ Pipeline analytics: {data['total_leads']} leads, {data['conversion_rate']}% conversion")
    
    def test_create_and_delete_lead(self):
        """Test creating and deleting a CRM lead"""
        # Create lead
        create_response = requests.post(f"{BASE_URL}/api/crm-edu/leads",
            headers=self.headers,
            json={
                "institution_name": "TEST_Academy",
                "contact_name": "Test Contact",
                "contact_email": "test_lead@example.com",
                "contact_phone": "+1234567890",
                "contact_role": "Director",
                "institution_type": "language_school",
                "estimated_students": 150,
                "exam_types_interested": ["ielts", "toefl"],
                "country": "US",
                "source": "website"
            }
        )
        assert create_response.status_code == 200
        lead_data = create_response.json()
        assert "id" in lead_data
        assert "lead_score" in lead_data
        lead_id = lead_data["id"]
        print(f"✓ Created lead: {lead_id} with score {lead_data['lead_score']}")
        
        # Delete lead (cleanup)
        delete_response = requests.delete(f"{BASE_URL}/api/crm-edu/leads/{lead_id}", headers=self.headers)
        # Note: Delete endpoint may not exist, so we just try
        print(f"✓ Lead cleanup attempted")


class TestInstitutionDashboard:
    """Tests for Institution Dashboard metrics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_institution_metrics(self):
        """Test GET /api/institution/metrics - get dashboard metrics"""
        response = requests.get(f"{BASE_URL}/api/institution/metrics", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "avg_pass_probability" in data
        assert "at_risk_students" in data
        print(f"✓ Institution metrics: {data['total_students']} students, {data['avg_pass_probability']}% avg pass probability")
    
    def test_institution_students(self):
        """Test GET /api/institution/students - list students"""
        response = requests.get(f"{BASE_URL}/api/institution/students", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Institution students: {len(data)} students")
    
    def test_library_items(self):
        """Test GET /api/library/items - list library items"""
        response = requests.get(f"{BASE_URL}/api/library/items", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Library items: {len(data)} items")


class TestPricingEndpoints:
    """Tests for pricing endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_platform_plans(self):
        """Test GET /api/pricing/platform-plans - get pricing plans"""
        response = requests.get(f"{BASE_URL}/api/pricing/platform-plans", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "exam_plans" in data
        assert "volume_pricing" in data
        assert "ai_tutor_options" in data
        print(f"✓ Platform plans: {len(data['exam_plans'])} exam plans")
    
    def test_pricing_calculator(self):
        """Test GET /api/pricing/calculator - calculate pricing"""
        response = requests.get(
            f"{BASE_URL}/api/pricing/calculator?exam_plan=plan_10&num_licenses=100&ai_tutor_option=none",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        # Response has nested structure with pricing details
        assert "pricing" in data
        assert "total_order_price" in data["pricing"]
        assert "price_per_license" in data["pricing"]
        print(f"✓ Pricing calculator: {data['summary']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
