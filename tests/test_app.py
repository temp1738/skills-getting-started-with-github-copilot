from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_new_participant():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_fails_when_student_already_signed_up():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_nonexistent_activity_returns_404():
    response = client.post("/activities/Nonexistent%20Activity/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "missing@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
