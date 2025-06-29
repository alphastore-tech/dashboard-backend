from airflow.decorators import dag, task
from pendulum import timezone, now
import requests, pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv
import os
import json
import boto3

from kis_api import fetch_realized_pnl

load_dotenv()
KST = timezone("Asia/Seoul")

def _get_aws_secret(secret_id: str, region: str = "ap-northeast-2") -> str:
    """
    AWS Secrets Manager에서 문자열(또는 JSON)을 바로 가져온다.
    """
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=secret_id)
    return resp["SecretString"]

@dag(schedule="10 16 * * 1-5", start_date=KST.datetime(2025, 6, 30))
def daily_kis_pnl_pipeline():

    @task
    def fetch_daily_pnl():
        appkey = os.getenv("KIS_APP_KEY")
        appsecret = os.getenv("KIS_APP_SECRET")
        # ① Secrets Manager 에서 access_token 불러오기
        secret_raw  = _get_aws_secret(os.getenv("AWS_SECRET_ID"))
        # Secret 값을 문자열 그대로 저장했다면 ↓ 한 줄로 끝.
        # access_token = secret_raw
        # JSON 형식 {"access_token": "..."} 로 저장했다면:
        access_token = json.loads(secret_raw)["access_token"]
        print("access_token: ", access_token)

        # ② 조회 기간: '당일'만
        today_ymd = now(KST).format("YYYYMMDD")
        start_dt = "20250601"
        end_dt = today_ymd
        cano = os.getenv("KIS_CANO")
        acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD")
        tr_id="TTTC8708R"

        df = fetch_realized_pnl(appkey, appsecret, access_token, cano, acnt_prdt_cd, start_dt, end_dt, tr_id)
        print(df)
        return df.to_dict("records")

    @task
    def load_to_postgres(records):
        engine = sa.create_engine("postgresql+psycopg2://...")
        pd.DataFrame(records).to_sql("realized_pnl", engine, if_exists="append")

    @task
    def calc_cumulative_return():
        engine = sa.create_engine("postgresql+psycopg2://...")
        with engine.begin() as conn:
            conn.execute("""
                insert into cumulative_return as c
                select trade_date,
                       sum(realized_profit)::float /
                       nullif(lag(sum(realized_profit)) over (), 0) as cum_ret
                from realized_pnl
                group by trade_date
                on conflict (trade_date) do update
                set cum_ret = excluded.cum_ret;
            """)

    df = fetch_daily_pnl()
    load_to_postgres(df) >> calc_cumulative_return()

dag = daily_kis_pnl_pipeline()
