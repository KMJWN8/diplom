from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings


class TelegramClientManager:
    """
    Асинхронный контекстный менеджер для TelegramClient.
    - Создает клиента при входе в контекст.
    - Отключает клиента при выходе.
    - Подходит для однократного использования в рамках одной операции.
    """

    def __init__(self):
        self.client: Optional[TelegramClient] = None

    async def __aenter__(self) -> TelegramClient:
        self.client = TelegramClient(
            (
                StringSession(settings.TG_SESSION_STRING)
                if settings.TG_SESSION_STRING
                else None
            ),
            settings.API_ID,
            settings.API_HASH,
            device_model="Telegram Parser Server",
            system_version="4.16.30-vxCUSTOM",
            app_version="1.0.0",
            timeout=10,
        )

        await self.client.connect()

        if not await self.client.is_user_authorized():
            raise RuntimeError(
                "Telegram client not authorized. Проверьте TG_SESSION_STRING."
            )

        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client and self.client.is_connected():
            await self.client.disconnect()
        self.client = None
