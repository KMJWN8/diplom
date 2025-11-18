import asyncio
from datetime import datetime, timezone
from typing import Any, Dict
import logging

from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.schemas.channel import ChannelCreate
from app.services.parser_service import ParserService


logger = logging.getLogger(__name__)


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
        logger.debug("ChannelService инициализирован")

    async def add_channel_if_not_exists(self, channel_link: str):
        username = channel_link.strip().lstrip("@").replace("https://t.me/", "")
        logger.info(f"Добавление канала: {channel_link} -> username: {username}")

        existing_channels = self.channel_repo.get_all_channels()
        channel = next((c for c in existing_channels if c.username == username), None)
        if channel:
            logger.info(f"Канал уже существует: {username} (ID: {channel.channel_id})")
        
        try:
            info = await self.parser_service.parser.get_channel_info(channel_link)
            logger.debug(f"Получена информация о канале: {info['title']}")
            data = ChannelCreate(
                channel_id=info["id"],
                username=info["username"],
                title=info["title"],
                participants_count=info["participants_count"],
            )

            channel = self.channel_repo.get_or_create_channel(data)
            logger.info(f"Канал добавлен: {channel.username} (ID: {channel.channel_id})")

        except Exception as e:
            logger.error(f"Ошибка при добавлении канала {channel_link}: {e}")
            raise

    async def parse_channels(self, delay: float = 0.1) -> Dict[str, Any]:
        channels = self.channel_repo.get_all_channels()
        logger.info(f"Начало парсинга {len(channels)} каналов")

        if not channels:
            logger.warning("Нет каналов для парсинга")
        
        results = []
        total_parsed = 0
        total_saved = 0

        async def parse_one(channel):
            channel_link = f"@{channel.username}"
            logger.debug(f"Парсинг канала: {channel.username or channel.title}")
            
            last_post = self.post_repo.get_last_post(channel.channel_id)
            last_post_id = last_post.post_id if last_post else None

            try:
                result = await self.parser_service.parse_and_save_posts(
                    channel_link=channel_link,
                    channel_id=channel.channel_id,
                    last_post_id=last_post_id,
                    delay=delay,
                )

                self.channel_repo.update_last_parsed(
                    channel.channel_id, datetime.now(timezone.utc)
                )

                # сериализация datetime
                last_post_date = result.get("last_post_date")
                if isinstance(last_post_date, datetime):
                    result["last_post_date"] = last_post_date.isoformat()

                logger.info(f"Канал {channel.username}: {result['posts_parsed']} получено, {result['posts_saved']} сохранено")

                return {"channel": channel.username or channel.title, **result}
            
            except Exception as e:
                logger.error(f"Ошибка парсинга канала {channel.username}: {e}")
                return {"channel": channel.username or channel.title, "error": str(e)}

        parsed_results = await asyncio.gather(
            *(parse_one(c) for c in channels if c.username),
            return_exceptions=True
        )

        for r in parsed_results:
            if isinstance(r, Exception):
                continue
            total_parsed += r["posts_parsed"]
            total_saved += r["posts_saved"]
            results.append(r)

        logger.info(f"Парсинг завершен: {len(channels)} каналов, {total_parsed} постов спаршено, {total_saved} постов сохранено")