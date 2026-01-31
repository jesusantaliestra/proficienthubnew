"""
Test Suite for Iteration 40 - New Features Testing
- Translation Service (80 languages)
- Avatar Service (Dual system: HeyGen Premium + Economic)
- Institution Sales Config
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://oet-learning.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "demo_academy@test.com"
TEST_PASSWORD = "Demo123!"


class TestTranslationService:
    """Translation Service - 80 languages support"""
    
    def test_get_supported_languages(self):
        """GET /api/translations/languages - Returns 79+ languages"""
        response = requests.get(f"{BASE_URL}/api/translations/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "count" in data
        assert data["count"] >= 79
        # Check some key languages exist
        lang_codes = [l["code"] for l in data["languages"]]
        assert "en" in lang_codes
        assert "es" in lang_codes
        assert "zh" in lang_codes
        assert "fr" in lang_codes
        assert "de" in lang_codes
        print(f"✓ Supported languages: {data['count']}")
    
    def test_get_cached_translations_spanish(self):
        """GET /api/translations/cached/es - Get cached Spanish translations"""
        response = requests.get(f"{BASE_URL}/api/translations/cached/es")
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert data["language"] == "es"
        assert "translations" in data
        print(f"✓ Cached Spanish translations: {data.get('count', len(data.get('translations', {})))} keys")
    
    def test_get_i18n_bundle_french(self):
        """GET /api/translations/i18n/fr - Get i18n bundle for French"""
        response = requests.get(f"{BASE_URL}/api/translations/i18n/fr")
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert data["language"] == "fr"
        assert "translations" in data
        print(f"✓ French i18n bundle loaded")
    
    def test_get_i18n_bundle_english(self):
        """GET /api/translations/i18n/en - English returns empty (source language)"""
        response = requests.get(f"{BASE_URL}/api/translations/i18n/en")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert data["translations"] == {}
        print("✓ English i18n returns empty (source language)")
    
    def test_unsupported_language_cached(self):
        """GET /api/translations/cached/xyz - Unsupported language returns 400"""
        response = requests.get(f"{BASE_URL}/api/translations/cached/xyz")
        assert response.status_code == 400
        print("✓ Unsupported language returns 400")
    
    def test_translate_bulk_endpoint(self):
        """POST /api/translations/translate-bulk - Bulk translation"""
        payload = {
            "target_language": "de",
            "source_texts": {
                "test.hello": "Hello",
                "test.world": "World"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/translations/translate-bulk",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert data["language"] == "de"
        assert "translations" in data
        assert "stats" in data
        print(f"✓ Bulk translation: {data['stats']}")
    
    def test_translate_bulk_empty_texts(self):
        """POST /api/translations/translate-bulk - Empty texts returns 400"""
        payload = {
            "target_language": "fr",
            "source_texts": {}
        }
        response = requests.post(
            f"{BASE_URL}/api/translations/translate-bulk",
            json=payload
        )
        assert response.status_code == 400
        print("✓ Empty texts returns 400")
    
    def test_translate_bulk_unsupported_language(self):
        """POST /api/translations/translate-bulk - Unsupported language returns 400"""
        payload = {
            "target_language": "xyz",
            "source_texts": {"test": "Hello"}
        }
        response = requests.post(
            f"{BASE_URL}/api/translations/translate-bulk",
            json=payload
        )
        assert response.status_code == 400
        print("✓ Unsupported language in bulk returns 400")


class TestAvatarServiceProviders:
    """Avatar Service - Provider endpoints"""
    
    def test_get_providers(self):
        """GET /api/avatar-service/providers - Returns available providers"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        providers = data["providers"]
        assert len(providers) == 2
        
        # Check HeyGen provider
        heygen = next((p for p in providers if p["id"] == "heygen"), None)
        assert heygen is not None
        assert heygen["tier"] == "premium"
        assert "streaming_video" in heygen["features"]
        
        # Check Economic provider
        economic = next((p for p in providers if p["id"] == "economic"), None)
        assert economic is not None
        assert economic["tier"] == "economic"
        assert economic["available"] == True  # Always available via TTS fallback
        print(f"✓ Providers: HeyGen available={heygen['available']}, Economic available={economic['available']}")
    
    def test_get_avatars_all(self):
        """GET /api/avatar-service/avatars - Returns all avatars"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/avatars")
        assert response.status_code == 200
        data = response.json()
        assert "avatars" in data
        assert "count" in data
        assert data["count"] >= 4  # At least economic avatars
        print(f"✓ Total avatars: {data['count']}")
    
    def test_get_avatars_premium_tier(self):
        """GET /api/avatar-service/avatars?tier=premium - Filter premium avatars"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/avatars?tier=premium")
        assert response.status_code == 200
        data = response.json()
        for avatar in data["avatars"]:
            assert avatar["tier"] == "premium"
        print(f"✓ Premium avatars: {data['count']}")
    
    def test_get_avatars_economic_tier(self):
        """GET /api/avatar-service/avatars?tier=economic - Filter economic avatars"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/avatars?tier=economic")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 4  # 4 economic avatars defined
        for avatar in data["avatars"]:
            assert avatar["tier"] == "economic"
        print(f"✓ Economic avatars: {data['count']}")


class TestAvatarServiceOETScenarios:
    """Avatar Service - OET Speaking Scenarios"""
    
    def test_get_oet_scenarios(self):
        """GET /api/avatar-service/oet/scenarios - Returns OET roleplay scenarios"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/oet/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "count" in data
        assert data["count"] >= 3
        
        # Check scenario structure
        scenario = data["scenarios"][0]
        assert "id" in scenario
        assert "title" in scenario
        assert "patient_name" in scenario
        assert "patient_age" in scenario
        assert "setting" in scenario
        assert "situation" in scenario
        assert "tasks" in scenario
        assert "difficulty" in scenario
        print(f"✓ OET scenarios: {data['count']}")
    
    def test_start_roleplay_economic(self):
        """POST /api/avatar-service/oet/start-roleplay - Start economic roleplay session"""
        response = requests.post(
            f"{BASE_URL}/api/avatar-service/oet/start-roleplay?scenario_id=s012b_diabetes&provider=economic"
        )
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "initial_greeting" in data
        
        session = data["session"]
        assert session["provider"] == "economic"
        assert session["tier"] == "economic"
        assert session["connection_type"] == "tts"
        assert session["use_web_speech"] == True
        assert "id" in session
        
        print(f"✓ Economic roleplay session created: {session['id'][:8]}...")
        return session["id"]
    
    def test_start_roleplay_heygen(self):
        """POST /api/avatar-service/oet/start-roleplay - Start HeyGen roleplay session"""
        response = requests.post(
            f"{BASE_URL}/api/avatar-service/oet/start-roleplay?scenario_id=s012b_diabetes&provider=heygen"
        )
        # HeyGen requires API key - may return 400 if not configured
        if response.status_code == 200:
            data = response.json()
            assert data["session"]["provider"] == "heygen"
            assert data["session"]["tier"] == "premium"
            print(f"✓ HeyGen roleplay session created")
        elif response.status_code == 400:
            # Expected if HeyGen not configured
            print("✓ HeyGen not configured (expected)")
        else:
            assert False, f"Unexpected status: {response.status_code}"


class TestAvatarServiceSessions:
    """Avatar Service - Session management"""
    
    @pytest.fixture
    def session_id(self):
        """Create a session for testing"""
        response = requests.post(
            f"{BASE_URL}/api/avatar-service/oet/start-roleplay?scenario_id=s012b_diabetes&provider=economic"
        )
        assert response.status_code == 200
        return response.json()["session"]["id"]
    
    def test_get_session(self, session_id):
        """GET /api/avatar-service/session/{id} - Get session details"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert data["session"]["id"] == session_id
        print(f"✓ Session retrieved: {session_id[:8]}...")
    
    def test_session_chat(self, session_id):
        """POST /api/avatar-service/session/{id}/chat - Send chat message"""
        payload = {
            "session_id": session_id,
            "user_message": "Hello, how are you feeling today?",
            "conversation_history": []
        }
        response = requests.post(
            f"{BASE_URL}/api/avatar-service/session/{session_id}/chat",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "avatar_response" in data
        assert len(data["avatar_response"]) > 0
        print(f"✓ Chat response received: {data['avatar_response'][:50]}...")
    
    def test_delete_session(self, session_id):
        """DELETE /api/avatar-service/session/{id} - End session"""
        response = requests.delete(f"{BASE_URL}/api/avatar-service/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Session ended: {session_id[:8]}...")
    
    def test_get_nonexistent_session(self):
        """GET /api/avatar-service/session/invalid - Returns 404"""
        response = requests.get(f"{BASE_URL}/api/avatar-service/session/nonexistent-id")
        assert response.status_code == 404
        print("✓ Nonexistent session returns 404")


class TestInstitutionSalesConfig:
    """Institution Sales Configuration"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_sales_config(self, auth_headers):
        """GET /api/institution/sales-config - Get sales configuration"""
        response = requests.get(
            f"{BASE_URL}/api/institution/sales-config",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        config = data["config"]
        assert "sales_channel" in config
        assert "api_enabled" in config
        print(f"✓ Sales config: channel={config.get('sales_channel')}, api_enabled={config.get('api_enabled')}")
    
    def test_update_sales_config(self, auth_headers):
        """PUT /api/institution/sales-config - Update sales configuration"""
        payload = {
            "sales_channel": "platform",
            "api_enabled": False,
            "webhook_url": "",
            "payment_methods": ["stripe", "paypal"]
        }
        response = requests.put(
            f"{BASE_URL}/api/institution/sales-config",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ Sales config updated")
    
    def test_generate_api_key(self, auth_headers):
        """POST /api/institution/generate-api-key - Generate new API key"""
        response = requests.post(
            f"{BASE_URL}/api/institution/generate-api-key",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert len(data["api_key"]) > 20
        print(f"✓ API key generated: {data['api_key'][:10]}...")
    
    def test_sales_config_unauthorized(self):
        """GET /api/institution/sales-config - Unauthorized returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/institution/sales-config")
        assert response.status_code in [401, 403, 422]
        print("✓ Unauthorized access blocked")


class TestInstitutionPacksIntegration:
    """Institution Packs - Integration with previous iteration"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_packs(self, auth_headers):
        """GET /api/institution-packs/packs - Verify packs from iteration 39"""
        response = requests.get(
            f"{BASE_URL}/api/institution-packs/packs",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "packs" in data
        print(f"✓ Institution packs: {data.get('count', len(data['packs']))}")
    
    def test_get_exam_types(self):
        """GET /api/institution-packs/exam-types - Verify exam types"""
        response = requests.get(f"{BASE_URL}/api/institution-packs/exam-types")
        assert response.status_code == 200
        data = response.json()
        assert "exam_types" in data
        assert len(data["exam_types"]) >= 10
        print(f"✓ Exam types: {len(data['exam_types'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
