import asyncio

from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, UsernameNotOccupiedError
from telethon.tl.types import Channel, Message, MessageMediaDocument, MessageMediaPhoto

from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    RateLimitException,
)
from app.repositories.telegram_repository import TelegramRepository
from app.schemas.telegram import ChannelCreate, ParseRequest, PostCreate


class TelegramService:
    def __init__(self, telegram_client: TelegramClient, repository: TelegramRepository):
        self.client = telegram_client
        self.repository = repository

    async def parse_channel_posts(self, parse_request: ParseRequest) -> dict:
        try:
            # Получаем entity канала
            entity = await self.client.get_entity(parse_request.channel_username)

            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Указанная сущность не является каналом")

            # Сохраняем/обновляем информацию о канале
            channel_data = ChannelCreate(
                channel_id=entity.id,
                username=getattr(entity, "username", None),
                title=entity.title,
            )
            channel = await self.repository.get_or_create_channel(channel_data)

            # Парсим посты
            posts_data = []
            async for message in self.client.iter_messages(
                entity, limit=parse_request.limit
            ):
                if not isinstance(message, Message):
                    continue

                # Получаем количество комментариев
                comments_count = 0
                if message.replies and message.replies.comments:
                    comments_count = message.replies.replies

                # Определяем тип медиа
                media_type = None
                if message.media:
                    if isinstance(message.media, MessageMediaPhoto):
                        media_type = "photo"
                    elif isinstance(message.media, MessageMediaDocument):
                        media_type = "document"

                post_data = PostCreate(
                    channel_id=entity.id,
                    post_id=message.id,
                    message=message.text,
                    date=message.date,
                    views=message.views,
                    comments_count=comments_count,
                    forwards=message.forwards,
                    media_type=media_type,
                )

                post = await self.repository.create_post(post_data)
                posts_data.append(post)

                # Задержка для избежания ограничений
                await asyncio.sleep(0.1)

            # Получаем статистику
            stats = await self.repository.get_channel_stats(entity.id)

            return {"channel": channel, "posts_parsed": len(posts_data), "stats": stats}

        except (ChannelInvalidError, UsernameNotOccupiedError):
            raise ChannelNotFoundException(
                f"Канал {parse_request.channel_username} не найден"
            )
        except Exception as e:
            raise RateLimitException(f"Ошибка при парсинге: {str(e)}")

    async def get_channel_info(self, channel_username: str) -> dict:
        try:
            entity = await self.client.get_entity(channel_username)

            if not isinstance(entity, Channel):
                raise ChannelNotFoundException("Указанная сущность не является каналом")

            return {
                "id": entity.id,
                "title": entity.title,
                "username": getattr(entity, "username", None),
                "participants_count": getattr(entity, "participants_count", None),
            }

        except (ChannelInvalidError, UsernameNotOccupiedError):
            raise ChannelNotFoundException(f"Канал {channel_username} не найден")
