import pandas as pd
import requests

from kis_types import RequestHeader
# ---------------------------------------------------------------------
# 3) 현물(주식) 계좌 자산 현황 조회
#    - 총자산(ending_equity), 평가손익(unrealized_pnl) 등을 반환
# ---------------------------------------------------------------------

BASE_URL = "https://openapi.koreainvestment.com:9443"
STOCK_BALANCE_URL = (
    f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-account-balance"
)

def fetch_stock_account_balance(
    appkey: str,
    appsecret: str,
    access_token: str,
    cano: str,
    acnt_prdt_cd: str,
    tr_id: str = "TTTC8434R",
) -> dict[str, float]:
    """
    투자계좌자산현황조회(주식) 호출 → ending_equity·unrealized_pnl 반환.

    Returns
    -------
    dict
        {
          "ending_equity": float,   # 총자산 (잔고+평가금액)
          "unrealized_pnl": float,  # 평가손익
          "cash_balance": float,    # 예수금
        }
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
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "01",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",
    }

    resp = requests.get(
        STOCK_BALANCE_URL,
        headers=header.to_http_headers(),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(f"KIS API error {data.get('msg_cd')}: {data.get('msg1')}")

    out2 = data["output2"][0]       # ← 총계가 들어 있음

    return {
        # 순자산 = 예수금까지 포함한 계좌 총자산
        "ending_equity": float(out2["nass_amt"]),
        # 평가손익 = 개별 종목 합산이 아니라 out2 에도 이미 합계 필드가 있음
        "unrealized_pnl": float(out2["evlu_pfls_smtl_amt"]),
        "cash_balance":   float(out2["dnca_tot_amt"]),
    }
