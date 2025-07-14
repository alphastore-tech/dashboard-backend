from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.database.connection import get_db_connection
from app.services.kisClient import KisClient
from datetime import timezone, timedelta

KST = timezone(timedelta(hours=9))


async def insert_daily_future_balance(
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None,
    domain: Optional[str] = None,
    cano: Optional[str] = None,
    acnt_prdt_cd: Optional[str] = None,
    aws_secret_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    특정 날짜의 선물옵션 잔고 데이터를 KIS API에서 가져와서 daily_future_balance_kis 테이블에 삽입합니다.

    Args:
        app_key: KIS API 앱 키
        app_secret: KIS API 앱 시크릿
        domain: KIS API 도메인
        cano: 계좌번호
        acnt_prdt_cd: 계좌상품코드
        aws_secret_id: AWS 시크릿 ID

    Returns:
        삽입된 데이터 딕셔너리
    """
    conn = await get_db_connection()
    try:
        date_obj = datetime.now(KST).date()

        # KisClient 인스턴스 생성
        client = KisClient(
            app_key=app_key,
            app_secret=app_secret,
            domain=domain,
            cano=cano,
            acnt_prdt_cd=acnt_prdt_cd,
            aws_secret_id=aws_secret_id
        )

        # KIS API에서 잔고 데이터 가져오기
        balance_data = await client.get_futureoption_balance()

        # 디버깅을 위한 로그
        print("KIS API Response:", balance_data)

        # API 응답에서 output2 데이터 추출 (잔고 정보)
        output2 = balance_data.get("output2", {})

        # 테이블 컬럼에 매핑되는 데이터 추출
        # 모든 필드를 0으로 초기화하고, API 응답에서 있는 값만 업데이트
        data = {
            "date": date_obj,
            "dnca_cash": Decimal(str(output2.get("dnca_cash", 0))),
            "frcr_dncl_amt": Decimal(str(output2.get("frcr_dncl_amt", 0))),
            "dnca_sbst": Decimal(str(output2.get("dnca_sbst", 0))),
            "tot_dncl_amt": Decimal(str(output2.get("tot_dncl_amt", 0))),
            "tot_ccld_amt": Decimal(str(output2.get("tot_ccld_amt", 0))),
            "cash_mgna": Decimal(str(output2.get("cash_mgna", 0))),
            "sbst_mgna": Decimal(str(output2.get("sbst_mgna", 0))),
            "mgna_tota": Decimal(str(output2.get("mgna_tota", 0))),
            "opt_dfpa": Decimal(str(output2.get("opt_dfpa", 0))),
            "thdt_dfpa": Decimal(str(output2.get("thdt_dfpa", 0))),
            "rnwl_dfpa": Decimal(str(output2.get("rnwl_dfpa", 0))),
            "fee": Decimal(str(output2.get("fee", 0))),
            "nxdy_dnca": Decimal(str(output2.get("nxdy_dnca", 0))),
            "nxdy_dncl_amt": Decimal(str(output2.get("nxdy_dncl_amt", 0))),
            "prsm_dpast": Decimal(str(output2.get("prsm_dpast", 0))),
            "prsm_dpast_amt": Decimal(str(output2.get("prsm_dpast_amt", 0))),
            "pprt_ord_psbl_cash": Decimal(str(output2.get("pprt_ord_psbl_cash", 0))),
            "add_mgna_cash": Decimal(str(output2.get("add_mgna_cash", 0))),
            "add_mgna_tota": Decimal(str(output2.get("add_mgna_tota", 0))),
            "futr_trad_pfls_amt": Decimal(str(output2.get("futr_trad_pfls_amt", 0))),
            "opt_trad_pfls_amt": Decimal(str(output2.get("opt_trad_pfls_amt", 0))),
            "futr_evlu_pfls_amt": Decimal(str(output2.get("futr_evlu_pfls_amt", 0))),
            "opt_evlu_pfls_amt": Decimal(str(output2.get("opt_evlu_pfls_amt", 0))),
            "trad_pfls_amt_smtl": Decimal(str(output2.get("trad_pfls_amt_smtl", 0))),
            "evlu_pfls_amt_smtl": Decimal(str(output2.get("evlu_pfls_amt_smtl", 0))),
            "wdrw_psbl_tot_amt": Decimal(str(output2.get("wdrw_psbl_tot_amt", 0))),
            "ord_psbl_cash": Decimal(str(output2.get("ord_psbl_cash", 0))),
            "ord_psbl_sbst": Decimal(str(output2.get("ord_psbl_sbst", 0))),
            "ord_psbl_tota": Decimal(str(output2.get("ord_psbl_tota", 0))),
            "pchs_amt_smtl": Decimal(str(output2.get("pchs_amt_smtl", 0))),
            "evlu_amt_smtl": Decimal(str(output2.get("evlu_amt_smtl", 0))),
        }

        # INSERT 쿼리 작성 (ON CONFLICT로 중복 처리)
        columns = list(data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]

        query = f"""
        INSERT INTO daily_future_balance_kis ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT (date) DO UPDATE SET
        """

        # UPDATE SET 절 생성 (date 제외)
        update_clauses = []
        for i, column in enumerate(columns[1:], 2):  # date 제외하고 시작
            update_clauses.append(f"{column} = ${i}")

        query += ", ".join(update_clauses)
        query += f" RETURNING {', '.join(columns)}"

        # 데이터베이스에 삽입
        row = await conn.fetchrow(query, *data.values())

        # 결과를 딕셔너리로 변환
        result = {}
        for i, column in enumerate(columns):
            value = row[column]
            if isinstance(value, Decimal):
                result[column] = float(value)
            elif hasattr(value, "strftime"):  # datetime.date 객체인지 확인
                result[column] = value.strftime("%Y-%m-%d")
            else:
                result[column] = value

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert daily future balance data: {str(e)}",
        )
    finally:
        await conn.close()


async def read_daily_future_balance(date: str) -> Optional[Dict[str, Any]]:
    """
    특정 날짜의 선물옵션 잔고 데이터를 조회합니다.

    Args:
        date: 조회할 날짜 (YYYY-MM-DD 형식)

    Returns:
        잔고 데이터 딕셔너리 또는 None
    """
    conn = await get_db_connection()
    try:
        # 날짜 형식 검증
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        query = """
        SELECT * FROM daily_future_balance_kis 
        WHERE date = $1
        """

        row = await conn.fetchrow(query, date_obj)

        if row:
            # 결과를 딕셔너리로 변환
            result = {}
            for column in row.keys():
                value = row[column]
                if isinstance(value, Decimal):
                    result[column] = float(value)
                elif hasattr(value, "strftime") and hasattr(value, "year"):  # datetime.date 객체인지 확인
                    result[column] = value.strftime("%Y-%m-%d")
                else:
                    result[column] = value
            return result
        return None

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read daily future balance data: {str(e)}",
        )
    finally:
        await conn.close()


async def delete_daily_future_balance(date: str) -> Dict[str, str]:
    """
    특정 날짜의 선물옵션 잔고 데이터를 삭제합니다.

    Args:
        date: 삭제할 날짜 (YYYY-MM-DD 형식)

    Returns:
        삭제 결과 메시지
    """
    conn = await get_db_connection()
    try:
        # 날짜 형식 검증
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        query = "DELETE FROM daily_future_balance_kis WHERE date = $1"
        result = await conn.execute(query, date_obj)

        if result == "DELETE 1":
            return {
                "message": f"Daily future balance data for {date} deleted successfully"
            }
        else:
            return {"message": f"No daily future balance data found for {date}"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete daily future balance data: {str(e)}",
        )
    finally:
        await conn.close()
