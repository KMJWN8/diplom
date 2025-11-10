from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


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


class PostCreate(BaseModel):
    channel_id: int
    post_id: int
    message: str
    date: datetime
    views: Optional[int] = None
    comments_count: int = 0
    topic: PostTopic = PostTopic.UNCLASSIFIED


class PostResponse(PostCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostTopicUpdate(BaseModel):
    post_id: int
    channel_id: int
    topic: PostTopic
