# app/schemas/post.py
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field


class PostTopic(str, Enum):
    ENVIRONMENT = "environment"
    MANUFACTURE = "manufacture"
    EMPLOYMENT = "employment"
    FINANCESANDCREDIT = "financesandcredit"
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
    topic: List[str] = []

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: List[str]) -> List[str]:
        """Валидирует список тем, оставляя только допустимые значения."""
        if not isinstance(v, list):
            return []
        
        validated = []
        valid_topics = {t.value for t in PostTopic}
        
        for topic in v:
            if isinstance(topic, str):
                clean_topic = topic.lower().strip()
                if clean_topic in valid_topics:
                    validated.append(clean_topic)
                else:
                    validated.append(PostTopic.UNCLASSIFIED.value)
        
        return list(dict.fromkeys(validated))


class PostResponse(PostCreate):
    id: int
    created_at: datetime
    channel_name: Optional[str] = None
    is_problem: bool = Field(default=False, description="Является ли пост проблемой")
    problem_probability: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0, 
        description="Вероятность того, что это проблема"
    )
    problem_confidence: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0, 
        description="Уверенность модели в предсказании"
    )
    model_config = ConfigDict(from_attributes=True)

class PostsByDateResponse(BaseModel):
    dates: List[str]
    counts: List[int]

class PostsByTopicResponse(BaseModel):
    topics: List[str]
    counts: List[int]

class Summary(BaseModel):
    summary: str