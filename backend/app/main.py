from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.parser import router as parser_router
from app.routes.analytics import router as analytics_router
from app.routes.summarization import router as summarization_router

app = FastAPI(title="Telegram Parser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parser_router)
app.include_router(analytics_router)
app.include_router(summarization_router)
