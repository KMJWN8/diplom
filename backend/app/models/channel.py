from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.post import Post


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    participants_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    last_parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    posts: Mapped[List["Post"]] = relationship("Post", back_populates="channel")
