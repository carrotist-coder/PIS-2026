"""Inbound adapters: REST controllers, CLI, etc."""

from .deal_controller import DealController
from .fastapi_deal_controller import router

__all__ = ["DealController", "router"]
