# fastapi/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Dashboard API")


@app.get("/")
async def root():
    """헬스 체크 및 간단한 인사."""
    return {"message": "Welcome to Dashboard!"}


@app.get("/returns/total")
async def get_total_return():
    """
    누적 수익률 반환용 엔드포인트
    (후에 DB 연결 로직으로 교체).
    """
    # TODO: PostgreSQL에서 가장 최신 누적 수익률 조회
    return {"total_return": None}
