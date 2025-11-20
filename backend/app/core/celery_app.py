from datetime import timedelta

from celery import Celery

import app.tasks.channel_cycle
from app.core.config import settings

REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    "parser_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


celery_app.conf.beat_schedule = {
    "parse-channels-every-30-mins": {
        "task": "parse_channels_cycle",
        "schedule": timedelta(minutes=30),
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
