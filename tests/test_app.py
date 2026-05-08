"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Sample activities data for testing"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


class TestActivitiesAPI:
    """Test suite for activities API endpoints"""

    def test_get_activities_success(self, client, sample_activities):
        """Test GET /activities returns all activities"""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Check that we get a dictionary
        assert isinstance(data, dict)

        # Check that all expected activities are present
        for activity_name in sample_activities.keys():
            assert activity_name in data

        # Check structure of first activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_root_redirect(self, client):
        """Test GET / redirects to static index"""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        email = "test@mergington.edu"
        activity = "Chess Club"

        response = client.post(f"/activities/{activity}/signup?email={email}")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" in data["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        email = "test@mergington.edu"
        activity = "NonExistentActivity"

        response = client.post(f"/activities/{activity}/signup?email={email}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_prevented(self, client):
        """Test that duplicate signups are prevented"""
        email = "duplicate@mergington.edu"
        activity = "Programming Class"

        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "Student is already signed up" in data["detail"]

    def test_unregistration_success(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"
        activity = "Gym Class"

        # First sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Then unregister
        delete_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity}" in data["message"]

    def test_unregistration_not_signed_up(self, client):
        """Test unregistration when not signed up"""
        email = "notsignedup@mergington.edu"
        activity = "Chess Club"

        response = client.delete(f"/activities/{activity}/signup?email={email}")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Not signed up for this activity" in data["detail"]

    def test_unregistration_activity_not_found(self, client):
        """Test unregistration for non-existent activity"""
        email = "test@mergington.edu"
        activity = "NonExistentActivity"

        response = client.delete(f"/activities/{activity}/signup?email={email}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]