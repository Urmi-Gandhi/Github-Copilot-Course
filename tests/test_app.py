from pathlib import Path
import sys

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure email not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # If already present (from previous test run), remove first
        client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email} for {activity}" in resp.json().get("message", "")

    # Confirm present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert f"Unregistered {email} from {activity}" in resp.json().get("message", "")

    # Confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_not_signed_up():
    activity = "Soccer Club"
    email = "not-signed-up@example.com"
    # Ensure not signed up
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/unregister", params={"email": email})

    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400
