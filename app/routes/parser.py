from fastapi import APIRouter, HTTPException
from typing import Union
from app.services.parser_service import ParserService
from app.schemas.parse import ParseRequest, MultipleChannelsRequest

router = APIRouter()

@router.post("/parse")
async def parse_channels(request_data: Union[ParseRequest, MultipleChannelsRequest]):
    """
    УНИВЕРСАЛЬНЫЙ endpoint для парсинга
    """
    try:
        if hasattr(request_data, 'channel_link'):
            # Парсим один канал
            task_id = ParserService.parse(request_data.channel_link, request_data.limit)
            return {
                "task_id": task_id,
                "type": "single",
                "status": "started",
                "channel_link": request_data.channel_link
            }
        else:
            # Парсим несколько каналов
            task_id = ParserService.parse(request_data.channels)
            return {
                "task_id": task_id,
                "type": "multiple", 
                "status": "started",
                "channels_count": len(request_data.channels)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))