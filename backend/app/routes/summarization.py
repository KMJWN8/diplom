from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.schemas.post import Summary
from app.tasks.summarizator import summarize_text_task
from app.core.celery_app import celery_app

router = APIRouter(prefix="/summarization", tags=["summarization"])


@router.post("/summarize", response_model=Summary)
async def summarize_text(request: Summary) -> Summary:
    """Суммаризация текста"""
    try:
        if not request.summary or not request.summary.strip():
            raise HTTPException(status_code=400, detail="Текст для суммаризации пуст")
        
        # Проверяем длину текста (опционально)
        if len(request.summary) > 10000:
            raise HTTPException(
                status_code=400, 
                detail=f"Текст слишком длинный ({len(request.summary)} символов). Максимум 10000 символов."
            )
        
        # Запускаем задачу
        task = summarize_text_task.delay(request.summary)
        
        # Ждем результат (можно настроить таймаут под ваши нужды)
        task_result = task.get(timeout=300)  # 5 минут таймаут
        
        return Summary(summary=task_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize-async")
async def summarize_text_async(request: Summary):
    """Асинхронная суммаризация с возвратом task_id"""
    try:
        if not request.summary or not request.summary.strip():
            raise HTTPException(status_code=400, detail="Текст для суммаризации пуст")
        
        # Проверяем длину текста
        if len(request.summary) > 10000:
            raise HTTPException(
                status_code=400, 
                detail=f"Текст слишком длинный ({len(request.summary)} символов). Максимум 10000 символов."
            )
        
        # Запускаем задачу и возвращаем только task_id
        task = summarize_text_task.delay(request.summary)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "Задача на суммаризацию запущена"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """Получение результата задачи по task_id"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.state,
            "ready": task_result.ready()
        }
        
        if task_result.state == 'SUCCESS':
            response["result"] = task_result.result
        elif task_result.state == 'FAILURE':
            response["error"] = str(task_result.result)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))