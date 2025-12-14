"""
Tests for the Mergington High School API
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, os.path.join(Path(__file__).parent.parent, "src"))

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "marcus@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    yield
    # Reset again after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that getting activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200(self, client, reset_activities):
        """Test that signup returns 200 status code"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds a participant to the activity"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post("/activities/NonExistent%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_returns_400(self, client, reset_activities):
        """Test that signing up twice returns 400 error"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]


class TestRemoveFromActivity:
    """Tests for POST /activities/{activity_name}/remove endpoint"""
    
    def test_remove_returns_200(self, client, reset_activities):
        """Test that remove returns 200 status code"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess%20Club/remove?email={email}")
        assert response.status_code == 200
    
    def test_remove_removes_participant(self, client, reset_activities):
        """Test that remove removes a participant from the activity"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess%20Club/remove?email={email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_remove_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that removing from nonexistent activity returns 404"""
        response = client.post("/activities/NonExistent%20Club/remove?email=michael@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant_returns_400(self, client, reset_activities):
        """Test that removing non-registered participant returns 400"""
        response = client.post("/activities/Chess%20Club/remove?email=nonexistent@mergington.edu")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_remove_returns_success_message(self, client, reset_activities):
        """Test that remove returns a success message"""
        response = client.post("/activities/Chess%20Club/remove?email=michael@mergington.edu")
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
