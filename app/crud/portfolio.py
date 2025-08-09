from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.database.connection import get_db_connection


async def read_future_balance(
    start_date: str,
    end_date: str,
) -> Optional[Dict[str, Any]]:
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.

    Args:
        start_date: 조회할 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 조회할 종료 날짜 (YYYY-MM-DD 형식)

    Returns:
        포트폴리오 데이터 딕셔너리 또는 None
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_future_balance_kis"

        query = f"""
        SELECT date, futr_trad_pfls_amt
        FROM {table_name} 
        WHERE date BETWEEN $1 AND $2
        """
        rows = await conn.fetch(
            query,
            datetime.strptime(start_date, "%Y-%m-%d").date(),
            datetime.strptime(end_date, "%Y-%m-%d").date(),
        )
        return rows
    finally:
        await conn.close()


async def read_spot_balance(
    start_date: str,
    end_date: str,
) -> Optional[Dict[str, Any]]:
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_spot_balance_kis"

        query = f"""
        SELECT trad_dt, rlzt_pfls
        FROM {table_name}
        WHERE trad_dt BETWEEN $1 AND $2
        """
        rows = await conn.fetch(
            query,
            datetime.strptime(start_date, "%Y-%m-%d").date(),
            datetime.strptime(end_date, "%Y-%m-%d").date(),
        )
        return rows
    finally:
        await conn.close()
