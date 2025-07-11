from fastapi import APIRouter

from app.utils.mock_data import generate_daily

router = APIRouter(tags=["general"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/pnl")
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


@router.get("/analysis")
async def get_analysis():
    # Mock data as fallback
    mock_analysis_metrics = [
        {"label": "Total Return", "value": "20.00%"},
        {"label": "CAGR(Annualized)", "value": "20.00%"},
        {"label": "Max Drawdown", "value": "-10.00%"},
        {"label": "Volatility", "value": "10.00%"},
        {"label": "Sharpe Ratio", "value": "1.00"},
    ]

    return mock_analysis_metrics
