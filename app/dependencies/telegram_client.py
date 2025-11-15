from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings


class TelegramClientManager:
    """Менеджер, который создает нового клиента для каждого контекста"""
    
    async def __aenter__(self) -> TelegramClient:
        client = TelegramClient(
            StringSession(settings.TG_SESSION_STRING) if settings.TG_SESSION_STRING else None,
            settings.API_ID,
            settings.API_HASH,
            device_model="Telegram Parser Server",
            system_version="4.16.30-vxCUSTOM",
            app_version="1.0.0",
            timeout=10,
        )

        await client.connect()

        if not await client.is_user_authorized():
            raise RuntimeError("Telegram client not authorized. Проверьте TG_SESSION_STRING.")

        return client

    async def __aexit__(self, exc_type, exc, tb):
        """Клиент автоматически закрывается при выходе из контекста"""
        pass

telegram_client = TelegramClientManager()