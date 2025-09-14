from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)


def test_get_users_superuser_me() -> None:
    r = client.get(f"/api/projects/?page=1&pageSize=10")
    rsp = r.json()
    assert r.status_code == 200, rsp
    assert "list" in rsp
    assert "total" in rsp
