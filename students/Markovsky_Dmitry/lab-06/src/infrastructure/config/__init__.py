"""Configuration: DI container, database settings."""

from .dependency_injection import DependencyContainer
from .database import DATABASE_URL, get_db

__all__ = ["DependencyContainer", "DATABASE_URL", "get_db"]
