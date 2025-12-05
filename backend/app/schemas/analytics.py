from typing import List

from pydantic import BaseModel, Field


class PostsByDateResponse(BaseModel):
    dates: List[str]
    counts: List[int]


class PostsByTopicResponse(BaseModel):
    topics: List[str]
    counts: List[int]
