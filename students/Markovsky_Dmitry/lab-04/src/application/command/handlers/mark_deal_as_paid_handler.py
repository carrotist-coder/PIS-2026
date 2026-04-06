"""Handler for MarkDealAsPaidCommand."""

from src.application.port.outbound.deal_repository import DealRepository
from ..mark_deal_as_paid_command import MarkDealAsPaidCommand


class MarkDealAsPaidHandler:
  """
  Handler for MarkDealAsPaidCommand.

  This handler marks an existing deal as paid:
  1. Load deal from repository
  2. Call domain method mark_as_paid()
  3. Save updated deal
  """

  def __init__(self, repository: DealRepository):
    self.repository = repository

  def handle(self, command: MarkDealAsPaidCommand) -> None:
    """
    Execute the command.

    Args:
        command: MarkDealAsPaidCommand with deal_id

    Raises:
        ValueError: If deal not found or cannot be paid
    """
    deal = self.repository.find_by_id(command.deal_id)
    if not deal:
      raise ValueError(f"Deal {command.deal_id} not found")

    deal.mark_as_paid()
    self.repository.save(deal)
