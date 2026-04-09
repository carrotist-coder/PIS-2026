"""Handler for CancelDealCommand."""

from src.application.port.outbound.deal_repository import DealRepository
from ..cancel_deal_command import CancelDealCommand


class CancelDealHandler:
  """
  Handler for CancelDealCommand.

  This handler cancels an existing deal:
  1. Load deal from repository
  2. Call domain method cancel()
  3. Save updated deal
  """

  def __init__(self, repository: DealRepository):
    self.repository = repository

  def handle(self, command: CancelDealCommand) -> None:
    """
    Execute the command.

    Args:
        command: CancelDealCommand with deal_id and reason

    Raises:
        ValueError: If deal not found or cannot be cancelled
    """
    deal = self.repository.find_by_id(command.deal_id)
    if not deal:
      raise ValueError(f"Deal {command.deal_id} not found")

    deal.cancel(command.reason)
    self.repository.save(deal)
