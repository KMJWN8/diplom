from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("channels.channel_id"), nullable=False, index=True
    )
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint('channel_id', 'post_id', name='uq_channel_post'),
    )
