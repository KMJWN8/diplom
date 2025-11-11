from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
        self,
        channel_link: str,
        channel_id: int,
        since_date: Optional[datetime] = None,
        limit: int = 100,
        delay: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Парсит посты Telegram-канала и сохраняет их в базу.
        Если указан since_date — парсинг начинается с этой даты (пропуская старые посты).
        """

        # 1️⃣ Получаем посты из Telegram
        posts_data = await self.parser.parse_posts(
            channel_link, limit=limit, delay=delay, since_date=since_date
        )

        # 2️⃣ Добавляем channel_id и фильтруем старые посты
        valid_posts: List[PostCreate] = []
        for post in posts_data:
            post_date = post.get("date")
            if since_date and post_date <= since_date:
                continue  # пропускаем старые
            post["channel_id"] = channel_id
            valid_posts.append(PostCreate(**post))

        if not valid_posts:
            return {
                "posts_parsed": len(posts_data),
                "posts_saved": 0,
                "status": "no_new_posts",
            }

        # 3️⃣ Массовое сохранение
        inserted = await self.post_repo.bulk_create(valid_posts)

        return {
            "posts_parsed": len(posts_data),
            "posts_saved": inserted,
            "status": "completed",
            "last_post_date": valid_posts[-1].date if valid_posts else since_date,
        }
