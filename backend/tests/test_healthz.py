"""
Tests for the /healthz endpoint.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

from main import app

client = TestClient(app)


def test_healthz_ok_without_redis():
    """Test healthz returns ok status when no REDIS_URL is set."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("core.database.check_database_health", return_value=True):
            response = client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["db"] == "healthy"
            assert data["redis"] == "unknown"
            assert "version" in data
            assert "timestamp" in data


def test_healthz_degraded_when_db_unhealthy():
    """Test healthz returns degraded status when DB is unhealthy."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("core.database.check_database_health", return_value=False):
            response = client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["db"] == "unhealthy"
            assert data["redis"] == "unknown"
            assert "version" in data
            assert "timestamp" in data


def test_healthz_with_redis_url():
    """Test healthz with REDIS_URL set - should report redis as healthy or unhealthy."""
    with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
        with patch("core.database.check_database_health", return_value=True):
            # Mock redis import and connection
            with patch("redis.from_url") as mock_redis:
                mock_redis_instance = MagicMock()
                mock_redis_instance.ping.return_value = True
                mock_redis.return_value = mock_redis_instance

                response = client.get("/healthz")

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["db"] == "healthy"
                assert data["redis"] == "healthy"
                assert "version" in data
                assert "timestamp" in data


def test_healthz_with_redis_url_unhealthy():
    """Test healthz with REDIS_URL set but Redis connection fails."""
    with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
        with patch("core.database.check_database_health", return_value=True):
            # Mock redis import and connection failure
            with patch("redis.from_url") as mock_redis:
                mock_redis_instance = MagicMock()
                mock_redis_instance.ping.side_effect = Exception("Connection failed")
                mock_redis.return_value = mock_redis_instance

                response = client.get("/healthz")

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "degraded"
                assert data["db"] == "healthy"
                assert data["redis"] == "unhealthy"
                assert "version" in data
                assert "timestamp" in data


def test_healthz_with_redis_import_error():
    """Test healthz when redis module is not available."""
    with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}, clear=True):
        with patch("core.database.check_database_health", return_value=True):
            # Mock redis import failure by patching the import in the _redis_state function
            with patch("main._redis_state") as mock_redis_state:
                mock_redis_state.return_value = "unhealthy"
                response = client.get("/healthz")

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "degraded"
                assert data["db"] == "healthy"
                assert data["redis"] == "unhealthy"
                assert "version" in data
                assert "timestamp" in data


def test_healthz_with_version_env():
    """Test healthz includes version from RELEASE_VERSION env var."""
    with patch.dict(os.environ, {"RELEASE_VERSION": "1.2.3"}, clear=True):
        with patch("core.database.check_database_health", return_value=True):
            response = client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["version"] == "1.2.3"
