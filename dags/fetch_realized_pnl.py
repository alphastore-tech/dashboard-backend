"""
kis_api.py
~~~~~~~~~~
한국투자증권 OpenAPI ― 실현손익(일별) 조회 래퍼
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional

import pandas as pd
import requests

from kis_types import RequestHeader

# ---------------------------------------------------------------------
# 1) 데이터클래스 정의ㅈ
#    (원본 헤더/파라미터 명의 하이픈은 파이썬 변수에 사용할 수 없으므로
#     snake_case 로 바꾸고, 실제 HTTP 전송 시 키를 다시 원형으로 매핑)
# ---------------------------------------------------------------------

@dataclass
class RequestQueryParam:
    ACNT_PRDT_CD: str
    CANO: str
    INQR_STRT_DT: str
    INQR_END_DT: str
    PDNO: str = ""            # 상품번호(전체)
    CTX_AREA_NK100: str = ""
    SORT_DVSN: str = "01"      # 정렬
    INQR_DVSN: str = "00"        # 조회구분(전체)
    CBLC_DVSN: str = "00"        # 잔고구분(전체)
    CTX_AREA_FK100: str = ""


@dataclass
class ResponseBodyoutput1:
    trad_dt: str
    buy_amt: str
    sll_amt: str
    rlzt_pfls: str
    fee: str
    loan_int: str
    tl_tax: str
    pfls_rt: str
    sll_qty1: str
    buy_qty1: str


@dataclass
class ResponseBodyoutput2:
    sll_qty_smtl: str
    sll_tr_amt_smtl: str
    sll_fee_smtl: str
    sll_tltx_smtl: str
    sll_excc_amt_smtl: str
    buy_qty_smtl: str
    buy_tr_amt_smtl: str
    buy_fee_smtl: str
    buy_tax_smtl: str
    buy_excc_amt_smtl: str
    tot_qty: str
    tot_tr_amt: str
    tot_fee: str
    tot_tltx: str
    tot_excc_amt: str
    tot_rlzt_pfls: str
    loan_int: str


@dataclass
class ResponseBody:
    rt_cd: str
    msg_cd: str
    msg1: str
    output1: List[ResponseBodyoutput1] = field(default_factory=list)
    output2: ResponseBodyoutput2 | None = None


# ---------------------------------------------------------------------
# 2) 퍼사드 함수(fetch_realized_pnl)
# ---------------------------------------------------------------------
BASE_URL = "https://openapi.koreainvestment.com:9443"
KIS_API_URL = (
    f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-period-profit"
)

def fetch_realized_pnl(
    appkey: str,
    appsecret: str,
    access_token: str,
    cano: str,
    acnt_prdt_cd: str,
    start_dt: str,
    end_dt: str,
    tr_id: str = "TTTC8708R",
) -> pd.DataFrame:
    """
    일별 실현손익을 조회해 DataFrame 으로 반환.

    Parameters
    ----------
    appkey, appsecret : str
        한국투자증권 발급 앱키/시크릿.
    access_token : str
        OAuth2 토큰.
    cano : str
        8자리 계좌번호
    acnt_prdt_cd : str
        2자리 계좌상품코드
    start_dt, end_dt : str
        'YYYYMMDD'.
    tr_id : str
        거래 ID (장 마감 후 실현손익: TTTC8001R).
    """
    header = RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization=f"Bearer {access_token}",
        appkey=appkey,
        appsecret=appsecret,
        tr_id=tr_id,
        custtype="P",
    )

    query = RequestQueryParam(
        ACNT_PRDT_CD=acnt_prdt_cd,
        CANO=cano,
        INQR_STRT_DT=start_dt,
        INQR_END_DT=end_dt,
        CTX_AREA_NK100="",
        CTX_AREA_FK100="",
    )

    resp = requests.get(
        KIS_API_URL,
        headers=header.to_http_headers(),
        params=asdict(query),
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # 성공 여부 확인
    if data.get("rt_cd") != "0":
        raise RuntimeError(f"KIS API error {data.get('msg_cd')}: {data.get('msg1')}")

    # output1 → DataFrame
    df = pd.json_normalize(data["output1"])
    # 필요한 컬럼/타입 캐스팅 등 후처리
    # numeric_cols = ["buy_amt", "sll_amt", "rlzt_pfls", "fee", "loan_int", "tl_tax"]
    # df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df  = df.apply(pd.to_numeric, errors="coerce")
    # df["trade_date"] = pd.to_datetime(df["trad_dt"])

    return df
