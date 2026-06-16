import copy
import sys
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.app import app, activities

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    signup_path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(signup_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    get_response = client.get("/activities")
    assert email in get_response.json()[activity_name]["participants"]


def test_unregister_participant_removes_participant():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    delete_path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.delete(delete_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    get_response = client.get("/activities")
    assert email not in get_response.json()[activity_name]["participants"]


def test_signup_for_invalid_activity_returns_404():
    # Arrange
    client = TestClient(app)
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"
    signup_path = f"/activities/{quote(invalid_activity)}/signup"

    # Act
    response = client.post(signup_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_invalid_participant_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    delete_path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.delete(delete_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
