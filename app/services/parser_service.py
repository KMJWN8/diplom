from typing import Any, Dict

from app.custom_classes.telegram_parser import TelegramParser
from app.repositories.post import PostRepository
from app.schemas.post import PostCreate


class ParserService:
    """
    Сервис для парсинга и сохранения постов Telegram-канала.
    """

    def __init__(self, parser: TelegramParser, post_repo: PostRepository):
        self.parser = parser
        self.post_repo = post_repo

    async def parse_and_save_posts(
        self, channel_link: str, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        posts_data = await self.parser.parse_posts(channel_link, limit, delay)

        # массовое сохранение
        posts = [PostCreate(**p) for p in posts_data]
        inserted = await self.post_repo.bulk_create(posts)

        return {
            "posts_parsed": len(posts_data),
            "posts_saved": inserted,
            "status": "completed",
        }
