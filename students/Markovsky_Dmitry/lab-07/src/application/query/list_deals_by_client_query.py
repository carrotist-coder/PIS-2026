"""Query for listing deals by client."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListDealsByClientQuery:
  """
  Query to list deals for a specific client.

  This query retrieves all deals belonging to a client.
  Supports pagination with limit and offset.
  """

  client_id: str
  limit: Optional[int] = None
  offset: Optional[int] = None

  def __post_init__(self):
    if not self.client_id or not self.client_id.strip():
      raise ValueError("client_id cannot be empty")

    if self.limit is not None and self.limit <= 0:
      raise ValueError("limit must be positive")

    if self.offset is not None and self.offset < 0:
      raise ValueError("offset cannot be negative")
