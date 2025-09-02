from fastapi.testclient import TestClient
from ..router import router


class TestHelloRouter:
    """Test cases for the Hello World tool router."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(router)

    def test_ping_post(self):
        """Test POST /ping endpoint."""
        response = self.client.post("/ping", json={"message": "Test message"})
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Hello! You said: Test message"
        assert data["tool"] == "hello"
        assert data["status"] == "success"
        assert "timestamp" in data

    def test_ping_post_default_message(self):
        """Test POST /ping endpoint with default message."""
        response = self.client.post("/ping", json={})
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Hello! You said: Hello"
        assert data["tool"] == "hello"

    def test_ping_get(self):
        """Test GET /ping endpoint."""
        response = self.client.get("/ping")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Hello from the Hello World tool!"
        assert data["tool"] == "hello"
        assert data["status"] == "success"

    def test_info(self):
        """Test /info endpoint."""
        response = self.client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert data["tool"] == "hello"
        assert data["name"] == "Hello World"
        assert (
            data["description"]
            == "A simple demonstration tool that shows the modular architecture"
        )
        assert data["version"] == "1.0.0"
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0

    def test_config(self):
        """Test /config endpoint."""
        response = self.client.get("/config")
        assert response.status_code == 200

        data = response.json()
        assert data["tool"] == "hello"
        assert data["name"] == "Hello World"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "features" in data
