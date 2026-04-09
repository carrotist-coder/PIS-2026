"""Query for getting a deal by ID."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetDealByIdQuery:
  """
  Query to get a deal by its ID.

  This query retrieves a single deal without modifying state.
  """

  deal_id: str

  def __post_init__(self):
    if not self.deal_id or not self.deal_id.strip():
      raise ValueError("deal_id cannot be empty")
