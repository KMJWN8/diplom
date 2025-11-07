from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.schemas.channel import ChannelResponse

class ParseRequest(BaseModel):
    channel_link: str = Field(
        ..., description="Ссылка на канал (t.me/...) или username"
    )
    limit: int = Field(100, ge=1, le=1000, description="Лимит постов для парсинга")


class MultipleChannelsRequest(BaseModel):
    channels: List[Dict[str, Any]]


class ParseResponse(BaseModel):
    channel: ChannelResponse
    posts_parsed: int = Field(..., description="Количество спарсенных постов")
    posts_classified: int = Field(0, description="Количество классифицированных постов")