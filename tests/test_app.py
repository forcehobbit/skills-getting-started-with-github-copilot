import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Test Activity": {
            "description": "An activity for tests",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activities = {
        "Test Activity": {
            "description": "An activity for tests",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["student@example.com"],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Test Activity"
    }
    assert app_module.activities["Test Activity"]["participants"] == [
        "student@example.com",
        email,
    ]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    # Arrange
    path = "/activities/Test Activity/signup"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        "/activities/Test Activity/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Test Activity"
    }
    assert app_module.activities["Test Activity"]["participants"] == []


def test_unregister_returns_404_for_nonparticipant(client):
    # Arrange
    email = "not-signed-up@example.com"

    # Act
    response = client.delete(
        "/activities/Test Activity/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_requires_email(client):
    # Arrange
    path = "/activities/Test Activity/participants"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 422