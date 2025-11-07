import asyncio
from typing import List, Dict, Any, Union
from celery import Celery, shared_task

from app.config import settings
from app.database import async_session_maker
from app.custom_classes.telegram_parser import TelegramParser
from app.services.parser_service import ChannelService
from app.repositories.channel import ChannelRepository
from app.repositories.post import PostRepository
from app.dependencies.telegram_client import TelegramClientManager

celery = Celery(
    'parser',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@shared_task(bind=True)
def parse_channels_task(self, channels_data: Union[str, List[Dict[str, Any]]], limit: int = 100):
    """
    УНИВЕРСАЛЬНАЯ задача для парсинга:
    - одного канала (передаем строку с ссылкой)
    - нескольких каналов (передаем список словарей)
    """
    async def run_parsing():
        client = await TelegramClientManager.get_client()
        
        async with async_session_maker() as session:
            # Инициализируем репозитории, парсер и сервис
            channel_repo = ChannelRepository(session)
            post_repo = PostRepository(session)
            parser = TelegramParser(client)
            channel_service = ChannelService(parser, channel_repo, post_repo)
            
            # Определяем тип входных данных
            if isinstance(channels_data, str):
                # Парсим один канал
                return await _parse_single_channel(channel_service, channels_data, limit)
            elif isinstance(channels_data, list):
                # Парсим несколько каналов
                return await _parse_multiple_channels(self, channel_service, channels_data)
            else:
                raise ValueError("Неправильный формат данных. Ожидается строка или список")
    
    return asyncio.run(run_parsing())


async def _parse_single_channel(
    channel_service: ChannelService, 
    channel_link: str, 
    limit: int
) -> Dict[str, Any]:
    """Парсинг одного канала"""
    try:
        result = await channel_service.parse_and_save_channel(channel_link, limit)
        return {
            "type": "single",
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "type": "single", 
            "status": "error",
            "channel_link": channel_link,
            "error": str(e)
        }


async def _parse_multiple_channels(
    task, 
    channel_service: ChannelService, 
    channels: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Парсинг нескольких каналов"""
    results = []
    total_channels = len(channels)
    
    for index, channel_data in enumerate(channels):
        try:
            # Извлекаем данные канала
            channel_link = channel_data.get("url") or channel_data.get("channel_link")
            limit = channel_data.get("limit", 100)
            channel_name = channel_data.get("name", "Unknown")
            
            if not channel_link:
                results.append({
                    "status": "error",
                    "channel_name": channel_name,
                    "error": "Отсутствует ссылка на канал"
                })
                continue
            
            # Парсим канал через сервис
            result = await channel_service.parse_and_save_channel(channel_link, limit)
            result["channel_name"] = channel_name
            results.append({
                "status": "success",
                **result
            })
            
            # Обновляем прогресс
            task.update_state(
                state='PROGRESS',
                meta={
                    'current': index + 1,
                    'total': total_channels,
                    'progress': ((index + 1) / total_channels) * 100,
                    'message': f'Обработано {index + 1} из {total_channels} каналов',
                    'processed_channels': results
                }
            )
            
            # Задержка между каналами
            await asyncio.sleep(5)
            
        except Exception as e:
            results.append({
                "status": "error",
                "channel_name": channel_data.get("name", "Unknown"),
                "error": str(e)
            })
            continue
    
    return {
        "type": "multiple",
        "total_channels": total_channels,
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"]),
        "results": results
    }