from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

import boto3
import json


def _get_aws_secret(secret_id: str, region: str = "ap-northeast-2") -> str:
    """
    AWS Secrets Manager에서 문자열(또는 JSON)을 바로 가져온다.
    """
    client = boto3.client("secretsmanager", region_name="ap-northeast-2")
    resp = client.get_secret_value(SecretId=secret_id)
    return resp["SecretString"]


# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db import get_session
# from app.models import RealizedPNL
from datetime import datetime, timedelta

app = FastAPI(title="Realized PnL API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


def random_int(a, b):
    import random

    return random.randint(a, b)


def generate_daily(n):
    res = []

    today = datetime.now()
    for i in range(n):
        d = today - timedelta(days=i)
        item = {
            "date": d.strftime("%Y-%m-%d"),
            "total_pnl": random_int(-50000, 80000),
            "stock_pnl": random_int(-30000, 50000),
            "future_pnl": random_int(-20000, 30000),
            "trade_count": random_int(1, 10),
            "contango_count": random_int(0, 3),
            "back_count": random_int(0, 3),
            "cash_flow": random_int(-200000, 200000),
        }
        res.append(item)
    return res


@app.get("/pnl")
async def read_pnl(start_date: str, end_date: str):
    # stmt = (
    #     select(RealizedPNL)
    #     .where(RealizedPNL.trade_date.between(start_date, end_date))
    #     .order_by(RealizedPNL.trade_date)
    # )
    # result = (await session.execute(stmt)).scalars().all()
    # if not result:
    #     raise HTTPException(status_code=404, detail="No data for given range")
    # return result
    return generate_daily(10)


@app.get("/analysis")
async def get_analysis():
    # Mock data as fallback
    mock_analysis_metrics = [
        {"label": "Total Return", "value": "20.00%"},
        {"label": "CAGR(Annualized)", "value": "20.00%"},
        {"label": "Max Drawdown", "value": "-10.00%"},
        {"label": "Volatility", "value": "10.00%"},
        {"label": "Sharpe Ratio", "value": "1.00"},
    ]

    return mock_analysis_metrics


@app.get("/futures/balance-settlement")
async def get_futures_balance_settlement(
    inqr_dt: str,
    ctx_area_fk200: str = "",
    ctx_area_nk200: str = "",
):
    """
    선물옵션 잔고정산손익내역 조회
    """

    # 환경변수에서 KIS API 정보 가져오기
    app_key = os.getenv("KIS_APP_KEY")
    app_secret = os.getenv("KIS_APP_SECRET")
    domain = os.getenv("KIS_DOMAIN")
    cano = os.getenv("NEXT_PUBLIC_KIS_CANO")
    acnt_prdt_cd = os.getenv("NEXT_PUBLIC_KIS_FUTURE_ACNT_PRDT_CD")

    if not all([app_key, app_secret, domain]):
        raise HTTPException(
            status_code=500, detail="KIS API credentials not configured"
        )

    print("aws_secret_id: ", os.getenv("AWS_SECRET_ID", ""))

    secret_raw = _get_aws_secret(os.getenv("AWS_SECRET_ID", ""))
    access_token = json.loads(secret_raw)["access_token"]

    # 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "CTFO6117R",
        "custtype": "P",
    }

    # 쿼리 파라미터 설정
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "INQR_DT": inqr_dt,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    try:
        # KIS API 호출
        response = requests.get(
            f"{domain}/uapi/domestic-futureoption/v1/trading/inquire-balance-settlement-pl",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        result = response.json()

        if result.get("rt_cd") != "0":
            raise HTTPException(
                status_code=400,
                detail=f"KIS API Error: {result.get('msg1', 'Unknown error')}",
            )

        print(result)

        return result

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/futureoption/balance")
async def get_futureoption_balance(
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

    # 환경변수에서 필요한 값들 가져오기
    app_key = os.getenv("KIS_APP_KEY")
    app_secret = os.getenv("KIS_APP_SECRET")
    domain = os.getenv("KIS_DOMAIN")
    cano = os.getenv("NEXT_PUBLIC_KIS_CANO")
    acnt_prdt_cd = os.getenv("NEXT_PUBLIC_KIS_FUTURE_ACNT_PRDT_CD")

    if not all([app_key, app_secret, domain, cano, acnt_prdt_cd]):
        raise HTTPException(
            status_code=500,
            detail="Missing required environment variables",
        )

    # AWS Secrets Manager에서 access token 가져오기
    secret_raw = _get_aws_secret(os.getenv("AWS_SECRET_ID", ""))
    access_token = json.loads(secret_raw)["access_token"]

    # 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "CTFO6118R",
        "custtype": "P",
    }

    # 쿼리 파라미터 설정
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN": mgna_dvsn,
        "EXCC_STAT_CD": excc_stat_cd,
        "CTX_AREA_FK200": ctx_area_fk200,
        "CTX_AREA_NK200": ctx_area_nk200,
    }

    try:
        # KIS API 호출
        response = requests.get(
            f"{domain}/uapi/domestic-futureoption/v1/trading/inquire-balance",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        result = response.json()

        if result.get("rt_cd") != "0":
            raise HTTPException(
                status_code=400,
                detail=f"KIS API Error: {result.get('msg1', 'Unknown error')}",
            )

        print(result)

        return result

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
