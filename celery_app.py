import os
from celery import Celery

broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "gcp_fastapi_backend",
    broker=broker,
    backend=backend,
)

celery.conf.update(task_track_started=True)

# Import tasks to ensure they are registered
import tasks  # noqa: F401
