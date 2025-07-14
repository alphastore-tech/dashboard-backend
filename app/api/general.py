from fastapi import APIRouter

from app.utils.mock_data import generate_daily_pnl, generate_monthly_pnl

router = APIRouter(tags=["general"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/pnl/daily")
async def get_daily_pnl():
    return generate_daily_pnl(30)

@router.get("/pnl/monthly")
async def get_monthly_pnl():
    return generate_monthly_pnl()


@router.get("/performance_metrics")
async def get_performance_metrics():
    mock_analysis_metrics = [
        {"label": "Total Return", "value": "20.00%"},
        {"label": "CAGR(Annualized)", "value": "20.00%"},
        {"label": "Max Drawdown", "value": "-10.00%"},
        {"label": "Volatility", "value": "10.00%"},
        {"label": "Sharpe Ratio", "value": "1.00"},
    ]

    return mock_analysis_metrics
