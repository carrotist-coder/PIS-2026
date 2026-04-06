"""Command for cancelling a deal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CancelDealCommand:
  """
  Command for cancelling a deal.

  This command cancels an existing deal with a reason.
  """

  deal_id: str
  reason: str

  def __post_init__(self):
    if not self.deal_id or not self.deal_id.strip():
      raise ValueError("deal_id cannot be empty")
    if not self.reason or not self.reason.strip():
      raise ValueError("reason cannot be empty")
