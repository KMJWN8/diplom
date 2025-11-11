from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.schemas.channel import ChannelCreate
from app.services.parser_service import ParserService


class ChannelService:
    """
    Сервис высокого уровня — управляет парсингом каналов.
    Решает:
      - откуда начинать парсинг (новый канал или продолжение);
      - когда обновлять информацию о канале;
      - вызывает ParserService для сохранения постов.
    """

    def __init__(
        self,
        channel_repo: ChannelRepository,
        post_repo: PostRepository,
        parser_service: ParserService,
    ):
        self.channel_repo = channel_repo
        self.post_repo = post_repo
        self.parser_service = parser_service

    async def parse_channel(
        self, channel_link: str, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Парсит конкретный канал:
         - если канал новый — добавляет его в БД и парсит с начала месяца
         - если уже существует — парсит только новые посты
        """
        # 1️⃣ Проверяем, есть ли канал в базе
        channel = await self.channel_repo.get_by_link(channel_link)

        if not channel:
            # Получаем инфо через парсер и создаём новый канал
            channel_info = await self.parser_service.parser.get_channel_info(
                channel_link
            )

            channel_data = ChannelCreate(
                channel_id=channel_info["channel_id"],
                username=channel_info["username"],
                title=channel_info["title"],
                participants_count=channel_info["participants_count"],
            )

            channel = await self.channel_repo.get_or_create_channel(channel_data)
            last_post_id = None
        else:
            # Получаем последний пост для определения точки продолжения
            last_post = await self.post_repo.get_last_post(channel.channel_id)
            last_post_id = last_post.post_id if last_post else None

        channel_id_to_parse = (
            channel_info["channel_id"] if not channel else channel.channel_id
        )

        # 2️⃣ Запускаем парсинг постов
        result = await self.parser_service.parse_and_save_posts(
            channel_link=channel_link,
            channel_id=channel_id_to_parse,
            limit=limit,
            delay=delay,
        )
        # 3️⃣ Обновляем дату последнего обновления
        await self.channel_repo.update_last_parsed(
            channel.channel_id, datetime.now(timezone.utc)
        )

        return {
            "channel": channel.username or channel.title,
            "posts_parsed": result["posts_parsed"],
            "posts_saved": result["posts_saved"],
            "status": result["status"],
        }

    async def parse_all_channels(
        self, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Парсит все каналы из БД, продолжая с последнего поста.
        Используй как Celery-задачу или фоновой цикл.
        """
        channels = await self.channel_repo.get_all_channels()
        total_parsed, total_saved = 0, 0

        for channel in channels:
            last_post = await self.post_repo.get_last_post(channel.channel_id)
            last_post_id = last_post.post_id if last_post else None

            result = await self.parser_service.parse_and_save_posts(
                channel_link=f"https://t.me/{channel.username or channel.channel_id}",
                limit=limit,
                delay=delay,
            )

            await self.channel_repo.update_last_parsed(channel.channel_id)

            total_parsed += result["posts_parsed"]
            total_saved += result["posts_saved"]

        return {
            "channels_parsed": len(channels),
            "total_posts_parsed": total_parsed,
            "total_posts_saved": total_saved,
            "status": "completed",
        }
