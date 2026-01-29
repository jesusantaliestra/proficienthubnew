"""
Test CRM Education Enhancements
Tests for drag-and-drop pipeline, lead detail modal, and education-specific metrics
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCRMEducationEnhancements:
    """Tests for CRM Education module enhancements"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
    
    # ==================== Pipeline Stages Tests ====================
    
    def test_get_pipeline_stages(self):
        """Test GET /api/crm-edu/pipeline-stages returns education-specific stages"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/pipeline-stages")
        assert response.status_code == 200
        
        data = response.json()
        assert "stages" in data
        stages = data["stages"]
        
        # Should have 11 education-specific stages
        assert len(stages) >= 10, f"Expected at least 10 stages, got {len(stages)}"
        
        # Verify stage structure
        for stage in stages:
            assert "id" in stage
            assert "name" in stage
            assert "color" in stage
            assert "order" in stage
        
        # Verify key education stages exist
        stage_ids = [s["id"] for s in stages]
        expected_stages = ["lead", "qualified", "demo_scheduled", "demo_completed", 
                          "trial", "proposal", "negotiation", "onboarding", "active"]
        for expected in expected_stages:
            assert expected in stage_ids, f"Missing stage: {expected}"
    
    # ==================== Leads CRUD Tests ====================
    
    def test_list_leads(self):
        """Test GET /api/crm-edu/leads returns leads with pagination"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "leads" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        
        # Verify seeded data exists
        assert data["total"] >= 15, f"Expected at least 15 seeded leads, got {data['total']}"
    
    def test_get_lead_detail(self):
        """Test GET /api/crm-edu/leads/{id} returns full lead details"""
        # Get a lead first
        list_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?per_page=1")
        leads = list_response.json()["leads"]
        assert len(leads) > 0, "No leads found"
        
        lead_id = leads[0]["id"]
        
        # Get lead detail
        response = self.session.get(f"{BASE_URL}/api/crm-edu/leads/{lead_id}")
        assert response.status_code == 200
        
        lead = response.json()
        
        # Verify all lead fields for modal display
        assert "id" in lead
        assert "institution_name" in lead
        assert "contact_name" in lead
        assert "contact_email" in lead
        assert "stage" in lead
        assert "lead_score" in lead
        assert "estimated_students" in lead
        assert "exam_types_interested" in lead
        assert "country" in lead
        assert "source" in lead
    
    def test_update_lead_stage_patch(self):
        """Test PATCH /api/crm-edu/leads/{id} for stage change (drag-drop)"""
        # Get a lead in 'lead' stage
        list_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?stage=lead&per_page=1")
        leads = list_response.json()["leads"]
        
        if len(leads) == 0:
            # Create a test lead if none in 'lead' stage
            create_response = self.session.post(f"{BASE_URL}/api/crm-edu/leads", json={
                "institution_name": "TEST_DragDrop_Academy",
                "contact_name": "Test Contact",
                "contact_email": "test_dragdrop@test.com",
                "estimated_students": 100,
                "exam_types_interested": ["ielts", "toefl"],
                "country": "USA",
                "source": "website"
            })
            assert create_response.status_code == 200
            lead_id = create_response.json()["id"]
            original_stage = "lead"
        else:
            lead_id = leads[0]["id"]
            original_stage = leads[0]["stage"]
        
        # Update stage (simulating drag-drop)
        new_stage = "qualified"
        response = self.session.patch(f"{BASE_URL}/api/crm-edu/leads/{lead_id}", json={
            "stage": new_stage
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Lead updated"
        
        # Verify stage was updated
        verify_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads/{lead_id}")
        assert verify_response.status_code == 200
        assert verify_response.json()["stage"] == new_stage
        
        # Restore original stage
        self.session.patch(f"{BASE_URL}/api/crm-edu/leads/{lead_id}", json={
            "stage": original_stage
        })
    
    def test_update_lead_stage_from_modal(self):
        """Test stage change from modal (same PATCH endpoint)"""
        # Get any lead
        list_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?per_page=1")
        leads = list_response.json()["leads"]
        assert len(leads) > 0
        
        lead_id = leads[0]["id"]
        original_stage = leads[0]["stage"]
        
        # Change to demo_scheduled (simulating modal stage selector)
        response = self.session.patch(f"{BASE_URL}/api/crm-edu/leads/{lead_id}", json={
            "stage": "demo_scheduled"
        })
        assert response.status_code == 200
        
        # Verify
        verify_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads/{lead_id}")
        assert verify_response.json()["stage"] == "demo_scheduled"
        
        # Restore
        self.session.patch(f"{BASE_URL}/api/crm-edu/leads/{lead_id}", json={
            "stage": original_stage
        })
    
    # ==================== Analytics Tests ====================
    
    def test_pipeline_analytics(self):
        """Test GET /api/crm-edu/analytics/pipeline returns conversion metrics"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/analytics/pipeline")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify analytics structure
        assert "total_leads" in data
        assert "active_customers" in data
        assert "conversion_rate" in data
        assert "by_stage" in data
        assert "by_source" in data
        
        # Verify data types
        assert isinstance(data["total_leads"], int)
        assert isinstance(data["conversion_rate"], (int, float))
        assert isinstance(data["by_stage"], dict)
        assert isinstance(data["by_source"], dict)
    
    def test_analytics_by_stage_breakdown(self):
        """Test analytics shows leads count per stage"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/analytics/pipeline")
        data = response.json()
        
        by_stage = data["by_stage"]
        
        # Each stage should have count and value
        for stage_id, stage_data in by_stage.items():
            assert "count" in stage_data, f"Stage {stage_id} missing count"
            assert "value" in stage_data, f"Stage {stage_id} missing value"
    
    def test_analytics_by_source(self):
        """Test analytics shows leads by source"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/analytics/pipeline")
        data = response.json()
        
        by_source = data["by_source"]
        assert len(by_source) > 0, "No source data found"
        
        # Verify sources are valid
        valid_sources = ["website", "referral", "google_ads", "facebook", "linkedin", 
                        "event", "cold_outreach", "partner"]
        for source in by_source.keys():
            assert source in valid_sources or source is None, f"Invalid source: {source}"
    
    # ==================== Tasks Tests ====================
    
    def test_list_tasks(self):
        """Test GET /api/crm-edu/tasks returns tasks"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
    
    # ==================== Lead Filtering Tests ====================
    
    def test_filter_leads_by_stage(self):
        """Test filtering leads by stage"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?stage=lead")
        assert response.status_code == 200
        
        leads = response.json()["leads"]
        for lead in leads:
            assert lead["stage"] == "lead"
    
    def test_filter_leads_by_exam_type(self):
        """Test filtering leads by exam type"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?exam_type=ielts")
        assert response.status_code == 200
        
        leads = response.json()["leads"]
        for lead in leads:
            assert "ielts" in lead.get("exam_types_interested", [])
    
    def test_search_leads(self):
        """Test searching leads by name/email"""
        response = self.session.get(f"{BASE_URL}/api/crm-edu/leads?search=Academy")
        assert response.status_code == 200
        
        data = response.json()
        assert "leads" in data


class TestERPDashboard:
    """Tests for ERP Dashboard with seeded data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
    
    def test_list_invoices(self):
        """Test GET /api/erp/invoices returns seeded invoices"""
        response = self.session.get(f"{BASE_URL}/api/erp/invoices?per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "invoices" in data
        assert "total" in data
        
        # Verify seeded data exists
        assert data["total"] >= 20, f"Expected at least 20 seeded invoices, got {data['total']}"
    
    def test_invoice_stats_summary(self):
        """Test GET /api/erp/invoices/stats/summary"""
        response = self.session.get(f"{BASE_URL}/api/erp/invoices/stats/summary?period=month")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "by_status" in data
        assert "totals" in data
    
    def test_subscription_mrr_metrics(self):
        """Test GET /api/erp/subscriptions/metrics/mrr"""
        response = self.session.get(f"{BASE_URL}/api/erp/subscriptions/metrics/mrr")
        assert response.status_code == 200
        
        data = response.json()
        assert "current_mrr" in data
        assert "current_arr" in data
        assert "active_subscriptions" in data
        
        # Verify seeded subscriptions
        assert data["active_subscriptions"] >= 5, f"Expected at least 5 subscriptions, got {data['active_subscriptions']}"
    
    def test_chart_of_accounts(self):
        """Test GET /api/erp/accounting/chart-of-accounts"""
        response = self.session.get(f"{BASE_URL}/api/erp/accounting/chart-of-accounts")
        assert response.status_code == 200


class TestCRMLeadCreate:
    """Tests for creating new leads"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
    
    def test_create_lead_with_exam_types(self):
        """Test creating a lead with multiple exam types"""
        response = self.session.post(f"{BASE_URL}/api/crm-edu/leads", json={
            "institution_name": "TEST_MultiExam_Academy",
            "contact_name": "Test Contact",
            "contact_email": "test_multiexam@test.com",
            "contact_phone": "+1 555 123 4567",
            "contact_role": "Director",
            "estimated_students": 500,
            "exam_types_interested": ["ielts", "toefl", "pte", "cambridge"],
            "country": "Canada",
            "source": "referral"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "lead_score" in data
        assert data["stage"] == "lead"
        
        # Verify lead was created with correct data
        lead_id = data["id"]
        verify_response = self.session.get(f"{BASE_URL}/api/crm-edu/leads/{lead_id}")
        lead = verify_response.json()
        
        assert lead["institution_name"] == "TEST_MultiExam_Academy"
        assert len(lead["exam_types_interested"]) == 4
        assert lead["estimated_students"] == 500
