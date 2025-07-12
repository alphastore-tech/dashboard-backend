from fastapi import APIRouter

from app.services.kis_api import KisClient
from app.crud.daily_future_balance import (
    insert_daily_future_balance,
    read_daily_future_balance,
    delete_daily_future_balance,
)

router = APIRouter(prefix="/kis", tags=["kis"])


@router.get("/futures/balance-settlement")
async def get_futures_balance_settlement_endpoint(
    inqr_dt: str,
    ctx_area_fk200: str = "",
    ctx_area_nk200: str = "",
):
    """
    선물옵션 잔고정산손익내역 조회
    """
    client = KisClient()
    return await client.get_futures_balance_settlement(
        inqr_dt, ctx_area_fk200, ctx_area_nk200
    )


@router.get("/futureoption/balance")
async def get_futureoption_balance_endpoint(
    mgna_dvsn: str = "01",  # 증거금 구분 (01: 개시, 02: 유지)
    excc_stat_cd: str = "2",  # 정산상태코드 (1: 정산, 2: 본정산)
    ctx_area_fk200: str = "",  # 연속조회검색조건200
    ctx_area_nk200: str = "",  # 연속조회키200
):
    """
    선물옵션 잔고현황 조회

    Parameters:
    - mgna_dvsn: 증거금 구분 (01: 개시, 02: 유지)
    - excc_stat_cd: 정산상태코드 (1: 정산, 2: 본정산)
    - ctx_area_fk200: 연속조회검색조건200 (다음페이지 조회시 이전 응답값 사용)
    - ctx_area_nk200: 연속조회키200 (다음페이지 조회시 이전 응답값 사용)
    """
    client = KisClient()
    return await client.get_futureoption_balance(
        mgna_dvsn, excc_stat_cd, ctx_area_fk200, ctx_area_nk200
    )


@router.post("/daily-future-balance")
async def create_daily_future_balance():
    """
    특정 날짜의 선물옵션 잔고 데이터를 KIS API에서 가져와서 daily_future_balance_kis 테이블에 삽입합니다.

    Args:
        date: 삽입할 날짜 (YYYY-MM-DD 형식)

    Returns:
        삽입된 데이터
    """
    return await insert_daily_future_balance()


# @router.get("/daily-future-balance/{date}")
# async def get_daily_future_balance(date: str):
#     """
#     특정 날짜의 선물옵션 잔고 데이터를 조회합니다.

#     Args:
#         date: 조회할 날짜 (YYYY-MM-DD 형식)

#     Returns:
#         잔고 데이터 또는 404 에러
#     """
#     data = await read_daily_future_balance(date)
#     if data is None:
#         from fastapi import HTTPException

#         raise HTTPException(
#             status_code=404,
#             detail=f"No daily future balance data found for date: {date}",
#         )
#     return data


# @router.delete("/daily-future-balance/{date}")
# async def remove_daily_future_balance(date: str):
#     """
#     특정 날짜의 선물옵션 잔고 데이터를 삭제합니다.

#     Args:
#         date: 삭제할 날짜 (YYYY-MM-DD 형식)

#     Returns:
#         삭제 결과 메시지
#     """
#     return await delete_daily_future_balance(date)
