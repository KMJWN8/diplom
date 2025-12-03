from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PostTopic(str, Enum):
    ENVIRONMENT = "environment"
    MANUFACTURE = "manufacture"
    EMPLOYMENT = "employment"
    FINANCEANDCREDIT = "financesandcredit"
    HOMEANDINFRASTRUCTURE = "homeandinfrastructure"
    HEALTHSERVICE = "healthservice"
    EDUCATIONANDSPORT = "educationandsport"
    SOCIALSPHERE = "socialsphere"
    POLITICS = "politics"
    CRIMINALITY = "criminality"
    DEMOGRAPHIC = "demographic"
    UNCLASSIFIED = "unclassified"


class PostCreate(BaseModel):
    channel_id: int
    post_id: int
    message: str
    date: datetime
    views: Optional[int] = None
    comments_count: int = 0
    topic: str


class PostResponse(PostCreate):
    id: int
    created_at: datetime
    channel_name: str

    model_config = ConfigDict(from_attributes=True)


class PostTopicUpdate(BaseModel):
    post_id: int
    channel_id: int
    topic: PostTopic
