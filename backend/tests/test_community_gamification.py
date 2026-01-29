"""
Community Gamification Backend Tests
Tests gamification config, profile, leaderboard, badges, and point awarding
"""
import pytest
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load frontend .env for REACT_APP_BACKEND_URL
load_dotenv(Path('/app/frontend/.env'))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCommunityGamificationConfig:
    """Community Gamification Configuration Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as institution and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_gamification_config(self):
        """GET /api/community/gamification/config - Returns config and badges"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/config",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "config" in data
        assert "badges" in data
        
        # Verify config structure
        config = data["config"]
        assert "community_gamification_enabled" in config
        assert "points_per_post" in config
        assert "points_per_reply" in config
        assert "points_per_solution" in config
        assert "points_per_like_received" in config
        assert "points_per_group_created" in config
        assert "points_per_group_joined" in config
        assert "show_contributor_leaderboard" in config
        assert "show_reputation_badges" in config
        assert "weekly_top_contributor_reward" in config
        
        # Verify badges - should have 7 community badges
        badges = data["badges"]
        assert len(badges) == 7
        
        badge_ids = [b["id"] for b in badges]
        assert "first_post" in badge_ids
        assert "helpful_10" in badge_ids
        assert "popular_post" in badge_ids
        assert "community_star" in badge_ids
        assert "group_leader" in badge_ids
        assert "mentor" in badge_ids
        assert "influencer" in badge_ids
    
    def test_update_gamification_config(self):
        """PUT /api/community/gamification/config - Updates settings"""
        config_data = {
            "community_gamification_enabled": True,
            "points_per_post": 15,
            "points_per_reply": 8,
            "points_per_solution": 60,
            "points_per_like_received": 3,
            "points_per_group_created": 30,
            "points_per_group_joined": 10,
            "show_contributor_leaderboard": True,
            "show_reputation_badges": True,
            "weekly_top_contributor_reward": 150
        }
        
        response = requests.put(
            f"{BASE_URL}/api/community/gamification/config",
            headers=self.headers,
            json=config_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Community gamification settings updated"
        
        # Verify config was updated
        get_response = requests.get(
            f"{BASE_URL}/api/community/gamification/config",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        updated_config = get_response.json()["config"]
        assert updated_config["points_per_post"] == 15
        assert updated_config["points_per_reply"] == 8
        assert updated_config["points_per_solution"] == 60
        
        # Reset to default values
        requests.put(
            f"{BASE_URL}/api/community/gamification/config",
            headers=self.headers,
            json={
                "community_gamification_enabled": True,
                "points_per_post": 10,
                "points_per_reply": 5,
                "points_per_solution": 50,
                "points_per_like_received": 2,
                "points_per_group_created": 25,
                "points_per_group_joined": 5,
                "show_contributor_leaderboard": True,
                "show_reputation_badges": True,
                "weekly_top_contributor_reward": 100
            }
        )


class TestCommunityGamificationProfile:
    """Community Gamification Profile Tests"""
    
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
    
    def test_get_gamification_profile(self):
        """GET /api/community/gamification/profile - Returns user profile"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        
        if data["enabled"]:
            assert "profile" in data
            profile = data["profile"]
            assert "user_id" in profile
            assert "reputation" in profile
            assert "posts_count" in profile
            assert "replies_count" in profile
            assert "solutions_count" in profile
            assert "badges" in profile
            assert "rank" in profile


class TestCommunityGamificationLeaderboard:
    """Community Gamification Leaderboard Tests"""
    
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
    
    def test_get_leaderboard(self):
        """GET /api/community/gamification/leaderboard - Returns top contributors"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/leaderboard?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        assert "leaderboard" in data
        
        if data["enabled"] and len(data["leaderboard"]) > 0:
            entry = data["leaderboard"][0]
            assert "user_id" in entry
            assert "reputation" in entry
            assert "name" in entry
            assert "position" in entry
            assert "is_current_user" in entry


class TestCommunityGamificationBadges:
    """Community Gamification Badges Tests"""
    
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
    
    def test_get_available_badges(self):
        """GET /api/community/gamification/badges - Returns all badges"""
        response = requests.get(
            f"{BASE_URL}/api/community/gamification/badges",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "badges" in data
        assert len(data["badges"]) == 7
        
        # Verify badge structure
        for badge in data["badges"]:
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "icon" in badge
            assert "requirement" in badge
            assert "type" in badge


class TestCommunityGamificationPointsAwarding:
    """Tests for automatic point awarding"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and ensure gamification is enabled"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_academy@test.com",
            "password": "Demo123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Ensure gamification is enabled
            requests.put(
                f"{BASE_URL}/api/community/gamification/config",
                headers=self.headers,
                json={
                    "community_gamification_enabled": True,
                    "points_per_post": 10,
                    "points_per_reply": 5,
                    "points_per_solution": 50,
                    "points_per_like_received": 2,
                    "points_per_group_created": 25,
                    "points_per_group_joined": 5,
                    "show_contributor_leaderboard": True,
                    "show_reputation_badges": True,
                    "weekly_top_contributor_reward": 100
                }
            )
        else:
            pytest.skip("Authentication failed")
    
    def test_post_awards_points(self):
        """Creating a post awards points when gamification enabled"""
        # Get initial profile
        profile_before = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        initial_rep = profile_before.get("profile", {}).get("reputation", 0)
        initial_posts = profile_before.get("profile", {}).get("posts_count", 0)
        
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json={
                "title": "TEST_Points Award Post",
                "content": "Testing point awarding",
                "category": "general",
                "tags": []
            }
        )
        assert post_response.status_code == 200
        
        # Check profile after
        profile_after = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        new_rep = profile_after["profile"]["reputation"]
        new_posts = profile_after["profile"]["posts_count"]
        
        # Verify points were awarded (10 points per post)
        assert new_rep >= initial_rep + 10
        assert new_posts == initial_posts + 1
    
    def test_reply_awards_points(self):
        """Creating a reply awards points when gamification enabled"""
        # First create a post
        post_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json={
                "title": "TEST_Post for Reply Points",
                "content": "Testing reply point awarding",
                "category": "general",
                "tags": []
            }
        )
        post_id = post_response.json()["id"]
        
        # Get profile before reply
        profile_before = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        initial_rep = profile_before["profile"]["reputation"]
        initial_replies = profile_before["profile"]["replies_count"]
        
        # Create a reply
        reply_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/reply",
            headers=self.headers,
            json={"content": "Test reply for points"}
        )
        assert reply_response.status_code == 200
        
        # Check profile after
        profile_after = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        new_rep = profile_after["profile"]["reputation"]
        new_replies = profile_after["profile"]["replies_count"]
        
        # Verify points were awarded (5 points per reply)
        assert new_rep >= initial_rep + 5
        assert new_replies == initial_replies + 1
    
    def test_solution_awards_points(self):
        """Marking solution awards points to reply author"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts",
            headers=self.headers,
            json={
                "title": "TEST_Post for Solution Points",
                "content": "Testing solution point awarding",
                "category": "questions",
                "tags": []
            }
        )
        post_id = post_response.json()["id"]
        
        # Create a reply
        reply_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/reply",
            headers=self.headers,
            json={"content": "This is the solution"}
        )
        reply_id = reply_response.json()["id"]
        
        # Get profile before marking solution
        profile_before = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        initial_rep = profile_before["profile"]["reputation"]
        initial_solutions = profile_before["profile"]["solutions_count"]
        
        # Mark as solution
        solution_response = requests.post(
            f"{BASE_URL}/api/community/forum/posts/{post_id}/solve/{reply_id}",
            headers=self.headers
        )
        assert solution_response.status_code == 200
        
        # Check profile after
        profile_after = requests.get(
            f"{BASE_URL}/api/community/gamification/profile",
            headers=self.headers
        ).json()
        
        new_rep = profile_after["profile"]["reputation"]
        new_solutions = profile_after["profile"]["solutions_count"]
        
        # Verify points were awarded (50 points per solution)
        assert new_rep >= initial_rep + 50
        assert new_solutions == initial_solutions + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
