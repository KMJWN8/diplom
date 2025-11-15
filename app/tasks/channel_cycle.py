import asyncio

from celery import shared_task

from app.services.channel_service import ChannelService
from app.decorators.channel_decorator import with_channel_service

@shared_task(name="parse_channels_cycle")
def parse_channels_cycle_task():
    asyncio.run(_parse_channels_cycle())

@shared_task(name="parse_channel_info")
def parse_channel_info_task(channel_link: str):
    asyncio.run(_parse_channel_info(channel_link))

@with_channel_service
async def _parse_channels_cycle(channel_service: ChannelService = None):
    result = await channel_service.parse_all_channels(limit=100, delay=0.1)
    print(f"[Celery] Результат парсинга: {result}")
    return result

@with_channel_service
async def _parse_channel_info(channel_link: str, channel_service: ChannelService = None):
    result = await channel_service.parse_channel_info(channel_link)
    print(f"[Celery] Информация о канале: {result}")
    return result