"""
Unit tests for quota management functionality.
"""

from utils.quotas import can_create_job, get_user_quota_status, reset_user_quota


class TestCanCreateJob:
    """Test job creation quota checking."""

    def test_can_create_job_new_user(self, mock_redis):
        """Test quota check for new user."""
        mock_redis.get.return_value = None
        mock_redis.incr.return_value = 1

        can_create, count = can_create_job("new_user", 10)

        assert can_create is True
        assert count == 1
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

    def test_can_create_job_within_limit(self, mock_redis):
        """Test quota check for user within limit."""
        mock_redis.get.return_value = "5"
        mock_redis.incr.return_value = 6

        can_create, count = can_create_job("existing_user", 10)

        assert can_create is True
        assert count == 6

    def test_can_create_job_at_limit(self, mock_redis):
        """Test quota check for user at limit."""
        mock_redis.get.return_value = "10"

        can_create, count = can_create_job("limit_user", 10)

        assert can_create is False
        assert count == 10
        mock_redis.incr.assert_not_called()

    def test_can_create_job_exceeds_limit(self, mock_redis):
        """Test quota check for user exceeding limit."""
        mock_redis.get.return_value = "15"

        can_create, count = can_create_job("exceeded_user", 10)

        assert can_create is False
        assert count == 15
        mock_redis.incr.assert_not_called()

    def test_can_create_job_redis_error(self, mock_redis):
        """Test quota check with Redis error (fail open)."""
        mock_redis.get.side_effect = Exception("Redis connection failed")

        can_create, count = can_create_job("error_user", 10)

        # Should fail open - allow job creation
        assert can_create is True
        assert count == 0

    def test_can_create_job_custom_limit(self, mock_redis):
        """Test quota check with custom daily limit."""
        mock_redis.get.return_value = "2"
        mock_redis.incr.return_value = 3

        can_create, count = can_create_job("custom_user", 5)

        assert can_create is True
        assert count == 3


class TestGetUserQuotaStatus:
    """Test user quota status retrieval."""

    def test_get_user_quota_status_new_user(self, mock_redis):
        """Test quota status for new user."""
        mock_redis.get.return_value = None

        status = get_user_quota_status("new_user", 10)

        assert status["user_id"] == "new_user"
        assert status["current_count"] == 0
        assert status["daily_limit"] == 10
        assert status["remaining"] == 10
        assert status["can_create"] is True
        assert "date" in status

    def test_get_user_quota_status_existing_user(self, mock_redis):
        """Test quota status for existing user."""
        mock_redis.get.return_value = "7"

        status = get_user_quota_status("existing_user", 10)

        assert status["user_id"] == "existing_user"
        assert status["current_count"] == 7
        assert status["daily_limit"] == 10
        assert status["remaining"] == 3
        assert status["can_create"] is True

    def test_get_user_quota_status_at_limit(self, mock_redis):
        """Test quota status for user at limit."""
        mock_redis.get.return_value = "10"

        status = get_user_quota_status("limit_user", 10)

        assert status["current_count"] == 10
        assert status["remaining"] == 0
        assert status["can_create"] is False

    def test_get_user_quota_status_redis_error(self, mock_redis):
        """Test quota status with Redis error."""
        mock_redis.get.side_effect = Exception("Redis connection failed")

        status = get_user_quota_status("error_user", 10)

        # Should return default values with error info
        assert status["user_id"] == "error_user"
        assert status["current_count"] == 0
        assert status["remaining"] == 10
        assert status["can_create"] is True
        assert "error" in status

    def test_get_user_quota_status_custom_limit(self, mock_redis):
        """Test quota status with custom limit."""
        mock_redis.get.return_value = "3"

        status = get_user_quota_status("custom_user", 5)

        assert status["daily_limit"] == 5
        assert status["current_count"] == 3
        assert status["remaining"] == 2


class TestResetUserQuota:
    """Test user quota reset functionality."""

    def test_reset_user_quota_today(self, mock_redis):
        """Test resetting quota for today."""
        mock_redis.delete.return_value = 1

        result = reset_user_quota("test_user")

        assert result is True
        mock_redis.delete.assert_called_once()
        # Check that the key format is correct
        call_args = mock_redis.delete.call_args[0]
        assert call_args[0].startswith("jobs:test_user:")

    def test_reset_user_quota_specific_date(self, mock_redis):
        """Test resetting quota for specific date."""
        mock_redis.delete.return_value = 1
        date_str = "2024-01-15"

        result = reset_user_quota("test_user", date_str)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"jobs:test_user:{date_str}")

    def test_reset_user_quota_redis_error(self, mock_redis):
        """Test reset quota with Redis error."""
        mock_redis.delete.side_effect = Exception("Redis connection failed")

        result = reset_user_quota("error_user")

        assert result is False

    def test_reset_user_quota_nonexistent_key(self, mock_redis):
        """Test resetting quota for nonexistent key."""
        mock_redis.delete.return_value = 0  # Key didn't exist

        result = reset_user_quota("nonexistent_user")

        assert result is True  # Should still return True even if key didn't exist
