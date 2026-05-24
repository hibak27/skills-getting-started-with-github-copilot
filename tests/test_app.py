import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

DEFAULT_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activity_data():
    """Reset in-memory activity state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))


def create_client():
    return TestClient(app)


def test_get_activities_returns_activity_list():
    # Arrange
    client = create_client()

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    client = create_client()
    activity_name = "Chess Club"
    new_email = "tester@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(new_email, safe='') }"

    # Act
    response = client.post(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {new_email} for {activity_name}"

    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert new_email in participants


def test_duplicate_signup_returns_400():
    # Arrange
    client = create_client()
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(existing_email, safe='') }"

    # Act
    response = client.post(url)
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student already signed up"


def test_remove_participant_unregisters_student():
    # Arrange
    client = create_client()
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants/{quote(participant_email, safe='')}"

    # Act
    response = client.delete(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Removed {participant_email} from {activity_name}"

    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert participant_email not in participants


def test_remove_missing_participant_returns_404():
    # Arrange
    client = create_client()
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants/{quote(missing_email, safe='')}"

    # Act
    response = client.delete(url)
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Participant not found"
