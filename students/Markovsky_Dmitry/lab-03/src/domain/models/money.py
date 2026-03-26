"""Money value object."""

from decimal import Decimal
from typing import Union


class Money:
    """
    Value Object representing money amount with currency.
    
    Immutable value object that encapsulates amount validation and
    currency formatting logic.
    """
    
    SUPPORTED_CURRENCIES = {"USD", "BYN", "EUR"}
    
    def __init__(self, amount: Union[int, float, Decimal, str], currency: str = "USD"):
        """
        Initialize Money object.
        
        Args:
            amount: Monetary value (must be >= 0)
            currency: Currency code (USD, BYN, EUR)
            
        Raises:
            ValueError: If amount is negative or currency is not supported
        """
        if isinstance(amount, str):
            self.amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            self.amount = Decimal(str(amount))
        else:
            self.amount = amount
        
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: {currency}. "
                f"Supported: {self.SUPPORTED_CURRENCIES}"
            )
        
        self.currency = currency
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
    
    def add(self, other: "Money") -> "Money":
        """
        Add two Money objects (same currency).
        
        Args:
            other: Money object to add
            
        Returns:
            New Money object with sum
            
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} != {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)