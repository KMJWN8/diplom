import asyncio
from typing import Any, Dict

from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError
from telethon.tl.types import Channel, Message

from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    InvalidLinkException,
    RateLimitException,
)


class TelegramParser:
    def __init__(self, client: TelegramClient):
        self.client = client

    def _extract_channel_identifier(self, channel_link: str) -> str:
        """
        Извлекает идентификатор канала из ссылки
        """
        if not channel_link.startswith(("http", "t.me/")):
            return channel_link.lstrip("@")

        if "t.me/" in channel_link:
            path = channel_link.split("t.me/")[-1].split("?")[0]

            if not path.startswith("joinchat/"):
                return path

            if path.startswith("joinchat/"):
                return path.replace("joinchat/", "")

        raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

    async def get_channel_info(self, channel_link: str) -> Dict[str, Any]:
        """
        Получает информацию о канале
        """
        try:
            channel_identifier = self._extract_channel_identifier(channel_link)
            entity = await self.client.get_entity(channel_identifier)

            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Указанная сущность не является каналом")

            return {
                "id": entity.id,
                "title": entity.title,
                "username": getattr(entity, "username", None),
                "participants_count": getattr(entity, "participants_count", None),
                "is_public": hasattr(entity, "username")
                and entity.username is not None,
            }

        except (ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError):
            raise ChannelNotFoundException(f"Канал {channel_link} не найден")
        except InvalidLinkException as e:
            raise

    async def parse_channel_posts(
        self, channel_link: str, limit: int = 100, delay: float = 0.1
    ) -> Dict[str, Any]:
        """
        Основной метод парсинга постов канала
        """
        try:
            # Получаем информацию о канале
            channel_info = await self.get_channel_info(channel_link)

            # Парсим посты
            entity = await self.client.get_entity(channel_link)
            posts_data = []

            async for message in self.client.iter_messages(entity, limit=limit):
                if (
                    not isinstance(message, Message)
                    or not message.text
                    or not message.text.strip()
                ):
                    continue

                # Получаем количество комментариев
                comments_count = 0
                if message.replies and hasattr(message.replies, "replies"):
                    comments_count = message.replies.replies

                # Создаем данные поста
                post_data = {
                    "channel_id": channel_info["id"],
                    "post_id": message.id,
                    "message": message.text,
                    "date": message.date,
                    "views": getattr(message, "views", None),
                    "comments_count": comments_count,
                    "forwards": getattr(message, "forwards", None),
                }

                posts_data.append(post_data)
                
                # Задержка для избежания ограничений
                await asyncio.sleep(delay)

            return {
                "channel_info": channel_info,
                "posts_data": posts_data,
                "posts_parsed": len(posts_data),
                "status": "completed",
            }

        except FloodWaitError as e:
            raise RateLimitException(f"Flood wait: {e}")
        except Exception as e:
            raise RateLimitException(f"Ошибка при парсинге: {str(e)}")