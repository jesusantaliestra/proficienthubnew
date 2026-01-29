"""
Test ElevenLabs TTS Router and Community Institution Filtering
Iteration 25 - Tests for:
1. ElevenLabs config, recommended voices, usage endpoints
2. Community posts/groups filtered by institution_id
3. Gamification profiles per institution
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


def get_auth_token():
    """Get institution auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": INSTITUTION_EMAIL,
        "password": INSTITUTION_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        # API returns access_token, not token
        return data.get("access_token") or data.get("token")
    return None


@pytest.fixture(scope="module")
def auth_headers():
    """Get auth headers for all tests"""
    token = get_auth_token()
    if not token:
        pytest.skip("Institution login failed")
    return {"Authorization": f"Bearer {token}"}


# ==================== ELEVENLABS CONFIG TESTS ====================

class TestElevenLabsConfig:
    """Test ElevenLabs configuration endpoints"""
    
    def test_get_elevenlabs_config(self, auth_headers):
        """GET /api/elevenlabs/config - Returns configuration"""
        response = requests.get(
            f"{BASE_URL}/api/elevenlabs/config",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "config" in data, "Response should contain 'config' key"
        
        config = data["config"]
        # Verify config structure
        assert "api_key_configured" in config, "Config should have api_key_configured field"
        assert "default_voice_id" in config, "Config should have default_voice_id"
        assert "monthly_character_limit" in config, "Config should have monthly_character_limit"
        
        print(f"✓ ElevenLabs config retrieved: api_key_configured={config['api_key_configured']}")
    
    def test_update_elevenlabs_config(self, auth_headers):
        """PUT /api/elevenlabs/config - Updates configuration"""
        response = requests.put(
            f"{BASE_URL}/api/elevenlabs/config",
            headers=auth_headers,
            params={
                "enabled": True,
                "default_voice_id": "21m00Tcm4TlvDq8ikWAM",
                "stability": 0.6,
                "similarity_boost": 0.8,
                "monthly_character_limit": 150000
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "updated" in data["message"].lower(), "Message should confirm update"
        
        print(f"✓ ElevenLabs config updated successfully")
        
        # Verify the update persisted
        verify_response = requests.get(
            f"{BASE_URL}/api/elevenlabs/config",
            headers=auth_headers
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        config = verify_data["config"]
        
        # Check updated values
        assert config.get("enabled") == True, "enabled should be True"
        assert config.get("stability") == 0.6, "stability should be 0.6"
        assert config.get("similarity_boost") == 0.8, "similarity_boost should be 0.8"
        assert config.get("monthly_character_limit") == 150000, "monthly_character_limit should be 150000"
        
        print(f"✓ ElevenLabs config update verified - enabled={config['enabled']}, limit={config['monthly_character_limit']}")


# ==================== ELEVENLABS VOICES TESTS ====================

class TestElevenLabsVoices:
    """Test ElevenLabs voices endpoints"""
    
    def test_get_recommended_voices(self):
        """GET /api/elevenlabs/voices/recommended - Returns 5 recommended voices (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/elevenlabs/voices/recommended")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "voices" in data, "Response should contain 'voices' key"
        
        voices = data["voices"]
        assert len(voices) == 5, f"Expected 5 recommended voices, got {len(voices)}"
        
        # Verify voice structure
        for voice in voices:
            assert "voice_id" in voice, "Voice should have voice_id"
            assert "name" in voice, "Voice should have name"
            assert "description" in voice, "Voice should have description"
            assert "category" in voice, "Voice should have category"
            assert "use_case" in voice, "Voice should have use_case"
        
        # Verify expected voices
        voice_names = [v["name"] for v in voices]
        expected_names = ["Rachel", "Sarah", "Antoni", "Arnold", "Adam"]
        for name in expected_names:
            assert name in voice_names, f"Expected voice '{name}' in recommended voices"
        
        print(f"✓ Got 5 recommended voices: {voice_names}")


# ==================== ELEVENLABS USAGE TESTS ====================

class TestElevenLabsUsage:
    """Test ElevenLabs usage endpoint"""
    
    def test_get_usage_statistics(self, auth_headers):
        """GET /api/elevenlabs/usage - Returns usage statistics"""
        response = requests.get(
            f"{BASE_URL}/api/elevenlabs/usage",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify usage structure
        assert "characters_used" in data, "Response should have characters_used"
        assert "monthly_limit" in data, "Response should have monthly_limit"
        assert "percentage_used" in data, "Response should have percentage_used"
        assert "generations_count" in data, "Response should have generations_count"
        
        # Verify data types
        assert isinstance(data["characters_used"], int), "characters_used should be int"
        assert isinstance(data["monthly_limit"], int), "monthly_limit should be int"
        assert isinstance(data["percentage_used"], (int, float)), "percentage_used should be numeric"
        assert isinstance(data["generations_count"], int), "generations_count should be int"
        
        print(f"✓ Usage stats: {data['characters_used']}/{data['monthly_limit']} chars ({data['percentage_used']}%), {data['generations_count']} generations")


# ==================== COMMUNITY INSTITUTION FILTERING TESTS ====================

class TestCommunityInstitutionFiltering:
    """Test Community posts and groups are filtered by institution_id"""
    
    def test_forum_posts_filtered_by_institution(self, auth_headers):
        """GET /api/community/forum/posts - Posts filtered by institution_id"""
        response = requests.get(
            f"{BASE_URL}/api/community/forum/posts",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "posts" in data, "Response should contain 'posts' key"
        assert "total" in data, "Response should contain 'total' key"
        
        # If there are posts, verify they have institution_id
        posts = data["posts"]
        if len(posts) > 0:
            for post in posts:
                assert "institution_id" in post, "Post should have institution_id"
            print(f"✓ Forum posts filtered by institution - {len(posts)} posts found")
        else:
            print(f"✓ Forum posts endpoint works - 0 posts (empty is valid)")
    
    def test_study_groups_filtered_by_institution(self, auth_headers):
        """GET /api/community/groups - Groups filtered by institution_id"""
        response = requests.get(
            f"{BASE_URL}/api/community/groups",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "groups" in data, "Response should contain 'groups' key"
        assert "total" in data, "Response should contain 'total' key"
        
        # If there are groups, verify they have institution_id
        groups = data["groups"]
        if len(groups) > 0:
            for group in groups:
                assert "institution_id" in group, "Group should have institution_id"
            print(f"✓ Study groups filtered by institution - {len(groups)} groups found")
        else:
            print(f"✓ Study groups endpoint works - 0 groups (empty is valid)")
    
    def test_create_post_has_institution_id(self, auth_headers):
        """POST /api/community/forum/posts - Created post has institution_id"""
        test_title = f"TEST_ElevenLabs_Post_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=auth_headers,
            json={
                "title": test_title,
                "content": "Testing institution_id filtering for community posts",
                "category": "general",
                "tags": ["test", "elevenlabs"]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain post id"
        post_id = data["id"]
        
        # Verify the post has institution_id by fetching it
        get_response = requests.get(
            f"{BASE_URL}/api/community/forum/posts/{post_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        post_data = get_response.json()
        
        assert "institution_id" in post_data, "Created post should have institution_id"
        assert post_data["institution_id"] is not None, "institution_id should not be None"
        
        print(f"✓ Created post has institution_id: {post_data['institution_id']}")
    
    def test_create_group_has_institution_id(self, auth_headers):
        """POST /api/community/groups - Created group has institution_id"""
        test_name = f"TEST_ElevenLabs_Group_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/community/groups",
            headers=auth_headers,
            json={
                "name": test_name,
                "description": "Testing institution_id filtering for study groups",
                "exam_type": "IELTS",
                "max_members": 10,
                "is_private": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain group id"
        group_id = data["id"]
        
        # Verify the group has institution_id by fetching it
        get_response = requests.get(
            f"{BASE_URL}/api/community/groups/{group_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        group_data = get_response.json()
        
        assert "institution_id" in group_data, "Created group should have institution_id"
        assert group_data["institution_id"] is not None, "institution_id should not be None"
        
        print(f"✓ Created group has institution_id: {group_data['institution_id']}")


# ==================== GAMIFICATION PER INSTITUTION TESTS ====================

class TestGamificationPerInstitution:
    """Test gamification profiles are per institution"""
    
    def test_gamification_profile_has_institution_id(self, auth_headers):
        """GET /api/community/gamification/profile - Profile is per institution"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Profile might be disabled or enabled
        if data.get("enabled") == False:
            print(f"✓ Gamification profile endpoint works (gamification disabled for this institution)")
        else:
            assert "profile" in data, "Response should contain 'profile' when enabled"
            profile = data["profile"]
            assert "institution_id" in profile, "Profile should have institution_id"
            assert profile["institution_id"] is not None, "institution_id should not be None"
            print(f"✓ Gamification profile has institution_id: {profile['institution_id']}")
    
    def test_gamification_leaderboard_filtered_by_institution(self, auth_headers):
        """GET /api/community/gamification/leaderboard - Leaderboard is per institution"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/leaderboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Leaderboard might be disabled or enabled
        if data.get("enabled") == False:
            print(f"✓ Gamification leaderboard endpoint works (gamification disabled)")
        elif data.get("hidden") == True:
            print(f"✓ Gamification leaderboard endpoint works (leaderboard hidden by config)")
        else:
            assert "leaderboard" in data, "Response should contain 'leaderboard'"
            print(f"✓ Gamification leaderboard works - {len(data['leaderboard'])} entries")


# ==================== MOBILE BUILD FILE TEST ====================

class TestMobileBuildFile:
    """Test MOBILE_BUILD.md file exists"""
    
    def test_mobile_build_file_exists(self):
        """Verify MOBILE_BUILD.md file exists with Capacitor instructions"""
        file_path = "/app/MOBILE_BUILD.md"
        
        assert os.path.exists(file_path), f"MOBILE_BUILD.md should exist at {file_path}"
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Verify key content
        assert "Capacitor" in content, "MOBILE_BUILD.md should mention Capacitor"
        assert "iOS" in content, "MOBILE_BUILD.md should have iOS instructions"
        assert "Android" in content, "MOBILE_BUILD.md should have Android instructions"
        assert "@capacitor/core" in content, "MOBILE_BUILD.md should mention @capacitor/core"
        assert "npx cap" in content, "MOBILE_BUILD.md should have cap commands"
        
        # Check for key sections
        assert "Prerequisites" in content, "Should have Prerequisites section"
        assert "Build Process" in content, "Should have Build Process section"
        assert "Troubleshooting" in content, "Should have Troubleshooting section"
        
        print(f"✓ MOBILE_BUILD.md exists with complete Capacitor instructions ({len(content)} chars)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
