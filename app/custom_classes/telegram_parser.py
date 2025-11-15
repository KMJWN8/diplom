import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from telethon import TelegramClient
from telethon.errors import (
    ChannelInvalidError,
    FloodWaitError,
    InviteHashInvalidError,
    UsernameNotOccupiedError,
)
from telethon.tl.types import Channel, Message

from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    InvalidLinkException,
    RateLimitException,
)


class TelegramParser:
    """
    Парсер Telegram-каналов: получает информацию о канале и посты.
    """

    def __init__(self, client: TelegramClient):
        self.client = client

    # -------------------------------
    #     Вспомогательные методы
    # -------------------------------

    def _extract_channel_identifier(self, channel_link: str) -> str:
        """
        Поддерживаемые форматы:
         - @channel
         - https://t.me/channel
        """
        if not channel_link:
            raise InvalidLinkException("Пустая ссылка")

        s = channel_link.strip()

        # формат @channel
        if s.startswith("@"):
            return s.lstrip("@")

        # формат https://t.me/channel
        if s.startswith("https://t.me/"):
            path = s.split("t.me/")[-1].split("?")[0].strip("/")
            if not path:
                raise InvalidLinkException(
                    f"Неподдерживаемый формат ссылки: {channel_link}"
                )
            return path

        raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

    # -------------------------------
    # 🔹 Информация о канале
    # -------------------------------

    async def get_channel_info(self, channel_link: str) -> Dict[str, Any]:
        """
        Возвращает метаданные канала и объект entity для дальнейшей работы.
        """
        try:
            ident = self._extract_channel_identifier(channel_link)
            entity = await self.client.get_entity(ident)

            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Сущность не является каналом")

            return {
                "channel_id": entity.id,
                "username": getattr(entity, "username", None),
                "title": getattr(entity, "title", None),
                "participants_count": getattr(entity, "participants_count", None),
                "entity": entity,
            }

        except (ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError):
            raise ChannelNotFoundException(f"Канал {channel_link} не найден")


    async def parse_posts(
        self,
        channel_link: str,
        last_post_id: Optional[int] = None,
        since_date: Optional[datetime] = None,
        limit: int = 100,
        delay: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Парсит новые посты в канале.
        Если указан last_post_id — продолжает после него.
        Если указан since_date — пропускает посты до этой даты.
        """
        try:
            # получаем entity один раз
            channel_info = await self.get_channel_info(channel_link)
            entity = channel_info["entity"]
            channel_id = channel_info["channel_id"]

            posts_data: List[Dict[str, Any]] = []
            async for message in self.client.iter_messages(entity, limit=limit):
                if not isinstance(message, Message) or not message.text:
                    continue

                # прекращаем, если достигли старого поста
                if last_post_id and message.id <= last_post_id:
                    break

                # пропускаем посты до since_date
                if since_date and message.date <= since_date:
                    continue

                posts_data.append(
                    {
                        "channel_id": channel_id,
                        "post_id": message.id,
                        "message": message.text.strip(),
                        "date": message.date,
                        "views": getattr(message, "views", None),
                        "comments_count": getattr(
                            getattr(message, "replies", None), "replies", 0
                        )
                        or 0,
                    }
                )
                await asyncio.sleep(delay)

            # возвращаем в хронологическом порядке (старые → новые)
            return posts_data[::-1]

        except FloodWaitError as e:
            raise RateLimitException(f"Flood wait: {e}")

        except ChannelNotFoundException:
            raise

        except Exception as e:
            raise Exception(f"Ошибка при парсинге канала {channel_link}: {e}")
