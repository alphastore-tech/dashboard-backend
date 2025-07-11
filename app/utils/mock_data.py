import random
from datetime import datetime, timedelta


def random_int(a, b):
    return random.randint(a, b)


def generate_daily(n):
    res = []

    today = datetime.now()
    for i in range(n):
        d = today - timedelta(days=i)
        item = {
            "date": d.strftime("%Y-%m-%d"),
            "total_pnl": random_int(-50000, 80000),
            "stock_pnl": random_int(-30000, 50000),
            "future_pnl": random_int(-20000, 30000),
            "trade_count": random_int(1, 10),
            "contango_count": random_int(0, 3),
            "back_count": random_int(0, 3),
            "cash_flow": random_int(-200000, 200000),
        }
        res.append(item)
    return res
