"""Deal entity."""

from datetime import datetime
from typing import List, Optional
from ..value_objects.money import Money
from ..value_objects.deal_status import DealStatus
from ..value_objects.client_id import ClientId
from ..value_objects.deal_title import DealTitle
from ..events.deal_events import (
    DealCreated,
    DealInvoiced,
    DealPaid,
    DealCancelled,
    DomainEvent
)


class Deal:
    """Entity: business deal with a client."""
    
    def __init__(
        self,
        deal_id: str,
        client_id: ClientId,
        title: DealTitle,
        amount: Money,
        status: DealStatus = None
    ):
        """
        Initialize Deal entity.
        
        Args:
            deal_id: Unique identifier
            client_id: Client reference
            title: Deal title
            amount: Deal value
            status: Initial status (default: NEGOTIATION)
        """
        self._id = deal_id
        self._client_id = client_id
        self._title = title
        self._amount = amount
        self._status = status or DealStatus.NEGOTIATION
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._events: List[DomainEvent] = []
        
        self._validate()
        self._register_event(DealCreated(deal_id, client_id, title, amount))
    
    def _validate(self) -> None:
        """Validate business invariants."""
        if self._amount.amount <= 0:
            raise ValueError(f"Deal amount must be positive, got: {self._amount.amount}")
    
    def _register_event(self, event: DomainEvent) -> None:
        """Register a domain event."""
        self._events.append(event)
    
    def mark_as_invoiced(self, invoice_id: str) -> None:
        """Mark deal as invoiced."""
        if not self._status.can_transition_to(DealStatus.INVOICED):
            raise ValueError(
                f"Cannot invoice deal: current status is {self._status}, "
                f"expected NEGOTIATION or APPROVAL"
            )
        
        self._status = DealStatus.INVOICED
        self._updated_at = datetime.now()
        self._register_event(DealInvoiced(self._id, invoice_id, self._amount))
    
    def mark_as_paid(self) -> None:
        """Mark deal as paid."""
        if not self._status.can_transition_to(DealStatus.PAID):
            raise ValueError(
                f"Cannot mark as paid: deal is in status {self._status}, "
                f"expected INVOICED"
            )
        
        self._status = DealStatus.PAID
        self._updated_at = datetime.now()
        self._register_event(DealPaid(self._id))
    
    def cancel(self, reason: str) -> None:
        """Cancel the deal."""
        if not self._status.can_transition_to(DealStatus.CANCELLED):
            raise ValueError(
                f"Cannot cancel deal: deal is in status {self._status}"
            )
        
        self._status = DealStatus.CANCELLED
        self._updated_at = datetime.now()
        self._register_event(DealCancelled(self._id, reason))
    
    def get_events(self) -> List[DomainEvent]:
        """Get all registered events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear all registered events."""
        self._events.clear()
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def client_id(self) -> ClientId:
        return self._client_id
    
    @property
    def title(self) -> DealTitle:
        return self._title
    
    @property
    def amount(self) -> Money:
        return self._amount
    
    @property
    def status(self) -> DealStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Equality based on ID
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Deal):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"Deal(id='{self._id}', client='{self._client_id}', amount={self._amount}, status={self._status})"