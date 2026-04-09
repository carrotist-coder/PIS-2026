"""Handler for GetDealByIdQuery."""

from typing import Optional
from src.application.port.outbound.deal_repository import DealRepository
from ..get_deal_by_id_query import GetDealByIdQuery
from ..dto.deal_dto import DealDto


class GetDealByIdHandler:
  """
  Handler for GetDealByIdQuery.

  This handler retrieves a deal by ID and converts it to a DTO.
  """

  def __init__(self, repository: DealRepository):
    self.repository = repository

  def handle(self, query: GetDealByIdQuery) -> Optional[DealDto]:
    """
    Execute the query.

    Args:
        query: GetDealByIdQuery with deal_id

    Returns:
        DealDto if found, None otherwise
    """
    deal = self.repository.find_by_id(query.deal_id)

    if not deal:
      return None

    return DealDto(
      id=deal.id,
      client_id=str(deal.client_id),
      title=str(deal.title),
      amount=float(deal.amount.amount),
      currency=deal.amount.currency,
      status=deal.status.value,
      created_at=deal.created_at
    )
