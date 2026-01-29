"""
Test file for new routers: A/B Testing, Gamification, Marketplace, Admin
Tests all CRUD operations and critical edge cases for the 4 new routers
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo_academy@test.com"
TEST_PASSWORD = "Demo123!"

# Test experiment ID from main agent context
TEST_EXPERIMENT_ID = "e37a3ed2-d668-45a8-aa42-1f2124a5ae08"


class TestAuthentication:
    """Authentication tests - run first"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self, auth_token):
        """Verify login works and returns token"""
        assert auth_token is not None
        assert len(auth_token) > 0


class TestABTesting:
    """A/B Testing router tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def created_experiment_id(self, auth_headers):
        """Create a test experiment and return its ID"""
        experiment_data = {
            "name": f"TEST_Experiment_{uuid.uuid4().hex[:8]}",
            "description": "Test experiment for automated testing",
            "experiment_type": "pricing",
            "target_metric": "conversion",
            "traffic_percentage": 100,
            "variants": [
                {"name": "Control", "config": {"price": 100}, "weight": 1},
                {"name": "Variant A", "config": {"price": 90}, "weight": 1}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/ab-testing/experiments",
            json=experiment_data,
            headers=auth_headers
        )
        if response.status_code == 200:
            return response.json()["id"]
        return None
    
    def test_create_experiment(self, auth_headers):
        """Test creating a new A/B experiment"""
        experiment_data = {
            "name": f"TEST_Create_Experiment_{uuid.uuid4().hex[:8]}",
            "description": "Test experiment creation",
            "experiment_type": "feature",
            "target_metric": "engagement",
            "traffic_percentage": 50,
            "variants": [
                {"name": "Control", "config": {"feature_enabled": False}, "weight": 1},
                {"name": "Treatment", "config": {"feature_enabled": True}, "weight": 1}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/ab-testing/experiments",
            json=experiment_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Create experiment failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "variants" in data
        assert len(data["variants"]) == 2
        assert data["message"] == "Experiment created successfully"
    
    def test_list_experiments(self, auth_headers):
        """Test listing all experiments"""
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/experiments",
            headers=auth_headers
        )
        assert response.status_code == 200, f"List experiments failed: {response.text}"
        data = response.json()
        assert "experiments" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["experiments"], list)
    
    def test_get_experiment_with_stats(self, auth_headers, created_experiment_id):
        """Test getting experiment details with stats"""
        if not created_experiment_id:
            pytest.skip("No experiment created")
        
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/experiments/{created_experiment_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get experiment failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "variants" in data
        assert "name" in data
        # Check conversion rate calculation
        for variant in data["variants"]:
            assert "conversion_rate" in variant
            assert "impressions" in variant
    
    def test_assign_variant_to_user(self, created_experiment_id):
        """Test assigning a variant to a user (public endpoint)"""
        if not created_experiment_id:
            pytest.skip("No experiment created")
        
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/assign",
            params={
                "experiment_id": created_experiment_id,
                "user_id": f"test_user_{uuid.uuid4().hex[:8]}"
            }
        )
        assert response.status_code == 200, f"Assign variant failed: {response.text}"
        data = response.json()
        assert "variant_id" in data
        assert "variant_name" in data
        assert "config" in data
        assert "in_experiment" in data
    
    def test_track_conversion_event(self, auth_headers, created_experiment_id):
        """Test tracking a conversion event"""
        if not created_experiment_id:
            pytest.skip("No experiment created")
        
        # First get a variant assignment
        assign_response = requests.get(
            f"{BASE_URL}/api/ab-testing/assign",
            params={
                "experiment_id": created_experiment_id,
                "user_id": f"test_user_{uuid.uuid4().hex[:8]}"
            }
        )
        variant_id = assign_response.json()["variant_id"]
        
        # Track conversion
        conversion_data = {
            "experiment_id": created_experiment_id,
            "variant_id": variant_id,
            "event_type": "signup",
            "value": 99.99,
            "metadata": {"source": "test"}
        }
        response = requests.post(
            f"{BASE_URL}/api/ab-testing/convert",
            json=conversion_data
        )
        assert response.status_code == 200, f"Track conversion failed: {response.text}"
        data = response.json()
        assert "event_id" in data
        assert data["message"] == "Conversion tracked"
    
    def test_get_existing_experiment(self, auth_headers):
        """Test getting the pre-existing test experiment"""
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/experiments/{TEST_EXPERIMENT_ID}",
            headers=auth_headers
        )
        # May return 404 if experiment doesn't exist for this user
        assert response.status_code in [200, 404], f"Unexpected error: {response.text}"
    
    def test_assign_variant_invalid_experiment(self):
        """Test assigning variant with invalid experiment ID"""
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/assign",
            params={
                "experiment_id": "invalid-experiment-id",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 404


class TestGamification:
    """Gamification router tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_available_badges(self):
        """Test getting all available badges (15 total)"""
        response = requests.get(f"{BASE_URL}/api/gamification/badges")
        assert response.status_code == 200, f"Get badges failed: {response.text}"
        data = response.json()
        assert "badges" in data
        assert "by_category" in data
        # Verify 15 badges as per requirements
        assert len(data["badges"]) == 15, f"Expected 15 badges, got {len(data['badges'])}"
        # Verify badge structure
        for badge in data["badges"]:
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "icon" in badge
            assert "category" in badge
            assert "points" in badge
            assert "rarity" in badge
    
    def test_get_badges_by_category(self):
        """Test badges are properly categorized"""
        response = requests.get(f"{BASE_URL}/api/gamification/badges")
        assert response.status_code == 200
        data = response.json()
        categories = data["by_category"]
        # Check expected categories exist
        expected_categories = ["progress", "achievement", "streak", "skill", "social"]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
    
    def test_get_my_badges(self, auth_headers):
        """Test getting user's earned badges"""
        response = requests.get(
            f"{BASE_URL}/api/gamification/badges/my",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get my badges failed: {response.text}"
        data = response.json()
        assert "earned" in data
        assert "in_progress" in data
        assert "total_badges" in data
        assert "total_points" in data
        assert isinstance(data["earned"], list)
        assert isinstance(data["in_progress"], list)
    
    def test_get_leaderboard(self, auth_headers):
        """Test getting leaderboard"""
        response = requests.get(
            f"{BASE_URL}/api/gamification/leaderboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get leaderboard failed: {response.text}"
        data = response.json()
        assert "leaderboard" in data
        assert "timeframe" in data
        assert isinstance(data["leaderboard"], list)
    
    def test_get_leaderboard_timeframes(self, auth_headers):
        """Test leaderboard with different timeframes"""
        for timeframe in ["daily", "weekly", "monthly", "all_time"]:
            response = requests.get(
                f"{BASE_URL}/api/gamification/leaderboard",
                params={"timeframe": timeframe},
                headers=auth_headers
            )
            assert response.status_code == 200, f"Leaderboard {timeframe} failed: {response.text}"
            data = response.json()
            assert data["timeframe"] == timeframe
    
    def test_get_streak(self, auth_headers):
        """Test getting user's streak"""
        response = requests.get(
            f"{BASE_URL}/api/gamification/streak",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get streak failed: {response.text}"
        data = response.json()
        assert "current_streak" in data
        assert "longest_streak" in data
        assert "last_activity" in data or data.get("last_activity") is None
        assert "streak_frozen" in data
    
    def test_record_streak_activity(self, auth_headers):
        """Test recording streak activity"""
        response = requests.post(
            f"{BASE_URL}/api/gamification/streak/activity",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Record activity failed: {response.text}"
        data = response.json()
        assert "current_streak" in data
        assert "message" in data
    
    def test_get_points(self, auth_headers):
        """Test getting user's points breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/gamification/points",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get points failed: {response.text}"
        data = response.json()
        assert "total_points" in data
        assert "badge_points" in data
        assert "activity_points" in data
        assert "badges_earned" in data
    
    def test_check_and_award_badges(self, auth_headers):
        """Test checking for new badges"""
        response = requests.post(
            f"{BASE_URL}/api/gamification/badges/check",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Check badges failed: {response.text}"
        data = response.json()
        assert "newly_earned" in data
        assert "points_earned" in data


class TestMarketplace:
    """Marketplace router tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def created_listing_id(self, auth_headers):
        """Create a test listing and return its ID"""
        listing_data = {
            "title": f"TEST_Listing_{uuid.uuid4().hex[:8]}",
            "description": "Test listing for automated testing",
            "category": "exam_packs",
            "exam_type": "IELTS",
            "content_type": "exam_pack",
            "price": 49.99,
            "currency": "USD",
            "tags": ["test", "ielts"]
        }
        response = requests.post(
            f"{BASE_URL}/api/marketplace/listings",
            json=listing_data,
            headers=auth_headers
        )
        if response.status_code == 200:
            return response.json()["id"]
        return None
    
    def test_list_categories(self):
        """Test getting marketplace categories"""
        response = requests.get(f"{BASE_URL}/api/marketplace/categories")
        assert response.status_code == 200, f"Get categories failed: {response.text}"
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 6  # 6 categories defined
        # Verify category structure
        for cat in data["categories"]:
            assert "id" in cat
            assert "name" in cat
            assert "icon" in cat
    
    def test_create_listing(self, auth_headers):
        """Test creating a marketplace listing"""
        listing_data = {
            "title": f"TEST_Create_Listing_{uuid.uuid4().hex[:8]}",
            "description": "Test listing creation",
            "category": "study_materials",
            "exam_type": "TOEFL",
            "content_type": "material",
            "price": 29.99,
            "currency": "USD",
            "preview_content": "Sample preview content",
            "tags": ["test", "toefl", "study"]
        }
        response = requests.post(
            f"{BASE_URL}/api/marketplace/listings",
            json=listing_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Create listing failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["message"] == "Listing created successfully"
    
    def test_get_listings(self):
        """Test getting marketplace listings"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings")
        assert response.status_code == 200, f"Get listings failed: {response.text}"
        data = response.json()
        assert "listings" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["listings"], list)
    
    def test_get_listings_with_filters(self):
        """Test getting listings with filters"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/listings",
            params={
                "category": "exam_packs",
                "min_price": 10,
                "max_price": 100
            }
        )
        assert response.status_code == 200, f"Get filtered listings failed: {response.text}"
    
    def test_get_my_listings(self, auth_headers):
        """Test getting user's own listings"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-listings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get my listings failed: {response.text}"
        data = response.json()
        assert "listings" in data
        assert "total" in data
    
    def test_get_specific_listing(self, auth_headers, created_listing_id):
        """Test getting a specific listing"""
        if not created_listing_id:
            pytest.skip("No listing created")
        
        response = requests.get(
            f"{BASE_URL}/api/marketplace/listings/{created_listing_id}"
        )
        assert response.status_code == 200, f"Get listing failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "price" in data
    
    def test_update_listing(self, auth_headers, created_listing_id):
        """Test updating a listing"""
        if not created_listing_id:
            pytest.skip("No listing created")
        
        update_data = {
            "title": f"TEST_Updated_Listing_{uuid.uuid4().hex[:8]}",
            "price": 39.99
        }
        response = requests.put(
            f"{BASE_URL}/api/marketplace/listings/{created_listing_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Update listing failed: {response.text}"
        
        # Verify update persisted
        get_response = requests.get(
            f"{BASE_URL}/api/marketplace/listings/{created_listing_id}"
        )
        assert get_response.status_code == 200
        assert get_response.json()["price"] == 39.99
    
    def test_create_order(self, auth_headers, created_listing_id):
        """Test creating a marketplace order"""
        if not created_listing_id:
            pytest.skip("No listing created")
        
        order_data = {
            "listing_id": created_listing_id,
            "quantity": 1
        }
        response = requests.post(
            f"{BASE_URL}/api/marketplace/orders",
            json=order_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Create order failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "total" in data
    
    def test_get_orders(self, auth_headers):
        """Test getting orders"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/orders",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get orders failed: {response.text}"
        data = response.json()
        assert "orders" in data
        assert "total" in data


class TestAdmin:
    """Admin router tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_admin_settings(self, auth_headers):
        """Test getting admin settings"""
        response = requests.get(
            f"{BASE_URL}/api/admin/settings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get admin settings failed: {response.text}"
    
    def test_update_admin_settings(self, auth_headers):
        """Test updating admin settings"""
        settings = {
            "test_setting": "test_value",
            "notifications_enabled": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/settings",
            json=settings,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Update admin settings failed: {response.text}"
        data = response.json()
        assert data["message"] == "Settings updated"
    
    def test_get_admin_stats(self, auth_headers):
        """Test getting admin dashboard stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get admin stats failed: {response.text}"
        data = response.json()
        assert "total_students" in data
        assert "active_students" in data
        assert "total_exams" in data
        assert "library_items" in data
    
    def test_get_exam_bank(self, auth_headers):
        """Test getting exam bank"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exam-bank",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get exam bank failed: {response.text}"
        data = response.json()
        assert "exams" in data
        assert "total" in data
    
    def test_get_exam_overview(self, auth_headers):
        """Test getting exam overview"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exam-overview",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get exam overview failed: {response.text}"
        data = response.json()
        assert "by_exam_type" in data
    
    def test_get_pricing_analysis(self, auth_headers):
        """Test getting pricing analysis"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pricing-analysis",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get pricing analysis failed: {response.text}"
        data = response.json()
        assert "total_mrr" in data
        assert "total_arr" in data
        assert "total_revenue" in data
        assert "active_subscriptions" in data
    
    def test_trial_requests_forbidden_for_institution(self, auth_headers):
        """Test that trial requests endpoint returns 403 for institution user"""
        response = requests.get(
            f"{BASE_URL}/api/admin/trial-requests",
            headers=auth_headers
        )
        # Institution user should get 403 (super admin only)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestRouterHealth:
    """Test that all new routers respond without 500 errors"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_ab_testing_router_health(self, auth_headers):
        """Test A/B Testing router responds"""
        response = requests.get(
            f"{BASE_URL}/api/ab-testing/experiments",
            headers=auth_headers
        )
        assert response.status_code != 500, f"A/B Testing router returned 500: {response.text}"
    
    def test_gamification_router_health(self):
        """Test Gamification router responds"""
        response = requests.get(f"{BASE_URL}/api/gamification/badges")
        assert response.status_code != 500, f"Gamification router returned 500: {response.text}"
    
    def test_marketplace_router_health(self):
        """Test Marketplace router responds"""
        response = requests.get(f"{BASE_URL}/api/marketplace/categories")
        assert response.status_code != 500, f"Marketplace router returned 500: {response.text}"
    
    def test_admin_router_health(self, auth_headers):
        """Test Admin router responds"""
        response = requests.get(
            f"{BASE_URL}/api/admin/settings",
            headers=auth_headers
        )
        assert response.status_code != 500, f"Admin router returned 500: {response.text}"


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test data after all tests complete"""
    yield
    # Note: In production, we would delete TEST_ prefixed data here
    # For now, we leave test data for debugging purposes
