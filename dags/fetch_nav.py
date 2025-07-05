

# ---------------------------------------------------------------------
# 5) 두 계좌를 합산해 Daily NAV 시계열 한 줄로 리턴
# ---------------------------------------------------------------------
from fetch_stock_account_balance import fetch_stock_account_balance
from fetch_future_account_balance import fetch_futures_account_assets


def fetch_daily_nav(
    spot_kwargs: dict,
    futures_kwargs: dict,
) -> dict[str, float]:
    """
    spot_kwargs / futures_kwargs 에는 각각 fetch_* 함수의 인자 전달.
    예)
        spot_kwargs = dict(appkey=..., appsecret=..., access_token=...,
                           cano="12345678", acnt_prdt_cd="01")
        futures_kwargs = dict(...)

    Returns
    -------
    dict
        {
          "spot_nav": float,
          "futures_nav": float,
          "total_nav": float,
          "spot_unrealized": float,
          "futures_unrealized": float,
        }
    """
    spot = fetch_stock_account_balance(**spot_kwargs)
    fut  = fetch_futures_account_assets(**futures_kwargs)


    result = {
        "spot_nav": spot["ending_equity"],
        "futures_nav": fut["ending_equity"],
        "total_nav": spot["ending_equity"] + fut["ending_equity"],
        "spot_unrealized": spot["unrealized_pnl"],
        "futures_unrealized": fut["unrealized_pnl"],
    }

    print(result)

    return result