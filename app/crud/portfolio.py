from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.database.connection import get_db_connection


async def read_portfolio_data(
    start_date: str,
    end_date: str,
    account_type: str = "future",
    account_number: str = "43037074",
) -> Optional[Dict[str, Any]]:
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.

    Args:
        start_date: 조회할 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 조회할 종료 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        포트폴리오 데이터 딕셔너리 또는 None
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_{account_type}_balance_kis"

        # 문자열 날짜를 datetime 객체로 변환
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        query = f"""
        SELECT date, futr_trad_pfls_amt
        FROM {table_name} 
        WHERE date BETWEEN $1 AND $2
        """
        rows = await conn.fetch(query, start_date_obj, end_date_obj)
        return rows
    finally:
        await conn.close()
