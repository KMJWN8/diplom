import asyncio
from datetime import datetime, timezone

from celery import shared_task

from app.core.database import get_async_session
from app.custom_classes.telegram_parser import TelegramParser
from app.dependencies.telegram_client import telegram_client
from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.services.channel_service import ChannelService
from app.services.parser_service import ParserService


@shared_task(name="parse_channels_cycle", queue="telegram_parser")
def parse_channels_cycle_task():
    asyncio.run(_parse_channels_cycle())


async def _parse_channels_cycle():
    async for session in get_async_session():
        channel_repo = ChannelRepository(session)
        post_repo = PostRepository(session)

        async with telegram_client as client:
            parser = TelegramParser(client)
            parser_service = ParserService(parser, post_repo)
            channel_service = ChannelService(channel_repo, post_repo, parser_service)

            result = await channel_service.parse_channel(
                channel_link="@chp_kzl", limit=100, delay=0.1
            )
            print(f"[Celery] Результат парсинга: {result}")

        break
