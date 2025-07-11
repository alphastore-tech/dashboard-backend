from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.crud.portfolio import (
    read_portfolio_data,
    insert_portfolio_data,
    delete_portfolio_data,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/{date}")
async def get_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
):
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.

    Args:
        date: 조회할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        포트폴리오 데이터 또는 404 에러
    """
    data = await read_portfolio_data(date, account_type, account_number)
    if data is None:
        raise HTTPException(
            status_code=404, detail=f"No portfolio data found for date: {date}"
        )
    return data


@router.post("/{date}")
async def create_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
):
    """
    특정 날짜의 포트폴리오 데이터를 생성합니다.
    KIS API에서 데이터를 가져와서 데이터베이스에 저장합니다.

    Args:
        date: 생성할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

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

    return await insert_portfolio_data(date, account_type, account_number)


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
