import asyncio
from typing import Any, Dict, List

from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError
from telethon.tl.types import Message

from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    InvalidLinkException,
    RateLimitException,
)


class TelegramParser:
    """
    Парсер постов Telegram-канала.
    Возвращает список сообщений в виде словарей.
    """

    def __init__(self, client: TelegramClient):
        self.client = client

    def _extract_channel_identifier(self, channel_link: str) -> str:
        """Извлекает username или invite hash из ссылки."""
        if not channel_link:
            raise InvalidLinkException("Пустая ссылка на канал")

        s = channel_link.strip()

        # если это @name или просто имя
        if not s.startswith("http") and "t.me" not in s:
            return s.lstrip("@")

        if "t.me/" in s:
            path = s.split("t.me/")[-1].split("?")[0].strip("/")

            if not path:
                raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

            if path.startswith("joinchat/"):
                return path.split("joinchat/")[-1]

            if path.startswith("+"):
                return path.lstrip("+")

            return path

        raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

    async def parse_posts(
        self, channel_link: str, limit: int = 100, delay: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Парсит посты Telegram-канала.
        Возвращает список словарей:
            {
                "post_id": int,
                "message": str,
                "date": datetime,
                "views": int | None,
                "comments_count": int,
            }
        """
        try:
            channel_identifier = self._extract_channel_identifier(channel_link)
            entity = await self.client.get_entity(channel_identifier)

            posts_data: List[Dict[str, Any]] = []
            async for i, message in enumerate(self.client.iter_messages(entity, limit=limit), start=1):
                if not isinstance(message, Message):
                    continue

                text = getattr(message, "text", None)
                if not text or not text.strip():
                    continue

                comments_count = getattr(getattr(message, "replies", None), "replies", 0) or 0

                posts_data.append(
                    {
                        "post_id": message.id,
                        "message": text.strip(),
                        "date": message.date,
                        "views": getattr(message, "views", None),
                        "comments_count": comments_count,
                    }
                )

                # каждые 10 сообщений — короткая пауза (антифлуд)
                if i % 10 == 0:
                    await asyncio.sleep(delay)

            return posts_data

        except (ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError):
            raise ChannelNotFoundException(f"Канал {channel_link} не найден")
        except FloodWaitError as e:
            raise RateLimitException(f"Flood wait: {e}")
        except InvalidLinkException:
            raise
        except Exception as e:
            raise Exception(f"Ошибка при парсинге постов: {e}")
