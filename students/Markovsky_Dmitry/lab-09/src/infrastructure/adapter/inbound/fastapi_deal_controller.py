"""FastAPI REST controller for Deal commands and queries."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from src.application.create_deal_command import CreateDealCommand
from src.application.mark_deal_as_paid_command import MarkDealAsPaidCommand
from src.application.cancel_deal_command import CancelDealCommand
from src.application.query.get_deal_by_id_query import GetDealByIdQuery
from src.application.service.deal_application_service import DealApplicationService
from src.infrastructure.config.dependency_injection import DependencyContainer

# Pydantic request/response models
class CreateDealRequest(BaseModel):
    client_id: str
    title: str
    amount: float
    currency: str = "USD"
    idempotency_key: Optional[str] = None

class MarkPaidRequest(BaseModel):
    deal_id: str

class CancelDealRequest(BaseModel):
    deal_id: str
    reason: str

class DealResponse(BaseModel):
    id: str
    client_id: str
    title: str
    amount: float
    currency: str
    status: str
    created_at: str

router = APIRouter(prefix="/api/deals", tags=["deals"])

def get_deal_service() -> DealApplicationService:
    container = DependencyContainer()
    return container.get_deal_service()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_deal(request: CreateDealRequest, service: DealApplicationService = Depends(get_deal_service)):
    command = CreateDealCommand(
        client_id=request.client_id,
        title=request.title,
        amount=request.amount,
        currency=request.currency,
        idempotency_key=request.idempotency_key
    )
    deal_id = service.create_deal(command)
    return {"deal_id": deal_id}

@router.post("/{deal_id}/mark-paid")
def mark_deal_as_paid(deal_id: str, service: DealApplicationService = Depends(get_deal_service)):
    command = MarkDealAsPaidCommand(deal_id=deal_id)
    service.mark_deal_as_paid(command)
    return {"message": f"Deal {deal_id} marked as paid"}

@router.post("/{deal_id}/cancel")
def cancel_deal(deal_id: str, request: CancelDealRequest, service: DealApplicationService = Depends(get_deal_service)):
    command = CancelDealCommand(deal_id=deal_id, reason=request.reason)
    service.cancel_deal(command)
    return {"message": f"Deal {deal_id} cancelled"}

@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: str, service: DealApplicationService = Depends(get_deal_service)):
    query = GetDealByIdQuery(deal_id=deal_id)
    dto = service.get_deal_by_id(query)
    if not dto:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponse(
        id=dto.id,
        client_id=dto.client_id,
        title=dto.title,
        amount=dto.amount,
        currency=dto.currency,
        status=dto.status,
        created_at=dto.created_at.isoformat()
    )
