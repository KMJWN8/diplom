from pydantic import BaseModel, ConfigDict, Field
from typing import List


class PostsByDateResponse(BaseModel):
    dates: List[str] = Field(example=["2024-01-01", "2024-01-02", "2024-01-03"])
    counts: List[int] = Field(example=[5, 3, 7])


