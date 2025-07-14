import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
from typing import Optional

from app.utils.aws_secrets import get_aws_secret

load_dotenv()


class KisSpotClient:
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
        self.acnt_prdt_cd = acnt_prdt_cd or os.getenv("NEXT_PUBLIC_KIS_ACNT_PRDT_CD")
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

    
