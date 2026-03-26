"""Deal aggregate root."""

from datetime import datetime
from typing import Optional
from enum import Enum

from .money import Money


class DealStatus(Enum):
    """
    Status of a deal in the CRM workflow.
    
    Possible states:
    - NEGOTIATION: Initial state, deal is being discussed
    - APPROVAL: Awaiting approval for high-value deals
    - INVOICED: Invoice has been created
    - PAID: Payment received
    - CANCELLED: Deal is closed without success
    """
    
    NEGOTIATION = "negotiation"
    APPROVAL = "approval"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"
    
    def __str__(self) -> str:
        return self.value


class Deal:
    """
    Aggregate root representing a business deal with a client.
    
    This is the core domain entity that encapsulates all business rules
    related to deal lifecycle management.
    """
    
    def __init__(
        self,
        deal_id: str,
        client_id: str,
        title: str,
        amount: Money,
        status: DealStatus = DealStatus.NEGOTIATION,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a Deal aggregate.
        
        Args:
            deal_id: Unique identifier (format: D-YYYY-NNNN)
            client_id: Reference to client entity
            title: Deal description/title
            amount: Deal value (Money value object)
            status: Current deal status
            created_at: Creation timestamp (defaults to now)
        """
        self.id = deal_id
        self.client_id = client_id
        self.title = title
        self.amount = amount
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        
        # Business rule: Validate deal on creation
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate business rules for deal.
        """
        if not self.title or not self.title.strip():
            raise ValueError("Deal title cannot be empty")
        
        if not self.client_id or not self.client_id.strip():
            raise ValueError("Client ID cannot be empty")
        
        if self.amount.amount <= 0:
            raise ValueError(f"Deal amount must be positive, got: {self.amount.amount}")
    
    def submit_for_approval(self, manager_id: str) -> None:
        """
        Submit deal for approval (when amount exceeds limit).
        
        Args:
            manager_id: ID of manager approving the deal
            
        Raises:
            ValueError: If deal is not in NEGOTIATION state
        """
        if self.status != DealStatus.NEGOTIATION:
            raise ValueError(
                f"Cannot submit for approval: deal is in state {self.status}, "
                f"expected NEGOTIATION"
            )
        
        self.status = DealStatus.APPROVAL
        self.updated_at = datetime.now()
        # In future: store approval request metadata
    
    def approve(self) -> None:
        """
        Approve deal (transition from APPROVAL to NEGOTIATION).
        
        Raises:
            ValueError: If deal is not in APPROVAL state
        """
        if self.status != DealStatus.APPROVAL:
            raise ValueError(
                f"Cannot approve deal: deal is in state {self.status}, "
                f"expected APPROVAL"
            )
        
        self.status = DealStatus.NEGOTIATION
        self.updated_at = datetime.now()
    
    def reject(self) -> None:
        """
        Reject deal (transition from APPROVAL to CANCELLED).
        
        Raises:
            ValueError: If deal is not in APPROVAL state
        """
        if self.status != DealStatus.APPROVAL:
            raise ValueError(
                f"Cannot reject deal: deal is in state {self.status}, "
                f"expected APPROVAL"
            )
        
        self.status = DealStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def mark_as_invoiced(self) -> None:
        """
        Mark deal as invoiced (invoice has been created).
        
        Raises:
            ValueError: If deal is not in NEGOTIATION state
        """
        if self.status not in [DealStatus.NEGOTIATION, DealStatus.APPROVAL]:
            raise ValueError(
                f"Cannot mark as invoiced: deal is in state {self.status}, "
                f"expected NEGOTIATION or APPROVAL"
            )
        
        self.status = DealStatus.INVOICED
        self.updated_at = datetime.now()
    
    def mark_as_paid(self) -> None:
        """
        Mark deal as paid (payment received).
        
        Raises:
            ValueError: If deal is not in INVOICED state
        """
        if self.status != DealStatus.INVOICED:
            raise ValueError(
                f"Cannot mark as paid: deal is in state {self.status}, "
                f"expected INVOICED"
            )
        
        self.status = DealStatus.PAID
        self.updated_at = datetime.now()
    
    def cancel(self) -> None:
        """
        Cancel deal (only possible before invoiced).
        
        Raises:
            ValueError: If deal is already INVOICED or PAID
        """
        if self.status in [DealStatus.INVOICED, DealStatus.PAID]:
            raise ValueError(
                f"Cannot cancel deal: deal is already {self.status}"
            )
        
        self.status = DealStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"Deal(id='{self.id}', client='{self.client_id}', amount={self.amount}, status={self.status})"