import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.schemas.channel import ChannelCreate
from app.services.parser_service import ParserService


class ChannelService:
    def __init__(
        self,
        channel_repo: ChannelRepository,
        post_repo: PostRepository,
        parser_service: ParserService,
    ):
        self.channel_repo = channel_repo
        self.post_repo = post_repo
        self.parser_service = parser_service

    async def add_channel_if_not_exists(self, channel_link: str):
        # извлекаем username
        username = channel_link.strip().lstrip("@").replace("https://t.me/", "")

        # проверяем, есть ли канал в базе
        existing_channels = self.channel_repo.get_all_channels()
        channel = next((c for c in existing_channels if c.username == username), None)
        if channel:
            return {
                "status": "exists",
                "channel": channel.username,
                "channel_id": channel.channel_id,
            }

        # парсим информацию о канале
        info = await self.parser_service.parser.get_channel_info(channel_link)
        data = ChannelCreate(
            channel_id=info["id"],
            username=info["username"],
            title=info["title"],
            participants_count=info["participants_count"],
        )
        # создаём запись в базе
        channel = self.channel_repo.get_or_create_channel(data)

        return {
            "status": "added",
            "channel": channel.username,
            "channel_id": channel.channel_id,
        }

    async def parse_channels(
        self, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        # Берём все каналы из базы
        channels = (
            self.channel_repo.get_all_channels()
        )  # возвращает объекты Channel с username
        results = []
        total_parsed = 0
        total_saved = 0

        async def parse_one(username: str):
            channel_link = f"@{username}"
            # ищем канал в списке
            channel = next((c for c in channels if c.username == username), None)

            if not channel:
                # создаём канал, если нет в базе
                info = await self.parser_service.parser.get_channel_info(channel_link)
                data = ChannelCreate(
                    channel_id=info["id"],
                    username=info["username"],
                    title=info["title"],
                    participants_count=info["participants_count"],
                )
                channel = self.channel_repo.get_or_create_channel(data)

            last_post = self.post_repo.get_last_post(channel.channel_id)
            last_post_id = last_post.post_id if last_post else None

            result = await self.parser_service.parse_and_save_posts(
                channel_link=channel_link,
                channel_id=channel.channel_id,
                last_post_id=last_post_id,
                limit=limit,
                delay=delay,
            )

            self.channel_repo.update_last_parsed(
                channel.channel_id, datetime.now(timezone.utc)
            )

            # сериализация datetime
            last_post_date = result.get("last_post_date")
            if isinstance(last_post_date, datetime):
                result["last_post_date"] = last_post_date.isoformat()

            return {"channel": channel.username or channel.title, **result}

        # Асинхронный парсинг всех каналов
        parsed_results = await asyncio.gather(
            *(parse_one(c.username) for c in channels if c.username)
        )

        for r in parsed_results:
            total_parsed += r["posts_parsed"]
            total_saved += r["posts_saved"]
            results.append(r)

        return {
            "channels_parsed": len(channels),
            "total_posts_parsed": total_parsed,
            "total_posts_saved": total_saved,
            "details": results,
            "status": "completed",
        }
