"""Unit tests for domain events."""

from datetime import datetime
from domain.value_objects.money import Money
from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from domain.events.deal_events import (
  DomainEvent,
  DealCreated,
  DealInvoiced,
  DealPaid,
  DealCancelled
)


class TestDomainEvents:
  """Test suite for domain events."""

  def test_deal_created_event_default_occurred_at(self):
    """Test that DealCreated sets occurred_at automatically."""
    client_id = ClientId("cli-0001")
    title = DealTitle("Test")
    amount = Money(1000, "USD")

    event = DealCreated("D-001", client_id, title, amount)

    assert event.deal_id == "D-001"
    assert event.client_id == client_id
    assert event.title == title
    assert event.amount == amount
    assert isinstance(event.occurred_at, datetime)
    # Проверка, что время установлено (разница с текущим не более 2 секунд)
    assert (datetime.now() - event.occurred_at).total_seconds() < 2

  def test_deal_created_event_explicit_occurred_at(self):
    """Test that DealCreated respects explicit occurred_at."""
    client_id = ClientId("cli-0001")
    title = DealTitle("Test")
    amount = Money(1000, "USD")
    dt = datetime(2026, 1, 1, 12, 0, 0)

    event = DealCreated("D-001", client_id, title, amount, occurred_at=dt)

    assert event.occurred_at == dt

  def test_deal_invoiced_event(self):
    """Test DealInvoiced event."""
    amount = Money(1000, "USD")
    event = DealInvoiced("D-001", "INV-001", amount)

    assert event.deal_id == "D-001"
    assert event.invoice_id == "INV-001"
    assert event.amount == amount
    assert isinstance(event.occurred_at, datetime)

  def test_deal_paid_event(self):
    """Test DealPaid event."""
    event = DealPaid("D-001")

    assert event.deal_id == "D-001"
    assert isinstance(event.occurred_at, datetime)

  def test_deal_cancelled_event(self):
    """Test DealCancelled event."""
    event = DealCancelled("D-001", "Client changed mind")

    assert event.deal_id == "D-001"
    assert event.reason == "Client changed mind"
    assert isinstance(event.occurred_at, datetime)

  def test_inheritance(self):
    """Test that all events inherit from DomainEvent."""
    client_id = ClientId("cli-0001")
    title = DealTitle("Test")
    amount = Money(1000, "USD")

    assert isinstance(DealCreated("D-001", client_id, title, amount), DomainEvent)
    assert isinstance(DealInvoiced("D-001", "INV-001", amount), DomainEvent)
    assert isinstance(DealPaid("D-001"), DomainEvent)
    assert isinstance(DealCancelled("D-001", "reason"), DomainEvent)
