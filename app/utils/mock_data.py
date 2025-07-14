import random
from datetime import datetime, timedelta
from app.services.kisSpotClient import KisSpotClient


def random_int(a, b):
    return random.randint(a, b)


def generate_daily_pnl(n):
    
    res = []
    today = datetime.now()
    
    # KIS API에서 데이터 가져오기
    try:
        client = KisSpotClient()
        start_date = (today - timedelta(days=n-1)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")
        
        api_response = client.get_spot_balance_daily_profit(start_date, end_date)
        
        # API 응답에서 output 데이터 추출
        output_data = api_response.get("output1", [])
        
        # 날짜별 stockPnl 매핑 생성
        stock_pnl_map = {}
        for item in output_data:
            trad_dt = item.get("trad_dt", "")
            rlzt_pfls = item.get("rlzt_pfls", "0")
            
            # 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
            if len(trad_dt) == 8:
                formatted_date = f"{trad_dt[:4]}-{trad_dt[4:6]}-{trad_dt[6:8]}"
                stock_pnl_map[formatted_date] = float(rlzt_pfls) if rlzt_pfls else 0.0
    
    except Exception as e:
        print(f"KIS API 호출 실패: {e}")
        stock_pnl_map = {}

    # n일간의 평일 데이터 생성
    current_date = today
    count = 0
    
    while count < n:
        # 평일(월요일~금요일)만 처리 (0=월요일, 6=일요일)
        if current_date.weekday() < 5:  # 0~4는 월요일~금요일
            date_str = current_date.strftime("%Y-%m-%d")
            
            # API에서 가져온 데이터가 있으면 사용, 없으면 0
            stock_pnl = stock_pnl_map.get(date_str, 0.0)
            
            item = {
                "date": date_str,
                "totalPnl": stock_pnl,
                "stockPnl": stock_pnl,
                "futurePnl": random_int(-20000, 30000) if stock_pnl != 0 else 0,
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
        month_date = today.replace(day=1) - timedelta(days=30*i)
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
