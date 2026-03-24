"""Inbound port for retrieving deals."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models.deal import Deal


class GetDealUseCase(ABC):
    """
    Inbound port: Get deal by ID use case.
    
    This interface defines how the outside world can retrieve existing deals.
    """
    
    @abstractmethod
    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """
        Retrieve a deal by its unique identifier.
        
        Args:
            deal_id: Unique identifier of the deal (format: D-YYYY-NNNN)
            
        Returns:
            Deal aggregate if found, None otherwise
            
        Example:
            deal = get_deal_use_case.get_deal("D-2026-001")
            if deal:
                print(f"Deal found: {deal.title}")
        """
        pass