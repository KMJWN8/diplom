from datetime import datetime, timezone
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.telegram import Channel, Post
from app.schemas.telegram import ChannelCreate, PostCreate


class TelegramRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.channels = self.db.channels
        self.posts = self.db.posts

    async def get_channel(self, channel_id: int) -> Optional[Channel]:
        channel_data = await self.channels.find_one({"channel_id": channel_id})
        if channel_data:
            return Channel(**channel_data)
        return None

    async def create_channel(self, channel: ChannelCreate) -> Channel:
        channel_data = channel.model_dump()
        channel_data["created_at"] = datetime.now(timezone.utc)
        channel_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.channels.insert_one(channel_data)
        return Channel(**channel_data)

    async def update_channel(
        self, channel_id: int, update_data: dict
    ) -> Optional[Channel]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.channels.update_one(
            {"channel_id": channel_id}, {"$set": update_data}
        )
        return await self.get_channel(channel_id)

    async def get_or_create_channel(self, channel_data: ChannelCreate) -> Channel:
        existing_channel = await self.get_channel(channel_data.channel_id)
        if existing_channel:
            return existing_channel
        return await self.create_channel(channel_data)

    async def create_post(self, post: PostCreate) -> Post:
        post_data = post.model_dump()
        post_data["created_at"] = datetime.now(timezone.utc)

        await self.posts.update_one(
            {"channel_id": post.channel_id, "post_id": post.post_id},
            {"$set": post_data},
            upsert=True,
        )

        saved_post = await self.posts.find_one(
            {"channel_id": post.channel_id, "post_id": post.post_id}
        )

        return Post(**saved_post)

    async def get_posts_by_channel(
        self, channel_id: int, limit: int = 100
    ) -> List[Post]:
        cursor = (
            self.posts.find({"channel_id": channel_id}).sort("date", -1).limit(limit)
        )
        posts = []
        async for post_data in cursor:
            posts.append(Post(**post_data))
        return posts

    async def get_channel_stats(self, channel_id: int) -> dict:
        pipeline = [
            {"$match": {"channel_id": channel_id}},
            {
                "$group": {
                    "_id": "$channel_id",
                    "total_posts": {"$sum": 1},
                    "total_comments": {"$sum": "$comments_count"},
                    "avg_comments": {"$avg": "$comments_count"},
                    "last_post_date": {"$max": "$date"},
                }
            },
        ]

        result = await self.posts.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {}
