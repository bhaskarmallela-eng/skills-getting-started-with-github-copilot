"""
Tests for signup endpoint in the FastAPI application.
"""

import pytest


def test_signup_success(client, reset_activities):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up" in data["message"]
    
    # Verify student was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_already_registered(client, reset_activities):
    """Test signup fails when student is already registered."""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "Already signed up" in data["detail"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup fails when activity doesn't exist."""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_activity_full(client, reset_activities):
    """Test signup fails when activity is at max capacity."""
    # Add students until activity is full
    for i in range(1, 11):  # 10 more students (12 max, already 2)
        email = f"student{i}@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
    
    # Try to add one more (should fail)
    response = client.post(
        "/activities/Chess%20Club/signup?email=extra@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"].lower()


def test_signup_with_spaces_in_activity_name(client, reset_activities):
    """Test signup with activity names containing spaces."""
    response = client.post(
        "/activities/Programming%20Class/signup?email=newcoder@mergington.edu"
    )
    assert response.status_code == 200
    
    # Verify student was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newcoder@mergington.edu" in activities["Programming Class"]["participants"]


def test_signup_multiple_activities(client, reset_activities):
    """Test that a student can sign up for multiple activities."""
    email = "multistudent@mergington.edu"
    
    # Sign up for first activity
    response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Sign up for second activity
    response2 = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert response2.status_code == 200
    
    # Verify student is in both
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Programming Class"]["participants"]
