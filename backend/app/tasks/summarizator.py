from celery import shared_task
import httpx
import json

# Конфигурация внешнего API
EXTERNAL_API_URL = "http://10.0.113.125:8000/v1/chat/completions"
TIMEOUT = 300  # 5 минут


@shared_task(name="summarize_text")
def summarize_text_task(text: str) -> str:
    """Таска для суммаризации текста через внешнее API"""
    try:
        if not text or not text.strip():
            return "Ошибка: текст для суммаризации пуст"
        
        # Формируем промпт для суммаризации
        prompt = f"""Пожалуйста, суммируй следующий текст кратко и информативно:

{text}

Краткая суммаризация:"""
        
        # Подготавливаем запрос к внешнему API
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,  # Ограничиваем длину ответа
            "temperature": 0.3  # Более детерминированный ответ
        }
                
        # Отправляем запрос синхронно (Celery task и так работает в отдельном процессе)
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                EXTERNAL_API_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "accept": "application/json"
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Парсим ответ
            if "choices" in result and len(result["choices"]) > 0:
                summary = result["choices"][0]["message"]["content"].strip()
                return summary
            else:
                return "Ошибка: неожиданный формат ответа от модели"
                
    except httpx.TimeoutException:
        return "Ошибка: превышено время ожидания ответа от модели"
    except httpx.HTTPStatusError as e:
        return f"Ошибка HTTP {e.response.status_code} от модели"
    except json.JSONDecodeError:
        return "Ошибка: невалидный JSON ответ от модели"
    except Exception as e:
        return f"Ошибка суммаризации: {str(e)}"