from datetime import date, datetime, timezone
from typing import List, Optional, Tuple

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostTopic
from app.services.classification_service import classification_service
from sqlalchemy import and_, func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, joinedload


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def _execute_query_to_responses(self, query) -> List[PostResponse]:
        result = self.session.execute(query)
        posts = result.scalars().all()
        return [post.to_response() for post in posts]

    def bulk_create(self, posts: List[PostCreate]) -> int:
        if not posts:
            return 0

        dicts = []
        for p in posts:
            predicted_topics = classification_service.predict_topics(p.message)
            
            dicts.append(
                {
                    "channel_id": p.channel_id,
                    "post_id": p.post_id,
                    "message": p.message,
                    "date": p.date,
                    "views": p.views,
                    "comments_count": p.comments_count,
                    "topic": predicted_topics,
                    "created_at": datetime.now(timezone.utc),
                }
            )

        stmt = pg_insert(Post).values(dicts)
        stmt = stmt.on_conflict_do_nothing(index_elements=["channel_id", "post_id"])

        self.session.execute(stmt)
        self.session.commit()
        return len(dicts)

    def get_last_post(self, channel_id: int) -> Optional[Post]:
        result = self.session.execute(
            select(Post)
            .where(Post.channel_id == channel_id)
            .order_by(Post.post_id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    def get_posts_by_topic(self, topic: PostTopic) -> List[PostResponse]:
        query = (
            select(Post)
            .options(joinedload(Post.channel))
            .where(Post.topic.contains([topic.value]))
            .order_by(Post.date.desc())
        )
        return self._execute_query_to_responses(query)

    def get_posts_by_topic_and_date(
        self, topic: PostTopic, date_param: date
    ) -> List[PostResponse]:
        query = (
            select(Post)
            .options(joinedload(Post.channel))
            .where(
                and_(
                    func.date(Post.date) == date_param,
                    Post.topic.op('@>')([topic.value]),
                )
            )
            .order_by(Post.date.desc())
        )
        return self._execute_query_to_responses(query)

    def get_posts_by_specific_date(self, date_param: date) -> List[PostResponse]:
        query = (
            select(Post)
            .options(joinedload(Post.channel))
            .where(func.date(Post.date) == date_param)
            .order_by(Post.date)
        )
        return self._execute_query_to_responses(query)

    def get_posts_counts_by_date(
        self, date_from: date, date_to: date
    ) -> List[Tuple[date, int]]:
        result = self.session.execute(
            select(func.date(Post.date), func.count(Post.id))
            .where(Post.date.between(date_from, date_to))
            .group_by(func.date(Post.date))
            .order_by(func.date(Post.date))
        )

        return result.all()

    def get_posts_counts_by_topic(
        self, date_from: date, date_to: date
    ) -> List[Tuple[str, int]]:
        result = self.session.execute(
            text(
                """
                SELECT 
                    jsonb_array_elements_text(topic) as topic_name,
                    COUNT(*) as count
                FROM posts
                WHERE date BETWEEN :date_from AND :date_to
                AND topic != '[]'::jsonb  -- Исключаем пустые массивы
                GROUP BY jsonb_array_elements_text(topic)
                ORDER BY count DESC
            """
            ).bindparams(date_from=date_from, date_to=date_to)
        )

        return result.all()
    