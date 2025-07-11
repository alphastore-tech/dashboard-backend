from fastapi import APIRouter

from app.services.kis_api import (
    get_futures_balance_settlement,
    get_futureoption_balance,
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
    return await get_futures_balance_settlement(inqr_dt, ctx_area_fk200, ctx_area_nk200)


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
    return await get_futureoption_balance(
        mgna_dvsn, excc_stat_cd, ctx_area_fk200, ctx_area_nk200
    )
