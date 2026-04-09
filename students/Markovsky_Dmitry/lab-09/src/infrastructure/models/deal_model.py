"""SQLAlchemy ORM model for Deal aggregate."""

from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class DealStatusSQL(str, enum.Enum):
    """SQL representation of DealStatus."""
    NEGOTIATION = "negotiation"
    APPROVAL = "approval"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"


class DealModel(Base):
    __tablename__ = "deals"

    id = Column(String(50), primary_key=True)
    client_id = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(SQLEnum(DealStatusSQL), nullable=False, default=DealStatusSQL.NEGOTIATION)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    invoice_id = Column(String(50), nullable=True)
    payment_link = Column(String(500), nullable=True)

    def to_domain(self):
        """Convert ORM model to domain Deal entity."""
        from src.domain.models.money import Money
        from src.domain.models.deal import Deal, DealStatus

        domain_status = {
            "negotiation": DealStatus.NEGOTIATION,
            "approval": DealStatus.APPROVAL,
            "invoiced": DealStatus.INVOICED,
            "paid": DealStatus.PAID,
            "cancelled": DealStatus.CANCELLED
        }[self.status.value]

        deal = Deal(
            deal_id=self.id,
            client_id=self.client_id,  # ClientId value object will be created in repository
            title=self.title,          # DealTitle value object
            amount=Money(self.amount, self.currency),
            status=domain_status
        )
        # Manually set created_at because domain sets it automatically, but we want from DB
        deal._created_at = self.created_at
        deal._updated_at = self.updated_at
        return deal

    @staticmethod
    def from_domain(deal):
        """Create ORM model from domain Deal entity."""
        return DealModel(
            id=deal.id,
            client_id=deal.client_id.value,
            title=deal.title.value,
            amount=deal.amount.amount,
            currency=deal.amount.currency,
            status=DealStatusSQL(deal.status.value),
            created_at=deal.created_at,
            updated_at=deal.updated_at
        )
