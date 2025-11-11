from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, post: PostCreate) -> Post:
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
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def bulk_create(self, posts: List[PostCreate]) -> int:
        """
        Массовая вставка постов с игнорированием конфликтов (по channel_id + post_id).
        """
        if not posts:
            return 0

        dicts = []
        for p in posts:
            d = {
                "channel_id": p.channel_id,
                "post_id": p.post_id,
                "message": p.message,
                "date": p.date,
                "views": p.views,
                "comments_count": p.comments_count,
                "topic": p.topic,
                "created_at": datetime.now(timezone.utc),
            }
            dicts.append(d)

        stmt = pg_insert(Post).values(dicts)
        stmt = stmt.on_conflict_do_nothing(index_elements=["channel_id", "post_id"])
        await self.session.execute(stmt)
        await self.session.commit()
        return len(dicts)

    async def get_last_post(self, channel_id: int) -> Optional[Post]:
        """
        Возвращает последний (самый новый) пост по каналу.
        """
        result = await self.session.execute(
            select(Post)
            .where(Post.channel_id == channel_id)
            .order_by(Post.post_id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_last_post_date(self, channel_id: int) -> Optional[datetime]:
        result = await self.session.execute(
            select(Post.date)
            .where(Post.channel_id == channel_id)
            .order_by(Post.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_posts_by_topic(
        self, topic: str, limit: int = 100
    ) -> List[PostResponse]:
        result = await self.session.execute(
            select(Post)
            .where(Post.topic == topic)
            .order_by(Post.date.desc())
            .limit(limit)
        )
        posts = result.scalars().all()
        return [PostResponse.model_validate(post) for post in posts]

    async def get_posts_by_date(
        self, date_from: datetime, date_to: datetime
    ) -> List[PostResponse]:
        result = await self.session.execute(
            select(Post)
            .where(Post.date.between(date_from, date_to))
            .order_by(Post.date)
        )
        posts = result.scalars().all()
        return [PostResponse.model_validate(post) for post in posts]

    async def update_post_topic(self, post_id: int, topic: str) -> Optional[Post]:
        result = await self.session.execute(select(Post).where(Post.post_id == post_id))
        post = result.scalar_one_or_none()
        if post:
            post.topic = topic
            await self.session.commit()
            await self.session.refresh(post)
        return post
