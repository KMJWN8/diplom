from datetime import datetime, timezone
from typing import List

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.schemas.channel import ChannelCreate


class ChannelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_channel(self, data: ChannelCreate) -> Channel:
        stmt = (
            pg_insert(Channel)
            .values(
                channel_id=data.channel_id,
                username=data.username,
                title=data.title,
                participants_count=data.participants_count,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_update(
                index_elements=["channel_id"],
                set_={
                    "username": data.username,
                    "title": data.title,
                    "participants_count": data.participants_count,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
            .returning(Channel)
        )

        result = self.session.execute(stmt)
        channel = result.scalar_one()
        self.session.commit()

        return channel

    def get_all_channels(self) -> List[Channel]:
        result = self.session.execute(select(Channel))
        return result.scalars().all()

    def update_last_parsed(self, channel_id: int, when: datetime):
        self.session.execute(
            update(Channel)
            .where(Channel.channel_id == channel_id)
            .values(last_parsed_at=when)
        )
        self.session.commit()
