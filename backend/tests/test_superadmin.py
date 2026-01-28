"""
Test suite for Superadmin Dashboard API endpoints
Tests: /api/superadmin/stats, /api/superadmin/institutions, /api/superadmin/activity-log,
       /api/superadmin/revenue-report, /api/superadmin/grant-credits, /api/superadmin/institutions/{id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPERADMIN_EMAIL = "santaliestralimited@gmail.com"
SUPERADMIN_PASSWORD = "Admin123!"
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestSuperadminAuth:
    """Test superadmin authentication and access control"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_superadmin_token(self):
        """Get superadmin auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def get_institution_token(self):
        """Get institution auth token (non-superadmin)"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def test_superadmin_login_success(self):
        """Test superadmin can login successfully"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "admin"
        print(f"✓ Superadmin login successful - user_type: {data['user']['user_type']}")


class TestSuperadminStats:
    """Test GET /api/superadmin/stats endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Get superadmin token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_get_stats_success(self):
        """Test superadmin can get platform stats"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify platform_stats structure
        assert "platform_stats" in data
        platform = data["platform_stats"]
        assert "total_institutions" in platform
        assert "total_students" in platform
        assert "total_individuals" in platform
        assert "total_users" in platform
        assert "active_users_7d" in platform
        assert "active_users_30d" in platform
        
        # Verify exam_stats structure
        assert "exam_stats" in data
        exam = data["exam_stats"]
        assert "total_exams_taken" in exam
        assert "exams_this_week" in exam
        assert "exams_this_month" in exam
        assert "exam_distribution" in exam
        assert "average_scores" in exam
        
        # Verify ai_stats structure
        assert "ai_stats" in data
        ai = data["ai_stats"]
        assert "total_ai_interactions" in ai
        assert "ai_interactions_this_week" in ai
        assert "total_credits_purchased" in ai
        assert "total_credits_used" in ai
        assert "total_free_credits_given" in ai
        
        # Verify growth_stats structure
        assert "growth_stats" in data
        growth = data["growth_stats"]
        assert "new_institutions_this_week" in growth
        assert "new_students_this_week" in growth
        
        # Verify business_metrics structure
        assert "business_metrics" in data
        business = data["business_metrics"]
        assert "estimated_revenue_from_credits" in business
        assert "avg_credits_per_institution" in business
        assert "student_to_institution_ratio" in business
        assert "platform_engagement_rate" in business
        
        print(f"✓ Stats retrieved - Institutions: {platform['total_institutions']}, Students: {platform['total_students']}")
    
    def test_stats_forbidden_for_non_superadmin(self):
        """Test non-superadmin cannot access stats"""
        # Get institution token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Failed to get institution token")
        
        inst_token = response.json().get("access_token")
        
        # Try to access superadmin stats with institution token
        response = self.session.get(
            f"{BASE_URL}/api/superadmin/stats",
            headers={"Authorization": f"Bearer {inst_token}"}
        )
        assert response.status_code == 403
        print("✓ Non-superadmin correctly denied access to stats (403)")


class TestSuperadminInstitutions:
    """Test GET /api/superadmin/institutions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_get_institutions_list(self):
        """Test superadmin can get list of institutions"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions")
        assert response.status_code == 200
        data = response.json()
        
        assert "institutions" in data
        assert "total" in data
        assert "limit" in data
        assert "skip" in data
        assert "has_more" in data
        
        # Verify institution data structure if any exist
        if data["institutions"]:
            inst = data["institutions"][0]
            assert "id" in inst
            assert "email" in inst
            assert "student_count" in inst
            assert "ai_credits" in inst
            assert "activity_this_week" in inst
            assert "has_zoom_configured" in inst
            assert "has_messaging_configured" in inst
            
            # Verify ai_credits structure
            credits = inst["ai_credits"]
            assert "total" in credits
            assert "used" in credits
            assert "available" in credits
            
            print(f"✓ Institutions list retrieved - Total: {data['total']}, First: {inst.get('institution_name', inst.get('email'))}")
        else:
            print(f"✓ Institutions list retrieved - Total: {data['total']} (empty)")
    
    def test_institutions_search(self):
        """Test institution search functionality"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions", params={"search": "demo"})
        assert response.status_code == 200
        data = response.json()
        assert "institutions" in data
        print(f"✓ Institution search works - Found {len(data['institutions'])} matching 'demo'")
    
    def test_institutions_pagination(self):
        """Test institution list pagination"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions", params={"limit": 5, "skip": 0})
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["skip"] == 0
        print(f"✓ Pagination works - limit: {data['limit']}, skip: {data['skip']}")


class TestSuperadminInstitutionDetails:
    """Test GET /api/superadmin/institutions/{id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_get_institution_details(self):
        """Test getting detailed institution info"""
        # First get list of institutions
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions", params={"limit": 1})
        if response.status_code != 200 or not response.json().get("institutions"):
            pytest.skip("No institutions available to test")
        
        inst_id = response.json()["institutions"][0]["id"]
        
        # Get details
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions/{inst_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "institution" in data
        assert "students" in data
        assert "student_count" in data
        assert "settings" in data
        assert "credits" in data
        assert "exam_stats" in data
        assert "ai_usage_this_week" in data
        
        print(f"✓ Institution details retrieved - ID: {inst_id}, Students: {data['student_count']}")
    
    def test_institution_not_found(self):
        """Test 404 for non-existent institution"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions/non-existent-id-12345")
        assert response.status_code == 404
        print("✓ Non-existent institution returns 404")


class TestSuperadminActivityLog:
    """Test GET /api/superadmin/activity-log endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_get_activity_log(self):
        """Test getting platform activity log"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/activity-log")
        assert response.status_code == 200
        data = response.json()
        
        assert "activities" in data
        
        # Verify activity structure if any exist
        if data["activities"]:
            activity = data["activities"][0]
            assert "type" in activity
            assert "description" in activity
            assert "timestamp" in activity
            assert activity["type"] in ["exam", "ai", "registration"]
            
            print(f"✓ Activity log retrieved - {len(data['activities'])} activities")
        else:
            print("✓ Activity log retrieved - empty (no recent activity)")
    
    def test_activity_log_filter_by_type(self):
        """Test filtering activity log by type"""
        for activity_type in ["exam", "ai", "registration"]:
            response = self.session.get(f"{BASE_URL}/api/superadmin/activity-log", params={"activity_type": activity_type})
            assert response.status_code == 200
            data = response.json()
            
            # All activities should be of the specified type
            for activity in data["activities"]:
                assert activity["type"] == activity_type
            
            print(f"✓ Activity filter '{activity_type}' works - {len(data['activities'])} activities")


class TestSuperadminRevenueReport:
    """Test GET /api/superadmin/revenue-report endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_get_revenue_report_month(self):
        """Test getting monthly revenue report"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/revenue-report", params={"period": "month"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"] == "month"
        assert "start_date" in data
        assert "end_date" in data
        assert "credits" in data
        assert "subscriptions" in data
        assert "summary" in data
        
        # Verify credits structure
        credits = data["credits"]
        assert "total_purchased" in credits
        assert "total_revenue" in credits
        assert "purchase_count" in credits
        
        # Verify summary structure
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "avg_revenue_per_purchase" in summary
        
        print(f"✓ Monthly revenue report - Revenue: ${summary['total_revenue']}")
    
    def test_get_revenue_report_week(self):
        """Test getting weekly revenue report"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/revenue-report", params={"period": "week"})
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "week"
        print(f"✓ Weekly revenue report retrieved")
    
    def test_get_revenue_report_year(self):
        """Test getting yearly revenue report"""
        response = self.session.get(f"{BASE_URL}/api/superadmin/revenue-report", params={"period": "year"})
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "year"
        print(f"✓ Yearly revenue report retrieved")


class TestSuperadminGrantCredits:
    """Test POST /api/superadmin/grant-credits endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Failed to get superadmin token")
    
    def test_grant_credits_success(self):
        """Test granting credits to an institution"""
        # First get an institution ID
        response = self.session.get(f"{BASE_URL}/api/superadmin/institutions", params={"limit": 1})
        if response.status_code != 200 or not response.json().get("institutions"):
            pytest.skip("No institutions available to test")
        
        inst_id = response.json()["institutions"][0]["id"]
        inst_name = response.json()["institutions"][0].get("institution_name", "Unknown")
        
        # Grant credits
        response = self.session.post(
            f"{BASE_URL}/api/superadmin/grant-credits",
            params={
                "institution_id": inst_id,
                "credits": 50,
                "reason": "Test grant from pytest"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Granted 50 credits" in data["message"]
        
        print(f"✓ Granted 50 credits to {inst_name}")
    
    def test_grant_credits_invalid_institution(self):
        """Test granting credits to non-existent institution"""
        response = self.session.post(
            f"{BASE_URL}/api/superadmin/grant-credits",
            params={
                "institution_id": "non-existent-id-12345",
                "credits": 50,
                "reason": "Test"
            }
        )
        assert response.status_code == 404
        print("✓ Grant credits to non-existent institution returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
