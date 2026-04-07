"""Outbound port for deal persistence."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models.deal import Deal


class DealRepository(ABC):
    """
    Outbound port: Repository for storing and retrieving deals.

    This interface defines how the application layer interacts with
    the persistence mechanism (database, in-memory, etc.).
    """

    @abstractmethod
    def save(self, deal: Deal) -> None:
        """
        Save a deal (create or update).

        Args:
            deal: Deal aggregate to persist
        """
        pass

    @abstractmethod
    def find_by_id(self, deal_id: str) -> Optional[Deal]:
        """
        Find a deal by its unique identifier.

        Args:
            deal_id: Unique identifier of the deal

        Returns:
            Deal aggregate if found, None otherwise
        """
        pass

    @abstractmethod
    def update_status(self, deal_id: str, status) -> None:
        """
        Update deal status (optimized operation).

        Args:
            deal_id: Unique identifier of the deal
            status: New deal status

        Raises:
            ValueError: If deal not found
        """
        pass

    @abstractmethod
    def exists_by_idempotency_key(self, key: str) -> bool:
        """
        Check if a request with given idempotency key was processed.

        Args:
            key: Idempotency key from request

        Returns:
            True if request already processed, False otherwise
        """
        pass

    @abstractmethod
    def save_idempotency_key(self, key: str, response: str) -> None:
        """
        Save idempotency key and response for deduplication.

        Args:
            key: Idempotency key from request
            response: Response to return on duplicate requests
        """
        pass

    @abstractmethod
    def get_cached_response(self, key: str) -> Optional[str]:
      """Get cached response for idempotency key."""
      pass
