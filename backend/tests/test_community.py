"""
Community Hub Backend Tests
Tests Forum posts, replies, study groups, and community features
"""
import pytest
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load frontend .env for REACT_APP_BACKEND_URL
load_dotenv(Path('/app/frontend/.env'))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://proficient-hub-1.preview.emergentagent.com').rstrip('/')

class TestCommunityForum:
    """Forum endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_forum_categories(self):
        """GET /api/community/forum/categories - Returns forum categories"""
        response = requests.get(f"{BASE_URL}/api/community/forum/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 6
        
        # Verify category structure
        category_ids = [c["id"] for c in data["categories"]]
        assert "general" in category_ids
        assert "exam_tips" in category_ids
        assert "study_partners" in category_ids
        assert "resources" in category_ids
        assert "questions" in category_ids
        assert "success_stories" in category_ids
    
    def test_get_forum_posts(self):
        """GET /api/community/forum/posts - Returns posts list"""
        response = requests.get(
            f"{BASE_URL}/api/community/forum/posts?sort_by=created_at",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "posts" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["posts"], list)
    
    def test_create_forum_post(self):
        """POST /api/community/forum/posts - Creates a new post"""
        post_data = {
            "title": "TEST_Forum Post Title",
            "content": "This is test content for the forum post",
            "category": "general",
            "tags": ["test", "pytest"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json=post_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["message"] == "Post created successfully"
        
        # Verify post was created by fetching it
        post_id = data["id"]
        get_response = requests.get(
            f"{BASE_URL}/api/community/forum/posts/{post_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        post = get_response.json()
        assert post["title"] == post_data["title"]
        assert post["content"] == post_data["content"]
        assert post["category"] == post_data["category"]
    
    def test_like_forum_post(self):
        """POST /api/community/forum/posts/{id}/like - Like a post"""
        # First create a post
        post_data = {
            "title": "TEST_Post to Like",
            "content": "Testing like functionality",
            "category": "general",
            "tags": []
        }
        create_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json=post_data
        )
        post_id = create_response.json()["id"]
        
        # Like the post
        like_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/like",
            headers=self.headers
        )
        assert like_response.status_code == 200
        
        data = like_response.json()
        assert data["action"] == "liked"
        assert data["likes"] == 1
        
        # Unlike the post
        unlike_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/like",
            headers=self.headers
        )
        assert unlike_response.status_code == 200
        assert unlike_response.json()["action"] == "unliked"
    
    def test_reply_to_post(self):
        """POST /api/community/forum/posts/{id}/reply - Reply to a post"""
        # First create a post
        post_data = {
            "title": "TEST_Post for Reply",
            "content": "Testing reply functionality",
            "category": "questions",
            "tags": []
        }
        create_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json=post_data
        )
        post_id = create_response.json()["id"]
        
        # Reply to the post
        reply_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/reply",
            headers=self.headers,
            json={"content": "This is a test reply"}
        )
        assert reply_response.status_code == 200
        
        data = reply_response.json()
        assert "id" in data
        assert data["message"] == "Reply posted"


class TestStudyGroups:
    """Study Groups endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_study_groups(self):
        """GET /api/community/groups - Returns groups list"""
        response = requests.get(
            f"{BASE_URL}/api/community/groups",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "groups" in data
        assert "total" in data
        assert isinstance(data["groups"], list)
    
    def test_create_study_group(self):
        """POST /api/community/groups - Creates a new study group"""
        group_data = {
            "name": "TEST_TOEFL Study Group",
            "description": "Preparing for TOEFL together",
            "exam_type": "TOEFL",
            "max_members": 15,
            "is_private": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/community/groups",
            headers=self.headers,
            json=group_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["message"] == "Study group created"
        
        # Verify group was created
        group_id = data["id"]
        get_response = requests.get(
            f"{BASE_URL}/api/community/groups/{group_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        group = get_response.json()
        assert group["name"] == group_data["name"]
        assert group["exam_type"] == group_data["exam_type"]
        assert group["is_member"] == True
        assert group["is_admin"] == True
    
    def test_get_community_stats(self):
        """GET /api/community/stats - Returns community statistics"""
        response = requests.get(
            f"{BASE_URL}/api/community/stats",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_posts" in data
        assert "total_groups" in data
        assert "active_contributors_this_week" in data


class TestWhiteLabelLivePreview:
    """White-Label Live Preview tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_preset_themes(self):
        """GET /api/whitelabel/themes - Returns preset themes"""
        response = requests.get(
            f"{BASE_URL}/api/whitelabel/themes",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "themes" in data
        assert len(data["themes"]) >= 6
        
        # Verify theme structure
        theme_names = [t["name"] for t in data["themes"]]
        assert "Classic" in theme_names
        assert "Ocean Blue" in theme_names
        assert "Forest Green" in theme_names
    
    def test_apply_preset_theme(self):
        """POST /api/whitelabel/apply-theme/{theme_id} - Applies a theme"""
        response = requests.post(
            f"{BASE_URL}/api/whitelabel/apply-theme/ocean",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Ocean" in data["message"]
    
    def test_get_whitelabel_config(self):
        """GET /api/whitelabel/config - Returns white-label config"""
        response = requests.get(
            f"{BASE_URL}/api/whitelabel/config",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "config" in data
        config = data["config"]
        assert "primary_color" in config
        assert "platform_name" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
