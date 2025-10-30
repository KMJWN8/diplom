from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Channel(BaseModel):
    channel_id: int
    username: Optional[str] = None
    title: str
    participants_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class Post(BaseModel):
    channel_id: int
    post_id: int
    message: Optional[str] = None
    date: datetime
    views: Optional[int] = None
    comments_count: int = 0
    forwards: Optional[int] = None
    media_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
