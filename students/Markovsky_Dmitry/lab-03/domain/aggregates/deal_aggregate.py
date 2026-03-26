"""Deal aggregate root."""

from typing import List, Optional
from ..entities.deal import Deal
from ..entities.invoice import Invoice
from ..value_objects.money import Money
from ..events.deal_events import DomainEvent


class DealAggregate:
    """
    Aggregate Root: Deal with its invoice.
    
    This aggregate encapsulates the deal and its associated invoice,
    ensuring consistency between them.
    """
    
    def __init__(self, deal: Deal):
        """
        Initialize deal aggregate.
        
        Args:
            deal: Deal entity (root)
        """
        self._deal = deal
        self._invoice: Optional[Invoice] = None
    
    def create_invoice(self, invoice_id: str) -> None:
        """
        Create an invoice for the deal.
        
        Args:
            invoice_id: Unique invoice identifier
            
        Raises:
            ValueError: If invoice already exists
        """
        if self._invoice is not None:
            raise ValueError(f"Invoice already exists for deal {self._deal.id}")
        
        self._invoice = Invoice(invoice_id, self._deal.id, self._deal.amount)
        self._deal.mark_as_invoiced(invoice_id)
    
    def mark_as_paid(self) -> None:
        """
        Mark the deal as paid.
        
        Raises:
            ValueError: If no invoice exists
        """
        if self._invoice is None:
            raise ValueError(f"Cannot pay deal {self._deal.id} without invoice")
        
        self._invoice.mark_as_paid()
        self._deal.mark_as_paid()
    
    def cancel(self, reason: str) -> None:
        """
        Cancel the deal.
        
        Args:
            reason: Cancellation reason
        """
        self._deal.cancel(reason)
    
    def set_payment_link(self, payment_link: str) -> None:
        """
        Set payment link for the invoice.
        
        Args:
            payment_link: URL for payment
            
        Raises:
            ValueError: If no invoice exists
        """
        if self._invoice is None:
            raise ValueError(f"Cannot set payment link: no invoice for deal {self._deal.id}")
        
        self._invoice.set_payment_link(payment_link)
    
    def get_events(self) -> List[DomainEvent]:
        """Get all events from the aggregate."""
        events = self._deal.get_events()
        return events
    
    def clear_events(self) -> None:
        """Clear all events from the aggregate."""
        self._deal.clear_events()
    
    # Properties
    @property
    def deal(self) -> Deal:
        return self._deal
    
    @property
    def invoice(self) -> Optional[Invoice]:
        return self._invoice
    
    def __repr__(self) -> str:
        return f"DealAggregate(deal={self._deal.id}, invoice={self._invoice.id if self._invoice else 'None'})"