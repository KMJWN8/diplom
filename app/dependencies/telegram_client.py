from telethon import TelegramClient

from app.config import settings


class TelegramClientManager:
    def __init__(self):
        self.client = None
        self.is_authenticated = False

    async def get_client(self) -> TelegramClient:
        if self.client is None:
            self.client = TelegramClient(
                settings.SESSION_NAME,
                settings.API_ID,
                settings.API_HASH,
                device_model="Telegram Parser Server",
                system_version="4.16.30-vxCUSTOM",
                app_version="1.0.0",
                timeout=10
            )
            await self.client.start(phone=settings.PHONE_NUMBER)
            self.is_authenticated = True

        if not self.client.is_connected():
            await self.client.connect()

        return self.client

    async def close(self):
        if self.client:
            await self.client.disconnect()


telegram_client = TelegramClientManager()
