"""Deal service implementation."""

from typing import Optional

from src.domain.models.deal import Deal
from src.application.port.inbound.create_deal_use_case import (
    CreateDealUseCase,
    CreateDealCommand
)
from src.application.port.inbound.get_deal_use_case import GetDealUseCase
from src.application.port.outbound.deal_repository import DealRepository
from src.application.port.outbound.invoice_service import InvoiceService
from src.application.port.outbound.notification_service import NotificationService


class DealService(CreateDealUseCase, GetDealUseCase):
    """
    Application service implementing deal-related use cases.

    This service orchestrates the business logic for deal management,
    coordinating between domain objects and external services through ports.

    Dependencies are injected via constructor (Dependency Inversion).
    """

    def __init__(
        self,
        deal_repository: DealRepository,
        invoice_service: InvoiceService,
        notification_service: NotificationService
    ):
        """
        Initialize DealService with required dependencies.

        Args:
            deal_repository: Repository for deal persistence (outbound port)
            invoice_service: Service for invoice creation (outbound port)
            notification_service: Service for notifications (outbound port)
        """
        self.repository = deal_repository
        self.invoice_service = invoice_service
        self.notification_service = notification_service

    def create_deal(self, command: CreateDealCommand) -> str:
        """
        Create a new deal.

        Steps:
        1. Check idempotency key (if provided)
        2. Validate command data
        3. Create domain Deal object
        4. Persist deal via repository
        5. Create invoice via invoice service
        6. Update deal status to INVOICED
        7. Send notification (async via queue in full implementation)
        8. Return deal ID

        Currently returns mock ID for skeleton.

        Args:
            command: Command with deal creation data

        Returns:
            Deal ID (format: D-YYYY-NNNN)

        Raises:
            ValueError: If validation fails
            DomainException: If business rules violated
        """
        # TODO: Full implementation
        raise NotImplementedError(
            "DealService.create_deal will be implemented"
        )

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """
        Retrieve a deal by ID.

        Args:
            deal_id: Deal identifier

        Returns:
            Deal aggregate if found, None otherwise
        """
        # TODO: Full implementation
        raise NotImplementedError(
            "DealService.get_deal will be implemented"
        )
