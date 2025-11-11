from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings


class TelegramClientManager:

    def __init__(self):
        self.client: Optional[TelegramClient] = None

    async def get_client(self) -> TelegramClient:
        if self.client is None:
            session_str = getattr(settings, "TG_SESSION_STRING", None)
            # if not session_str:
            #     raise RuntimeError("TG_SESSION_STRING не задан в настройках (env).")

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
            # await self.client.start(phone=settings.PHONE_NUMBER)

            if not await self.client.is_user_authorized():
                raise RuntimeError(
                    "Telegram client not authorized. Проверьте TG_SESSION_STRING."
                )

        if not self.client.is_connected():
            await self.client.connect()

        return self.client

    async def __aenter__(self):
        return await self.get_client()

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.disconnect()


telegram_client = TelegramClientManager()
