from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    channel_id: int
    username: Optional[str] = None
    title: str


class ChannelCreate(ChannelBase):
    participants_count: Optional[int] = None


class ChannelResponse(ChannelBase):
    participants_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    channel_id: int
    post_id: int
    message: str
    date: datetime
    comments_count: int


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    views: Optional[int] = None
    forwards: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParseRequest(BaseModel):
    channel_link: str = Field(
        ..., description="Ссылка на канал (t.me/...) или username"
    )
    limit: int = Field(100, ge=1, le1=1000, description="Лимит постов для парсинга")
