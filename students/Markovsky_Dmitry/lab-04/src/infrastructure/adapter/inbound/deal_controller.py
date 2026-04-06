"""REST-like controller for Deal Service."""

from typing import Dict, Any, Optional

from src.application.port.inbound.create_deal_use_case import (
    CreateDealUseCase,
    CreateDealCommand
)
from src.application.port.inbound.get_deal_use_case import GetDealUseCase


class DealController:
    """
    Inbound adapter for HTTP requests.

    This is a simplified REST-like controller that demonstrates how
    external clients interact with the application layer through ports.

    In a real application, this would be a proper HTTP framework
    (Flask, FastAPI, Django REST, etc.).
    """

    def __init__(self, create_deal_uc: CreateDealUseCase, get_deal_uc: GetDealUseCase):
        """
        Initialize controller with use cases.

        Args:
            create_deal_uc: Create deal use case implementation
            get_deal_uc: Get deal use case implementation
        """
        self.create_deal_uc = create_deal_uc
        self.get_deal_uc = get_deal_uc

    def create_deal(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle POST /api/deals request.

        Expected request body:
        {
            "clientId": "cli-001",
            "title": "Landing Page Development",
            "amount": 1500.00,
            "currency": "USD",
            "idempotencyKey": "optional-unique-key"
        }

        Returns:
            Response with deal_id on success, error on failure
        """
        try:
            # Extract and validate required fields
            client_id = request_body.get("clientId")
            if not client_id:
                return {
                    "status": 400,
                    "error": "clientId is required"
                }

            title = request_body.get("title")
            if not title:
                return {
                    "status": 400,
                    "error": "title is required"
                }

            amount = request_body.get("amount")
            if amount is None:
                return {
                    "status": 400,
                    "error": "amount is required"
                }

            currency = request_body.get("currency", "USD")
            idempotency_key = request_body.get("idempotencyKey")

            command = CreateDealCommand(
                client_id=client_id,
                title=title,
                amount=float(amount),
                currency=currency,
                idempotency_key=idempotency_key
            )

            deal_id = self.create_deal_uc.create_deal(command)

            return {
                "status": 201,
                "dealId": deal_id,
                "message": "Deal created successfully"
            }

        except ValueError as e:
            return {
                "status": 400,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": 500,
                "error": f"Internal server error: {str(e)}"
            }

    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """
        Handle GET /api/deals/{id} request.

        Args:
            deal_id: Deal identifier

        Returns:
            Deal data if found, 404 otherwise
        """
        try:
            # Execute use case
            deal = self.get_deal_uc.get_deal(deal_id)

            if not deal:
                return {
                    "status": 404,
                    "error": f"Deal {deal_id} not found"
                }

            return {
                "status": 200,
                "deal": {
                    "id": deal.id,
                    "clientId": deal.client_id,
                    "title": deal.title,
                    "amount": float(deal.amount.amount),
                    "currency": deal.amount.currency,
                    "status": deal.status.value,
                    "createdAt": deal.created_at.isoformat(),
                    "updatedAt": deal.updated_at.isoformat()
                }
            }

        except Exception as e:
            return {
                "status": 500,
                "error": f"Internal server error: {str(e)}"
            }

    def handle_request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict:
        """
        Simple request router for demonstration.

        Args:
            method: HTTP method (GET, POST)
            path: Request path
            body: Request body (for POST)

        Returns:
            Response dictionary
        """
        # POST /api/deals
        if method == "POST" and path == "/api/deals":
            return self.create_deal(body or {})

        # GET /api/deals/{id}
        if method == "GET" and path.startswith("/api/deals/"):
            deal_id = path.split("/")[-1]
            return self.get_deal(deal_id)

        # 404 Not Found
        return {
            "status": 404,
            "error": f"Endpoint not found: {method} {path}"
        }
