"""Deal status value object."""

from enum import Enum


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
    
    def can_transition_to(self, new_status: "DealStatus") -> bool:
        """Check if transition to new status is allowed."""
        transitions = {
            DealStatus.NEGOTIATION: [DealStatus.APPROVAL, DealStatus.INVOICED, DealStatus.CANCELLED],
            DealStatus.APPROVAL: [DealStatus.NEGOTIATION, DealStatus.CANCELLED],
            DealStatus.INVOICED: [DealStatus.PAID, DealStatus.CANCELLED],
            DealStatus.PAID: [],
            DealStatus.CANCELLED: [],
        }
        return new_status in transitions.get(self, [])