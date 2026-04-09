"""Application layer with CQRS pattern."""

from .command import (
    CreateDealCommand,
    MarkDealAsPaidCommand,
    CancelDealCommand,
)
from .query import (
    GetDealByIdQuery,
    ListDealsByClientQuery,
    DealDto,
)
from .service import DealApplicationService

__all__ = [
    'CreateDealCommand',
    'MarkDealAsPaidCommand',
    'CancelDealCommand',
    'GetDealByIdQuery',
    'ListDealsByClientQuery',
    'DealDto',
    'DealApplicationService',
]
