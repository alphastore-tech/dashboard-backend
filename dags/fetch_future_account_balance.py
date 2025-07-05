
# ---------------------------------------------------------------------
# 4) 선물·옵션 계좌 자산 현황 조회
#    - 총자산(ending_equity), 평가손익(unrealized_pnl) 등을 반환
# ---------------------------------------------------------------------
import pandas as pd
import requests

from kis_types import RequestHeader

BASE_URL = "https://openapi.koreainvestment.com:9443"
FUTURES_ASSETS_URL = (
    f"{BASE_URL}/uapi/domestic-futureoption/v1/trading/inquire-balance"
)

def fetch_futures_account_assets(
    appkey: str,
    appsecret: str,
    access_token: str,
    cano: str,
    acnt_prdt_cd: str,
    tr_id: str = "CTFO6118R",
) -> dict[str, float]:
    """
    선물옵션 총자산현황 조회 → ending_equity·unrealized_pnl 반환.
    """
    header = RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization=f"Bearer {access_token}",
        appkey=appkey,
        appsecret=appsecret,
        tr_id=tr_id,
        custtype="P",
    )

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": "01",  # 증거금 구분: 01(개시), 02(유지)
        "EXCC_STAT_CD": "2",  # 정산상태코드: 1(정산), 2(본정산)
        "CTX_AREA_FK200": "",  # 연속조회검색조건200: 최초 조회시 공란
        "CTX_AREA_NK200": "",  # 연속조회키200: 최초 조회시 공란
    }

    resp = requests.get(
        FUTURES_ASSETS_URL,
        headers=header.to_http_headers(),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(f"KIS API error {data.get('msg_cd')}: {data.get('msg1')}")

    out = data["output2"]
    return {
        "ending_equity": float(out["prsm_dpast_amt"]),      # 추정예탁자산금액 (NAV)
        "unrealized_pnl": float(out["evlu_pfls_amt_smtl"]), # 평가손익합계
        "cash_balance": float(out["dnca_cash"]),         # 예수금
    }
