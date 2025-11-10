from fastapi import APIRouter

from app.tasks.parse_tasks import parse_channel_task

router = APIRouter(prefix="/channels", tags=["parsing"])


@router.post("/parse")
async def start_parsing(channel_link: str, limit: int = 100):
    parse_channel_task.delay(channel_link, limit)
    return {"status": "queued", "channel": channel_link}
