from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.database.connection import get_db_connection
from app.services.kis_api import KisClient


async def read_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
) -> Optional[Dict[str, Any]]:
    """
    특정 날짜의 포트폴리오 데이터를 조회합니다.

    Args:
        date: 조회할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        포트폴리오 데이터 딕셔너리 또는 None
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_{account_type}_balance_kis_{account_number}"

        # 문자열 날짜를 datetime 객체로 변환
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        query = f"""
        SELECT date, nav, cash, unrealized_pnl, realized_pnl, net_cashflow, fee
        FROM {table_name} 
        WHERE date = $1
        """
        row = await conn.fetchrow(query, date_obj)

        if row:
            return {
                "date": row["date"].strftime("%Y-%m-%d"),
                "nav": float(row["nav"]),
                "cash": float(row["cash"]) if row["cash"] else 0.0,
                "unrealized_pnl": (
                    float(row["unrealized_pnl"]) if row["unrealized_pnl"] else 0.0
                ),
                "realized_pnl": (
                    float(row["realized_pnl"]) if row["realized_pnl"] else 0.0
                ),
                "net_cashflow": (
                    float(row["net_cashflow"]) if row["net_cashflow"] else 0.0
                ),
                "fee": float(row["fee"]) if row["fee"] else 0.0,
            }
        return None
    finally:
        await conn.close()


async def insert_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
) -> Dict[str, Any]:
    """
    특정 날짜의 포트폴리오 데이터를 삽입합니다.
    KIS API에서 데이터를 가져와서 테이블에 저장합니다.

    Args:
        date: 삽입할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        삽입된 데이터 딕셔너리
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_{account_type}_balance_kis_{account_number}"

        # 계좌 타입에 따라 다른 API 함수 호출
        # 기본값 설정
        nav = 0.0
        cash = 0.0
        unrealized_pnl = 0.0
        realized_pnl = 0.0
        net_cashflow = 0.0
        fee = 0.0
        if account_type == "future":
            # 선물 계좌인 경우
            # KIS API는 YYYYMMDD 형식을 요구하므로 날짜 형식 변환
            kis_date = date.replace("-", "")

            # KisClient 인스턴스 생성
            client = KisClient()
            futures_data = await client.get_futures_balance_settlement(kis_date)

            # 디버깅을 위한 로그
            print("KIS API Response:", futures_data)

            # API 응답에서 필요한 데이터 추출
            output1 = futures_data.get("output1", [])  # 리스트로 변경
            output2 = futures_data.get("output2", {})  # 딕셔너리로 변경

            # output2에서 데이터 추출 (잔고 정보)
            if output2 and isinstance(output2, dict):
                # NAV (총 평가금액) - opt_lqd_evlu_amt 사용
                nav = float(output2.get("opt_lqd_evlu_amt", 0))
                # 현금 - dnca_cash 사용
                cash = float(output2.get("dnca_cash", 0))
                # 수수료
                fee = float(output2.get("fee", 0))

            # output1에서 데이터 추출 (거래 정보)
            if output1 and isinstance(output1, list):
                total_realized_pnl = 0.0

                for item in output1:
                    # 실현손익 (trad_pfls_amt)
                    realized_pnl_item = float(item.get("trad_pfls_amt", 0))

                    total_realized_pnl += realized_pnl_item

                realized_pnl = total_realized_pnl

        elif account_type == "spot":
            # 현물 계좌인 경우 - 현재는 기본값으로 설정
            # TODO: 현물 계좌 API 호출 함수가 필요할 경우 여기에 추가
            nav = 0.0
            cash = 0.0
            unrealized_pnl = 0.0
            realized_pnl = 0.0
            net_cashflow = 0.0
            fee = 0.0
        else:
            raise HTTPException(
                status_code=400, detail="Invalid account_type. Use 'future' or 'spot'"
            )

        # 데이터베이스에 삽입
        query = f"""
        INSERT INTO {table_name} (date, nav, cash, unrealized_pnl, realized_pnl, net_cashflow, fee)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (date) DO UPDATE SET
            nav = EXCLUDED.nav,
            cash = EXCLUDED.cash,
            unrealized_pnl = EXCLUDED.unrealized_pnl,
            realized_pnl = EXCLUDED.realized_pnl,
            net_cashflow = EXCLUDED.net_cashflow,
            fee = EXCLUDED.fee
        RETURNING date, nav, cash, unrealized_pnl, realized_pnl, net_cashflow, fee
        """

        # 문자열 날짜를 datetime 객체로 변환
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        row = await conn.fetchrow(
            query,
            date_obj,
            Decimal(str(nav)),
            Decimal(str(cash)),
            Decimal(str(unrealized_pnl)),
            Decimal(str(realized_pnl)),
            Decimal(str(net_cashflow)),
            Decimal(str(fee)),
        )

        return {
            "date": row["date"].strftime("%Y-%m-%d"),
            "nav": float(row["nav"]),
            "cash": float(row["cash"]) if row["cash"] else 0.0,
            "unrealized_pnl": (
                float(row["unrealized_pnl"]) if row["unrealized_pnl"] else 0.0
            ),
            "realized_pnl": float(row["realized_pnl"]) if row["realized_pnl"] else 0.0,
            "net_cashflow": float(row["net_cashflow"]) if row["net_cashflow"] else 0.0,
            "fee": float(row["fee"]) if row["fee"] else 0.0,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to insert portfolio data: {str(e)}"
        )
    finally:
        await conn.close()


async def delete_portfolio_data(
    date: str, account_type: str = "future", account_number: str = "43037074"
) -> Dict[str, str]:
    """
    특정 날짜의 포트폴리오 데이터를 삭제합니다.

    Args:
        date: 삭제할 날짜 (YYYY-MM-DD 형식)
        account_type: 계좌 타입 ("future" 또는 "spot")
        account_number: 계좌번호

    Returns:
        삭제 결과 메시지
    """
    conn = await get_db_connection()
    try:
        # 테이블 이름 결정
        table_name = f"daily_{account_type}_balance_kis_{account_number}"

        # 문자열 날짜를 datetime 객체로 변환
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        query = f"DELETE FROM {table_name} WHERE date = $1"
        result = await conn.execute(query, date_obj)

        if result == "DELETE 1":
            return {"message": f"Portfolio data for {date} deleted successfully"}
        else:
            return {"message": f"No portfolio data found for {date}"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete portfolio data: {str(e)}"
        )
    finally:
        await conn.close()
