"""
Test Suite for Institution Custom Packs API
Tests: CRUD operations, duplicate, public packs, purchase, and sales analytics
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestInstitutionCustomPacksAPI:
    """Test suite for Institution Custom Packs endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def institution_id(self, auth_token):
        """Get institution ID from auth"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        return data.get("id") or data.get("institution_id")
    
    # =============================================
    # Reference Data Tests
    # =============================================
    
    def test_get_exam_types(self, auth_headers):
        """Test GET /api/institution-packs/exam-types - Get supported exam types"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/exam-types",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify exam types structure
        assert "exam_types" in data
        exam_types = data["exam_types"]
        assert len(exam_types) >= 10, "Should have at least 10 exam types"
        
        # Verify OET is present with professions
        oet = next((e for e in exam_types if e["id"] == "OET"), None)
        assert oet is not None, "OET exam type should exist"
        assert oet["has_professions"] == True
        
        # Verify IELTS types
        ielts_academic = next((e for e in exam_types if e["id"] == "IELTS_ACADEMIC"), None)
        assert ielts_academic is not None
        assert ielts_academic["has_professions"] == False
        
        print(f"✓ Found {len(exam_types)} exam types")
    
    def test_get_oet_professions(self, auth_headers):
        """Test GET /api/institution-packs/oet-professions - Get OET professions"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/oet-professions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify professions structure
        assert "professions" in data
        professions = data["professions"]
        assert len(professions) == 12, "Should have 12 OET professions"
        
        # Verify nursing profession
        nursing = next((p for p in professions if p["id"] == "nursing"), None)
        assert nursing is not None
        assert nursing["name"] == "Enfermería"
        assert nursing["name_en"] == "Nursing"
        
        print(f"✓ Found {len(professions)} OET professions")
    
    # =============================================
    # Pack CRUD Tests
    # =============================================
    
    def test_create_pack(self, auth_headers):
        """Test POST /api/institution-packs/packs - Create custom pack"""
        pack_data = {
            "name": f"TEST_Pack_{uuid.uuid4().hex[:8]}",
            "description": "Test pack for automated testing",
            "exam_type": "OET",
            "profession": "nursing",
            "num_mocks": 5,
            "include_ai_tutor": True,
            "ai_tutor_minutes": -1,  # Unlimited
            "include_speaking": True,
            "speaking_sessions": 10,
            "include_writing_evaluation": True,
            "writing_evaluations": 5,
            "validity_days": 60,
            "custom_services": [
                {"name": "Clases grabadas", "description": "10 horas de video", "type": "service"},
                {"name": "Libro digital", "description": "PDF completo", "type": "material"}
            ],
            "price": 149.99,
            "currency": "EUR",
            "is_popular": True,
            "badge_text": "Mejor Valor",
            "sort_order": 1
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs",
            headers=auth_headers,
            json=pack_data
        )
        
        assert response.status_code == 200, f"Create pack failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert "pack" in data
        pack = data["pack"]
        
        # Verify pack data
        assert pack["name"] == pack_data["name"]
        assert pack["exam_type"] == "OET"
        assert pack["profession"] == "nursing"
        assert pack["num_mocks"] == 5
        assert pack["include_ai_tutor"] == True
        assert pack["ai_tutor_minutes"] == -1
        assert pack["price"] == 149.99
        assert pack["currency"] == "EUR"
        assert len(pack["custom_services"]) == 2
        assert "id" in pack
        
        print(f"✓ Created pack: {pack['name']} with ID: {pack['id']}")
        
        # Store pack ID for later tests
        TestInstitutionCustomPacksAPI.created_pack_id = pack["id"]
        return pack["id"]
    
    def test_get_institution_packs(self, auth_headers):
        """Test GET /api/institution-packs/packs - List institution packs"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "packs" in data
        assert "count" in data
        
        packs = data["packs"]
        assert isinstance(packs, list)
        assert data["count"] == len(packs)
        
        # Verify at least one pack exists (from previous test or seed data)
        assert len(packs) >= 1, "Should have at least 1 pack"
        
        # Verify pack structure
        if packs:
            pack = packs[0]
            assert "id" in pack
            assert "name" in pack
            assert "exam_type" in pack
            assert "price" in pack
        
        print(f"✓ Found {len(packs)} institution packs")
    
    def test_get_single_pack(self, auth_headers):
        """Test GET /api/institution-packs/packs/{pack_id} - Get specific pack"""
        # Use the pack created in previous test
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'created_pack_id', None)
        if not pack_id:
            pytest.skip("No pack ID from previous test")
        
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pack" in data
        pack = data["pack"]
        assert pack["id"] == pack_id
        
        print(f"✓ Retrieved pack: {pack['name']}")
    
    def test_update_pack(self, auth_headers):
        """Test PUT /api/institution-packs/packs/{pack_id} - Update pack"""
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'created_pack_id', None)
        if not pack_id:
            pytest.skip("No pack ID from previous test")
        
        updated_data = {
            "name": f"TEST_Updated_Pack_{uuid.uuid4().hex[:8]}",
            "description": "Updated description",
            "exam_type": "OET",
            "profession": "nursing",
            "num_mocks": 10,  # Changed from 5
            "include_ai_tutor": True,
            "ai_tutor_minutes": 120,  # Changed from unlimited
            "include_speaking": True,
            "speaking_sessions": 15,  # Changed from 10
            "include_writing_evaluation": True,
            "writing_evaluations": 10,  # Changed from 5
            "validity_days": 90,  # Changed from 60
            "custom_services": [
                {"name": "Clases grabadas", "description": "20 horas de video", "type": "service"}
            ],
            "price": 199.99,  # Changed from 149.99
            "currency": "EUR",
            "is_popular": False,  # Changed
            "badge_text": "Premium",  # Changed
            "sort_order": 2
        }
        
        response = requests.put(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers,
            json=updated_data
        )
        
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        assert "message" in data
        
        # Verify update by fetching the pack
        get_response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        pack = get_response.json()["pack"]
        
        assert pack["num_mocks"] == 10
        assert pack["price"] == 199.99
        assert pack["validity_days"] == 90
        
        print(f"✓ Updated pack: {pack['name']}")
    
    def test_duplicate_pack(self, auth_headers):
        """Test POST /api/institution-packs/packs/{pack_id}/duplicate - Duplicate pack"""
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'created_pack_id', None)
        if not pack_id:
            pytest.skip("No pack ID from previous test")
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}/duplicate",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Duplicate failed: {response.text}"
        data = response.json()
        
        assert "message" in data
        assert "pack" in data
        
        duplicated_pack = data["pack"]
        assert duplicated_pack["id"] != pack_id, "Duplicated pack should have new ID"
        assert "(Copia)" in duplicated_pack["name"], "Duplicated pack name should contain '(Copia)'"
        assert duplicated_pack["total_sold"] == 0, "Duplicated pack should have 0 sales"
        
        print(f"✓ Duplicated pack: {duplicated_pack['name']}")
        
        # Store for cleanup
        TestInstitutionCustomPacksAPI.duplicated_pack_id = duplicated_pack["id"]
    
    # =============================================
    # Public Packs Tests
    # =============================================
    
    def test_get_public_packs(self, auth_headers, institution_id):
        """Test GET /api/institution-packs/public/{institution_id} - Get public packs"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/public/{institution_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "institution_name" in data
        assert "packs" in data
        assert "count" in data
        
        packs = data["packs"]
        assert isinstance(packs, list)
        
        # Verify packs don't expose institution_id
        for pack in packs:
            assert "institution_id" not in pack, "Public packs should not expose institution_id"
        
        print(f"✓ Found {len(packs)} public packs for institution")
    
    def test_get_public_packs_by_exam_type(self, auth_headers, institution_id):
        """Test GET /api/institution-packs/public/{institution_id}/by-exam/{exam_type}"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/public/{institution_id}/by-exam/OET"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "exam_type" in data
        assert data["exam_type"] == "OET"
        assert "packs" in data
        
        # All returned packs should be OET type
        for pack in data["packs"]:
            assert pack["exam_type"] == "OET"
        
        print(f"✓ Found {len(data['packs'])} OET packs")
    
    # =============================================
    # Sales Analytics Tests
    # =============================================
    
    def test_get_institution_sales(self, auth_headers):
        """Test GET /api/institution-packs/institution-sales - Get sales analytics"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/institution-sales?days=30",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "period_days" in data
        assert data["period_days"] == 30
        assert "total_sales" in data
        assert "total_revenue" in data
        assert "by_pack" in data
        assert "recent_sales" in data
        
        assert isinstance(data["total_sales"], int)
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["by_pack"], dict)
        assert isinstance(data["recent_sales"], list)
        
        print(f"✓ Sales analytics: {data['total_sales']} sales, {data['total_revenue']} EUR revenue")
    
    # =============================================
    # Purchase Tests
    # =============================================
    
    def test_purchase_pack(self, auth_headers):
        """Test POST /api/institution-packs/purchase - Purchase pack for student"""
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'created_pack_id', None)
        if not pack_id:
            pytest.skip("No pack ID from previous test")
        
        purchase_data = {
            "pack_id": pack_id,
            "student_email": f"test_student_{uuid.uuid4().hex[:8]}@test.com",
            "student_name": "Test Student",
            "payment_reference": f"PAY-{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/purchase",
            headers=auth_headers,
            json=purchase_data
        )
        
        assert response.status_code == 200, f"Purchase failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data["success"] == True
        assert "access_id" in data
        assert "student_id" in data
        assert "is_new_student" in data
        assert "expires_at" in data
        assert "message" in data
        
        # New student should get temp password
        if data["is_new_student"]:
            assert "temp_password" in data
            assert data["temp_password"] is not None
        
        print(f"✓ Purchase successful: access_id={data['access_id']}, new_student={data['is_new_student']}")
    
    def test_purchase_pack_invalid_pack(self, auth_headers):
        """Test purchase with invalid pack ID"""
        purchase_data = {
            "pack_id": "invalid-pack-id-12345",
            "student_email": "test@test.com",
            "student_name": "Test Student"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/purchase",
            headers=auth_headers,
            json=purchase_data
        )
        
        assert response.status_code == 404
        print("✓ Invalid pack ID returns 404")
    
    # =============================================
    # Validation Tests
    # =============================================
    
    def test_create_pack_invalid_exam_type(self, auth_headers):
        """Test create pack with invalid exam type"""
        pack_data = {
            "name": "Invalid Pack",
            "exam_type": "INVALID_EXAM",
            "price": 99.99
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs",
            headers=auth_headers,
            json=pack_data
        )
        
        assert response.status_code == 400
        print("✓ Invalid exam type returns 400")
    
    def test_create_pack_invalid_profession(self, auth_headers):
        """Test create OET pack with invalid profession"""
        pack_data = {
            "name": "Invalid Profession Pack",
            "exam_type": "OET",
            "profession": "invalid_profession",
            "price": 99.99
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs",
            headers=auth_headers,
            json=pack_data
        )
        
        assert response.status_code == 400
        print("✓ Invalid profession returns 400")
    
    def test_get_pack_not_found(self, auth_headers):
        """Test get pack with non-existent ID"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs/non-existent-pack-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        print("✓ Non-existent pack returns 404")
    
    def test_update_pack_not_found(self, auth_headers):
        """Test update pack with non-existent ID"""
        pack_data = {
            "name": "Updated Pack",
            "exam_type": "OET",
            "price": 99.99
        }
        
        response = requests.put(
            f"{BASE_URL}/api/institution-packs/packs/non-existent-pack-id",
            headers=auth_headers,
            json=pack_data
        )
        
        assert response.status_code == 404
        print("✓ Update non-existent pack returns 404")
    
    def test_duplicate_pack_not_found(self, auth_headers):
        """Test duplicate pack with non-existent ID"""
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs/non-existent-pack-id/duplicate",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        print("✓ Duplicate non-existent pack returns 404")
    
    # =============================================
    # Authorization Tests
    # =============================================
    
    def test_get_packs_unauthorized(self):
        """Test get packs without auth token"""
        response = requests.get(f"{BASE_URL}/api/institution-packs/packs")
        
        # Should return 401 or 403
        assert response.status_code in [401, 403]
        print("✓ Unauthorized request returns 401/403")
    
    def test_create_pack_unauthorized(self):
        """Test create pack without auth token"""
        pack_data = {
            "name": "Unauthorized Pack",
            "exam_type": "OET",
            "price": 99.99
        }
        
        response = requests.post(
            f"{BASE_URL}/api/institution-packs/packs",
            json=pack_data
        )
        
        assert response.status_code in [401, 403]
        print("✓ Unauthorized create returns 401/403")
    
    # =============================================
    # Cleanup Tests
    # =============================================
    
    def test_delete_pack(self, auth_headers):
        """Test DELETE /api/institution-packs/packs/{pack_id} - Delete pack"""
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'created_pack_id', None)
        if not pack_id:
            pytest.skip("No pack ID from previous test")
        
        response = requests.delete(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Delete failed: {response.text}"
        data = response.json()
        assert "message" in data
        
        # Verify pack is deleted (soft delete)
        get_response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404, "Deleted pack should return 404"
        
        print(f"✓ Deleted pack: {pack_id}")
    
    def test_delete_duplicated_pack(self, auth_headers):
        """Cleanup: Delete duplicated pack"""
        pack_id = getattr(TestInstitutionCustomPacksAPI, 'duplicated_pack_id', None)
        if not pack_id:
            pytest.skip("No duplicated pack ID")
        
        response = requests.delete(
            f"{BASE_URL}/api/institution-packs/packs/{pack_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        print(f"✓ Cleaned up duplicated pack: {pack_id}")
    
    def test_delete_pack_not_found(self, auth_headers):
        """Test delete pack with non-existent ID"""
        response = requests.delete(
            f"{BASE_URL}/api/institution-packs/packs/non-existent-pack-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        print("✓ Delete non-existent pack returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
