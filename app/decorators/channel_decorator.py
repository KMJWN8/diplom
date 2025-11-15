import asyncio
from functools import wraps

from app.core.database import get_session
from app.custom_classes.telegram_parser import TelegramParser
from app.dependencies.telegram_client import TelegramClientManager
from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.services.channel_service import ChannelService
from app.services.parser_service import ParserService

telegram_client = TelegramClientManager()


def with_channel_service(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = next(get_session())

        channel_repo = ChannelRepository(session)
        post_repo = PostRepository(session)

        async def async_runner():
            async with telegram_client as client:
                parser = TelegramParser(client)
                parser_service = ParserService(parser, post_repo)
                channel_service = ChannelService(
                    channel_repo, post_repo, parser_service
                )
                kwargs["channel_service"] = channel_service
                return await func(*args, **kwargs)

        return asyncio.run(async_runner())

    return wrapper
