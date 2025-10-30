from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.database


async def init_db():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.mongodb_db_name]

    # Создаем индексы
    await db.database.channels.create_index("channel_id", unique=True)
    await db.database.posts.create_index(
        [("channel_id", 1), ("post_id", 1)], unique=True
    )


async def close_db():
    db.client.close()
