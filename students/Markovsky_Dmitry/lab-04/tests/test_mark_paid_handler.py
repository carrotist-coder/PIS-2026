import pytest
from unittest.mock import Mock

from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from src.application.command.mark_deal_as_paid_command import MarkDealAsPaidCommand
from src.application.command.handlers.mark_deal_as_paid_handler import MarkDealAsPaidHandler
from src.domain.models.deal import Deal
from src.domain.models.money import Money


class TestMarkDealAsPaidHandler:
  def test_mark_paid_success(self):
    mock_repo = Mock()
    client_id = ClientId("cli-0001")
    title = DealTitle("Test Deal")
    amount = Money(1000, "USD")
    deal = Deal("D-001", str(client_id), str(title), amount)
    deal.mark_as_invoiced()

    mock_repo.find_by_id.return_value = deal
    handler = MarkDealAsPaidHandler(mock_repo)
    command = MarkDealAsPaidCommand("D-001")

    handler.handle(command)

    assert deal.status.value == "paid"
    mock_repo.save.assert_called_once()

  def test_mark_paid_deal_not_found_raises_error(self):
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None
    handler = MarkDealAsPaidHandler(mock_repo)
    command = MarkDealAsPaidCommand("D-999")

    with pytest.raises(ValueError, match="not found"):
      handler.handle(command)
