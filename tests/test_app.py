from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_all_activity_data(client):
    # Arrange
    expected_activities = deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "student@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "UnknownClub"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "student@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "UnknownClub"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"