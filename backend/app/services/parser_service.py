from typing import Any, Dict, List, Optional

from app.custom_classes.telegram_parser import TelegramParser
from app.repositories.post import PostRepository
from app.schemas.post import PostCreate


class ParserService:

    def __init__(self, parser: TelegramParser, post_repo: PostRepository):
        self.parser = parser
        self.post_repo = post_repo

    async def parse_and_save_posts(
        self,
        channel_link: str,
        channel_id: int,
        last_post_id: Optional[int] = None,
        delay: float = 0.1,
    ) -> Dict[str, Any]:

        info = await self.parser.get_channel_info(channel_link)
        entity = info["entity"]

        posts_data = await self.parser.parse_posts(
            entity, delay=delay, min_id=last_post_id
        )

        valid_posts: List[PostCreate] = []
        for post in posts_data:
            if last_post_id is not None and int(post["post_id"]) <= last_post_id:
                continue

            post["channel_id"] = channel_id
            valid_posts.append(PostCreate(**post))

        inserted = self.post_repo.bulk_create(valid_posts)

        return {
            "posts_parsed": len(posts_data),
            "posts_saved": inserted,
            "status": "completed" if inserted else "no_new_posts",
            "last_post_date": valid_posts[-1].date if valid_posts else None,
        }
