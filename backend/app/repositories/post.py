from datetime import datetime, timezone, date
from typing import List, Optional, Tuple

from sqlalchemy import insert, select, func, cast, Date
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, joinedload

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_post(self, post: PostCreate) -> Post:
        stmt = (
            insert(Post)
            .values(
                channel_id=post.channel_id,
                post_id=post.post_id,
                message=post.message,
                date=post.date,
                views=post.views,
                comments_count=post.comments_count,
                topic=post.topic,
                created_at=datetime.now(timezone.utc),
            )
            .returning(Post)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.scalar_one()

    def bulk_create(self, posts: List[PostCreate]) -> int:
        """
        Массовая вставка постов с игнорированием конфликтов
        (конфликт по channel_id + post_id).
        """
        if not posts:
            return 0

        dicts = [
            {
                "channel_id": p.channel_id,
                "post_id": p.post_id,
                "message": p.message,
                "date": p.date,
                "views": p.views,
                "comments_count": p.comments_count,
                "topic": p.topic,
                "created_at": datetime.now(timezone.utc),
            }
            for p in posts
        ]

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

    def get_last_post_date(self, channel_id: int) -> Optional[datetime]:
        result = self.session.execute(
            select(Post.date)
            .where(Post.channel_id == channel_id)
            .order_by(Post.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    def get_posts_by_topic(self, topic: str) -> List[PostResponse]:
        result = self.session.execute(
            select(Post).where(Post.topic == topic).order_by(Post.date.desc())
        )
        posts = result.scalars().all()
        return [PostResponse.model_validate(post) for post in posts]

    def get_posts_by_specific_date(self, date: date) -> List[PostResponse]:
        result = self.session.execute(
            select(Post)
            .options(joinedload(Post.channel))
            .where(cast(Post.date, Date) == date)
            .order_by(Post.date)
        )
        posts = result.scalars().all()
        return [PostResponse(
            id=post.id,
            channel_id=post.channel_id,
            channel_name=post.channel.title,  # получаем название из relationship
            post_id=post.post_id,
            message=post.message,
            date=post.date,
            views=post.views,
            comments_count=post.comments_count,
            topic=post.topic,
            created_at=post.created_at
        ) for post in posts]
    
    def get_posts_count_by_date(
            self, date_from: date, date_to: date
    ) -> List[Tuple[date, int]]:
        result = self.session.execute(
            select(cast(Post.date, Date), func.count(Post.id))
            .where(Post.date.between(date_from, date_to))
            .group_by(cast(Post.date, Date))
            .order_by(cast(Post.date, Date))
        )

        return result.all()

    def get_posts_count_by_topics(
            self
    ) -> List[Tuple[str, int]]:
        result = self.session.execute(
            select(Post.topic, func.count(Post.id))
            .group_by(Post.topic)
            .order_by(func.count(Post.id).desc())
        )

        return result.all()

    def update_post_topic(self, post_id: int, topic: str) -> Optional[Post]:
        result = self.session.execute(select(Post).where(Post.post_id == post_id))
        post = result.scalar_one_or_none()

        if post:
            post.topic = topic
            self.session.commit()
            self.session.refresh(post)

        return post
