"""Inbound port for creating deals."""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class CreateDealCommand:
    """
    Command DTO for creating a new deal.
    
    Contains all data required to create a deal in the system.
    """
    client_id: str
    title: str
    amount: float
    currency: str = "USD"
    idempotency_key: Optional[str] = None


class CreateDealUseCase(ABC):
    """
    Inbound port: Deal creation use case.
    
    This interface defines how the outside world can create new deals.
    Implementations (like DealService) contain the actual business logic.
    """
    
    @abstractmethod
    def create_deal(self, command: CreateDealCommand) -> str:
        """
        Create a new deal.
        
        Args:
            command: Command DTO with deal creation data
            
        Returns:
            Unique identifier of the created deal (format: D-YYYY-NNNN)
            
        Raises:
            ValueError: If validation fails (e.g., negative amount, empty title)
            DomainException: If domain rules are violated
            
        Example:
            command = CreateDealCommand(
                client_id="cli-001",
                title="Landing Page Development",
                amount=1500.00,
                currency="USD"
            )
            deal_id = create_deal_use_case.create_deal(command)
        """
        pass