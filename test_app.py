from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)

def test_send_email_success():
    with patch("backend.main.send_test_email", return_value=True) as mock_send:
        response = client.post("/api/send-email", json={"email": "user@example.com"})
        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "Email sent successfully"}
        mock_send.assert_called_once_with("user@example.com")

def test_send_email_failure():
    with patch("backend.main.send_test_email", return_value=False):
        response = client.post("/api/send-email", json={"email": "user@example.com"})
        assert response.status_code == 500
        assert "Failed to send email" in response.json()["detail"]

def test_send_email_invalid_email():
    response = client.post("/api/send-email", json={"email": "invalid-email"})
    assert response.status_code == 422
