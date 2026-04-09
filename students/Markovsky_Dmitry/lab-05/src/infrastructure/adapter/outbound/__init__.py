"""Outbound adapters: repositories, external services."""

from .in_memory_deal_repository import InMemoryDealRepository
from .postgres_deal_repository import PostgresDealRepository
from .mock_invoice_service import MockInvoiceService
from .console_notification_service import ConsoleNotificationService

__all__ = [
    "InMemoryDealRepository",
    "PostgresDealRepository",
    "MockInvoiceService",
    "ConsoleNotificationService",
]
