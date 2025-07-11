import os
import asyncpg
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()


async def get_db_connection():
    """PostgreSQL 데이터베이스 연결을 반환합니다."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

    try:
        conn = await asyncpg.connect(database_url)
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )
