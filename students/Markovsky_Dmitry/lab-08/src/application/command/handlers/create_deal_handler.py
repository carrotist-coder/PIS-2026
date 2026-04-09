"""Handler for CreateDealCommand."""

import uuid
from datetime import datetime

from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from src.domain.models.deal import Deal
from src.domain.models.money import Money
from src.application.port.outbound.deal_repository import DealRepository
from src.application.port.outbound.invoice_service import InvoiceService
from src.application.port.outbound.notification_service import NotificationService
from ..create_deal_command import CreateDealCommand


class CreateDealHandler:
    """
    Handler for CreateDealCommand.

    This handler orchestrates the creation of a new deal:
    1. Check idempotency
    2. Create domain aggregate
    3. Save deal
    4. Create invoice
    5. Send notification
    """

    def __init__(
        self,
        repository: DealRepository,
        invoice_service: InvoiceService,
        notification_service: NotificationService
    ):
        self.repository = repository
        self.invoice_service = invoice_service
        self.notification_service = notification_service

    def handle(self, command: CreateDealCommand) -> str:
        """
        Execute the command.

        Args:
            command: CreateDealCommand with deal data

        Returns:
            Created deal ID

        Raises:
            ValueError: If validation fails
        """
        if command.idempotency_key:
            cached = self.repository.get_cached_response(command.idempotency_key)
            if cached:
                return cached

        year = datetime.now().year
        deal_id = f"D-{year}-{uuid.uuid4().hex[:6].upper()}"

        client_id = ClientId(command.client_id)
        title = DealTitle(command.title)
        amount = Money(command.amount, command.currency)
        deal = Deal(deal_id, str(client_id), str(title), amount)

        self.repository.save(deal)

        invoice_id = self.invoice_service.create_invoice(deal_id, amount)

        deal.mark_as_invoiced()
        self.repository.save(deal)

        payment_link = self.invoice_service.get_payment_link(invoice_id)
        client_email = f"{command.client_id}@example.com"
        self.notification_service.send_invoice_created(
            client_email, command.title, invoice_id, payment_link
        )

        if command.idempotency_key:
            self.repository.save_idempotency_key(command.idempotency_key, deal_id)

        return deal_id
