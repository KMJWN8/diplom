from fastapi import APIRouter

from app.core.celery_app import celery_app
from app.tasks.channel_cycle import parse_channels_cycle_task, parse_channel_info_task

router = APIRouter(tags=["parsing"])


@router.post("/parse")
async def start_parsing():
    parse_channels_cycle_task.delay()
    return {"status": "queued"}


@router.post("/channel")
async def add_channel(channel_link: str):
    parse_channel_info_task.delay(channel_link)
    return {"status": "queued"}
