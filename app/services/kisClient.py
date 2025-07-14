import os
import json
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
from typing import Optional

from app.utils.aws_secrets import get_aws_secret

load_dotenv()


class KisClient:
    """
    KIS API 클라이언트 클래스
    한국투자증권 API와의 통신을 담당합니다.
    """

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        domain: Optional[str] = None,
        cano: Optional[str] = None,
        acnt_prdt_cd: Optional[str] = None,
        aws_secret_id: Optional[str] = None
    ):
        """KIS API 클라이언트 초기화"""
        # 파라미터로 받은 값이 있으면 사용하고, 없으면 환경변수에서 가져옴
        self.app_key = app_key or os.getenv("KIS_APP_KEY")
        self.app_secret = app_secret or os.getenv("KIS_APP_SECRET")
        self.domain = domain or os.getenv("KIS_DOMAIN")
        self.cano = cano or os.getenv("NEXT_PUBLIC_KIS_CANO")
        self.acnt_prdt_cd = acnt_prdt_cd or os.getenv("NEXT_PUBLIC_KIS_FUTURE_ACNT_PRDT_CD")
        self.aws_secret_id = aws_secret_id or os.getenv("AWS_SECRET_ID", "")

        # 필수 환경변수 검증
        if not all([self.app_key, self.app_secret, self.domain]):
            raise HTTPException(
                status_code=500, detail="KIS API credentials not configured"
            )

    def _get_base_headers(self, tr_id: str) -> dict:
        """
        KIS API 요청에 사용할 기본 헤더를 생성합니다.

        Args:
            tr_id (str): 거래 ID

        Returns:
            dict: 헤더 딕셔너리
        """
        access_token = get_aws_secret(self.aws_secret_id)

        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
            "custtype": "P",
        }

    def _make_api_request(self, endpoint: str, headers: dict, params: dict) -> dict:
        """
        KIS API 요청을 수행합니다.

        Args:
            endpoint (str): API 엔드포인트
            headers (dict): 요청 헤더
            params (dict): 쿼리 파라미터

        Returns:
            dict: API 응답 결과
        """
        try:
            response = requests.get(
                f"{self.domain}{endpoint}",
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
            raise HTTPException(
                status_code=500, detail=f"HTTP error occurred: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    async def get_futures_balance_settlement(
        self,
        inqr_dt: str,
        ctx_area_fk200: str = "",
        ctx_area_nk200: str = "",
    ) -> dict:
        """
        선물옵션 잔고정산손익내역 조회

        Args:
            inqr_dt (str): 조회일자
            ctx_area_fk200 (str): 연속조회검색조건200
            ctx_area_nk200 (str): 연속조회키200

        Returns:
            dict: 잔고정산손익내역 데이터
        """
        headers = self._get_base_headers("CTFO6117R")

        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "INQR_DT": inqr_dt,
            "CTX_AREA_FK200": ctx_area_fk200,
            "CTX_AREA_NK200": ctx_area_nk200,
        }

        endpoint = (
            "/uapi/domestic-futureoption/v1/trading/inquire-balance-settlement-pl"
        )
        return self._make_api_request(endpoint, headers, params)

    async def get_futureoption_balance(
        self,
        mgna_dvsn: str = "01",  # 증거금 구분 (01: 개시, 02: 유지)
        excc_stat_cd: str = "2",  # 정산상태코드 (1: 정산, 2: 본정산)
        ctx_area_fk200: str = "",  # 연속조회검색조건200
        ctx_area_nk200: str = "",  # 연속조회키200
    ) -> dict:
        """
        선물옵션 잔고현황 조회

        Args:
            mgna_dvsn (str): 증거금 구분 (01: 개시, 02: 유지)
            excc_stat_cd (str): 정산상태코드 (1: 정산, 2: 본정산)
            ctx_area_fk200 (str): 연속조회검색조건200 (다음페이지 조회시 이전 응답값 사용)
            ctx_area_nk200 (str): 연속조회키200 (다음페이지 조회시 이전 응답값 사용)

        Returns:
            dict: 잔고현황 데이터
        """
        if not all([self.cano, self.acnt_prdt_cd]):
            raise HTTPException(
                status_code=500,
                detail="Missing required environment variables",
            )

        headers = self._get_base_headers("CTFO6118R")

        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "MGNA_DVSN": mgna_dvsn,
            "EXCC_STAT_CD": excc_stat_cd,
            "CTX_AREA_FK200": ctx_area_fk200,
            "CTX_AREA_NK200": ctx_area_nk200,
        }

        endpoint = "/uapi/domestic-futureoption/v1/trading/inquire-balance"
        return self._make_api_request(endpoint, headers, params)
