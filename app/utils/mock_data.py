import random
from datetime import datetime, timedelta
from app.services.kisSpotClient import KisSpotClient
from app.services.kisClient import KisClient
from app.crud.portfolio import read_future_balance, read_spot_balance
import os
from dotenv import load_dotenv

load_dotenv()


def random_int(a, b):
    return random.randint(a, b)


async def generate_daily_pnl(n):

    res = []
    today = datetime.now()

    # KIS API에서 데이터 가져오기
    try:
        portfolio_start_date = (today - timedelta(days=n - 1)).strftime("%Y-%m-%d")
        portfolio_end_date = today.strftime("%Y-%m-%d")

        spot_output_data = await read_spot_balance(
            portfolio_start_date, portfolio_end_date
        )

        future_output_data = await read_future_balance(
            portfolio_start_date, portfolio_end_date
        )

        stock_pnl_map = {}
        for item in spot_output_data:
            trad_dt = item.get("trad_dt", "")
            rlzt_pfls = item.get("rlzt_pfls", "0")
            stock_pnl_map[str(trad_dt)] = float(rlzt_pfls) if rlzt_pfls else 0.0

        future_pnl_map = {}
        if future_output_data:
            for item in future_output_data:
                date = item.get("date")
                futr_trad_pfls_amt = item.get("futr_trad_pfls_amt", 0)
                future_pnl_map[str(date)] = (
                    float(futr_trad_pfls_amt) if futr_trad_pfls_amt else 0.0
                )

        # 환경변수 가져오기
        app_key = os.getenv("NEXT_PUBLIC_KIS_SPOT_APP_KEY")
        app_secret = os.getenv("NEXT_PUBLIC_KIS_SPOT_APP_SECRET")
        cano = os.getenv("NEXT_PUBLIC_KIS_SPOT_CANO")
        acnt_prdt_cd = os.getenv("NEXT_PUBLIC_KIS_ACNT_PRDT_CD")
        aws_secret_id = os.getenv("AWS_SECRET_ID_SPOT")

        spot_client = KisSpotClient(
            app_key=app_key,
            app_secret=app_secret,
            cano=cano,
            acnt_prdt_cd=acnt_prdt_cd,
            aws_secret_id=aws_secret_id,
        )

        today_str = today.strftime("%Y-%m-%d")

        today_spot_response = spot_client.get_spot_balance_daily_profit(
            today.strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        )
        output1 = today_spot_response.get("output1", [])
        if output1:
            today_spot_pnl = output1[0]["rlzt_pfls"]
            stock_pnl_map[today_str] = float(today_spot_pnl)

        future_client = KisClient()
        future_response = await future_client.get_futureoption_balance()

        output2 = future_response.get("output2", {})
        today_future_pnl = output2.get("futr_trad_pfls_amt", 0)
        future_pnl_map[today_str] = float(today_future_pnl)

    except Exception as e:
        print(f"KIS API 호출 실패: {e}")
        stock_pnl_map = {}
        future_pnl_map = {}

    print("stock_pnl_map", stock_pnl_map)
    print("future_pnl_map", future_pnl_map)
    count = 0

    while count < n:
        # 평일(월요일~금요일)만 처리 (0=월요일, 6=일요일)
        if today.weekday() < 5:  # 0~4는 월요일~금요일
            date_str = today.strftime("%Y-%m-%d")

            # API에서 가져온 데이터가 있으면 사용, 없으면 0
            stock_pnl = stock_pnl_map.get(date_str, 0.0)
            future_pnl = future_pnl_map.get(date_str, 0.0)

            item = {
                "date": date_str,
                "totalPnl": stock_pnl + future_pnl,
                "stockPnl": stock_pnl,
                "futurePnl": future_pnl,
                "tradeCount": 0,
                "contangoCount": 0,
                "backCount": 0,
                "cashFlow": 0,
            }
            res.append(item)
            count += 1

        today -= timedelta(days=1)

    return res


def generate_monthly_pnl():
    res = []

    today = datetime.now()
    for i in range(12):  # 12개월 데이터 생성
        # 현재 월에서 i개월 전
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        month_date = month_date.replace(day=1)  # 월의 첫째 날로 설정

        item = {
            "date": month_date.strftime("%Y-%m"),
            "totalPnl": random_int(-500000, 800000),
            "stockPnl": random_int(-300000, 500000),
            "futurePnl": random_int(-200000, 300000),
            "tradeCount": random_int(20, 200),
            "contangoCount": random_int(5, 50),
            "backCount": random_int(5, 50),
            "cashFlow": random_int(-2000000, 2000000),
        }
        res.append(item)

    return res
