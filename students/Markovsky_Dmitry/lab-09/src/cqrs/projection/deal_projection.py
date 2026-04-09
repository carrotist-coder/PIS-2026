from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.events.deal_events import (
  DealCreated, DealInvoiced, DealPaid, DealCancelled
)
from cqrs.read_model.deal_view import DealViewORM


class DealProjection:
  """
  Projection Handler: События → DealView

  Синхронизирует Write Model и Read Model через доменные события.
  """

  STATUS_DISPLAY = {
    "negotiation": "На согласовании",
    "approval": "Требуется подтверждение",
    "invoiced": "Инвойс выставлен",
    "paid": "Оплачено",
    "cancelled": "Отменено"
  }

  def __init__(self, session: Session):
    self.session = session

  def on_deal_created(self, event: DealCreated):
    """Обработка DealCreated: INSERT в deal_views"""
    view = DealViewORM(
      deal_id=event.deal_id,
      client_id=str(event.client_id),
      client_name=None,
      title=str(event.title),
      amount=float(event.amount.amount),
      currency=event.amount.currency,
      status="negotiation",
      status_display=self.STATUS_DISPLAY["negotiation"],
      created_at=event.occurred_at,
      updated_at=event.occurred_at,
      invoice_id=None,
      payment_link=None,
      is_paid=False,
      days_since_created=0
    )
    self.session.add(view)
    self.session.commit()

  def on_deal_invoiced(self, event: DealInvoiced):
    """Обработка DealInvoiced: UPDATE invoice_id, payment_link"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.invoice_id = event.invoice_id
      # В реальности payment_link приходит из InvoiceService
      view.payment_link = f"https://pay.example.com/{event.invoice_id}"
      view.status = "invoiced"
      view.status_display = self.STATUS_DISPLAY["invoiced"]
      view.updated_at = datetime.now()
      self.session.commit()

  def on_deal_paid(self, event: DealPaid):
    """Обработка DealPaid: UPDATE status, is_paid"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.status = "paid"
      view.status_display = self.STATUS_DISPLAY["paid"]
      view.is_paid = True
      view.updated_at = datetime.now()
      self.session.commit()

  def on_deal_cancelled(self, event: DealCancelled):
    """Обработка DealCancelled: UPDATE status"""
    view = self.session.query(DealViewORM).filter_by(
      deal_id=event.deal_id
    ).first()

    if view:
      view.status = "cancelled"
      view.status_display = self.STATUS_DISPLAY["cancelled"]
      view.updated_at = datetime.now()
      self.session.commit()


# Event Bus Integration
class EventBus:
  def __init__(self, projection: DealProjection):
    self.projection = projection
    self.handlers = {
      "DealCreated": self.projection.on_deal_created,
      "DealInvoiced": self.projection.on_deal_invoiced,
      "DealPaid": self.projection.on_deal_paid,
      "DealCancelled": self.projection.on_deal_cancelled
    }

  def publish(self, event):
    event_type = event.__class__.__name__
    handler = self.handlers.get(event_type)
    if handler:
      handler(event)
