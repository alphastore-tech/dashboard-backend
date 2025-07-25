import random
from datetime import datetime, timedelta
from app.services.kisSpotClient import KisSpotClient
from app.crud.portfolio import read_portfolio_data


def random_int(a, b):
    return random.randint(a, b)


async def generate_daily_pnl(n):

    res = []
    today = datetime.now()

    # KIS API에서 데이터 가져오기
    try:
        client = KisSpotClient()
        start_date = (today - timedelta(days=n - 1)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

        api_response = client.get_spot_balance_daily_profit(start_date, end_date)

        # API 응답에서 output 데이터 추출
        stock_output_data = api_response.get("output1", [])

        # 날짜 형식 변환하여 포트폴리오 데이터 조회
        portfolio_start_date = (today - timedelta(days=n - 1)).strftime("%Y-%m-%d")
        portfolio_end_date = today.strftime("%Y-%m-%d")
        future_output_data = await read_portfolio_data(
            portfolio_start_date, portfolio_end_date
        )

        print("future_output_data", future_output_data)

        # 날짜별 stockPnl 매핑 생성
        stock_pnl_map = {}
        for item in stock_output_data:
            trad_dt = item.get("trad_dt", "")
            rlzt_pfls = item.get("rlzt_pfls", "0")

            # 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
            if len(trad_dt) == 8:
                formatted_date = f"{trad_dt[:4]}-{trad_dt[4:6]}-{trad_dt[6:8]}"
                stock_pnl_map[formatted_date] = float(rlzt_pfls) if rlzt_pfls else 0.0

        # 날짜별 futurePnl 매핑 생성
        future_pnl_map = {}
        if future_output_data:
            for item in future_output_data:
                date = item.get("date")
                futr_trad_pfls_amt = item.get("futr_trad_pfls_amt", 0)

                # date가 datetime 객체인 경우 문자열로 변환
                if hasattr(date, "strftime"):
                    date_str = date.strftime("%Y-%m-%d")
                else:
                    date_str = str(date)

                future_pnl_map[date_str] = (
                    float(futr_trad_pfls_amt) if futr_trad_pfls_amt else 0.0
                )

    except Exception as e:
        print(f"KIS API 호출 실패: {e}")
        stock_pnl_map = {}
        future_pnl_map = {}

    # n일간의 평일 데이터 생성
    current_date = today
    count = 0

    print("stock_pnl_map", stock_pnl_map)
    print("future_pnl_map", future_pnl_map)

    while count < n:
        # 평일(월요일~금요일)만 처리 (0=월요일, 6=일요일)
        if current_date.weekday() < 5:  # 0~4는 월요일~금요일
            date_str = current_date.strftime("%Y-%m-%d")

            # API에서 가져온 데이터가 있으면 사용, 없으면 0
            stock_pnl = stock_pnl_map.get(date_str, 0.0)
            future_pnl = future_pnl_map.get(date_str, 0.0)

            item = {
                "date": date_str,
                "totalPnl": stock_pnl + future_pnl,
                "stockPnl": stock_pnl,
                "futurePnl": future_pnl,
                "tradeCount": random_int(1, 10) if stock_pnl != 0 else 0,
                "contangoCount": random_int(0, 3) if stock_pnl != 0 else 0,
                "backCount": random_int(0, 3) if stock_pnl != 0 else 0,
                "cashFlow": random_int(-200000, 200000) if stock_pnl != 0 else 0,
            }
            res.append(item)
            count += 1

        current_date -= timedelta(days=1)

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
