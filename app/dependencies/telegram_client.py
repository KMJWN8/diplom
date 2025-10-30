from telethon import TelegramClient

from app.config import settings


class TelegramClientManager:
    def __init__(self):
        self.client = None
        self.is_authenticated = False

    async def get_client(self) -> TelegramClient:
        if self.client is None:
            self.client = TelegramClient(
                settings.session_name,
                settings.api_id,
                settings.api_hash,
                device_model="Telegram Parser Server",
                system_version="Linux",
                app_version="1.0.0",
            )
            await self.client.start(phone=settings.phone_number)
            self.is_authenticated = True

        if not self.client.is_connected():
            await self.client.connect()

        return self.client

    async def close(self):
        if self.client:
            await self.client.disconnect()


telegram_client = TelegramClientManager()
