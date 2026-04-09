"""Unit tests for DealAggregate."""

import pytest
from domain.value_objects.money import Money
from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from domain.entities.deal import Deal
from domain.aggregates.deal_aggregate import DealAggregate


class TestDealAggregate:
  """Test suite for DealAggregate."""

  def setup_method(self):
    """Setup test data."""
    self.client_id = ClientId("cli-0001")
    self.title = DealTitle("Test Deal")
    self.amount = Money(1000, "USD")
    self.deal = Deal("D-001", self.client_id, self.title, self.amount)
    self.aggregate = DealAggregate(self.deal)

  def test_create_invoice_success(self):
    """Test creating invoice in aggregate."""
    self.aggregate.create_invoice("INV-001")

    assert self.aggregate.invoice is not None
    assert self.aggregate.invoice.id == "INV-001"
    assert self.aggregate.invoice.deal_id == "D-001"
    assert self.aggregate.deal.status.value == "invoiced"

  def test_create_invoice_twice_raises_error(self):
    """Test that cannot create invoice twice."""
    self.aggregate.create_invoice("INV-001")

    with pytest.raises(ValueError, match="already exists"):
      self.aggregate.create_invoice("INV-002")

  def test_mark_as_paid_success(self):
    """Test marking deal as paid through aggregate."""
    self.aggregate.create_invoice("INV-001")
    self.aggregate.mark_as_paid()

    assert self.aggregate.deal.status.value == "paid"
    assert self.aggregate.invoice.is_paid is True

  def test_mark_as_paid_without_invoice_raises_error(self):
    """Test that cannot mark as paid without invoice."""
    with pytest.raises(ValueError, match="without invoice"):
      self.aggregate.mark_as_paid()

  def test_set_payment_link_success(self):
    """Test setting payment link."""
    self.aggregate.create_invoice("INV-001")
    self.aggregate.set_payment_link("https://pay.example.com/INV-001")

    assert self.aggregate.invoice.payment_link == "https://pay.example.com/INV-001"

  def test_set_payment_link_without_invoice_raises_error(self):
    """Test that cannot set payment link without invoice."""
    with pytest.raises(ValueError, match="no invoice"):
      self.aggregate.set_payment_link("https://pay.example.com/")

  def test_cancel_deal_success(self):
    """Test cancelling deal through aggregate."""
    self.aggregate.cancel("Client not interested")

    assert self.aggregate.deal.status.value == "cancelled"
    events = self.aggregate.get_events()
    assert len(events) == 2  # Created + Cancelled
