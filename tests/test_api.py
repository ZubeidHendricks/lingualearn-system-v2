from fastapi.testclient import TestClient

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}