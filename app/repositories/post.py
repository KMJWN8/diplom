from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, UnclassifiedPostResponse, PostTopicUpdate


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, post: PostCreate) -> Post:
        # Проверяем существование поста
        existing_post = await self.session.execute(
            select(Post).where(
                Post.channel_id == post.channel_id,
                Post.post_id == post.post_id
            )
        )
        existing_post = existing_post.scalar_one_or_none()

        if existing_post:
            # Обновляем существующий пост
            for field, value in post.model_dump().items():
                if hasattr(existing_post, field):
                    setattr(existing_post, field, value)
            db_post = existing_post
        else:
            # Создаем новый пост
            db_post = Post(
                **post.model_dump(),
                created_at=datetime.now(timezone.utc)
            )
            self.session.add(db_post)

        await self.session.commit()
        await self.session.refresh(db_post)
        return db_post

    async def get_posts_by_channel(self, channel_id: int, limit: int = 100) -> List[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.channel_id == channel_id)
            .order_by(Post.date.desc())
            .limit(limit)
        )
        return result.scalars().all()


    async def get_posts_by_topic(self, topic: str, limit: int = 100) -> List[PostResponse]:
        """Получить посты по теме"""
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
        return result.scalars().all()

    async def get_unclassified_posts(self, limit: int = 100) -> List[UnclassifiedPostResponse]:
        """Получить посты без классификации (topic = 'unclassified')"""
        result = await self.session.execute(
            select(Post)
            .where(Post.topic == 'unclassified')
            .order_by(Post.date.desc())
            .limit(limit)
        )
        posts = result.scalars().all()
        return [UnclassifiedPostResponse.model_validate(post) for post in posts]
    
    async def update_post_topic(self, post_id: int, channel_id: int, topic: str) -> Optional[Post]:
        """Обновить тему поста"""
        result = await self.session.execute(
            select(Post)
            .where(Post.post_id == post_id, Post.channel_id == channel_id)
        )
        post = result.scalar_one_or_none()
        
        if post:
            post.topic = topic
            await self.session.commit()
            await self.session.refresh(post)
        
        return post
    
    async def bulk_update_post_topics(self, updates: List[PostTopicUpdate]) -> int:
        """Массовое обновление тем постов - ОПТИМИЗИРОВАННАЯ версия"""
        if not updates:
            return 0
        
        # Собираем все условия для обновления
        update_cases = []
        for update in updates:
            update_cases.append(
                (update.post_id, update.channel_id, update.topic)
            )
        
        # Создаем SQL выражение для массового обновления
        from sqlalchemy import case
        
        # Строим CASE выражение для topic
        case_stmt = case(
            *[
                (
                    (Post.post_id == post_id) & (Post.channel_id == channel_id),
                    topic
                )
                for post_id, channel_id, topic in update_cases
            ],
            else_=Post.topic  # если условие не подошло, оставляем старое значение
        )
        
        # Выполняем одно массовое обновление
        stmt = (
            update(Post)
            .where(
                # Обновляем только те посты, которые есть в нашем списке
                (Post.post_id, Post.channel_id).in_(
                    [(post_id, channel_id) for post_id, channel_id, _ in update_cases]
                )
            )
            .values(topic=case_stmt)
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount  # возвращаем количество обновленных строк
    