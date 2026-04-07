"""Query DTOs and read models for application layer."""

from .get_deal_by_id_query import GetDealByIdQuery
from .list_deals_by_client_query import ListDealsByClientQuery
from .dto import DealDto

__all__ = [
    'GetDealByIdQuery',
    'ListDealsByClientQuery',
    'DealDto',
]
