from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    channel_id: int = Field(..., description="ID канала в Telegram")
    username: Optional[str] = Field(None, description="Username канала")
    title: str = Field(..., description="Название канала")


class ChannelCreate(ChannelBase):
    participants_count: Optional[int] = Field(None, description="Количество участников")


class ChannelResponse(ChannelBase):
    id: int = Field(..., description="Внутренний ID в базе")
    participants_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
