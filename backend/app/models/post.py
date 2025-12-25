from datetime import datetime, timezone
from typing import Optional

from app.core.database import Base
from app.schemas.post import PostResponse, PostTopic
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    Boolean,
    Float,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("channels.channel_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    topic: Mapped[JSONB] = mapped_column(JSONB, default=list, nullable=False)
    is_problem: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    problem_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    problem_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    channel: Mapped["Channel"] = relationship("Channel", back_populates="posts")

    __table_args__ = (
        UniqueConstraint("channel_id", "post_id", name="uq_channel_post"),
        Index("idx_post_date", "date"),
        Index("idx_post_is_problem", "is_problem"),
        Index("idx_post_problem_probability", "problem_probability"),
        Index("idx_post_topic", "topic", postgresql_using="gin"),
        Index("idx_post_channel_date", "channel_id", "date"),
        Index("idx_post_updated_at", "updated_at"),
    )

    def to_response(self) -> PostResponse:
        return PostResponse(
            id=self.id,
            channel_id=self.channel_id,
            channel_name=self.channel.title if self.channel else None,
            post_id=self.post_id,
            message=self.message,
            date=self.date,
            views=self.views,
            comments_count=self.comments_count,
            topic=[PostTopic(t) for t in self.topic],
            is_problem=self.is_problem,
            problem_probability=self.problem_probability,
            problem_confidence=self.problem_confidence,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )