"""
Tests for unregister endpoint in the FastAPI application.
"""

import pytest


def test_unregister_success(client, reset_activities):
    """Test successful unregister from an activity."""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    
    # Verify student was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 1


def test_unregister_not_registered(client, reset_activities):
    """Test unregister fails when student is not registered."""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"].lower()


def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister fails when activity doesn't exist."""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_removes_correct_student(client, reset_activities):
    """Test that unregister only removes the specified student."""
    # Get initial state
    initial_response = client.get("/activities")
    initial = initial_response.json()
    initial_count = len(initial["Chess Club"]["participants"])
    
    # Unregister one student
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    # Verify only one was removed and the other remains
    final_response = client.get("/activities")
    final = final_response.json()
    assert len(final["Chess Club"]["participants"]) == initial_count - 1
    assert "michael@mergington.edu" not in final["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in final["Chess Club"]["participants"]


def test_unregister_with_spaces_in_activity_name(client, reset_activities):
    """Test unregister with activity names containing spaces."""
    # First add a student
    client.post("/activities/Programming%20Class/signup?email=testuser@mergington.edu")
    
    # Then unregister them
    response = client.delete(
        "/activities/Programming%20Class/unregister?email=testuser@mergington.edu"
    )
    assert response.status_code == 200
    
    # Verify they were removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "testuser@mergington.edu" not in activities["Programming Class"]["participants"]
