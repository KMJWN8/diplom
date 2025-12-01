from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.repositories.post import PostRepository
from app.schemas.analytics import PostsByDateResponse
from app.schemas.post import PostResponse
from datetime import date
from typing import List

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/posts-by-date")
async def get_posts_count_by_date(
    date_from: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    date_to: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    db: Session = Depends(get_session)
) -> PostsByDateResponse:
    repo = PostRepository(db)
    data = repo.get_posts_count_by_date(date_from, date_to)

    dates = [item[0].isoformat() for item in data]
    counts = [item[1] for item in data]

    return {
        "dates": dates,
        "counts": counts
    }

@router.get("/posts-by-specific-date")
async def get_posts_by_specific_date(
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    db: Session = Depends(get_session)
) -> List[PostResponse]:
    repo = PostRepository(db)
    posts = repo.get_posts_by_specific_date(date)

    return posts

