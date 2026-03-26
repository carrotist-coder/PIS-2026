"""Invoice entity."""

from datetime import datetime
from typing import List, Optional
from ..value_objects.money import Money
from ..events.deal_events import DomainEvent


class Invoice:
    """Entity: invoice for a deal."""
    
    def __init__(
        self,
        invoice_id: str,
        deal_id: str,
        amount: Money,
        payment_link: Optional[str] = None
    ):
        """
        Initialize Invoice entity.
        
        Args:
            invoice_id: Unique identifier (INV-YYYY-NNNN)
            deal_id: Associated deal ID
            amount: Invoice amount
            payment_link: URL for payment
        """
        self._id = invoice_id
        self._deal_id = deal_id
        self._amount = amount
        self._payment_link = payment_link
        self._paid = False
        self._created_at = datetime.now()
        self._paid_at: Optional[datetime] = None
        self._events: List[DomainEvent] = []
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate business invariants."""
        if self._amount.amount <= 0:
            raise ValueError(f"Invoice amount must be positive: {self._amount}")
    
    def mark_as_paid(self) -> None:
        """Mark invoice as paid."""
        if self._paid:
            raise ValueError(f"Invoice {self._id} is already paid")
        
        self._paid = True
        self._paid_at = datetime.now()
    
    def set_payment_link(self, payment_link: str) -> None:
        """Set payment link for invoice."""
        if not payment_link or not payment_link.strip():
            raise ValueError("Payment link cannot be empty")
        
        if self._payment_link is not None:
            raise ValueError(f"Payment link already set for invoice {self._id}")
        
        self._payment_link = payment_link
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def deal_id(self) -> str:
        return self._deal_id
    
    @property
    def amount(self) -> Money:
        return self._amount
    
    @property
    def payment_link(self) -> Optional[str]:
        return self._payment_link
    
    @property
    def is_paid(self) -> bool:
        return self._paid
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def paid_at(self) -> Optional[datetime]:
        return self._paid_at
    
    # Equality based on ID
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Invoice):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"Invoice(id='{self._id}', deal='{self._deal_id}', amount={self._amount}, paid={self._paid})"