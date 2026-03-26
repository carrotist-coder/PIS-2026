"""In-memory implementation of DealRepository."""

from typing import Dict, Optional

from src.domain.models.deal import Deal
from src.application.port.outbound.deal_repository import DealRepository


class InMemoryDealRepository(DealRepository):
    """
    In-memory implementation of DealRepository.

    Stores deals in a Python dictionary for testing and development.
    This is a simple adapter that demonstrates the outbound port pattern.

    Note: This is NOT for production use (no persistence across restarts).
    """

    def __init__(self):
        """Initialize empty storage."""
        self._deals: Dict[str, Deal] = {}
        self._idempotency_keys: Dict[str, str] = {}

    def save(self, deal: Deal) -> None:
        """
        Save a deal (create or update).

        Args:
            deal: Deal aggregate to store
        """
        self._deals[deal.id] = deal

    def find_by_id(self, deal_id: str) -> Optional[Deal]:
        """
        Find a deal by its ID.

        Args:
            deal_id: Unique deal identifier

        Returns:
            Deal if found, None otherwise
        """
        return self._deals.get(deal_id)

    def update_status(self, deal_id: str, status) -> None:
        """
        Update deal status.

        Args:
            deal_id: Deal identifier
            status: New status

        Raises:
            ValueError: If deal not found
        """
        deal = self.find_by_id(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        deal.status = status

    def exists_by_idempotency_key(self, key: str) -> bool:
        """
        Check if idempotency key exists.

        Args:
            key: Idempotency key

        Returns:
            True if key exists, False otherwise
        """
        return key in self._idempotency_keys

    def save_idempotency_key(self, key: str, response: str) -> None:
        """
        Save idempotency key and response.

        Args:
            key: Idempotency key
            response: Response to cache
        """
        self._idempotency_keys[key] = response

    def get_cached_response(self, key: str) -> Optional[str]:
        """
        Get cached response for idempotency key.

        Args:
            key: Idempotency key

        Returns:
            Cached response if found, None otherwise
        """
        return self._idempotency_keys.get(key)

    def clear(self) -> None:
        self._deals.clear()
        self._idempotency_keys.clear()
