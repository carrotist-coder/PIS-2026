"""
Application service facade for Deal operations.

This service delegates to specialized Command/Query handlers
following the CQRS pattern.
"""
from src.application.command import CreateDealCommand, MarkDealAsPaidCommand, CancelDealCommand
from src.application.command.handlers import CreateDealHandler, MarkDealAsPaidHandler, CancelDealHandler
from src.application.port.outbound.deal_repository import DealRepository
from src.application.port.outbound.invoice_service import InvoiceService
from src.application.port.outbound.notification_service import NotificationService
from src.application.query.handlers import GetDealByIdHandler

from src.application.query import GetDealByIdQuery, DealDto


class DealApplicationService:
  """
  Application service facade.

  This class provides a simple interface for external clients
  and delegates all operations to specialized handlers.
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

    # Initialize handlers
    self._create_deal_handler = CreateDealHandler(
      repository, invoice_service, notification_service
    )
    self._mark_paid_handler = MarkDealAsPaidHandler(repository)
    self._cancel_deal_handler = CancelDealHandler(repository)
    self._get_deal_handler = GetDealByIdHandler(repository)

  # Commands
  def create_deal(self, command: CreateDealCommand) -> str:
    """
    Create a new deal.

    Args:
        command: CreateDealCommand with deal data

    Returns:
        Created deal ID
    """
    return self._create_deal_handler.handle(command)

  def mark_deal_as_paid(self, command: MarkDealAsPaidCommand) -> None:
    """
    Mark a deal as paid.

    Args:
        command: MarkDealAsPaidCommand with deal_id
    """
    self._mark_paid_handler.handle(command)

  def cancel_deal(self, command: CancelDealCommand) -> None:
    """
    Cancel a deal.

    Args:
        command: CancelDealCommand with deal_id and reason
    """
    self._cancel_deal_handler.handle(command)

  # Queries
  def get_deal_by_id(self, query: GetDealByIdQuery) -> DealDto:
    """
    Get a deal by ID.

    Args:
        query: GetDealByIdQuery with deal_id

    Returns:
        DealDto if found, None otherwise
    """
    return self._get_deal_handler.handle(query)
