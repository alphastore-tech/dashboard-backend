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


async def generate_monthly_pnl():
    res = []
    today = datetime.now()

    # 12개월 동안의 데이터 생성
    for i in range(10):
        # 현재 월에서 i개월 전
        if i == 0:
            # 현재 월: 월 시작부터 오늘까지
            month_start = today.replace(day=1)
            month_end = today
        else:
            # 이전 월들: 전체 월
            current_month = today.replace(day=1)
            for _ in range(i):
                current_month = (current_month - timedelta(days=1)).replace(day=1)
            month_start = current_month
            # 해당 월의 마지막 날 계산
            if current_month.month == 12:
                next_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                next_month = current_month.replace(month=current_month.month + 1)
            month_end = next_month - timedelta(days=1)

        # 해당 월의 모든 일별 데이터 가져오기
        try:
            start_date_str = month_start.strftime("%Y-%m-%d")
            end_date_str = month_end.strftime("%Y-%m-%d")

            # API/DB에서 데이터 가져오기
            spot_output_data = await read_spot_balance(start_date_str, end_date_str)
            future_output_data = await read_future_balance(start_date_str, end_date_str)

            # 월별 합계 계산
            monthly_stock_pnl = 0.0
            monthly_future_pnl = 0.0

            # 현물 PnL 합계
            if spot_output_data:
                for item in spot_output_data:
                    rlzt_pfls = item.get("rlzt_pfls", "0")
                    monthly_stock_pnl += float(rlzt_pfls) if rlzt_pfls else 0.0

            # 선물 PnL 합계
            if future_output_data:
                for item in future_output_data:
                    futr_trad_pfls_amt = item.get("futr_trad_pfls_amt", 0)
                    monthly_future_pnl += (
                        float(futr_trad_pfls_amt) if futr_trad_pfls_amt else 0.0
                    )

        except Exception as e:
            print(f"월별 데이터 조회 실패 ({month_start.strftime('%Y-%m')}): {e}")
            monthly_stock_pnl = 0.0
            monthly_future_pnl = 0.0

        item = {
            "date": month_start.strftime("%Y-%m"),
            "totalPnl": monthly_stock_pnl + monthly_future_pnl,
            "stockPnl": monthly_stock_pnl,
            "futurePnl": monthly_future_pnl,
            "tradeCount": 0,  # TODO: 거래 횟수 데이터 추가 필요
            "contangoCount": 0,  # TODO: 컨탱고 횟수 데이터 추가 필요
            "backCount": 0,  # TODO: 백워데이션 횟수 데이터 추가 필요
            "cashFlow": 0,  # TODO: 현금 흐름 데이터 추가 필요
        }
        res.append(item)

    return res
