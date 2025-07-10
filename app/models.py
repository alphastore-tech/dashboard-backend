from sqlalchemy import Column, Date, Numeric, String, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RealizedPNL(Base):
    """ORM 매핑: realized_pnl_daily 테이블"""

    __tablename__ = "realized_pnl_daily"

    trade_date = Column(Date, primary_key=True, index=True)
    account_no = Column(String(30), nullable=False)
    realized_pnl = Column(Numeric(18, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
