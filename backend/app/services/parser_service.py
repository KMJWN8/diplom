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
        limit: int = 2000,
    ) -> Dict[str, Any]:

        info = await self.parser.get_channel_info(channel_link)
        entity = info["entity"]

        posts_data = await self.parser.parse_posts(
            entity, delay=delay, last_post_id=last_post_id, limit=limit
        )

        if not posts_data:
            return {
                "posts_parsed": 0,
                "posts_saved": 0,
                "status": "no_new_posts",
                "last_post_date": None,
                "new_last_post_id": last_post_id,
            }

        valid_posts: List[PostCreate] = []
        for post in posts_data:
            if last_post_id and post["post_id"] <= last_post_id:
                continue

            post["channel_id"] = channel_id
            valid_posts.append(PostCreate(**post))

        inserted = self.post_repo.bulk_create(valid_posts)

        new_last_post_id = (
            max(p["post_id"] for p in posts_data) if posts_data else last_post_id
        )

        return {
            "posts_parsed": len(posts_data),
            "posts_saved": inserted,
            "status": "completed" if inserted else "no_new_posts",
            "last_post_date": valid_posts[-1].date if valid_posts else None,
            "new_last_post_id": new_last_post_id,
        }
