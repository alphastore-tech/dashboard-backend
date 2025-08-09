from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import kis, general

app = FastAPI(title="Realized PnL API")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(general.router)
app.include_router(kis.router)
