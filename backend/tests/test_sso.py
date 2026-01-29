"""
SSO (SAML 2.0) Backend API Tests
Tests for /api/sso/* endpoints - SAML SSO configuration and authentication
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"
STUDENT_EMAIL = "gamification_test@demo.com"
STUDENT_PASSWORD = "Test123!"


class TestSSOEndpoints:
    """SSO SAML 2.0 endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as institution
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if login_resp.status_code == 200:
            self.institution_token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.institution_token}"})
        else:
            pytest.skip("Institution login failed - skipping SSO tests")
        
        # Store created config IDs for cleanup
        self.created_configs = []
        
        yield
        
        # Cleanup created configs
        for config_id in self.created_configs:
            try:
                self.session.delete(f"{BASE_URL}/api/sso/saml/config/{config_id}")
            except:
                pass
    
    def test_list_sso_configs_empty(self):
        """Test listing SSO configs when none exist"""
        response = self.session.get(f"{BASE_URL}/api/sso/saml/configs")
        assert response.status_code == 200
        data = response.json()
        assert "configs" in data
        assert isinstance(data["configs"], list)
        print("✓ List SSO configs endpoint works")
    
    def test_create_sso_config(self):
        """Test creating a new SSO configuration"""
        payload = {
            "name": "Test Azure AD SSO",
            "idp_entity_id": "https://sts.windows.net/test-tenant-id/",
            "idp_sso_url": "https://login.microsoftonline.com/test-tenant-id/saml2",
            "idp_certificate": "-----BEGIN CERTIFICATE-----\nMIIDpDCCAoygAwIBAgIGAXtest\n-----END CERTIFICATE-----",
            "auto_create_users": True,
            "default_role": "student",
            "allowed_domains": ["testcompany.com"],
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sso/saml/config", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "sp_entity_id" in data
        assert "sp_acs_url" in data
        assert "sp_slo_url" in data
        assert "message" in data
        
        # Verify SP URLs use correct domain (not localhost)
        assert "localhost" not in data["sp_entity_id"], "SP Entity ID should not use localhost"
        assert "localhost" not in data["sp_acs_url"], "SP ACS URL should not use localhost"
        
        self.created_configs.append(data["id"])
        print(f"✓ SSO config created with ID: {data['id']}")
        return data["id"]
    
    def test_list_sso_configs_after_creation(self):
        """Test listing SSO configs after creating one"""
        # Create a config first
        config_id = self.test_create_sso_config()
        
        response = self.session.get(f"{BASE_URL}/api/sso/saml/configs")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["configs"]) >= 1
        
        # Find our created config
        config = next((c for c in data["configs"] if c["id"] == config_id), None)
        assert config is not None
        assert config["name"] == "Test Azure AD SSO"
        assert config["is_active"] == True
        assert "idp_certificate" not in config  # Certificate should not be exposed in list
        
        print("✓ SSO config appears in list after creation")
    
    def test_get_sso_config_by_id(self):
        """Test getting a specific SSO config by ID"""
        # Create a config first
        config_id = self.test_create_sso_config()
        
        response = self.session.get(f"{BASE_URL}/api/sso/saml/config/{config_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == config_id
        assert data["name"] == "Test Azure AD SSO"
        assert "idp_certificate" in data  # Full details include certificate
        
        print("✓ Get SSO config by ID works")
    
    def test_update_sso_config(self):
        """Test updating an SSO configuration"""
        # Create a config first
        config_id = self.test_create_sso_config()
        
        # Update the config
        update_payload = {
            "is_active": False,
            "default_role": "teacher"
        }
        
        response = self.session.patch(f"{BASE_URL}/api/sso/saml/config/{config_id}", json=update_payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Configuration updated"
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/sso/saml/config/{config_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["is_active"] == False
        assert data["default_role"] == "teacher"
        
        print("✓ SSO config update works")
    
    def test_delete_sso_config(self):
        """Test deleting an SSO configuration"""
        # Create a config first
        create_payload = {
            "name": "Config to Delete",
            "idp_entity_id": "https://delete-test.com/entity",
            "idp_sso_url": "https://delete-test.com/sso",
            "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----",
            "is_active": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/sso/saml/config", json=create_payload)
        config_id = create_response.json()["id"]
        
        # Delete the config
        response = self.session.delete(f"{BASE_URL}/api/sso/saml/config/{config_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Configuration deleted"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/sso/saml/config/{config_id}")
        assert get_response.status_code == 404
        
        print("✓ SSO config deletion works")
    
    def test_get_sp_metadata_xml(self):
        """Test getting SP metadata XML"""
        # Create a config first
        config_id = self.test_create_sso_config()
        
        response = self.session.get(f"{BASE_URL}/api/sso/metadata/{config_id}")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        
        # Verify XML content
        xml_content = response.text
        assert "EntityDescriptor" in xml_content
        assert "SPSSODescriptor" in xml_content
        assert "AssertionConsumerService" in xml_content
        assert "SingleLogoutService" in xml_content
        assert "ProficientHub" in xml_content
        
        print("✓ SP metadata XML generation works")
    
    def test_sso_login_url_check_available(self):
        """Test checking SSO availability for a domain with SSO configured"""
        # Create a config with specific domain
        config_id = self.test_create_sso_config()
        
        # Check SSO availability for the configured domain
        response = requests.get(f"{BASE_URL}/api/sso/login-url?email=user@testcompany.com")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sso_available"] == True
        assert "provider_name" in data
        assert "login_url" in data
        assert config_id in data["login_url"]
        
        print("✓ SSO availability check works for configured domain")
    
    def test_sso_login_url_check_not_available(self):
        """Test checking SSO availability for a domain without SSO"""
        response = requests.get(f"{BASE_URL}/api/sso/login-url?email=user@randomdomain.xyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sso_available"] == False
        
        print("✓ SSO availability check returns false for non-SSO domain")
    
    def test_sso_analytics(self):
        """Test SSO analytics endpoint"""
        response = self.session.get(f"{BASE_URL}/api/sso/analytics?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "period_days" in data
        assert data["period_days"] == 30
        assert "by_provider" in data
        assert "total_sso_users" in data
        
        print("✓ SSO analytics endpoint works")
    
    def test_saml_login_initiation(self):
        """Test SAML login initiation redirects to IdP"""
        # Create a config first
        config_id = self.test_create_sso_config()
        
        # Test login initiation (should redirect)
        response = requests.get(
            f"{BASE_URL}/api/sso/saml/login/{config_id}",
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # Verify redirect location contains IdP URL and SAMLRequest
        location = response.headers.get("location", "")
        assert "login.microsoftonline.com" in location
        assert "SAMLRequest=" in location
        
        print("✓ SAML login initiation redirects to IdP correctly")
    
    def test_saml_login_inactive_config(self):
        """Test SAML login with inactive config returns 404"""
        # Create and deactivate a config
        config_id = self.test_create_sso_config()
        self.session.patch(f"{BASE_URL}/api/sso/saml/config/{config_id}", json={"is_active": False})
        
        # Try to initiate login
        response = requests.get(
            f"{BASE_URL}/api/sso/saml/login/{config_id}",
            allow_redirects=False
        )
        assert response.status_code == 404
        
        print("✓ SAML login with inactive config returns 404")
    
    def test_saml_login_nonexistent_config(self):
        """Test SAML login with non-existent config returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/sso/saml/login/nonexistent-config-id",
            allow_redirects=False
        )
        assert response.status_code == 404
        
        print("✓ SAML login with non-existent config returns 404")


class TestSSOAuthorization:
    """Test SSO endpoint authorization"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as student (non-institution user)
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        if login_resp.status_code == 200:
            self.student_token = login_resp.json().get("access_token")
        else:
            pytest.skip("Student login failed - skipping authorization tests")
    
    def test_student_cannot_list_sso_configs(self):
        """Test that students cannot list SSO configs"""
        response = self.session.get(
            f"{BASE_URL}/api/sso/saml/configs",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        assert response.status_code == 403
        print("✓ Students cannot list SSO configs (403)")
    
    def test_student_cannot_create_sso_config(self):
        """Test that students cannot create SSO configs"""
        payload = {
            "name": "Unauthorized Config",
            "idp_entity_id": "https://test.com/entity",
            "idp_sso_url": "https://test.com/sso",
            "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/sso/saml/config",
            json=payload,
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        assert response.status_code == 403
        print("✓ Students cannot create SSO configs (403)")
    
    def test_student_cannot_view_sso_analytics(self):
        """Test that students cannot view SSO analytics"""
        response = self.session.get(
            f"{BASE_URL}/api/sso/analytics",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        assert response.status_code == 403
        print("✓ Students cannot view SSO analytics (403)")
    
    def test_unauthenticated_cannot_list_configs(self):
        """Test that unauthenticated users cannot list SSO configs"""
        response = requests.get(f"{BASE_URL}/api/sso/saml/configs")
        assert response.status_code in [401, 403]
        print("✓ Unauthenticated users cannot list SSO configs")


class TestSSOPublicEndpoints:
    """Test SSO public endpoints (no auth required)"""
    
    def test_login_url_check_no_auth(self):
        """Test that login-url check works without authentication"""
        response = requests.get(f"{BASE_URL}/api/sso/login-url?email=test@example.com")
        assert response.status_code == 200
        print("✓ SSO login-url check works without auth")
    
    def test_metadata_endpoint_no_auth(self):
        """Test that metadata endpoint works without authentication (for IdP to fetch)"""
        # First create a config as institution
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        token = login_resp.json().get("access_token")
        
        # Create config
        create_resp = session.post(
            f"{BASE_URL}/api/sso/saml/config",
            json={
                "name": "Public Metadata Test",
                "idp_entity_id": "https://test.com/entity",
                "idp_sso_url": "https://test.com/sso",
                "idp_certificate": "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        config_id = create_resp.json()["id"]
        
        # Test metadata without auth
        response = requests.get(f"{BASE_URL}/api/sso/metadata/{config_id}")
        assert response.status_code == 200
        assert "EntityDescriptor" in response.text
        
        # Cleanup
        session.delete(
            f"{BASE_URL}/api/sso/saml/config/{config_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print("✓ SP metadata endpoint works without auth (for IdP)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
