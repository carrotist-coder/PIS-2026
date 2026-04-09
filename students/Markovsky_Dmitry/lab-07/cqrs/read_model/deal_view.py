from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DealView:
  """Read Model: Денормализованная проекция Deal"""

  deal_id: str
  client_id: str
  client_name: Optional[str]
  title: str
  amount: float
  currency: str
  status: str
  status_display: str
  created_at: datetime
  updated_at: datetime
  invoice_id: Optional[str]
  payment_link: Optional[str]
  is_paid: bool
  days_since_created: int

  def __post_init__(self):
    """Вычисление производных полей"""
    if self.days_since_created is None and self.created_at:
      delta = datetime.now() - self.created_at
      self.days_since_created = delta.days


# ORM Model для таблицы deal_views
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DealViewORM(Base):
  __tablename__ = "deal_views"

  deal_id = Column(String(50), primary_key=True, index=True)
  client_id = Column(String(50), nullable=False, index=True)
  client_name = Column(String(200), nullable=True)
  title = Column(String(200), nullable=False)
  amount = Column(Numeric(12, 2), nullable=False)
  currency = Column(String(3), nullable=False)
  status = Column(String(20), nullable=False, index=True)
  status_display = Column(String(50), nullable=True)
  created_at = Column(DateTime, nullable=False)
  updated_at = Column(DateTime, nullable=False)
  invoice_id = Column(String(50), nullable=True)
  payment_link = Column(String(500), nullable=True)
  is_paid = Column(Boolean, default=False)
  days_since_created = Column(Integer, nullable=True)
