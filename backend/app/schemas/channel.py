from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    channel_id: int = Field(..., description="ID канала в Telegram")
    username: Optional[str] = None
    title: str


class ChannelCreate(ChannelBase):
    pass

class ChannelResponse(ChannelBase):
    id: int = Field(..., description="Внутренний ID в базе")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
