"""
Unit tests for API endpoints.
"""

from unittest.mock import patch


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_health_check_structure(self, client):
        """Test health check response structure."""
        response = client.get("/api/health")
        data = response.json()

        # Should have required fields
        required_fields = ["status", "timestamp"]
        for field in required_fields:
            assert field in data


class TestConfigEndpoint:
    """Test configuration endpoint."""

    def test_get_config(self, client):
        """Test configuration endpoint."""
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()

        assert "api_mode" in data
        assert "default_model" in data
        assert "valid_models" in data
        assert isinstance(data["valid_models"], list)
        assert len(data["valid_models"]) > 0

    def test_get_config_with_env_vars(self, client):
        """Test configuration with environment variables."""
        with patch.dict("os.environ", {"API_MODE": "real", "DEFAULT_MODEL": "gpt-4o"}):
            response = client.get("/api/config")
            data = response.json()

            assert data["api_mode"] == "real"
            assert data["default_model"] == "gpt-4o"


class TestKPIsEndpoint:
    """Test KPIs endpoint."""

    def test_get_kpis(self, client):
        """Test KPIs endpoint."""
        response = client.get("/api/kpis")

        assert response.status_code == 200
        data = response.json()

        assert "jobs_processed" in data
        assert "hours_saved" in data
        assert "avg_edit_min" in data
        assert "export_bundles" in data

        # Check data types
        assert isinstance(data["jobs_processed"], int)
        assert isinstance(data["hours_saved"], (int, float))
        assert isinstance(data["avg_edit_min"], int)
        assert isinstance(data["export_bundles"], int)


class TestJobsEndpoints:
    """Test jobs-related endpoints."""

    def test_get_jobs(self, client):
        """Test get all jobs endpoint."""
        response = client.get("/api/jobs")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Check job structure
        job = data[0]
        required_fields = [
            "id",
            "client",
            "words",
            "status",
            "created_at",
            "source_url",
        ]
        for field in required_fields:
            assert field in job

    def test_get_job_by_id(self, client):
        """Test get job by ID endpoint."""
        # First get all jobs to get a valid ID
        jobs_response = client.get("/api/jobs")
        jobs = jobs_response.json()
        job_id = jobs[0]["id"]

        response = client.get(f"/api/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == job_id
        assert "client" in data
        assert "status" in data

    def test_get_job_by_id_not_found(self, client):
        """Test get job by ID with nonexistent ID."""
        response = client.get("/api/jobs/nonexistent_id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestGenerateEndpoint:
    """Test content generation endpoint."""

    def test_generate_content_success(
        self, client, sample_generate_request, mock_redis
    ):
        """Test successful content generation."""
        response = client.post("/api/generate", json=sample_generate_request)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        required_fields = [
            "job_id",
            "status",
            "variants",
            "token_usage",
            "model",
            "api_mode",
        ]
        for field in required_fields:
            assert field in data

        # Check variants structure
        assert "linkedin" in data["variants"]
        assert "twitter" in data["variants"]
        assert len(data["variants"]["linkedin"]) > 0
        assert len(data["variants"]["twitter"]) > 0

        # Check token usage structure
        token_usage = data["token_usage"]
        assert "input_tokens" in token_usage
        assert "output_tokens" in token_usage
        assert "total_tokens" in token_usage
        assert "total_cost" in token_usage

    def test_generate_content_input_too_short(self, client, mock_redis):
        """Test content generation with input too short."""
        request = {
            "input_text": "Short",
            "channels": ["linkedin"],
            "user_id": "test_user",
        }

        response = client.post("/api/generate", json=request)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "too short" in data["detail"]["message"].lower()

    def test_generate_content_input_too_large(self, client, mock_redis):
        """Test content generation with input too large."""
        large_text = "A" * 150000  # Exceeds character limit
        request = {
            "input_text": large_text,
            "channels": ["linkedin"],
            "user_id": "test_user",
        }

        response = client.post("/api/generate", json=request)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "validation failed" in data["detail"]["error"].lower()

    def test_generate_content_quota_exceeded(
        self, client, sample_generate_request, mock_redis
    ):
        """Test content generation with quota exceeded."""
        # Mock quota check to return False
        with patch("utils.quotas.can_create_job") as mock_can_create:
            mock_can_create.return_value = (False, 10)  # Can't create, at limit

            response = client.post("/api/generate", json=sample_generate_request)

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "quota exceeded" in data["detail"]["error"].lower()

    def test_generate_content_invalid_channels(self, client, mock_redis):
        """Test content generation with invalid channels."""
        request = {
            "input_text": "This is a valid test input that meets the minimum length requirement.",
            "channels": [],  # Empty channels
            "user_id": "test_user",
        }

        response = client.post("/api/generate", json=request)

        # Should still work with empty channels (uses default)
        assert response.status_code == 200

    def test_generate_content_missing_fields(self, client, mock_redis):
        """Test content generation with missing required fields."""
        request = {
            "input_text": "This is a valid test input that meets the minimum length requirement."
            # Missing channels and user_id
        }

        response = client.post("/api/generate", json=request)

        # Should work with defaults
        assert response.status_code == 200


class TestExportEndpoint:
    """Test export endpoint."""

    def test_export_content(self, client):
        """Test content export."""
        request = {
            "job_id": "test_job_123",
            "format": "csv",
            "selected_variants": ["variant_1", "variant_2"],
        }

        response = client.post("/api/export", json=request)

        assert response.status_code == 200
        data = response.json()

        assert "file_url" in data
        assert "filename" in data
        assert data["filename"].endswith(".csv")
        assert "test_job_123" in data["filename"]

    def test_export_content_json_format(self, client):
        """Test content export with JSON format."""
        request = {
            "job_id": "test_job_456",
            "format": "json",
            "selected_variants": ["variant_1"],
        }

        response = client.post("/api/export", json=request)

        assert response.status_code == 200
        data = response.json()

        assert data["filename"].endswith(".json")
        assert "test_job_456" in data["filename"]

    def test_export_content_missing_fields(self, client):
        """Test export with missing fields."""
        request = {
            "job_id": "test_job_789"
            # Missing format and selected_variants
        }

        response = client.post("/api/export", json=request)

        # Should work with defaults
        assert response.status_code == 200
        data = response.json()
        assert data["filename"].endswith(".csv")  # Default format


class TestPresetsEndpoints:
    """Test presets-related endpoints."""

    def test_get_presets(self, client):
        """Test get all presets endpoint."""
        response = client.get("/api/presets")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Check preset structure
        preset = data[0]
        required_fields = ["id", "name", "description", "config"]
        for field in required_fields:
            assert field in preset

    def test_get_preset_by_id(self, client):
        """Test get preset by ID endpoint."""
        # First get all presets to get a valid ID
        presets_response = client.get("/api/presets")
        presets = presets_response.json()
        preset_id = presets[0]["id"]

        response = client.get(f"/api/presets/{preset_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == preset_id
        assert "name" in data
        assert "config" in data

    def test_get_preset_by_id_not_found(self, client):
        """Test get preset by ID with nonexistent ID."""
        response = client.get("/api/presets/nonexistent_id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_create_preset(self, client):
        """Test create preset endpoint."""
        request = {
            "name": "Test Preset",
            "description": "A test preset for unit testing",
            "config": {"tone": "professional", "length": "medium"},
        }

        response = client.post("/api/presets", json=request)

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Test Preset"
        assert data["description"] == "A test preset for unit testing"
        assert data["config"]["tone"] == "professional"
        assert "id" in data

    def test_update_preset(self, client):
        """Test update preset endpoint."""
        # First create a preset
        create_request = {
            "name": "Original Preset",
            "description": "Original description",
            "config": {"tone": "professional"},
        }
        create_response = client.post("/api/presets", json=create_request)
        preset_id = create_response.json()["id"]

        # Update the preset
        update_request = {
            "name": "Updated Preset",
            "description": "Updated description",
            "config": {"tone": "casual"},
        }

        response = client.put(f"/api/presets/{preset_id}", json=update_request)

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Preset"
        assert data["description"] == "Updated description"
        assert data["config"]["tone"] == "casual"

    def test_delete_preset(self, client):
        """Test delete preset endpoint."""
        # First create a preset
        create_request = {
            "name": "To Delete",
            "description": "This will be deleted",
            "config": {"tone": "professional"},
        }
        create_response = client.post("/api/presets", json=create_request)
        preset_id = create_response.json()["id"]

        # Delete the preset
        response = client.delete(f"/api/presets/{preset_id}")

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

        # Verify it's deleted
        get_response = client.get(f"/api/presets/{preset_id}")
        assert get_response.status_code == 404


class TestQuotaEndpoints:
    """Test quota-related endpoints."""

    def test_get_user_quota(self, client, mock_redis):
        """Test get user quota endpoint."""
        user_id = "test_user_123"

        response = client.get(f"/api/quota/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == user_id
        assert "current_count" in data
        assert "daily_limit" in data
        assert "remaining" in data
        assert "can_create" in data
        assert "date" in data

    def test_reset_user_quota(self, client, mock_redis):
        """Test reset user quota endpoint."""
        user_id = "test_user_456"

        response = client.post(f"/api/quota/{user_id}/reset")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert user_id in data["message"]
        assert "reset successfully" in data["message"]

    def test_reset_user_quota_with_date(self, client, mock_redis):
        """Test reset user quota with specific date."""
        user_id = "test_user_789"
        date_str = "2024-01-15"

        response = client.post(f"/api/quota/{user_id}/reset?date_str={date_str}")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert user_id in data["message"]


class TestTokenStatsEndpoint:
    """Test token statistics endpoint."""

    def test_get_token_stats(self, client):
        """Test token statistics endpoint."""
        request = {
            "input_text": "This is a test input for token statistics calculation.",
            "channels": ["linkedin"],
            "user_id": "test_user",
        }

        response = client.post("/api/token-stats", json=request)

        assert response.status_code == 200
        data = response.json()

        assert "token_stats" in data
        assert "validation" in data
        assert "recommendations" in data

        # Check token stats structure
        token_stats = data["token_stats"]
        assert "character_count" in token_stats
        assert "word_count" in token_stats
        assert "estimated_tokens" in token_stats

        # Check validation structure
        validation = data["validation"]
        assert "valid" in validation
        assert "errors" in validation
        assert "stats" in validation

        # Check recommendations structure
        recommendations = data["recommendations"]
        assert "can_process" in recommendations
        assert "estimated_cost" in recommendations
        assert "efficiency_tip" in recommendations

    def test_get_token_stats_large_text(self, client):
        """Test token statistics with large text."""
        large_text = "This is a test sentence. " * 1000  # ~25,000 characters
        request = {
            "input_text": large_text,
            "channels": ["linkedin"],
            "user_id": "test_user",
        }

        response = client.post("/api/token-stats", json=request)

        assert response.status_code == 200
        data = response.json()

        token_stats = data["token_stats"]
        assert token_stats["character_count"] == len(large_text)
        assert token_stats["estimated_tokens"] > 0
        assert token_stats["usage_percentage"]["characters"] > 0
