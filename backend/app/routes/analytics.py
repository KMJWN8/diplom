from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.repositories.post import PostRepository
from datetime import date

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/posts-by-date")
async def get_posts_by_date(
    date_from: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    date_to: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    db: Session = Depends(get_session)
):
    repo = PostRepository(db)
    data = repo.get_posts_count_by_date(date_from, date_to)

    dates = [item[0].isoformat() for item in data]
    counts = [item[1] for item in data]

    return {
        "dates": dates,
        "counts": counts
    }

@router.post("/posts-by-specific-date")
async def get_posts_by_specific_date(
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"), 
    db: Session = Depends(get_session)
):
    repo = PostRepository(db)
    posts = repo.get_posts_by_specific_date(date)

    return posts

