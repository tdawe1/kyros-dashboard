"""
Celery application configuration for the scheduler system.
"""

from celery import Celery
import os

# Get Redis URL from environment
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "kyros_scheduler",
    broker=redis_url,
    backend=redis_url,
    include=["core.scheduler.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Define task queues
celery_app.conf.task_routes = {
    "core.scheduler.tasks.*": {"queue": "default"},
    "core.scheduler.tasks.repurposer.*": {"queue": "tool.repurposer"},
    "core.scheduler.tasks.translator.*": {"queue": "tool.translator"},
}

if __name__ == "__main__":
    celery_app.start()
