import random
from datetime import datetime, timedelta


def random_int(a, b):
    return random.randint(a, b)


def generate_daily_pnl(n):
    res = []

    today = datetime.now()
    for i in range(n):
        d = today - timedelta(days=i)
        item = {
            "date": d.strftime("%Y-%m-%d"),
            "totalPnl": random_int(-50000, 80000),
            "stockPnl": random_int(-30000, 50000),
            "futurePnl": random_int(-20000, 30000),
            "tradeCount": random_int(1, 10),
            "contangoCount": random_int(0, 3),
            "backCount": random_int(0, 3),
            "cashFlow": random_int(-200000, 200000),
        }
        res.append(item)
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
