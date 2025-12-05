from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostTopic
from app.services.classification_service import classification_service
from sqlalchemy import Date, and_, func, insert, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, joinedload


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def bulk_create(self, posts: List[PostCreate]) -> int:
        """
        Массовая вставка постов с игнорированием конфликтов
        (конфликт по channel_id + post_id).
        """
        if not posts:
            return 0

        dicts = []
        for p in posts:
            # classification_service возвращает список строк (topic names)
            # Например: ["environment", "politics", "education"]
            topic_strings = classification_service.predict_topics(p.message)

            # Маппинг строк из classification_service в PostTopic Enum
            # Нужно убедиться, что строки соответствуют значениям PostTopic
            validated_topics = []
            for topic_str in topic_strings:
                # Пробуем найти соответствующий Enum
                # Приводим к нижнему регистру для сравнения
                topic_str_lower = topic_str.lower().strip()

                # Сопоставляем строки из классификатора с PostTopic Enum
                # Возможно, нужно будет настроить маппинг
                topic_mapping = {
                    "environment": PostTopic.ENVIRONMENT,
                    "manufacture": PostTopic.MANUFACTURE,
                    "employment": PostTopic.EMPLOYMENT,
                    "financesandcredit": PostTopic.FINANCEANDCREDIT,
                    "homeandinfrastructure": PostTopic.HOMEANDINFRASTRUCTURE,
                    "healthservice": PostTopic.HEALTHSERVICE,
                    "educationandsport": PostTopic.EDUCATIONANDSPORT,
                    "socialsphere": PostTopic.SOCIALSPHERE,
                    "politics": PostTopic.POLITICS,
                    "criminality": PostTopic.CRIMINALITY,
                    "demographic": PostTopic.DEMOGRAPHIC,
                    "unclassified": PostTopic.UNCLASSIFIED,
                }

                if topic_str_lower in topic_mapping:
                    validated_topics.append(topic_mapping[topic_str_lower].value)
                else:
                    try:
                        for enum_member in PostTopic:
                            if enum_member.value.lower() == topic_str_lower:
                                validated_topics.append(enum_member.value)
                                break
                    except:
                        validated_topics.append(PostTopic.UNCLASSIFIED.value)

            dicts.append(
                {
                    "channel_id": p.channel_id,
                    "post_id": p.post_id,
                    "message": p.message,
                    "date": p.date,
                    "views": p.views,
                    "comments_count": p.comments_count,
                    "topic": validated_topics,  # JSON массив строк
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
        result = self.session.execute(
            select(Post)
            .options(joinedload(Post.channel))
            .where(Post.topic.contains([topic.value]))
            .order_by(Post.date.desc())
        )
        posts = result.scalars().all()

        return [
            PostResponse(
                id=post.id,
                channel_id=post.channel_id,
                channel_name=post.channel.title if post.channel else None,
                post_id=post.post_id,
                message=post.message,
                date=post.date,
                views=post.views,
                comments_count=post.comments_count,
                topic=[PostTopic(t) for t in post.topic],
                created_at=post.created_at,
            )
            for post in posts
        ]

    def get_posts_by_topic_and_date(
        self, topic: PostTopic, date_param: date
    ) -> List[PostResponse]:
        result = self.session.execute(
            select(Post)
            .options(joinedload(Post.channel))
            .where(
                and_(
                    func.date(Post.date) == date_param,
                    Post.topic.contains([topic.value]),
                )
            )
            .order_by(Post.date.desc())
        )

        posts = result.scalars().all()

        return [
            PostResponse(
                id=post.id,
                channel_id=post.channel_id,
                channel_name=post.channel.title if post.channel else None,
                post_id=post.post_id,
                message=post.message,
                date=post.date,
                views=post.views,
                comments_count=post.comments_count,
                topic=[PostTopic(t) for t in post.topic],
                created_at=post.created_at,
            )
            for post in posts
        ]

    def get_posts_by_specific_date(self, date_param: date) -> List[PostResponse]:
        result = self.session.execute(
            select(Post)
            .options(joinedload(Post.channel))
            .where(func.date(Post.date) == date_param)
            .order_by(Post.date)
        )

        posts = result.scalars().all()

        return [
            PostResponse(
                id=post.id,
                channel_id=post.channel_id,
                channel_name=post.channel.title if post.channel else None,
                post_id=post.post_id,
                message=post.message,
                date=post.date,
                views=post.views,
                comments_count=post.comments_count,
                topic=[PostTopic(t) for t in post.topic],
                created_at=post.created_at,
            )
            for post in posts
        ]

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
        """
        Подсчет постов по темам.
        Используем jsonb_array_elements_text для "разворачивания" JSONB массива.
        """
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

    def get_topics_statistics(self) -> Dict[str, int]:
        """
        Получить статистику по всем темам.
        """
        result = self.session.execute(
            text(
                """
                SELECT 
                    jsonb_array_elements_text(topic) as topic_name,
                    COUNT(*) as count
                FROM posts
                WHERE topic != '[]'::jsonb
                GROUP BY jsonb_array_elements_text(topic)
                ORDER BY count DESC
            """
            )
        )

        stats = {}
        for row in result:
            stats[row[0]] = row[1]

        return stats
