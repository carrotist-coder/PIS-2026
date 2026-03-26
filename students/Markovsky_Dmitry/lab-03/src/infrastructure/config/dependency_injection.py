"""
Dependency Injection container for Deal Service.

This demonstrates the Dependency Inversion Principle:
- High-level modules (DealService) do not depend on low-level modules
- Both depend on abstractions (ports)
- Abstractions do not depend on details; details depend on abstractions
"""
from src.application.service.deal_service import DealService
from src.application.port.outbound.deal_repository import DealRepository
from src.application.port.outbound.invoice_service import InvoiceService
from src.application.port.outbound.notification_service import NotificationService
from src.infrastructure.adapter.outbound.in_memory_deal_repository import (
    InMemoryDealRepository
)
from src.infrastructure.adapter.outbound.mock_invoice_service import (
    MockInvoiceService
)
from src.infrastructure.adapter.outbound.console_notification_service import (
    ConsoleNotificationService
)
from src.infrastructure.adapter.inbound.deal_controller import DealController


class DependencyContainer:
    """
    DI Container that wires all components together.

    This container creates all necessary dependencies and injects them
    according to the hexagonal architecture pattern.

    Key principle: The application service (DealService) receives its
    dependencies through constructor injection, not by creating them itself.
    """

    def __init__(self):
        """
        Initialize all dependencies.

        Flow:
        1. Create outbound adapters (concrete implementations of ports)
        2. Inject outbound adapters into application service
        3. Inject application service into inbound adapters
        """
        self.deal_repository: DealRepository = InMemoryDealRepository()
        self.invoice_service: InvoiceService = MockInvoiceService(
            simulate_failure=False  # Set to True for testing error handling
        )
        self.notification_service: NotificationService = ConsoleNotificationService()

        self.deal_service: DealService = DealService(
            deal_repository=self.deal_repository,
            invoice_service=self.invoice_service,
            notification_service=self.notification_service
        )

        self.deal_controller: DealController = DealController(
            create_deal_uc=self.deal_service,
            get_deal_uc=self.deal_service
        )

    def get_deal_service(self) -> DealService:
        return self.deal_service

    def get_deal_controller(self) -> DealController:
        return self.deal_controller

    def get_repository(self) -> DealRepository:
        return self.deal_repository
