from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database import close_db, init_db
from app.dependencies.telegram_client import telegram_client
from app.routes.telegram import router as telegram_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await telegram_client.close()
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Parser API",
        description="API для парсинга Telegram каналов",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Подключаем роутеры
    app.include_router(telegram_router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
