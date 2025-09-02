"""
Unit tests for token storage functionality.
"""

import json
from utils.token_storage import (
    save_token_usage,
    get_token_usage,
    get_all_token_usage,
    save_job_record,
    get_job_record,
    get_all_job_records,
    get_token_usage_stats,
    export_token_usage_data,
    clear_all_data,
)


class TestTokenUsageStorage:
    """Test token usage storage functionality."""

    def test_save_token_usage_new_job(self, clean_storage):
        """Test saving token usage for new job."""
        job_id = "test_job_1"
        token_usage = {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150,
        }

        result = save_token_usage(job_id, token_usage, "gpt-4o-mini", "linkedin")

        assert result is True

        # Verify the data was saved
        saved_data = get_token_usage(job_id)
        assert saved_data is not None
        assert saved_data["job_id"] == job_id
        assert saved_data["total_tokens"] == 150
        assert abs(saved_data["total_cost"] - 0.015) < 0.0001  # 150 * 0.0001
        assert saved_data["model"] == "gpt-4o-mini"
        assert "linkedin" in saved_data["channels"]

    def test_save_token_usage_existing_job(self, clean_storage):
        """Test saving token usage for existing job."""
        job_id = "test_job_2"
        token_usage_1 = {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150,
        }
        token_usage_2 = {
            "prompt_tokens": 30,
            "completion_tokens": 80,
            "total_tokens": 110,
        }

        # Save first usage
        save_token_usage(job_id, token_usage_1, "gpt-4o-mini", "linkedin")

        # Save second usage
        result = save_token_usage(job_id, token_usage_2, "gpt-4o-mini", "twitter")

        assert result is True

        # Verify cumulative data
        saved_data = get_token_usage(job_id)
        assert saved_data["total_tokens"] == 260  # 150 + 110
        assert abs(saved_data["total_cost"] - 0.026) < 0.0001  # 260 * 0.0001
        assert len(saved_data["channels"]) == 2
        assert "linkedin" in saved_data["channels"]
        assert "twitter" in saved_data["channels"]

    def test_save_token_usage_invalid_data(self, clean_storage):
        """Test saving token usage with invalid data."""
        job_id = "test_job_3"
        invalid_token_usage = None

        result = save_token_usage(
            job_id, invalid_token_usage, "gpt-4o-mini", "linkedin"
        )

        # Should handle gracefully
        assert result is False

    def test_get_token_usage_nonexistent_job(self, clean_storage):
        """Test getting token usage for nonexistent job."""
        result = get_token_usage("nonexistent_job")
        assert result is None

    def test_get_all_token_usage(self, clean_storage):
        """Test getting all token usage data."""
        # Save some test data
        save_token_usage("job_1", {"total_tokens": 100}, "gpt-4o-mini", "linkedin")
        save_token_usage("job_2", {"total_tokens": 200}, "gpt-4o", "twitter")

        all_data = get_all_token_usage()

        assert len(all_data) == 2
        assert "job_1" in all_data
        assert "job_2" in all_data
        assert all_data["job_1"]["total_tokens"] == 100
        assert all_data["job_2"]["total_tokens"] == 200


class TestJobRecordStorage:
    """Test job record storage functionality."""

    def test_save_job_record(self, clean_storage):
        """Test saving job record."""
        job_id = "test_job_4"
        job_data = {
            "user_id": "test_user",
            "input_text": "Test input",
            "channels": ["linkedin"],
            "tone": "professional",
            "status": "completed",
        }

        result = save_job_record(job_id, job_data)

        assert result is True

        # Verify the data was saved
        saved_record = get_job_record(job_id)
        assert saved_record is not None
        assert saved_record["user_id"] == "test_user"
        assert saved_record["input_text"] == "Test input"
        assert "created_at" in saved_record
        assert "updated_at" in saved_record

    def test_save_job_record_invalid_data(self, clean_storage):
        """Test saving job record with invalid data."""
        job_id = "test_job_5"
        invalid_job_data = None

        result = save_job_record(job_id, invalid_job_data)

        assert result is False

    def test_get_job_record_nonexistent(self, clean_storage):
        """Test getting job record for nonexistent job."""
        result = get_job_record("nonexistent_job")
        assert result is None

    def test_get_all_job_records(self, clean_storage):
        """Test getting all job records."""
        # Save some test data
        save_job_record("job_1", {"user_id": "user1", "status": "completed"})
        save_job_record("job_2", {"user_id": "user2", "status": "pending"})

        all_records = get_all_job_records()

        assert len(all_records) == 2
        assert "job_1" in all_records
        assert "job_2" in all_records


class TestTokenUsageStats:
    """Test token usage statistics functionality."""

    def test_get_token_usage_stats_empty(self, clean_storage):
        """Test stats with no data."""
        stats = get_token_usage_stats()

        assert stats["total_jobs"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost"] == 0
        assert stats["avg_tokens_per_job"] == 0
        assert stats["model_usage"] == {}
        assert "last_updated" in stats

    def test_get_token_usage_stats_with_data(self, clean_storage):
        """Test stats with data."""
        # Save some test data
        save_token_usage("job_1", {"total_tokens": 100}, "gpt-4o-mini", "linkedin")
        save_token_usage("job_2", {"total_tokens": 200}, "gpt-4o", "twitter")
        save_token_usage("job_3", {"total_tokens": 150}, "gpt-4o-mini", "newsletter")

        stats = get_token_usage_stats()

        assert stats["total_jobs"] == 3
        assert stats["total_tokens"] == 450  # 100 + 200 + 150
        assert stats["total_cost"] == 0.045  # 450 * 0.0001
        assert stats["avg_tokens_per_job"] == 150  # 450 / 3
        assert stats["model_usage"]["gpt-4o-mini"] == 250  # 100 + 150
        assert stats["model_usage"]["gpt-4o"] == 200

    def test_get_token_usage_stats_single_job(self, clean_storage):
        """Test stats with single job."""
        save_token_usage("job_1", {"total_tokens": 100}, "gpt-4o-mini", "linkedin")

        stats = get_token_usage_stats()

        assert stats["total_jobs"] == 1
        assert stats["total_tokens"] == 100
        assert stats["avg_tokens_per_job"] == 100


class TestExportFunctionality:
    """Test export functionality."""

    def test_export_token_usage_data(self, clean_storage):
        """Test exporting token usage data."""
        # Save some test data
        save_token_usage("job_1", {"total_tokens": 100}, "gpt-4o-mini", "linkedin")
        save_job_record("job_1", {"user_id": "test_user", "status": "completed"})

        export_data = export_token_usage_data()

        # Should be valid JSON
        parsed_data = json.loads(export_data)

        assert "token_usage" in parsed_data
        assert "job_records" in parsed_data
        assert "statistics" in parsed_data
        assert "exported_at" in parsed_data
        assert "job_1" in parsed_data["token_usage"]
        assert "job_1" in parsed_data["job_records"]

    def test_export_empty_data(self, clean_storage):
        """Test exporting empty data."""
        export_data = export_token_usage_data()
        parsed_data = json.loads(export_data)

        assert parsed_data["token_usage"] == {}
        assert parsed_data["job_records"] == {}
        assert parsed_data["statistics"]["total_jobs"] == 0


class TestClearData:
    """Test data clearing functionality."""

    def test_clear_all_data(self, clean_storage):
        """Test clearing all data."""
        # Save some test data
        save_token_usage("job_1", {"total_tokens": 100}, "gpt-4o-mini", "linkedin")
        save_job_record("job_1", {"user_id": "test_user", "status": "completed"})

        # Verify data exists
        assert get_token_usage("job_1") is not None
        assert get_job_record("job_1") is not None

        # Clear data
        result = clear_all_data()

        assert result is True
        assert get_token_usage("job_1") is None
        assert get_job_record("job_1") is None
        assert get_all_token_usage() == {}
        assert get_all_job_records() == {}
