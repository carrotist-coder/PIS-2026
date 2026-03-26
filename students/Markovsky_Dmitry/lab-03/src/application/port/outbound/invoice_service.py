"""Outbound port for invoice creation."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models.money import Money


class InvoiceService(ABC):
    """
    Outbound port: Service for creating invoices.
    
    This interface defines how the application layer interacts with
    the invoice service (external or internal) to generate invoices.
    """
    
    @abstractmethod
    def create_invoice(self, deal_id: str, amount: Money) -> str:
        """
        Create an invoice for a deal.
        
        Args:
            deal_id: Unique identifier of the deal
            amount: Amount to invoice (should match deal amount)
            
        Returns:
            Invoice ID (format: INV-YYYY-NNNN)
            
        Raises:
            Exception: If invoice creation fails (will be handled by retry logic)
            
        Note:
            This operation is synchronous in the happy path but may be
            retried asynchronously on failure.
        """
        pass
    
    @abstractmethod
    def get_payment_link(self, invoice_id: str) -> Optional[str]:
        """
        Get payment link for an existing invoice.
        
        Args:
            invoice_id: Invoice identifier
            
        Returns:
            Payment URL if available, None otherwise
        """
        pass