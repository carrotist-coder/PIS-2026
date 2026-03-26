"""Client ID value object."""

import re


class ClientId:
    """
    Value Object representing client identifier.
    
    Format: cli-XXXX where XXXX are alphanumeric characters.
    """
    
    PATTERN = re.compile(r'^cli-[A-Za-z0-9]{4,}$')
    
    def __init__(self, value: str):
        """
        Initialize ClientId.
        
        Args:
            value: Client ID string
            
        Raises:
            ValueError: If format is invalid
        """
        if not value or not value.strip():
            raise ValueError("Client ID cannot be empty")
        
        if not self.PATTERN.match(value):
            raise ValueError(
                f"Invalid client ID format: {value}. "
                f"Expected format: cli-XXXX (at least 4 alphanumeric chars)"
            )
        
        self.value = value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClientId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"ClientId('{self.value}')"