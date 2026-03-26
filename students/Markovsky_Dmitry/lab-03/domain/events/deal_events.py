"""Domain events for deal aggregate."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.money import Money
from ..value_objects.client_id import ClientId
from ..value_objects.deal_title import DealTitle


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()


@dataclass
class DealCreated(DomainEvent):
    """Event raised when a deal is created."""
    
    deal_id: str
    client_id: ClientId
    title: DealTitle
    amount: Money


@dataclass
class DealInvoiced(DomainEvent):
    """Event raised when an invoice is created for a deal."""
    
    deal_id: str
    invoice_id: str
    amount: Money


@dataclass
class DealPaid(DomainEvent):
    """Event raised when a deal is paid."""
    
    deal_id: str


@dataclass
class DealCancelled(DomainEvent):
    """Event raised when a deal is cancelled."""
    
    deal_id: str
    reason: str