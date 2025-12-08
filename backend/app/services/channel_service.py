#services/channel_service.py
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

    async def add_channel_if_not_exists(self, channel_link: str):
        # Извлекаем username разными способами
        username = None
        if channel_link.startswith("@"):
            username = channel_link.lstrip("@")
        elif channel_link.startswith("https://t.me/"):
            username = channel_link.split("t.me/")[-1].split("?")[0].strip("/")
        else:
            username = channel_link.strip()
        
        logger.info(f"Добавление канала: {channel_link} -> username: {username}")

        # Проверяем существование канала
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
                # При создании канала не устанавливаем last_post_id
                # он будет определен при первом парсинге
            )

            channel = self.channel_repo.get_or_create_channel(data)
            logger.info(f"Канал добавлен: {channel.username} (ID: {channel.channel_id})")

        except Exception as e:
            logger.error(f"Ошибка при добавлении канала {channel_link}: {e}")
            raise
        return {
            "success": True,
            "channel_id": channel.channel_id,
            "username": channel.username,
            "title": channel.title
        }

    async def parse_channels(
        self, 
        limit: int,
        delay: float = 0.1, 
        max_concurrent: int = 5  # Максимум параллельных парсингов
    ) -> Dict[str, Any]:
        channels = self.channel_repo.get_all_channels()
        logger.info(f"Начало парсинга {len(channels)} каналов")

        if not channels:
            logger.warning("Нет каналов для парсинга")
            return {
                "results": [], 
                "total_parsed": 0, 
                "total_saved": 0,
                "channels_processed": 0
            }
        
        results = []
        total_parsed = 0
        total_saved = 0
        channels_with_errors = 0

        async def parse_one(channel):
            """Парсинг одного канала"""
            if not channel.username:
                logger.warning(f"У канала {channel.title} нет username, пропускаем")
                return {
                    "channel": channel.title,
                    "error": "No username",
                    "posts_parsed": 0,
                    "posts_saved": 0
                }
            
            channel_link = f"@{channel.username}"
            logger.info(f"Начинаем парсинг канала: {channel.username}")
            
            # Получаем последний сохраненный пост
            last_post = self.post_repo.get_last_post(channel.channel_id)
            last_post_id = last_post.post_id if last_post else None
            
            logger.debug(f"Канал {channel.username}: last_post_id = {last_post_id}")
            
            try:
                result = await self.parser_service.parse_and_save_posts(
                    channel_link=channel_link,
                    channel_id=channel.channel_id,
                    last_post_id=last_post_id,  # передаем ID последнего сохраненного
                    delay=delay,
                    limit=limit,
                )

                # Обновляем время последнего парсинга
                self.channel_repo.update_last_parsed(
                    channel.channel_id, 
                    datetime.now(timezone.utc)
                )

                # Если спарсили новые посты, обновляем last_post_id
                if result["posts_saved"] > 0 and result.get("new_last_post_id"):
                    # Здесь можно добавить обновление last_post_id в канале
                    # если вы хотите хранить его там
                    pass

                # Логируем результат
                status_msg = f"Канал {channel.username}: "
                if result["posts_saved"] > 0:
                    status_msg += f"{result['posts_saved']} новых постов сохранено"
                else:
                    status_msg += "нет новых постов"
                
                logger.info(status_msg)

                return {
                    "channel": channel.username,
                    "channel_title": channel.title,
                    **result
                }
            
            except Exception as e:
                logger.error(f"Ошибка парсинга канала {channel.username}: {str(e)}")
                return {
                    "channel": channel.username,
                    "channel_title": channel.title,
                    "error": str(e), 
                    "posts_parsed": 0, 
                    "posts_saved": 0
                }

        # Ограничиваем количество одновременных запросов
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def parse_with_semaphore(channel):
            async with semaphore:
                return await parse_one(channel)
        
        # Запускаем парсинг всех каналов
        tasks = [parse_with_semaphore(c) for c in channels if c.username]
        parsed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        for r in parsed_results:
            if isinstance(r, Exception):
                logger.error(f"Исключение при парсинге: {r}")
                channels_with_errors += 1
                continue
            
            if "error" in r and r["error"] not in ["No username", "no_new_posts"]:
                channels_with_errors += 1
            
            total_parsed += r.get("posts_parsed", 0)
            total_saved += r.get("posts_saved", 0)
            results.append(r)

        # Итоговое логирование
        successful_channels = len([r for r in results if r.get("posts_saved", 0) > 0])
        
        logger.info(
            f"Парсинг завершен:\n"
            f"  - Всего каналов: {len(channels)}\n"
            f"  - Успешно спарсено: {successful_channels}\n"
            f"  - С ошибками: {channels_with_errors}\n"
            f"  - Всего постов получено: {total_parsed}\n"
            f"  - Новых постов сохранено: {total_saved}"
        )
        
        return {
            "results": results,
            "total_parsed": total_parsed,
            "total_saved": total_saved,
            "channels_processed": len(channels),
            "successful_channels": successful_channels,
            "channels_with_errors": channels_with_errors,
        }