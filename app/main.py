from fastapi import FastAPI, Depends, HTTPException

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db import get_session
# from app.models import RealizedPNL
from datetime import datetime, timedelta

app = FastAPI(title="Realized PnL API")


@app.get("/")
async def root():
    return {"message": "Hello World"}


def random_int(a, b):
    import random

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


@app.get("/pnl")
async def read_pnl(start_date: str, end_date: str):
    # stmt = (
    #     select(RealizedPNL)
    #     .where(RealizedPNL.trade_date.between(start_date, end_date))
    #     .order_by(RealizedPNL.trade_date)
    # )
    # result = (await session.execute(stmt)).scalars().all()
    # if not result:
    #     raise HTTPException(status_code=404, detail="No data for given range")
    # return result
    return generate_daily(10)
