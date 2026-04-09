"""Mock implementation of InvoiceService."""

import uuid
from datetime import datetime

from src.domain.models.money import Money
from src.application.port.outbound.invoice_service import InvoiceService


class MockInvoiceService(InvoiceService):
    """
    Mock implementation of InvoiceService for development.

    Simulates invoice creation without actual payment gateway integration.
    Returns mock invoice IDs and payment links for testing.

    In production, this would be replaced with a real implementation
    integrating with Stripe, CloudPayments, etc.
    """

    def __init__(self, simulate_failure: bool = False):
        """
        Initialize mock invoice service.

        Args:
            simulate_failure: If True, randomly fail to test error handling
        """
        self.simulate_failure = simulate_failure
        self._invoices: dict = {}

    def create_invoice(self, deal_id: str, amount: Money) -> str:
        """
        Create a mock invoice.

        Args:
            deal_id: Deal identifier
            amount: Invoice amount

        Returns:
            Mock invoice ID

        Raises:
            Exception: If simulate_failure is True (for testing)
        """
        # Simulate failure for testing error handling
        if self.simulate_failure:
            raise Exception("Mock: Invoice service temporarily unavailable")

        # Generate mock invoice ID
        year = datetime.now().year
        invoice_id = f"INV-{year}-{uuid.uuid4().hex[:6].upper()}"

        # Store mock invoice data
        self._invoices[invoice_id] = {
            "deal_id": deal_id,
            "amount": amount,
            "created_at": datetime.now(),
            "payment_link": f"https://mock-payment.example.com/{invoice_id}"
        }

        return invoice_id

    def get_payment_link(self, invoice_id: str) -> str:
        """
        Get mock payment link for invoice.

        Args:
            invoice_id: Invoice identifier

        Returns:
            Mock payment URL
        """
        invoice = self._invoices.get(invoice_id)
        if invoice:
            return invoice["payment_link"]

        # Return generic link if invoice not found
        return f"https://mock-payment.example.com/{invoice_id}"

    def get_invoice(self, invoice_id: str) -> dict:
        """
        Get invoice details (helper method for testing).

        Args:
            invoice_id: Invoice identifier

        Returns:
            Invoice data if found
        """
        return self._invoices.get(invoice_id)
