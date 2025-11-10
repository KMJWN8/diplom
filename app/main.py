import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
from app.models import Base  # импорт базовой модели для создания таблиц
from app.routes.parser import router as parser_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Parser API",
        description="Сервис для парсинга Telegram-каналов и сохранения постов",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # можно ограничить доменами фронтенда
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(parser_router)

    # --- События старта/остановки ---
    @app.on_event("startup")
    async def on_startup():
        # Создаём таблицы при первом запуске (если их нет)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database connected and tables checked.")

    @app.on_event("shutdown")
    async def on_shutdown():
        await engine.dispose()
        print("🛑 Database connection closed.")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
