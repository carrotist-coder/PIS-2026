"""Command for marking a deal as paid."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarkDealAsPaidCommand:
  """
  Command for marking a deal as paid.

  This command marks an existing deal as paid after invoice payment.
  """

  deal_id: str

  def __post_init__(self):
    if not self.deal_id or not self.deal_id.strip():
      raise ValueError("deal_id cannot be empty")
