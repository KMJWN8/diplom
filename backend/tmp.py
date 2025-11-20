from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings

client = TelegramClient(
    StringSession(),
    settings.API_ID,
    settings.API_HASH,
    device_model="Telegram Parser Server",
    system_version="4.16.30-vxCUSTOM",
    app_version="1.0.0",
)
client.start(phone=settings.PHONE_NUMBER)  # тут введёшь код вручную
print("String session:", client.session.save())
