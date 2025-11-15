from app.core.database import get_async_session
from app.custom_classes.telegram_parser import TelegramParser
from app.dependencies.telegram_client import telegram_client
from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.services.channel_service import ChannelService
from app.services.parser_service import ParserService


def with_channel_service(func):
    """Декоратор, который инжектит channel_service в функцию"""
    async def wrapper(*args, **kwargs):
        async for session in get_async_session():
            channel_repo = ChannelRepository(session)
            post_repo = PostRepository(session)
            
            async with telegram_client as client:
                parser = TelegramParser(client)
                parser_service = ParserService(parser, post_repo)
                channel_service = ChannelService(channel_repo, post_repo, parser_service)
                
                kwargs['channel_service'] = channel_service
                result = await func(*args, **kwargs)
                
                # Явно закрываем сессию
                await session.close()
                return result
    return wrapper