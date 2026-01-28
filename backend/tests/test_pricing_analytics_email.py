"""
Test suite for Pricing, Analytics, and Email routers
Tests new features: Dynamic pricing config, Real predictive analytics, Email notifications
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
STUDENT_EMAIL = "maria@demo.com"
STUDENT_PASSWORD = "Demo123!"


@pytest.fixture(scope="module")
def superadmin_token():
    """Get superadmin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Superadmin authentication failed")


@pytest.fixture(scope="module")
def institution_token():
    """Get institution authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Institution authentication failed")


@pytest.fixture(scope="module")
def student_token():
    """Get student authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Student authentication failed")


class TestPricingPublic:
    """Test public pricing endpoints (no auth required)"""
    
    def test_get_public_pricing(self):
        """GET /api/pricing/public - returns public pricing data"""
        response = requests.get(f"{BASE_URL}/api/pricing/public")
        assert response.status_code == 200
        
        data = response.json()
        # Verify all pricing categories exist
        assert "exam_plans" in data
        assert "volume_tiers" in data
        assert "ai_tutor_options" in data
        assert "mobile_app_pricing" in data
        assert "credit_packages" in data
        
        # Verify exam plans structure
        assert len(data["exam_plans"]) > 0
        plan = data["exam_plans"][0]
        assert "plan_id" in plan
        assert "exams" in plan
        assert "price" in plan
        assert "label" in plan
        # Public endpoint should NOT include base_cost
        assert "base_cost" not in plan
        
    def test_public_pricing_volume_tiers(self):
        """Verify volume tiers have correct structure"""
        response = requests.get(f"{BASE_URL}/api/pricing/public")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["volume_tiers"]) >= 7  # Should have 7 tiers
        
        tier = data["volume_tiers"][0]
        assert "tier_id" in tier
        assert "min_licenses" in tier
        assert "max_licenses" in tier
        assert "discount_percent" in tier
        # Public should NOT include price_multiplier
        assert "price_multiplier" not in tier
        
    def test_public_pricing_mobile_app(self):
        """Verify mobile app pricing tiers"""
        response = requests.get(f"{BASE_URL}/api/pricing/public")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["mobile_app_pricing"]) >= 3  # standard, premium, enterprise
        
        # Check for expected tiers
        tier_ids = [t["tier_id"] for t in data["mobile_app_pricing"]]
        assert "standard" in tier_ids
        assert "premium" in tier_ids
        assert "enterprise" in tier_ids
        
    def test_public_pricing_credit_packages(self):
        """Verify credit packages structure"""
        response = requests.get(f"{BASE_URL}/api/pricing/public")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["credit_packages"]) > 0
        
        pkg = data["credit_packages"][0]
        assert "package_id" in pkg
        assert "credits" in pkg
        assert "price" in pkg
        assert "bonus_credits" in pkg


class TestPricingConfig:
    """Test pricing configuration endpoints (superadmin only)"""
    
    def test_get_pricing_config_superadmin(self, superadmin_token):
        """GET /api/pricing/config - superadmin gets full config with costs"""
        response = requests.get(
            f"{BASE_URL}/api/pricing/config",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Superadmin should see base_cost
        assert "exam_plans" in data
        if data["exam_plans"]:
            assert "base_cost" in data["exam_plans"][0]
            
    def test_get_pricing_config_unauthorized(self, institution_token):
        """GET /api/pricing/config - non-superadmin gets filtered data"""
        response = requests.get(
            f"{BASE_URL}/api/pricing/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Non-superadmin should NOT see base_cost
        if data.get("exam_plans"):
            assert "base_cost" not in data["exam_plans"][0]
            
    def test_update_pricing_config_superadmin(self, superadmin_token):
        """PUT /api/pricing/config - superadmin can update pricing"""
        # Update just credit packages
        update_data = {
            "credit_packages": [
                {"package_id": "starter", "credits": 100, "price": 10.0, "bonus_credits": 0, "label": "100 Credits", "popular": False, "enabled": True},
                {"package_id": "basic", "credits": 500, "price": 45.0, "bonus_credits": 50, "label": "500 + 50 Bonus", "popular": False, "enabled": True},
                {"package_id": "standard", "credits": 1000, "price": 80.0, "bonus_credits": 150, "label": "1000 + 150 Bonus", "popular": True, "enabled": True},
                {"package_id": "pro", "credits": 2500, "price": 175.0, "bonus_credits": 500, "label": "2500 + 500 Bonus", "popular": False, "enabled": True},
                {"package_id": "enterprise", "credits": 5000, "price": 300.0, "bonus_credits": 1500, "label": "5000 + 1500 Bonus", "popular": False, "enabled": True}
            ]
        }
        
        response = requests.put(
            f"{BASE_URL}/api/pricing/config",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json=update_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        
    def test_update_pricing_config_forbidden(self, institution_token):
        """PUT /api/pricing/config - non-superadmin cannot update"""
        response = requests.put(
            f"{BASE_URL}/api/pricing/config",
            headers={"Authorization": f"Bearer {institution_token}"},
            json={"credit_packages": []}
        )
        assert response.status_code == 403


class TestAnalyticsInstitution:
    """Test institution analytics endpoints"""
    
    def test_get_institution_overview(self, institution_token):
        """GET /api/analytics/institution/overview - returns analytics with pass probability"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/institution/overview",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify structure
        assert "period_days" in data
        assert "students" in data
        assert "exams" in data
        assert "sections" in data
        assert "ai_usage" in data
        assert "prediction" in data
        assert "generated_at" in data
        
        # Verify students data
        assert "total" in data["students"]
        assert "active" in data["students"]
        assert "activity_rate" in data["students"]
        
        # Verify prediction data
        assert "avg_pass_probability" in data["prediction"]
        assert "students_analyzed" in data["prediction"]
        
    def test_get_institution_overview_with_period(self, institution_token):
        """GET /api/analytics/institution/overview?period_days=60"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/institution/overview?period_days=60",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 60
        
    def test_get_students_at_risk(self, institution_token):
        """GET /api/analytics/institution/students-at-risk - returns at-risk students"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/institution/students-at-risk",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "threshold" in data
        assert "students_at_risk" in data
        assert "total_at_risk" in data
        assert "generated_at" in data
        
        # Default threshold should be 50
        assert data["threshold"] == 50
        
    def test_get_students_at_risk_custom_threshold(self, institution_token):
        """GET /api/analytics/institution/students-at-risk?threshold=40"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/institution/students-at-risk?threshold=40",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["threshold"] == 40
        
    def test_institution_analytics_forbidden_for_student(self, student_token):
        """Institution analytics should be forbidden for students"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/institution/overview",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403


class TestAnalyticsStudent:
    """Test student predictive analytics endpoints"""
    
    def test_get_student_predictive(self, student_token):
        """GET /api/analytics/student/predictive - returns student prediction"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/student/predictive",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify structure
        assert "prediction" in data
        assert "section_analysis" in data
        assert "weak_areas" in data
        assert "strong_areas" in data
        assert "total_practice_time" in data
        assert "generated_at" in data
        
        # Verify prediction structure
        pred = data["prediction"]
        assert "probability" in pred
        assert "risk_level" in pred
        assert "factors" in pred
        assert "recommendation" in pred
        
    def test_student_predictive_forbidden_for_institution(self, institution_token):
        """Student predictive should be forbidden for institutions"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/student/predictive",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 403


class TestEmailProviders:
    """Test email provider endpoints"""
    
    def test_get_email_providers(self):
        """GET /api/email/providers - returns list of providers (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/email/providers")
        assert response.status_code == 200
        
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) >= 4  # sendgrid, resend, smtp, mailgun
        
        # Verify provider structure
        provider = data["providers"][0]
        assert "id" in provider
        assert "name" in provider
        assert "description" in provider
        
        # Check expected providers exist
        provider_ids = [p["id"] for p in data["providers"]]
        assert "sendgrid" in provider_ids
        assert "resend" in provider_ids
        assert "smtp" in provider_ids


class TestEmailConfig:
    """Test email configuration endpoints (institution only)"""
    
    def test_get_email_config(self, institution_token):
        """GET /api/email/config - returns email config for institution"""
        response = requests.get(
            f"{BASE_URL}/api/email/config",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should have safe config fields
        assert "provider" in data
        assert "from_email" in data
        assert "from_name" in data
        assert "enabled" in data
        assert "has_credentials" in data
        
    def test_save_email_config(self, institution_token):
        """POST /api/email/config - saves email configuration"""
        config_data = {
            "provider": "sendgrid",
            "from_email": "test@demo-academy.com",
            "from_name": "Demo Academy",
            "enabled": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/email/config",
            headers={"Authorization": f"Bearer {institution_token}"},
            json=config_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        
    def test_email_config_forbidden_for_student(self, student_token):
        """Email config should be forbidden for students"""
        response = requests.get(
            f"{BASE_URL}/api/email/config",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
        
    def test_email_config_forbidden_for_superadmin(self, superadmin_token):
        """Email config should be forbidden for superadmin (institution only)"""
        response = requests.get(
            f"{BASE_URL}/api/email/config",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        assert response.status_code == 403


class TestPricingCalculator:
    """Test pricing calculator endpoint (uses server.py version with num_licenses param)"""
    
    def test_calculate_pricing(self):
        """GET /api/pricing/calculator - calculates total pricing"""
        # Note: server.py version uses num_licenses and ai_tutor_option params
        response = requests.get(
            f"{BASE_URL}/api/pricing/calculator?exam_plan=plan_10&num_licenses=50&ai_tutor_option=basic"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "exam_plan" in data
        assert "volume_tier" in data
        assert "ai_tutor_option" in data
        assert "num_licenses" in data
        assert "price_per_license" in data
        assert "total_order_price" in data
        assert "savings" in data
        
        # Verify calculations make sense
        assert data["num_licenses"] == 50
        assert data["total_order_price"] > 0
        
    def test_calculate_pricing_invalid_plan(self):
        """Calculator should return 400 for invalid plan"""
        response = requests.get(
            f"{BASE_URL}/api/pricing/calculator?exam_plan=invalid_plan&num_licenses=50"
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
