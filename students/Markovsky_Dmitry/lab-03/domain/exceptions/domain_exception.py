"""Base domain exception."""


class DomainException(Exception):
    """
    Base exception for domain layer errors.
    
    All domain-specific exceptions should inherit from this class.
    """
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"