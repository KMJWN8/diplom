import asyncio
import re
from urllib.parse import urlparse

from telethon import TelegramClient
from telethon.errors import (
    ChannelInvalidError,
    InviteHashInvalidError,
    UsernameNotOccupiedError,
)
from telethon.tl.types import Channel, Message

from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    InvalidLinkException,
    RateLimitException,
)
from app.repositories.telegram_repository import TelegramRepository
from app.schemas.telegram import ChannelCreate, ParseRequest, PostCreate


class TelegramService:
    def __init__(self, telegram_client: TelegramClient, repository: TelegramRepository):
        self.client = telegram_client
        self.repository = repository

    def _extract_channel_identifier(self, channel_link: str) -> str:
        """
        Извлекает идентификатор канала из ссылки
        Поддерживает форматы:
        - https://t.me/channel_name
        - https://t.me/joinchat/ABCDEF12345 (приватные каналы)
        - @channel_name
        - channel_name
        """
        # Если это уже username (с @ или без)
        if not channel_link.startswith(("http", "t.me/")):
            return channel_link.lstrip("@")

        # Обрабатываем ссылки
        if "t.me/" in channel_link:
            # Извлекаем часть после t.me/
            path = channel_link.split("t.me/")[-1]

            # Убираем параметры запроса если есть
            path = path.split("?")[0]

            # Для публичных каналов
            if not path.startswith("joinchat/"):
                return path

            # Для приватных каналов (invite links)
            if path.startswith("joinchat/"):
                invite_hash = path.replace("joinchat/", "")
                return invite_hash

        raise InvalidLinkException(f"Неподдерживаемый формат ссылки: {channel_link}")

    async def parse_channel_posts(self, parse_request: ParseRequest) -> dict:
        try:
            # Извлекаем идентификатор из ссылки
            channel_identifier = self._extract_channel_identifier(
                parse_request.channel_link
            )

            # Получаем entity канала
            entity = await self.client.get_entity(channel_identifier)

            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Указанная сущность не является каналом")

            # Сохраняем/обновляем информацию о канале
            channel_data = ChannelCreate(
                channel_id=entity.id,
                username=getattr(entity, "username", None),
                title=entity.title,
                participants_count=getattr(entity, "participants_count", None),
            )
            channel = await self.repository.get_or_create_channel(channel_data)

            # Парсим посты (ТОЛЬКО ТЕКСТ)
            posts_data = []
            async for message in self.client.iter_messages(
                entity, limit=parse_request.limit
            ):
                if not isinstance(message, Message):
                    continue

                # Пропускаем посты без текста
                if not message.text or not message.text.strip():
                    continue

                # Получаем количество комментариев
                comments_count = 0
                if message.replies and hasattr(message.replies, "replies"):
                    comments_count = message.replies.replies

                post_data = PostCreate(
                    channel_id=entity.id,
                    post_id=message.id,
                    message=message.text,  # Сохраняем только текст
                    date=message.date,
                    views=getattr(message, "views", None),
                    comments_count=comments_count,
                    forwards=getattr(message, "forwards", None),
                    # Убрали media_type - не нужно
                )

                post = await self.repository.create_post(post_data)
                posts_data.append(post)

                # Задержка для избежания ограничений
                await asyncio.sleep(0.1)

            # Получаем статистику
            stats = await self.repository.get_channel_stats(entity.id)

            return {"channel": channel, "posts_parsed": len(posts_data), "stats": stats}

        except (ChannelInvalidError, UsernameNotOccupiedError, InviteHashInvalidError):
            raise ChannelNotFoundException(
                f"Канал {parse_request.channel_link} не найден или недоступен"
            )
        except InvalidLinkException as e:
            raise
        except Exception as e:
            raise RateLimitException(f"Ошибка при парсинге: {str(e)}")

    async def get_channel_info(self, channel_link: str) -> dict:
        try:
            # Извлекаем идентификатор из ссылки
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
