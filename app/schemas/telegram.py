from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChannelBase(BaseModel):
    channel_id: int
    username: Optional[str]
    title: str


class ChannelCreate(ChannelBase):
    pass


class ChannelResponse(ChannelBase):
    participants_count: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    channel_id: int
    post_id: int
    message: Optional[str]
    date: datetime
    comments_count: int


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    views: Optional[int]
    forwards: Optional[int]
    media_type: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParseRequest(BaseModel):
    channel_username: str
    limit: int = 100
