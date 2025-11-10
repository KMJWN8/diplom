from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.parser import router as parser_router


app = FastAPI(title="Telegram Parser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parser_router)
