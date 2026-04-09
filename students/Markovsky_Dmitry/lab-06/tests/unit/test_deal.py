"""Unit tests for Deal entity."""

import pytest
from domain.value_objects.money import Money
from domain.value_objects.deal_status import DealStatus
from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from domain.entities.deal import Deal


class TestDeal:
  """Test suite for Deal entity."""

  def setup_method(self):
    """Setup test data."""
    self.client_id = ClientId("cli-0001")
    self.title = DealTitle("Test Deal")
    self.amount = Money(1000, "USD")

  def test_create_deal_success(self):
    """Test successful deal creation."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)

    assert deal.id == "D-001"
    assert deal.client_id == self.client_id
    assert deal.title == self.title
    assert deal.amount == self.amount
    assert deal.status == DealStatus.NEGOTIATION

  def test_mark_as_invoiced_success(self):
    """Test marking deal as invoiced."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    deal.mark_as_invoiced("INV-001")

    assert deal.status == DealStatus.INVOICED
    events = deal.get_events()
    assert len(events) == 2  # Created + Invoiced
    assert events[1].invoice_id == "INV-001"

  def test_mark_as_invoiced_when_paid_raises_error(self):
    """Test that cannot invoice already paid deal."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    deal.mark_as_invoiced("INV-001")
    deal.mark_as_paid()

    with pytest.raises(ValueError, match="Cannot invoice"):
      deal.mark_as_invoiced("INV-002")

  def test_mark_as_paid_success(self):
    """Test marking deal as paid."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    deal.mark_as_invoiced("INV-001")
    deal.mark_as_paid()

    assert deal.status == DealStatus.PAID
    events = deal.get_events()
    assert len(events) == 3  # Created + Invoiced + Paid
    assert events[2].deal_id == "D-001"

  def test_mark_as_paid_without_invoice_raises_error(self):
    """Test that cannot mark as paid without invoice."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)

    with pytest.raises(ValueError, match="Cannot mark as paid"):
      deal.mark_as_paid()

  def test_cancel_success(self):
    """Test cancelling a deal."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    deal.cancel("Client changed mind")

    assert deal.status == DealStatus.CANCELLED
    events = deal.get_events()
    assert len(events) == 2  # Created + Cancelled
    assert events[1].reason == "Client changed mind"

  def test_cancel_paid_deal_raises_error(self):
    """Test that cannot cancel paid deal."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    deal.mark_as_invoiced("INV-001")
    deal.mark_as_paid()

    with pytest.raises(ValueError, match="Cannot cancel"):
      deal.cancel("Try to cancel")

  def test_events_are_registered(self):
    """Test that events are properly registered."""
    deal = Deal("D-001", self.client_id, self.title, self.amount)
    events = deal.get_events()
    assert len(events) == 1
    assert events[0].deal_id == "D-001"

    deal.mark_as_invoiced("INV-001")
    events = deal.get_events()
    assert len(events) == 2

    deal.clear_events()
    events = deal.get_events()
    assert len(events) == 0

  def test_equality_by_id(self):
    """Test that deals are equal by ID."""
    deal1 = Deal("D-001", self.client_id, self.title, self.amount)
    deal2 = Deal("D-001", self.client_id, self.title, self.amount)
    deal3 = Deal("D-002", self.client_id, self.title, self.amount)

    assert deal1 == deal2
    assert deal1 != deal3
