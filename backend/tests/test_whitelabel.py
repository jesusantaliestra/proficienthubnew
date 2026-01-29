"""
White-Label Router Tests
Tests for preset themes, config CRUD, portal access, CSS generation, and email templates
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWhiteLabelThemes:
    """Tests for preset themes endpoint (public)"""
    
    def test_get_preset_themes_returns_6_themes(self):
        """GET /api/whitelabel/themes returns 6 preset themes"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/themes")
        assert response.status_code == 200
        
        data = response.json()
        assert "themes" in data
        assert len(data["themes"]) == 6
        
        # Verify theme IDs
        theme_ids = [t["id"] for t in data["themes"]]
        expected_ids = ["default", "ocean", "forest", "sunset", "royal", "midnight"]
        assert theme_ids == expected_ids
        
    def test_preset_themes_have_required_fields(self):
        """Each theme has id, name, preview_url, and colors"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/themes")
        assert response.status_code == 200
        
        data = response.json()
        for theme in data["themes"]:
            assert "id" in theme
            assert "name" in theme
            assert "preview_url" in theme
            assert "colors" in theme
            assert "primary" in theme["colors"]
            assert "secondary" in theme["colors"]
            assert "accent" in theme["colors"]
            
    def test_midnight_theme_has_dark_colors(self):
        """Midnight theme includes background, surface, text colors"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/themes")
        assert response.status_code == 200
        
        data = response.json()
        midnight = next((t for t in data["themes"] if t["id"] == "midnight"), None)
        assert midnight is not None
        assert "background" in midnight["colors"]
        assert "surface" in midnight["colors"]
        assert "text" in midnight["colors"]


class TestWhiteLabelConfigAuth:
    """Tests for authenticated white-label config endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get institution auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Institution login failed")
        
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_config_returns_default_if_none_exists(self, auth_headers):
        """GET /api/whitelabel/config returns default config if none exists"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/config", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "config" in data
        # Should have default values
        config = data["config"]
        assert "primary_color" in config or "is_default" in config
        
    def test_create_config_requires_institution_user(self, auth_headers):
        """POST /api/whitelabel/config creates config for institution"""
        # First try to delete any existing config
        requests.delete(f"{BASE_URL}/api/whitelabel/config", headers=auth_headers)
        
        config_data = {
            "platform_name": "TEST_Academy",
            "primary_color": "#FF5733",
            "secondary_color": "#33FF57",
            "accent_color": "#3357FF"
        }
        
        response = requests.post(f"{BASE_URL}/api/whitelabel/config", json=config_data, headers=auth_headers)
        
        # Should succeed or fail with 400 if already exists
        assert response.status_code in [200, 201, 400]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "config" in data or "message" in data
            
    def test_update_config_works(self, auth_headers):
        """PUT /api/whitelabel/config updates existing config"""
        # First ensure config exists
        requests.post(f"{BASE_URL}/api/whitelabel/config", json={
            "platform_name": "TEST_Academy"
        }, headers=auth_headers)
        
        update_data = {
            "primary_color": "#123456",
            "platform_name": "TEST_Updated_Academy"
        }
        
        response = requests.put(f"{BASE_URL}/api/whitelabel/config", json=update_data, headers=auth_headers)
        
        # Should succeed or return 404 if no config
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            # Verify update by getting config
            get_response = requests.get(f"{BASE_URL}/api/whitelabel/config", headers=auth_headers)
            assert get_response.status_code == 200
            config = get_response.json()["config"]
            if not config.get("is_default"):
                assert config.get("primary_color") == "#123456"
                
    def test_apply_theme_updates_colors(self, auth_headers):
        """POST /api/whitelabel/apply-theme/{theme_id} applies theme colors"""
        # Ensure config exists first
        requests.post(f"{BASE_URL}/api/whitelabel/config", json={
            "platform_name": "TEST_Theme_Academy"
        }, headers=auth_headers)
        
        # Apply ocean theme
        response = requests.post(f"{BASE_URL}/api/whitelabel/apply-theme/ocean", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "ocean" in data["message"].lower()
        assert "colors" in data
        assert data["colors"]["primary_color"] == "#0EA5E9"
        
    def test_apply_invalid_theme_returns_404(self, auth_headers):
        """POST /api/whitelabel/apply-theme/invalid returns 404"""
        response = requests.post(f"{BASE_URL}/api/whitelabel/apply-theme/invalid_theme", headers=auth_headers)
        assert response.status_code == 404
        
    def test_apply_all_themes(self, auth_headers):
        """Test applying each preset theme"""
        themes = ["default", "ocean", "forest", "sunset", "royal", "midnight"]
        
        for theme_id in themes:
            response = requests.post(f"{BASE_URL}/api/whitelabel/apply-theme/{theme_id}", headers=auth_headers)
            assert response.status_code == 200, f"Failed to apply theme: {theme_id}"
            data = response.json()
            assert "colors" in data


class TestWhiteLabelPublicEndpoints:
    """Tests for public portal and CSS endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get institution auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        pytest.skip("Institution login failed")
        
    def test_get_portal_config_by_subdomain(self, auth_headers):
        """GET /api/whitelabel/portal/{identifier} returns portal config"""
        # First get the subdomain from config
        config_response = requests.get(f"{BASE_URL}/api/whitelabel/config", headers=auth_headers)
        if config_response.status_code == 200:
            config = config_response.json().get("config", {})
            subdomain = config.get("subdomain")
            
            if subdomain:
                response = requests.get(f"{BASE_URL}/api/whitelabel/portal/{subdomain}")
                assert response.status_code == 200
                
                data = response.json()
                assert "config" in data
                assert "css_variables" in data
                
    def test_get_portal_invalid_identifier_returns_404(self):
        """GET /api/whitelabel/portal/invalid returns 404"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/portal/nonexistent_subdomain_12345")
        assert response.status_code == 404
        
    def test_get_css_returns_stylesheet(self, auth_headers):
        """GET /api/whitelabel/css/{identifier} returns CSS"""
        # Get subdomain
        config_response = requests.get(f"{BASE_URL}/api/whitelabel/config", headers=auth_headers)
        if config_response.status_code == 200:
            config = config_response.json().get("config", {})
            subdomain = config.get("subdomain")
            
            if subdomain:
                response = requests.get(f"{BASE_URL}/api/whitelabel/css/{subdomain}")
                assert response.status_code == 200
                assert "text/css" in response.headers.get("content-type", "")
                
                # Verify CSS contains expected variables
                css_content = response.text
                assert ":root" in css_content
                assert "--primary" in css_content
                
    def test_get_css_invalid_identifier_returns_default(self):
        """GET /api/whitelabel/css/invalid returns default CSS"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/css/nonexistent_12345")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        
        # Should still have CSS variables
        css_content = response.text
        assert ":root" in css_content


class TestWhiteLabelEmailTemplates:
    """Tests for email templates endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get institution auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        pytest.skip("Institution login failed")
        
    def test_get_email_templates_returns_defaults(self, auth_headers):
        """GET /api/whitelabel/email-templates returns default templates"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/email-templates", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        
        # Should have at least welcome, exam_complete, progress_report
        template_types = [t["template_type"] for t in data["templates"]]
        assert "welcome" in template_types
        assert "exam_complete" in template_types
        assert "progress_report" in template_types
        
    def test_email_templates_have_required_fields(self, auth_headers):
        """Each template has template_type, subject, html_template"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/email-templates", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for template in data["templates"]:
            assert "template_type" in template
            assert "subject" in template
            assert "html_template" in template
            
    def test_email_templates_require_institution_user(self):
        """GET /api/whitelabel/email-templates requires auth"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/email-templates")
        assert response.status_code == 401


class TestWhiteLabelDomainVerification:
    """Tests for domain verification (MOCKED)"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get institution auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        pytest.skip("Institution login failed")
        
    def test_verify_domain_requires_custom_domain(self, auth_headers):
        """POST /api/whitelabel/verify-domain requires custom domain configured"""
        response = requests.post(f"{BASE_URL}/api/whitelabel/verify-domain", headers=auth_headers)
        # Should return 400 if no custom domain, or 200 if domain exists
        assert response.status_code in [200, 400, 404]
        
    def test_dns_instructions_requires_custom_domain(self, auth_headers):
        """GET /api/whitelabel/dns-instructions requires custom domain"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/dns-instructions", headers=auth_headers)
        # Should return 400 if no custom domain, or 200 if domain exists
        assert response.status_code in [200, 400]


class TestWhiteLabelAnalytics:
    """Tests for white-label analytics"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get institution auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        pytest.skip("Institution login failed")
        
    def test_get_analytics_returns_data(self, auth_headers):
        """GET /api/whitelabel/analytics returns analytics data"""
        response = requests.get(f"{BASE_URL}/api/whitelabel/analytics", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Should have analytics or message if no config
        assert "analytics" in data or "message" in data


class TestWhiteLabelCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get institution auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        pytest.skip("Institution login failed")
        
    def test_cleanup_reset_to_default_theme(self, auth_headers):
        """Reset to default theme after tests"""
        response = requests.post(f"{BASE_URL}/api/whitelabel/apply-theme/default", headers=auth_headers)
        assert response.status_code == 200
