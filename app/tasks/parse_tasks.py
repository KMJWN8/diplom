import asyncio

from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.custom_classes.telegram_parser import TelegramParser
from app.dependencies.telegram_client import telegram_client
from app.repositories.post import PostRepository
from app.services.parser_service import ParserService


@celery_app.task(name="app.tasks.parse_channel")
def parse_channel_task(channel_link: str, limit: int = 100, delay: float = 0.1):
    """Фоновая задача для парсинга Telegram-канала."""
    asyncio.run(_run_parse(channel_link, limit, delay))


async def _run_parse(channel_link: str, limit: int, delay: float):
    async with async_session_maker() as session:
        parser = TelegramParser(telegram_client)
        repo = PostRepository(session)
        service = ParserService(parser, repo)
        result = await service.parse_and_save_posts(channel_link, limit, delay)
        print(f"[Celery] Finished parsing {channel_link}: {result}")
