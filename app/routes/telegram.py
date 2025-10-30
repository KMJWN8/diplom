from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from telethon import TelegramClient

from app.database import get_database
from app.dependencies.telegram_client import telegram_client
from app.exceptions.custom_exceptions import (
    ChannelNotFoundException,
    RateLimitException,
)
from app.repositories.telegram_repository import TelegramRepository
from app.schemas.telegram import ParseRequest
from app.services.telegram_service import TelegramService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/parse-channel")
async def parse_channel(
    parse_request: ParseRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    client: TelegramClient = Depends(telegram_client.get_client),
):
    try:
        repository = TelegramRepository(db)
        service = TelegramService(client, repository)

        result = await service.parse_channel_posts(parse_request)
        return {
            "status": "success",
            "message": f"Успешно спаршено {result['posts_parsed']} постов",
            "data": result,
        }

    except ChannelNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RateLimitException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


@router.get("/channel-info/{channel_username}")
async def get_channel_info(
    channel_username: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    client: TelegramClient = Depends(telegram_client.get_client),
):
    try:
        repository = TelegramRepository(db)
        service = TelegramService(client, repository)

        channel_info = await service.get_channel_info(channel_username)
        return {"status": "success", "data": channel_info}

    except ChannelNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/posts/{channel_id}")
async def get_channel_posts(
    channel_id: int, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database)
):
    repository = TelegramRepository(db)
    posts = await repository.get_posts_by_channel(channel_id, limit)

    return {"status": "success", "data": posts}


@router.get("/stats/{channel_id}")
async def get_channel_stats(
    channel_id: int, db: AsyncIOMotorDatabase = Depends(get_database)
):
    repository = TelegramRepository(db)
    stats = await repository.get_channel_stats(channel_id)

    return {"status": "success", "data": stats}
