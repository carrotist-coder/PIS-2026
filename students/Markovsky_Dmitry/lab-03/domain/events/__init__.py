"""Domain events module."""

from .deal_events import (
    DomainEvent,
    DealCreated,
    DealInvoiced,
    DealPaid,
    DealCancelled
)

__all__ = [
    'DomainEvent',
    'DealCreated',
    'DealInvoiced',
    'DealPaid',
    'DealCancelled',
]