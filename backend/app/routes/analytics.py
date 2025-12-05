from datetime import date
from typing import List

from app.core.database import get_session
from app.repositories.post import PostRepository
from app.schemas.post import PostsByDateResponse, PostsByTopicResponse
from app.schemas.post import PostResponse, PostTopic
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/posts-count-by-date")
async def get_posts_count_by_date(
    date_from: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    date_to: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_session),
) -> PostsByDateResponse:
    repo = PostRepository(db)
    data = repo.get_posts_counts_by_date(date_from, date_to)

    dates = [item[0].isoformat() for item in data]
    counts = [item[1] for item in data]

    return {"dates": dates, "counts": counts}


@router.get("/posts-count-by-topic")
async def get_posts_count_by_topic(
    date_from: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    date_to: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_session),
) -> PostsByTopicResponse:
    repo = PostRepository(db)
    data = repo.get_posts_counts_by_topic(date_from, date_to)

    topics = [item[0] for item in data]
    counts = [item[1] for item in data]

    return {"topics": topics, "counts": counts}


@router.get("/posts-by-specific-date")
async def get_posts_by_specific_date(
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_session),
) -> List[PostResponse]:
    repo = PostRepository(db)
    posts = repo.get_posts_by_specific_date(date)

    return posts


@router.get("/posts-by-topic")
async def get_posts_by_topic(
    topic: PostTopic = PostTopic.UNCLASSIFIED, db: Session = Depends(get_session)
) -> List[PostResponse]:
    repo = PostRepository(db)
    posts = repo.get_posts_by_topic(topic)

    return posts


@router.get("/posts-by-date-and-topic")
async def get_posts_by_date_and_topic(
    topic: PostTopic = PostTopic.UNCLASSIFIED,
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_session),
) -> List[PostResponse]:
    repo = PostRepository(db)
    posts = repo.get_posts_by_topic_and_date(topic, date)

    return posts
