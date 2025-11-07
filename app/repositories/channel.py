from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.schemas.channel import ChannelCreate


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_channel(self, channel_id: int) -> Optional[Channel]:
        result = await self.session.execute(
            select(Channel).where(Channel.channel_id == channel_id)
        )
        return result.scalar_one_or_none()

    async def create_channel(self, channel: ChannelCreate) -> Channel:
        db_channel = Channel(
            **channel.model_dump(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.session.add(db_channel)
        await self.session.commit()
        await self.session.refresh(db_channel)
        return db_channel

    async def update_channel(self, channel_id: int, update_data: dict) -> Optional[Channel]:
        # Исключаем поля, которые не должны обновляться напрямую
        update_data = update_data.copy()
        update_data.pop("id", None)
        update_data.pop("channel_id", None)
        update_data.pop("created_at", None)
        update_data["updated_at"] = datetime.now(timezone.utc)

        stmt = (
            update(Channel)
            .where(Channel.channel_id == channel_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        return await self.get_channel(channel_id)

    async def get_or_create_channel(self, channel_data: ChannelCreate) -> Channel:
        existing_channel = await self.get_channel(channel_data.channel_id)
        if existing_channel:
            return existing_channel
        return await self.create_channel(channel_data)