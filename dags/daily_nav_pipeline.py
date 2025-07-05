"""
daily_nav_pipeline.py
~~~~~~~~~~~~~~~~~~~~~
현물+선물 NAV(총자산)·평가손익을 하루 한 번 PostgreSQL 에 적재하는 DAG
"""
from __future__ import annotations

from airflow.decorators import dag, task
from pendulum import timezone, now
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
from dotenv import load_dotenv
import os
import json
from utils.aws import _get_aws_secret

# -------------- 사용자 작성 래퍼 ----------------
from fetch_nav import fetch_daily_nav  # 앞서 만든 함수 import
# ----------------------------------------------

load_dotenv()
KST = timezone("Asia/Seoul")


@dag(
    schedule="20 16 * * 1-5",      # 평일 16:20 (장 마감 + 버퍼 15분)
    start_date=KST.datetime(2025, 6, 30),
    catchup=False,                 # 과거 날짜→수동 backfill 권장
    tags=["kis", "daily_nav"],
)
def daily_nav_pipeline():

    # ──────────────────────────────────────────
    # 1) fetch_daily_nav : 한국투자 API 호출
    # ──────────────────────────────────────────
    @task
    def fetch_nav():
        # 공통 인증 정보
        appkey = os.getenv("KIS_APP_KEY")
        appsecret = os.getenv("KIS_APP_SECRET")
        aws_secret_id = os.getenv("AWS_SECRET_ID", "")
        print("appkey: ", appkey)
        print("appsecret: ", appsecret)
        print("aws_secret_id: ", aws_secret_id)

        
        secret_raw  = _get_aws_secret(aws_secret_id)
        access_token = json.loads(secret_raw)["access_token"]
        print("access_token: ", access_token)

        # ── 현물 계좌 정보
        spot_kwargs = dict(
            appkey=appkey,
            appsecret=appsecret,
            access_token=access_token,
            cano=os.getenv("KIS_SPOT_CANO"),
            acnt_prdt_cd=os.getenv("KIS_SPOT_PRDT_CD"),
        )

        # ── 선물·옵션 계좌 정보
        futures_kwargs = dict(
            appkey=appkey,
            appsecret=appsecret,
            access_token=access_token,
            cano=os.getenv("KIS_FUT_CANO"),
            acnt_prdt_cd=os.getenv("KIS_FUT_PRDT_CD"),
        )

        nav_dict = fetch_daily_nav(
            spot_kwargs=spot_kwargs,
            futures_kwargs=futures_kwargs,
        )

        # 날짜를 붙여 DataFrame 으로 직렬화
        today = now(KST).format("YYYY-MM-DD")
        df = (
            pd.DataFrame([nav_dict])
            .assign(trade_date=today)  # 열 순서 맞추기 위해 뒤에 넣어도 OK
            .loc[
                :,
                [
                    "trade_date",
                    "spot_nav",
                    "futures_nav",
                    "total_nav",
                    "spot_unrealized",
                    "futures_unrealized",
                ],
            ]
        )

        return df.to_dict("records")

    # ──────────────────────────────────────────
    # 2) load_to_postgres : 결과 적재
    # ──────────────────────────────────────────
    @task
    def load_to_postgres(records: list[dict]) -> int:
        if not records:
            return 0

        df = pd.DataFrame.from_records(records)

        # Airflow connection 대신 간단히 ENV 사용
        db_url = os.getenv(
            "KIS_DB_URL",
            "postgresql+psycopg2://kis:kispass@kis-postgres:5432/kis",
        )
        engine = sa.create_engine(db_url, pool_pre_ping=True, future=True)

        # 테이블 스키마 (존재하지 않으면 생성)
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS daily_nav (
                    trade_date DATE PRIMARY KEY,
                    spot_nav NUMERIC(20,2),
                    futures_nav NUMERIC(20,2),
                    total_nav NUMERIC(20,2),
                    spot_unrealized NUMERIC(20,2),
                    futures_unrealized NUMERIC(20,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                )
            )

        # 컬럼별 dtype 매핑
        dtype_map = {
            "trade_date": sa.Date(),
            "spot_nav": sa.Numeric(20, 2),
            "futures_nav": sa.Numeric(20, 2),
            "total_nav": sa.Numeric(20, 2),
            "spot_unrealized": sa.Numeric(20, 2),
            "futures_unrealized": sa.Numeric(20, 2),
        }

        # UPSERT 처리 (PostgreSQL ON CONFLICT 사용)
        with engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(
                    text(
                        """
                        INSERT INTO daily_nav (
                            trade_date, spot_nav, futures_nav, total_nav, 
                            spot_unrealized, futures_unrealized
                        ) VALUES (
                            :trade_date, :spot_nav, :futures_nav, :total_nav,
                            :spot_unrealized, :futures_unrealized
                        )
                        ON CONFLICT (trade_date) 
                        DO UPDATE SET
                            spot_nav = EXCLUDED.spot_nav,
                            futures_nav = EXCLUDED.futures_nav,
                            total_nav = EXCLUDED.total_nav,
                            spot_unrealized = EXCLUDED.spot_unrealized,
                            futures_unrealized = EXCLUDED.futures_unrealized,
                            created_at = CURRENT_TIMESTAMP
                        """
                    ),
                    {
                        "trade_date": row["trade_date"],
                        "spot_nav": row["spot_nav"],
                        "futures_nav": row["futures_nav"],
                        "total_nav": row["total_nav"],
                        "spot_unrealized": row["spot_unrealized"],
                        "futures_unrealized": row["futures_unrealized"],
                    }
                )

        return len(records)

    # ──────────────────────────────────────────
    # DAG dependency
    # ──────────────────────────────────────────

    records = fetch_nav()
    load_to_postgres(records)


dag = daily_nav_pipeline()
