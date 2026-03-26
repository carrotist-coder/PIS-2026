"""Deal title value object."""


class DealTitle:
    """
    Value Object representing deal title.
    
    Validation rules:
    - Not empty
    - Length between 3 and 100 characters
    """
    
    MIN_LENGTH = 3
    MAX_LENGTH = 100
    
    def __init__(self, value: str):
        """
        Initialize DealTitle.
        
        Args:
            value: Title string
            
        Raises:
            ValueError: If validation fails
        """
        if not value or not value.strip():
            raise ValueError("Deal title cannot be empty")
        
        stripped = value.strip()
        if len(stripped) < self.MIN_LENGTH:
            raise ValueError(f"Deal title too short: minimum {self.MIN_LENGTH} characters")
        
        if len(stripped) > self.MAX_LENGTH:
            raise ValueError(f"Deal title too long: maximum {self.MAX_LENGTH} characters")
        
        self.value = stripped
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DealTitle):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"DealTitle('{self.value}')"