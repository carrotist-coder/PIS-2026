import pytest
from unittest.mock import Mock

from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from src.application.command.cancel_deal_command import CancelDealCommand
from src.application.command.handlers.cancel_deal_handler import CancelDealHandler
from src.domain.models.deal import Deal
from src.domain.models.money import Money


class TestCancelDealHandler:
  def test_cancel_deal_success(self):
    mock_repo = Mock()
    client_id = ClientId("cli-0001")
    title = DealTitle("Test Deal")
    amount = Money(1000, "USD")
    deal = Deal("D-001", str(client_id), str(title), amount)

    mock_repo.find_by_id.return_value = deal
    handler = CancelDealHandler(mock_repo)
    command = CancelDealCommand("D-001", "Client changed mind")

    handler.handle(command)

    assert deal.status.value == "cancelled"
    mock_repo.save.assert_called_once()

  def test_cancel_deal_not_found_raises_error(self):
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None
    handler = CancelDealHandler(mock_repo)
    command = CancelDealCommand("D-999", "Not found")

    with pytest.raises(ValueError, match="not found"):
      handler.handle(command)
