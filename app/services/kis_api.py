import os
import json
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from app.utils.aws_secrets import get_aws_secret

load_dotenv()


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

    secret_raw = get_aws_secret(os.getenv("AWS_SECRET_ID", ""))
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
    secret_raw = get_aws_secret(os.getenv("AWS_SECRET_ID", ""))
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
