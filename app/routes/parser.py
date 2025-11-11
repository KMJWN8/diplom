from fastapi import APIRouter

from app.core.celery_app import celery_app
from app.tasks.channel_cycle import parse_channels_cycle_task

router = APIRouter(prefix="/channels", tags=["parsing"])


@router.post("/parse")
async def start_parsing():
    parse_channels_cycle_task.delay()
    return {"status": "queued"}
