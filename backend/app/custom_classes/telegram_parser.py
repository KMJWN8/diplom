import asyncio
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
    def __init__(self, client: TelegramClient):
        self.client = client

    def _extract_channel_identifier(self, channel_link: str) -> str:
        if not channel_link:
            raise InvalidLinkException("Пустая ссылка")
        s = channel_link.strip()
        if s.startswith("@"):
            return s.lstrip("@")
        if s.startswith("https://t.me/"):
            path = s.split("t.me/")[-1].split("?")[0].strip("/")
            if not path:
                raise InvalidLinkException(
                    f"Неподдерживаемый формат ссылки: {channel_link}"
                )
            return path
        raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

    async def get_channel_info(self, channel_link: str) -> Dict[str, Any]:
        try:
            ident = self._extract_channel_identifier(channel_link)

            if ident.isdigit():
                raise ChannelNotFoundException(
                    f"Числовой ID канала {ident} не поддерживается"
                )

            entity = await self.client.get_entity(ident)
            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Сущность не является каналом")

            return {
                "id": entity.id,
                "username": getattr(entity, "username", None),
                "title": getattr(entity, "title", None),
                "participants_count": getattr(entity, "participants_count", None),
                "entity": entity,
            }

        except (ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError):
            raise ChannelNotFoundException(f"Канал {channel_link} не найден")

    async def parse_posts(
        self, 
        entity: Channel, 
        delay: float = 0.1, 
        last_post_id: Optional[int] = None,
        limit: int = 1000  # Добавляем лимит
    ) -> List[Dict[str, Any]]:
        posts_data = []
        try:            
            async for message in self.client.iter_messages(
                entity, 
                limit=limit,
                reverse=True
            ):
                if not isinstance(message, Message) or not message.text:
                    continue
                
                if last_post_id is not None and message.id <= last_post_id:
                    continue
                
                posts_data.append(
                    {
                        "post_id": message.id,
                        "message": message.text.strip(),
                        "date": message.date,
                        "views": getattr(message, "views", None),
                        "comments_count": getattr(
                            getattr(message, "replies", None), "replies", 0
                        ) or 0,
                    }
                )
                
                if len(posts_data) >= limit:
                    break
                    
                await asyncio.sleep(delay)
            
            return posts_data[::-1]
        except FloodWaitError as e:
            raise RateLimitException(f"Flood wait: {e}")
        except Exception as e:
            raise Exception(f"Ошибка парсинга Telegram: {e}")