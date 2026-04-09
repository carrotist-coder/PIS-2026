"""Read model DTO for deal data."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DealDto:
  """
  Read model for deal data.

  This DTO is used for query responses and contains
  a simplified view of the deal aggregate.
  """

  id: str
  client_id: str
  title: str
  amount: float
  currency: str
  status: str
  created_at: datetime
  invoice_id: Optional[str] = None
  payment_link: Optional[str] = None
