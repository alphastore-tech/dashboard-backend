from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.crud.portfolio import (
    read_portfolio_data,
    insert_portfolio_data,
    delete_portfolio_data,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/{date}")
async def get_portfolio_data(
    start_date: str,
    end_date: str,
    account_type: str = "future",
    account_number: str = "43037074",
):
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.

    Args:
        start_date: 조회할 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 조회할 종료 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        포트폴리오 데이터 또는 404 에러
    """
    data = await read_portfolio_data(start_date, end_date, account_type, account_number)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No portfolio data found for date: {start_date}~{end_date}",
        )
    return data


@router.post("/{date}")
async def create_portfolio_data(
    date: str,
    account_type: str = "future",
    account_number: str = "43037074",
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None,
    domain: Optional[str] = None,
    cano: Optional[str] = None,
    acnt_prdt_cd: Optional[str] = None,
    aws_secret_id: Optional[str] = None,
):
    """
    특정 날짜의 포트폴리오 데이터를 생성합니다.
    KIS API에서 데이터를 가져와서 데이터베이스에 저장합니다.

    Args:
        date: 생성할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호
        app_key: KIS API 앱 키
        app_secret: KIS API 앱 시크릿
        domain: KIS API 도메인
        cano: 계좌번호
        acnt_prdt_cd: 계좌상품코드
        aws_secret_id: AWS 시크릿 ID

    Returns:
        생성된 포트폴리오 데이터
    """
    try:
        # 날짜 형식 검증
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    # 계좌 타입 검증
    if account_type not in ["future", "spot"]:
        raise HTTPException(
            status_code=400, detail="Invalid account_type. Use 'future' or 'spot'"
        )

    return await insert_portfolio_data(
        date,
        account_type,
        account_number,
        app_key,
        app_secret,
        domain,
        cano,
        acnt_prdt_cd,
        aws_secret_id,
    )


@router.delete("/{date}")
async def remove_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
):
    """
    특정 날짜의 포트폴리오 데이터를 삭제합니다.

    Args:
        date: 삭제할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        삭제 결과 메시지
    """
    try:
        # 날짜 형식 검증
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    # 계좌 타입 검증
    if account_type not in ["future", "spot"]:
        raise HTTPException(
            status_code=400, detail="Invalid account_type. Use 'future' or 'spot'"
        )

    return await delete_portfolio_data(date, account_type, account_number)
