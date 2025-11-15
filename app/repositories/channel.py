from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.schemas.channel import ChannelCreate

class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_link(self, channel_link: str) -> Optional[Channel]:
        """
        Ищет канал по username, ссылке или id (если вдруг был добавлен без username).
        """
        username = channel_link.replace("https://t.me/", "").replace("@", "").strip()

        stmt = select(Channel).where((Channel.username == username))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_channel(self, data: ChannelCreate) -> Channel:
        """
        Используем INSERT ... ON CONFLICT для атомарной операции.
        """
        stmt = (
            insert(Channel)
            .values(
                channel_id=data.channel_id,
                username=data.username,
                title=data.title,
                participants_count=data.participants_count,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_update(
                index_elements=['channel_id'],
                set_={
                    'username': data.username,
                    'title': data.title,
                    'participants_count': data.participants_count,
                    'updated_at': datetime.now(timezone.utc),
                }
            )
            .returning(Channel)
        )
        
        result = await self.session.execute(stmt)
        channel = result.scalar_one()
        await self.session.commit()
        
        return channel

    async def get_all_channels(self):
        result = await self.session.execute(select(Channel))
        return result.scalars().all()

    async def update_last_parsed(self, channel_id: int, when: datetime):
        await self.session.execute(
            update(Channel)
            .where(Channel.channel_id == channel_id)
            .values(last_parsed_at=when)
        )
        await self.session.commit()

    async def update_last_checked(self, channel_id: int, when: datetime):
        await self.session.execute(
            update(Channel)
            .where(Channel.channel_id == channel_id)
            .values(last_checked_at=when)
        )
        await self.session.commit()
