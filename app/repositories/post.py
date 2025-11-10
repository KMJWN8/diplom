from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, post: PostCreate) -> Post:
        stmt = insert(Post).values(
            post_id=post.post_id,
            message=post.message,
            date=post.date,
            views=post.views,
            comments_count=post.comments_count,
            created_at=datetime.now(timezone.utc),
        ).returning(Post)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def bulk_create(self, posts: List[PostCreate]) -> int:
        """
        Пытаемся выполнить bulk insert с игнорированием конфликтов (Postgres).
        Возвращаем количество вставленных записей (приблизительно).
        """
        if not posts:
            return 0

        dicts = []
        for p in posts:
            d = {
                "post_id": p.post_id,
                "message": p.message,
                "date": p.date,
                "views": p.views,
                "comments_count": p.comments_count,
                "forwards": p.forwards,
                "created_at": datetime.now(timezone.utc),
            }
            dicts.append(d)

        try:
            stmt = pg_insert(Post).values(dicts)
            stmt = stmt.on_conflict_do_nothing(index_elements=["post_id"])
            result = await self.session.execute(stmt)
            await self.session.commit()
            return len(dicts)
        except Exception:
            # fallback: поштучный insert с игнорированием дубликатов
            inserted = 0
            for d in dicts:
                try:
                    stmt = insert(Post).values(**d).returning(Post)
                    res = await self.session.execute(stmt)
                    await self.session.commit()
                    inserted += 1
                except Exception:
                    await self.session.rollback()
                    continue
            return inserted

    async def get_posts_by_topic(self, topic: str, limit: int = 100) -> List[PostResponse]:
        result = await self.session.execute(
            select(Post)
            .where(Post.topic == topic)
            .order_by(Post.date.desc())
            .limit(limit)
        )
        posts = result.scalars().all()
        return [PostResponse.model_validate(post) for post in posts]

    async def get_posts_by_date(self, date_from: datetime, date_to: datetime) -> List[PostResponse]:
        result = await self.session.execute(
            select(Post)
            .where(Post.date.between(date_from, date_to))
            .order_by(Post.date)
        )
        posts = result.scalars().all()
        return [PostResponse.model_validate(post) for post in posts]

    async def get_unclassified_posts(self, limit: int = 100) -> List[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.topic == 'unclassified')
            .order_by(Post.date.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def update_post_topic(self, post_id: int, topic: str) -> Optional[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.post_id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if post:
            post.topic = topic
            await self.session.commit()
            await self.session.refresh(post)
        
        return post