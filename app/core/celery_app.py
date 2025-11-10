import os

from celery import Celery

from app.core.config import settings

REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    "diplom_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_routes={
        "app.tasks.*": {"queue": "default"},
    },
    result_expires=3600,
)
