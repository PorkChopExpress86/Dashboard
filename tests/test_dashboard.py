from fastapi.testclient import TestClient
from app.main import app


def test_homepage_renders():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "HomeBrain" in resp.text
    assert "radar-map" in resp.text
