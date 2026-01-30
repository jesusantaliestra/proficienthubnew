"""
Test Analytics Dashboard Endpoints - Iteration 27
Tests for the new Advanced Analytics Dashboard feature with 8 endpoints:
- Executive Summary
- Revenue Analytics
- Lead Source Analytics
- Student Engagement
- Pipeline Velocity
- Cohort Analysis
- Export Reports
Also tests CRM router migration
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnalyticsDashboard:
    """Test Analytics Dashboard endpoints"""
    
    @pytest.fixture(scope="class")
    def institution_auth(self):
        """Register and login as institution to get auth token"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"test_analytics_inst_{unique_id}@test.com"
        
        # Register institution
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "name": f"Analytics Test Institution {unique_id}",
            "password": "TestPass123!",
            "user_type": "institution",
            "institution_name": f"Analytics Academy {unique_id}"
        })
        
        if register_response.status_code == 200:
            data = register_response.json()
            return {
                "token": data["access_token"],
                "user_id": data["user"]["id"],
                "email": email
            }
        
        # If registration fails (email exists), try login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": "TestPass123!"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            return {
                "token": data["access_token"],
                "user_id": data["user"]["id"],
                "email": email
            }
        
        pytest.skip("Could not authenticate institution")
    
    @pytest.fixture(scope="class")
    def student_auth(self, institution_auth):
        """Register a student under the institution"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"test_analytics_student_{unique_id}@test.com"
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "name": f"Analytics Test Student {unique_id}",
            "password": "TestPass123!",
            "user_type": "student"
        })
        
        if register_response.status_code == 200:
            data = register_response.json()
            return {
                "token": data["access_token"],
                "user_id": data["user"]["id"],
                "email": email
            }
        
        pytest.skip("Could not create student")
    
    # ==================== EXECUTIVE SUMMARY TESTS ====================
    
    def test_executive_summary_default_period(self, institution_auth):
        """Test GET /api/analytics-dashboard/executive-summary with default period"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/executive-summary",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "period" in data
        assert "kpis" in data
        assert "quick_insights" in data
        
        # Verify KPIs structure
        kpis = data["kpis"]
        assert "total_students" in kpis
        assert "active_students" in kpis
        assert "total_leads" in kpis
        assert "revenue" in kpis
        assert "exam_attempts" in kpis
        assert "conversion_rate" in kpis
        
        # Verify KPI values have expected fields
        assert "value" in kpis["total_students"]
        assert "change" in kpis["total_students"]
        assert "trend" in kpis["total_students"]
        
        print(f"Executive Summary - Period: {data['period']}, Total Students: {kpis['total_students']['value']}")
    
    def test_executive_summary_week_period(self, institution_auth):
        """Test executive summary with week period"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/executive-summary?period=week",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "week"
        print(f"Week period summary retrieved successfully")
    
    def test_executive_summary_quarter_period(self, institution_auth):
        """Test executive summary with quarter period"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/executive-summary?period=quarter",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "quarter"
        print(f"Quarter period summary retrieved successfully")
    
    def test_executive_summary_year_period(self, institution_auth):
        """Test executive summary with year period"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/executive-summary?period=year",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "year"
        print(f"Year period summary retrieved successfully")
    
    def test_executive_summary_unauthorized(self):
        """Test executive summary without auth returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/analytics-dashboard/executive-summary")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Unauthorized access correctly rejected")
    
    def test_executive_summary_student_forbidden(self, student_auth):
        """Test that students cannot access executive summary"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/executive-summary",
            headers={"Authorization": f"Bearer {student_auth['token']}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("Student access correctly forbidden")
    
    # ==================== REVENUE ANALYTICS TESTS ====================
    
    def test_revenue_analytics(self, institution_auth):
        """Test GET /api/analytics-dashboard/revenue"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/revenue",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "summary" in data
        assert "monthly_breakdown" in data
        assert "forecast" in data
        assert "insights" in data
        
        # Verify summary fields
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "total_deals_won" in summary
        assert "total_deals_lost" in summary
        assert "avg_deal_size" in summary
        assert "win_rate" in summary
        
        # Verify forecast structure
        assert isinstance(data["forecast"], list)
        if data["forecast"]:
            forecast_item = data["forecast"][0]
            assert "month" in forecast_item
            assert "predicted_revenue" in forecast_item
            assert "confidence" in forecast_item
        
        print(f"Revenue Analytics - Total Revenue: ${summary['total_revenue']}, Win Rate: {summary['win_rate']}%")
    
    def test_revenue_analytics_custom_months(self, institution_auth):
        """Test revenue analytics with custom months parameter"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/revenue?months=6",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "monthly_breakdown" in data
        print(f"Revenue analytics with 6 months retrieved successfully")
    
    # ==================== LEAD SOURCE ANALYTICS TESTS ====================
    
    def test_lead_source_analytics(self, institution_auth):
        """Test GET /api/analytics-dashboard/lead-sources"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/lead-sources",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "sources" in data
        assert "recommendations" in data
        
        # Verify sources is a list
        assert isinstance(data["sources"], list)
        
        # If there are sources, verify structure
        if data["sources"]:
            source = data["sources"][0]
            assert "source" in source
            assert "label" in source
            assert "leads" in source
            assert "conversion_rate" in source
        
        print(f"Lead Source Analytics - {len(data['sources'])} sources found")
    
    # ==================== STUDENT ENGAGEMENT TESTS ====================
    
    def test_student_engagement(self, institution_auth):
        """Test GET /api/analytics-dashboard/student-engagement"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/student-engagement",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "summary" in data
        assert "categories" in data
        assert "daily_activity" in data
        assert "recommendations" in data
        
        # Verify summary fields
        summary = data["summary"]
        assert "total_students" in summary
        assert "active" in summary
        assert "at_risk" in summary
        assert "inactive" in summary
        assert "engagement_rate" in summary
        
        # Verify categories structure
        categories = data["categories"]
        assert "active" in categories
        assert "at_risk" in categories
        assert "inactive" in categories
        
        print(f"Student Engagement - Total: {summary['total_students']}, Active: {summary['active']}, At Risk: {summary['at_risk']}")
    
    def test_student_engagement_custom_days(self, institution_auth):
        """Test student engagement with custom days parameter"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/student-engagement?days=7",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        print(f"Student engagement with 7 days retrieved successfully")
    
    # ==================== PIPELINE VELOCITY TESTS ====================
    
    def test_pipeline_velocity(self, institution_auth):
        """Test GET /api/analytics-dashboard/pipeline-velocity"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/pipeline-velocity",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "velocity" in data
        assert "pipeline_health" in data
        assert "stale_leads" in data
        assert "benchmarks" in data
        
        # Verify velocity structure
        velocity = data["velocity"]
        assert "total_cycle" in velocity
        
        # Verify pipeline health
        health = data["pipeline_health"]
        assert "total_in_pipeline" in health
        assert "stale_leads" in health
        assert "stale_percentage" in health
        
        # Verify benchmarks
        benchmarks = data["benchmarks"]
        assert "ideal_cycle_days" in benchmarks
        assert "warning_threshold_days" in benchmarks
        assert "critical_threshold_days" in benchmarks
        
        print(f"Pipeline Velocity - Avg Cycle: {velocity['total_cycle']['avg_days']} days, Stale: {health['stale_leads']}")
    
    # ==================== COHORT ANALYSIS TESTS ====================
    
    def test_cohort_analysis(self, institution_auth):
        """Test GET /api/analytics-dashboard/cohort-analysis"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/cohort-analysis",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "cohorts" in data
        assert "insights" in data
        
        # Verify cohorts is a list
        assert isinstance(data["cohorts"], list)
        
        # If there are cohorts, verify structure
        if data["cohorts"]:
            cohort = data["cohorts"][0]
            assert "cohort" in cohort
            assert "enrolled" in cohort
            assert "avg_score" in cohort
            assert "exams_per_student" in cohort
        
        # Verify insights
        insights = data["insights"]
        assert "total_cohorts" in insights
        
        print(f"Cohort Analysis - {insights['total_cohorts']} cohorts found")
    
    # ==================== EXPORT REPORTS TESTS ====================
    
    def test_export_executive_report(self, institution_auth):
        """Test GET /api/analytics-dashboard/export/executive"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/executive",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "format" in data
        assert "report_type" in data
        assert "generated_at" in data
        assert "data" in data
        assert data["report_type"] == "executive"
        
        print(f"Executive report exported successfully")
    
    def test_export_revenue_report(self, institution_auth):
        """Test GET /api/analytics-dashboard/export/revenue"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/revenue",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "revenue"
        print(f"Revenue report exported successfully")
    
    def test_export_leads_report(self, institution_auth):
        """Test GET /api/analytics-dashboard/export/leads"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/leads",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "leads"
        print(f"Leads report exported successfully")
    
    def test_export_students_report(self, institution_auth):
        """Test GET /api/analytics-dashboard/export/students"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/students",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "students"
        print(f"Students report exported successfully")
    
    def test_export_csv_format(self, institution_auth):
        """Test export with CSV format parameter"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/executive?format=csv",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "csv"
        print(f"CSV format export successful")
    
    def test_export_invalid_type(self, institution_auth):
        """Test export with invalid report type returns 400"""
        response = requests.get(
            f"{BASE_URL}/api/analytics-dashboard/export/invalid_type",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"Invalid report type correctly rejected")


class TestCRMRouter:
    """Test CRM Router endpoints (migrated from server.py)"""
    
    @pytest.fixture(scope="class")
    def institution_auth(self):
        """Register and login as institution"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"test_crm_inst_{unique_id}@test.com"
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "name": f"CRM Test Institution {unique_id}",
            "password": "TestPass123!",
            "user_type": "institution",
            "institution_name": f"CRM Academy {unique_id}"
        })
        
        if register_response.status_code == 200:
            data = register_response.json()
            return {
                "token": data["access_token"],
                "user_id": data["user"]["id"],
                "email": email
            }
        
        pytest.skip("Could not authenticate institution")
    
    def test_get_pipeline_stages(self):
        """Test GET /api/crm/pipeline-stages - Public endpoint"""
        response = requests.get(f"{BASE_URL}/api/crm/pipeline-stages")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "stages" in data
        stages = data["stages"]
        
        # Verify expected stages exist
        expected_stages = ["new", "contacted", "demo_scheduled", "demo_completed", "proposal_sent", "negotiating", "won", "lost"]
        for stage in expected_stages:
            assert stage in stages, f"Missing stage: {stage}"
            assert "label" in stages[stage]
            assert "color" in stages[stage]
        
        print(f"Pipeline stages retrieved: {list(stages.keys())}")
    
    def test_create_lead(self, institution_auth):
        """Test POST /api/crm/leads - Create a new lead"""
        unique_id = str(uuid.uuid4())[:8]
        
        response = requests.post(
            f"{BASE_URL}/api/crm/leads",
            headers={"Authorization": f"Bearer {institution_auth['token']}"},
            json={
                "institution_name": f"Test Lead Academy {unique_id}",
                "contact_name": f"John Doe {unique_id}",
                "email": f"lead_{unique_id}@test.com",
                "phone": "+1234567890",
                "country": "USA",
                "students_count": 100,
                "exam_types": ["ielts-academic", "toefl"],
                "source": "organic",
                "notes": "Test lead for analytics dashboard testing",
                "estimated_value": 5000
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert "lead" in data
        assert data["lead"]["institution_name"] == f"Test Lead Academy {unique_id}"
        assert data["lead"]["stage"] == "new"
        
        print(f"Lead created successfully: {data['id']}")
        return data["id"]
    
    def test_get_leads(self, institution_auth):
        """Test GET /api/crm/leads - List all leads"""
        response = requests.get(
            f"{BASE_URL}/api/crm/leads",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "pipeline" in data
        assert "stages" in data
        assert "stats" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "total_leads" in stats
        assert "total_value" in stats
        assert "won_value" in stats
        assert "conversion_rate" in stats
        
        print(f"Leads retrieved - Total: {stats['total_leads']}, Value: ${stats['total_value']}")
    
    def test_get_crm_dashboard(self, institution_auth):
        """Test GET /api/crm/dashboard - CRM dashboard metrics"""
        response = requests.get(
            f"{BASE_URL}/api/crm/dashboard",
            headers={"Authorization": f"Bearer {institution_auth['token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "metrics" in data
        assert "by_stage" in data
        assert "by_source" in data
        
        metrics = data["metrics"]
        assert "total_leads" in metrics
        assert "new_leads" in metrics
        assert "won_deals" in metrics
        assert "lost_deals" in metrics
        assert "conversion_rate" in metrics
        assert "total_value" in metrics
        assert "won_value" in metrics
        assert "pipeline_value" in metrics
        
        print(f"CRM Dashboard - Total Leads: {metrics['total_leads']}, Conversion: {metrics['conversion_rate']}%")


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"Health check passed: {data}")
    
    def test_backend_url_configured(self):
        """Verify REACT_APP_BACKEND_URL is configured"""
        assert BASE_URL, "REACT_APP_BACKEND_URL not configured"
        assert BASE_URL.startswith("http"), f"Invalid URL format: {BASE_URL}"
        print(f"Backend URL: {BASE_URL}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
