"""Domain events for deal aggregate."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from ..value_objects.money import Money
from ..value_objects.client_id import ClientId
from ..value_objects.deal_title import DealTitle


class DomainEvent:
    """Base class for all domain events (non-dataclass)."""

    def __init__(self, occurred_at: Optional[datetime] = None):
        self.occurred_at = occurred_at or datetime.now()


@dataclass
class DealCreated(DomainEvent):
    """Event raised when a deal is created."""

    deal_id: str
    client_id: ClientId
    title: DealTitle
    amount: Money
    occurred_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Вызов инициализации базового класса не обязателен, но для единообразия
        super().__init__(self.occurred_at)


@dataclass
class DealInvoiced(DomainEvent):
    """Event raised when an invoice is created for a deal."""

    deal_id: str
    invoice_id: str
    amount: Money
    occurred_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        super().__init__(self.occurred_at)


@dataclass
class DealPaid(DomainEvent):
    """Event raised when a deal is paid."""

    deal_id: str
    occurred_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        super().__init__(self.occurred_at)


@dataclass
class DealCancelled(DomainEvent):
    """Event raised when a deal is cancelled."""

    deal_id: str
    reason: str
    occurred_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        super().__init__(self.occurred_at)
