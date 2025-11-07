from typing import Dict, Any

from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.schemas.channel import ChannelCreate
from app.schemas.post import PostCreate
from app.custom_classes.telegram_parser import TelegramParser


class ChannelService:
    def __init__(
        self,
        parser: TelegramParser,
        channel_repo: ChannelRepository,
        post_repo: PostRepository,
    ):
        self.parser = parser
        self.channel_repo = channel_repo
        self.post_repo = post_repo

    async def parse_and_save_channel(
        self, channel_link: str, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Парсит канал и сохраняет данные в БД
        """
        # Парсим данные с помощью парсера
        parsing_result = await self.parser.parse_channel_posts(channel_link, limit, delay)
        
        channel_info = parsing_result["channel_info"]
        posts_data = parsing_result["posts_data"]

        # Сохраняем/обновляем канал в БД
        channel_data = ChannelCreate(
            channel_id=channel_info["id"],
            username=channel_info["username"],
            title=channel_info["title"],
            participants_count=channel_info["participants_count"],
        )
        channel = await self.channel_repo.get_or_create_channel(channel_data)

        # Сохраняем посты в БД
        posts_saved = 0
        for post_data in posts_data:
            post_create = PostCreate(**post_data)
            await self.post_repo.create_post(post_create)
            posts_saved += 1

        return {
            "channel": channel,
            "posts_parsed": parsing_result["posts_parsed"],
            "posts_saved": posts_saved,
            "status": "completed",
        }

    async def get_channel_info(self, channel_link: str) -> Dict[str, Any]:
        """
        Получает информацию о канале (без сохранения в БД)
        """
        return await self.parser.get_channel_info(channel_link)