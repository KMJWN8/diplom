from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PostTopic(str, Enum):
    TECHNOLOGY = "technology"
    POLITICS = "politics"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    HEALTH = "health"
    SCIENCE = "science"
    OTHER = "other"
    UNCLASSIFIED = "unclassified"


class PostBase(BaseModel):
    channel_id: int = Field(..., description="ID канала")
    post_id: int = Field(..., description="ID поста в канале")
    message: str = Field(..., description="Текст поста")
    date: datetime = Field(..., description="Дата публикации")
    comments_count: int = Field(0, description="Количество комментариев")


class PostCreate(PostBase):
    topic: str = Field(PostTopic.UNCLASSIFIED, description="Тема поста")
    views: Optional[int] = Field(None, description="Количество просмотров")
    forwards: Optional[int] = Field(None, description="Количество пересылок")


class PostResponse(PostBase):
    id: int = Field(..., description="Внутренний ID в базе")
    topic: str = Field(..., description="Тема поста")
    views: Optional[int] = None
    forwards: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostTopicUpdate(BaseModel):
    post_id: int = Field(..., description="ID поста")
    channel_id: int = Field(..., description="ID канала")
    topic: str = Field(..., description="Новая тема поста")


# Схема для массового обновления тем
class BulkPostTopicUpdate(BaseModel):
    updates: List[PostTopicUpdate] = Field(..., description="Список обновлений тем")


# Схема для постов, ожидающих классификацию
class UnclassifiedPostResponse(BaseModel):
    id: int
    channel_id: int
    post_id: int
    message: str
    date: datetime

    model_config = ConfigDict(from_attributes=True)
