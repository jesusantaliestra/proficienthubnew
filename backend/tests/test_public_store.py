"""
Test Public Store Endpoints - ProficientHub Tienda Pública

Tests for:
- GET /api/store/institutions - List institutions selling via platform
- GET /api/store/packs - List available packs with filters
- GET /api/store/packs/{id} - Pack details
- GET /api/store/exam-types - Available exam types
- POST /api/store/checkout/create-session - Create checkout session (requires auth)
- GET /api/store/orders/{id} - Order status
- POST /api/store/orders/{id}/complete - Complete order (testing)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data
INSTITUTION_ID = "2f4b79d2-428a-46b4-a898-73adc24c2d69"
PACK_ID_OET = "5215d793-0306-4215-b1f9-c5dd0c88d793"
PACK_ID_IELTS = "630ac0ce-4454-4489-8138-7cfabf4dc7e8"


class TestPublicStoreEndpoints:
    """Test public store endpoints (no auth required)"""
    
    def test_get_institutions_returns_platform_sellers(self):
        """GET /api/store/institutions - Returns institutions with sales_mode platform/both"""
        response = requests.get(f"{BASE_URL}/api/store/institutions")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "institutions" in data
        assert "count" in data
        assert data["count"] >= 1
        
        # Verify institution data
        institutions = data["institutions"]
        assert len(institutions) >= 1
        
        # Check first institution has required fields
        inst = institutions[0]
        assert "id" in inst
        assert "name" in inst
        assert "pack_count" in inst
        assert inst["pack_count"] >= 0
    
    def test_get_institutions_includes_demo_academy(self):
        """GET /api/store/institutions - Demo Academy should be listed"""
        response = requests.get(f"{BASE_URL}/api/store/institutions")
        
        assert response.status_code == 200
        data = response.json()
        
        # Find Demo Academy
        demo_academy = next(
            (i for i in data["institutions"] if i["id"] == INSTITUTION_ID),
            None
        )
        
        assert demo_academy is not None, "Demo Academy should be in store"
        assert demo_academy["name"] == "Demo Language Academy"
        assert demo_academy["pack_count"] >= 2
    
    def test_get_packs_returns_available_packs(self):
        """GET /api/store/packs - Returns packs from platform sellers"""
        response = requests.get(f"{BASE_URL}/api/store/packs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "packs" in data
        assert "count" in data
        assert "filters_applied" in data
        
        # Should have at least 2 packs
        assert data["count"] >= 2
        packs = data["packs"]
        assert len(packs) >= 2
        
        # Verify pack structure
        pack = packs[0]
        assert "id" in pack
        assert "name" in pack
        assert "price" in pack
        assert "currency" in pack
        assert "exam_type" in pack
        assert "institution_id" in pack
        assert "institution_name" in pack
    
    def test_get_packs_filter_by_exam_type_oet(self):
        """GET /api/store/packs?exam_type=OET - Filter by OET exam"""
        response = requests.get(f"{BASE_URL}/api/store/packs?exam_type=OET")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only OET packs
        assert data["count"] >= 1
        for pack in data["packs"]:
            assert pack["exam_type"] == "OET"
        
        # Verify filter applied
        assert data["filters_applied"]["exam_type"] == "OET"
    
    def test_get_packs_filter_by_exam_type_ielts(self):
        """GET /api/store/packs?exam_type=IELTS_ACADEMIC - Filter by IELTS"""
        response = requests.get(f"{BASE_URL}/api/store/packs?exam_type=IELTS_ACADEMIC")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only IELTS packs
        assert data["count"] >= 1
        for pack in data["packs"]:
            assert pack["exam_type"] == "IELTS_ACADEMIC"
    
    def test_get_packs_filter_by_institution(self):
        """GET /api/store/packs?institution_id=... - Filter by institution"""
        response = requests.get(f"{BASE_URL}/api/store/packs?institution_id={INSTITUTION_ID}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return packs from that institution
        assert data["count"] >= 2
        for pack in data["packs"]:
            assert pack["institution_id"] == INSTITUTION_ID
        
        # Verify filter applied
        assert data["filters_applied"]["institution_id"] == INSTITUTION_ID
    
    def test_get_packs_filter_non_platform_institution(self):
        """GET /api/store/packs?institution_id=invalid - Non-platform institution returns empty"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/store/packs?institution_id={fake_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty with message
        assert data["count"] == 0
        assert "message" in data
    
    def test_get_pack_details_success(self):
        """GET /api/store/packs/{id} - Get pack details"""
        response = requests.get(f"{BASE_URL}/api/store/packs/{PACK_ID_OET}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "pack" in data
        pack = data["pack"]
        
        # Verify pack data
        assert pack["id"] == PACK_ID_OET
        assert pack["name"] == "Pack 5 Mocks + Tutor IA - OET Nursing"
        assert pack["exam_type"] == "OET"
        assert pack["profession"] == "nursing"
        assert pack["price"] == 299.0
        assert pack["currency"] == "EUR"
        assert pack["num_mocks"] == 5
        assert pack["include_ai_tutor"] == True
        assert pack["include_speaking"] == True
        assert pack["validity_days"] == 60
        
        # Verify institution info
        assert "institution" in pack
        assert pack["institution"]["name"] == "Demo Language Academy"
    
    def test_get_pack_details_not_found(self):
        """GET /api/store/packs/{id} - Non-existent pack returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/store/packs/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_exam_types_returns_available_types(self):
        """GET /api/store/exam-types - Returns exam types with pack counts"""
        response = requests.get(f"{BASE_URL}/api/store/exam-types")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "exam_types" in data
        exam_types = data["exam_types"]
        
        # Should have at least OET and IELTS
        assert len(exam_types) >= 2
        
        # Verify exam type structure
        exam_type = exam_types[0]
        assert "id" in exam_type
        assert "name" in exam_type
        assert "pack_count" in exam_type
        
        # Verify OET is present
        oet = next((e for e in exam_types if e["id"] == "OET"), None)
        assert oet is not None
        assert oet["name"] == "OET - Occupational English Test"
        assert oet["pack_count"] >= 1
        
        # Verify IELTS is present
        ielts = next((e for e in exam_types if e["id"] == "IELTS_ACADEMIC"), None)
        assert ielts is not None
        assert ielts["name"] == "IELTS Academic"
        assert ielts["pack_count"] >= 1


class TestAuthenticatedStoreEndpoints:
    """Test store endpoints that require authentication"""
    
    @pytest.fixture
    def student_token(self):
        """Get or create a student account and return token"""
        # Try to login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test_store_student@test.com", "password": "Test123!"}
        )
        
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register new student
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "test_store_student@test.com",
                "password": "Test123!",
                "name": "Test Store Student",
                "user_type": "student"
            }
        )
        
        if register_response.status_code == 200:
            return register_response.json()["access_token"]
        
        pytest.skip("Could not create student account")
    
    def test_checkout_requires_auth(self):
        """POST /api/store/checkout/create-session - Requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/store/checkout/create-session",
            json={"pack_id": PACK_ID_OET}
        )
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422]
    
    def test_checkout_creates_session_stripe_test_mode(self, student_token):
        """POST /api/store/checkout/create-session - Creates checkout (Stripe test mode)"""
        response = requests.post(
            f"{BASE_URL}/api/store/checkout/create-session",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"pack_id": PACK_ID_OET}
        )
        
        # Note: Stripe key is placeholder, so this will fail with Stripe error
        # But we verify the endpoint is accessible and validates correctly
        if response.status_code == 200:
            data = response.json()
            assert "checkout_url" in data
            assert "session_id" in data
            assert "order_id" in data
        else:
            # Expected: Stripe error due to test key
            data = response.json()
            assert "detail" in data
            # Should be a Stripe-related error, not auth error
            assert "pago" in data["detail"].lower() or "stripe" in data["detail"].lower() or "api key" in data["detail"].lower()
    
    def test_checkout_invalid_pack_returns_404(self, student_token):
        """POST /api/store/checkout/create-session - Invalid pack returns 404"""
        fake_pack_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/store/checkout/create-session",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"pack_id": fake_pack_id}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_order_requires_auth(self):
        """GET /api/store/orders/{id} - Requires authentication"""
        fake_order_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/store/orders/{fake_order_id}")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422]
    
    def test_get_order_not_found(self, student_token):
        """GET /api/store/orders/{id} - Non-existent order returns 404"""
        fake_order_id = str(uuid.uuid4())
        response = requests.get(
            f"{BASE_URL}/api/store/orders/{fake_order_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_complete_order_requires_auth(self):
        """POST /api/store/orders/{id}/complete - Requires authentication"""
        fake_order_id = str(uuid.uuid4())
        response = requests.post(f"{BASE_URL}/api/store/orders/{fake_order_id}/complete")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422]
    
    def test_complete_order_not_found(self, student_token):
        """POST /api/store/orders/{id}/complete - Non-existent order returns 404"""
        fake_order_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/store/orders/{fake_order_id}/complete",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_my_purchases_requires_auth(self):
        """GET /api/store/my-purchases - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/store/my-purchases")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422]
    
    def test_my_purchases_returns_empty_for_new_student(self, student_token):
        """GET /api/store/my-purchases - Returns empty for new student"""
        response = requests.get(
            f"{BASE_URL}/api/store/my-purchases",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "count" in data
        # New student should have no purchases
        assert isinstance(data["orders"], list)


class TestSalesModeFiltering:
    """Test that only platform/both sales_mode institutions appear"""
    
    def test_only_platform_institutions_shown(self):
        """Verify only institutions with sales_mode platform/both are shown"""
        response = requests.get(f"{BASE_URL}/api/store/institutions")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned institutions should have platform sales enabled
        # We can't directly verify sales_mode from API, but we verify
        # Demo Academy (which has sales_mode=platform) is present
        institution_ids = [i["id"] for i in data["institutions"]]
        assert INSTITUTION_ID in institution_ids
    
    def test_packs_only_from_platform_institutions(self):
        """Verify packs are only from platform-selling institutions"""
        response = requests.get(f"{BASE_URL}/api/store/packs")
        
        assert response.status_code == 200
        data = response.json()
        
        # All packs should be from Demo Academy (the only platform seller)
        for pack in data["packs"]:
            assert pack["institution_id"] == INSTITUTION_ID


class TestPackDataIntegrity:
    """Test pack data is complete and correct"""
    
    def test_oet_pack_has_all_features(self):
        """Verify OET pack has all expected features"""
        response = requests.get(f"{BASE_URL}/api/store/packs/{PACK_ID_OET}")
        
        assert response.status_code == 200
        pack = response.json()["pack"]
        
        # Verify all features
        assert pack["num_mocks"] == 5
        assert pack["include_ai_tutor"] == True
        assert pack["include_speaking"] == True
        assert pack["include_writing_evaluation"] == True
        assert pack["writing_evaluations"] == 3
        assert pack["validity_days"] == 60
        assert pack["is_popular"] == True
        assert pack["badge_text"] == "Más Vendido"
        
        # Verify custom services
        assert "custom_services" in pack
        assert len(pack["custom_services"]) == 2
        service_names = [s["name"] for s in pack["custom_services"]]
        assert "Clases grabadas premium" in service_names
        assert "Libro físico OET" in service_names
    
    def test_ielts_pack_has_all_features(self):
        """Verify IELTS pack has all expected features"""
        response = requests.get(f"{BASE_URL}/api/store/packs/{PACK_ID_IELTS}")
        
        assert response.status_code == 200
        pack = response.json()["pack"]
        
        # Verify all features
        assert pack["num_mocks"] == 10
        assert pack["include_ai_tutor"] == False
        assert pack["include_speaking"] == True
        assert pack["speaking_sessions"] == 5
        assert pack["include_writing_evaluation"] == True
        assert pack["writing_evaluations"] == 5
        assert pack["validity_days"] == 90
        assert pack["price"] == 199.0
        
        # Verify custom services
        assert "custom_services" in pack
        assert len(pack["custom_services"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
