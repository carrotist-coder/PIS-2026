"""Command for creating a new deal."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateDealCommand:
  """
  Command for creating a new deal.

  Contains all data needed to create a deal.
  Validation is performed at the command level for primitive values.
  """

  client_id: str
  title: str
  amount: float
  currency: str = "USD"
  idempotency_key: Optional[str] = None

  def __post_init__(self):
    if not self.client_id or not self.client_id.strip():
      raise ValueError("client_id cannot be empty")

    if not self.title or not self.title.strip():
      raise ValueError("title cannot be empty")

    if len(self.title.strip()) < 3:
      raise ValueError("title must be at least 3 characters")

    if len(self.title) > 100:
      raise ValueError("title must be at most 100 characters")

    if self.amount <= 0:
      raise ValueError(f"amount must be positive, got {self.amount}")

    if self.currency not in ["USD", "BYN", "EUR"]:
      raise ValueError(f"unsupported currency: {self.currency}")
