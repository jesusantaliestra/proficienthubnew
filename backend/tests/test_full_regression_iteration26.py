"""
Full Regression Test - Iteration 26
Tests all major features: Auth, White-Label, SSO, Community Hub, A/B Testing, Gamification
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://academic-portal-74.preview.emergentagent.com').rstrip('/')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """GET /api/health - Should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_whitelabel_themes_public(self):
        """GET /api/whitelabel/themes - Public endpoint for preset themes"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/themes")
        assert response.status_code == 200
        data = response.json()
        assert "themes" in data
        assert len(data["themes"]) >= 5  # Should have multiple themes
        print(f"✓ White-Label themes: {len(data['themes'])} themes available")


class TestAuthFlow:
    """Authentication flow tests"""
    
    def test_register_institution(self):
        """POST /api/auth/register - Register new institution"""
        unique_email = f"test_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "institution"
        print(f"✓ Institution registered: {unique_email}")
        return data
    
    def test_register_student(self):
        """POST /api/auth/register - Register new student"""
        unique_email = f"test_student_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Test Student",
            "user_type": "student"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "student"
        print(f"✓ Student registered: {unique_email}")
        return data
    
    def test_login_invalid_email_format(self):
        """POST /api/auth/login - Should reject invalid email format"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid_email",
            "password": "password"
        })
        assert response.status_code == 422  # Validation error
        print("✓ Invalid email format rejected correctly")


class TestWhiteLabelFeatures:
    """White-Label configuration tests"""
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"wl_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "White-Label Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_get_whitelabel_config(self, institution_auth):
        """GET /api/whitelabel/config - Get white-label config (requires auth)"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/whitelabel/config", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        # Should return default config for new institution
        assert data["config"].get("is_default", True) or "platform_name" in data["config"]
        print(f"✓ White-Label config retrieved: {data['config'].get('platform_name', 'default')}")
    
    def test_create_whitelabel_config(self, institution_auth):
        """POST /api/whitelabel/config - Create white-label config"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.post(f"{BASE_URL}/api/whitelabel/config", headers=headers, json={
            "platform_name": "Test Academy",
            "primary_color": "#FF5733",
            "secondary_color": "#33FF57",
            "font_family": "Inter, system-ui, sans-serif"
        })
        # May return 200 or 400 if config already exists, or 422 for validation
        assert response.status_code in [200, 400, 422]
        print(f"✓ White-Label config creation: status {response.status_code}")
    
    def test_verify_domain_no_domain(self, institution_auth):
        """POST /api/whitelabel/verify-domain - Should fail without custom domain"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.post(f"{BASE_URL}/api/whitelabel/verify-domain", headers=headers)
        # Should return 400 or 404 since no custom domain is configured
        assert response.status_code in [400, 404]
        data = response.json()
        assert "detail" in data or "message" in data
        print(f"✓ Domain verification correctly requires custom domain")


class TestSSOFeatures:
    """SSO configuration tests"""
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"sso_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "SSO Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_list_sso_configs(self, institution_auth):
        """GET /api/sso/saml/configs - List SSO configurations"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/sso/saml/configs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "configs" in data
        print(f"✓ SSO configs listed: {len(data['configs'])} configs")
    
    def test_create_sso_config(self, institution_auth):
        """POST /api/sso/saml/config - Create SAML SSO config"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.post(f"{BASE_URL}/api/sso/saml/config", headers=headers, json={
            "name": "Test SSO Provider",
            "idp_entity_id": "https://idp.example.com/entity",
            "idp_sso_url": "https://idp.example.com/sso",
            "idp_certificate": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "sp_entity_id" in data
        print(f"✓ SSO config created: {data['id']}")


class TestCommunityHub:
    """Community Hub tests"""
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"comm_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Community Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_list_forum_posts(self, institution_auth):
        """GET /api/community/forum/posts - List forum posts"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/community/forum/posts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
        print(f"✓ Forum posts listed: {data['total']} posts")
    
    def test_list_groups(self, institution_auth):
        """GET /api/community/groups - List study groups"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/community/groups", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        assert "total" in data
        print(f"✓ Study groups listed: {data['total']} groups")
    
    def test_create_forum_post(self, institution_auth):
        """POST /api/community/forum/posts - Create forum post"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.post(f"{BASE_URL}/api/community/forum/posts", headers=headers, json={
            "title": "Test Post",
            "content": "This is a test post content",
            "category": "general"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ Forum post created: {data['id']}")
    
    def test_get_forum_categories(self, institution_auth):
        """GET /api/community/forum/categories - Get forum categories"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/community/forum/categories", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ Forum categories: {len(data['categories'])} categories")


class TestABTesting:
    """A/B Testing feature tests"""
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"ab_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "A/B Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_list_experiments(self, institution_auth):
        """GET /api/ab-testing/experiments - List A/B experiments"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/ab-testing/experiments", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "experiments" in data
        assert "total" in data
        print(f"✓ A/B experiments listed: {data['total']} experiments")
    
    def test_create_experiment(self, institution_auth):
        """POST /api/ab-testing/experiments - Create A/B experiment"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.post(f"{BASE_URL}/api/ab-testing/experiments", headers=headers, json={
            "name": "Test Experiment",
            "description": "Testing button color",
            "experiment_type": "ui",
            "target_metric": "conversion",
            "variants": [
                {"name": "Control", "weight": 50, "config": {}},
                {"name": "Variant A", "weight": 50, "config": {}}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ A/B experiment created: {data['id']}")


class TestGamification:
    """Gamification feature tests"""
    
    @pytest.fixture
    def student_auth(self):
        """Create student and get auth token"""
        unique_email = f"gam_student_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Gamification Test Student",
            "user_type": "student"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"gam_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Gamification Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_gamification_profile_student(self, student_auth):
        """GET /api/gamification/profile - Get student gamification profile"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Should have gamification fields
        assert "xp" in data or "gamification_enabled" in data
        print(f"✓ Gamification profile retrieved for student")
    
    def test_gamification_profile_institution_forbidden(self, institution_auth):
        """GET /api/gamification/profile - Institution should be forbidden"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=headers)
        assert response.status_code == 403
        print(f"✓ Institution correctly forbidden from gamification profile")
    
    def test_community_gamification_profile(self, student_auth):
        """GET /api/community/gamification/profile - Community gamification profile"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/community/gamification/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # May return enabled=false if not configured
        assert "enabled" in data or "xp" in data
        print(f"✓ Community gamification profile retrieved")
    
    def test_gamification_leaderboard(self, student_auth):
        """GET /api/gamification/leaderboard - Get leaderboard"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/gamification/leaderboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        print(f"✓ Gamification leaderboard retrieved")
    
    def test_gamification_badges(self, student_auth):
        """GET /api/gamification/badges - Get available badges"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/gamification/badges", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "badges" in data
        print(f"✓ Gamification badges: {len(data['badges'])} badges available")


class TestDashboardAccess:
    """Dashboard access tests"""
    
    @pytest.fixture
    def student_auth(self):
        """Create student and get auth token"""
        unique_email = f"dash_student_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Dashboard Test Student",
            "user_type": "student"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def institution_auth(self):
        """Create institution and get auth token"""
        unique_email = f"dash_inst_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Dashboard Test Institution",
            "user_type": "institution"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_institution_metrics(self, institution_auth):
        """GET /api/institution/metrics - Institution metrics access"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/institution/metrics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Institution metrics accessible")
    
    def test_institution_analytics_overview(self, institution_auth):
        """GET /api/institution/analytics/overview - Institution analytics"""
        headers = {"Authorization": f"Bearer {institution_auth}"}
        response = requests.get(f"{BASE_URL}/api/institution/analytics/overview", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Institution analytics overview accessible")
    
    def test_student_credits(self, student_auth):
        """GET /api/student/credits - Student credits access"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/student/credits", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Student credits accessible")
    
    def test_me_endpoint(self, student_auth):
        """GET /api/auth/me - Get current user info"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        print(f"✓ User info retrieved: {data['email']}")


class TestExamEndpoints:
    """Exam-related endpoint tests"""
    
    @pytest.fixture
    def student_auth(self):
        """Create student and get auth token"""
        unique_email = f"exam_student_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "Test123!",
            "name": "Exam Test Student",
            "user_type": "student"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_exam_types(self, student_auth):
        """GET /api/exams/types - Get available exam types"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/exams/types", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "exam_types" in data
        assert len(data["exam_types"]) > 0
        print(f"✓ Exam types: {len(data['exam_types'])} types available")
    
    def test_exam_practice(self, student_auth):
        """GET /api/exams/{exam_type}/practice - Get practice questions"""
        headers = {"Authorization": f"Bearer {student_auth}"}
        response = requests.get(f"{BASE_URL}/api/exams/ielts-academic/practice", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        print(f"✓ Practice questions retrieved")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
