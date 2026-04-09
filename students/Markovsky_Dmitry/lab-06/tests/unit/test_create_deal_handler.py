import pytest
from unittest.mock import Mock
from src.application.command.create_deal_command import CreateDealCommand
from src.application.command.handlers.create_deal_handler import CreateDealHandler


class TestCreateDealHandler:
  def test_create_deal_success(self):
    mock_repo = Mock()
    mock_invoice = Mock()
    mock_notify = Mock()
    mock_invoice.create_invoice.return_value = "INV-001"
    mock_invoice.get_payment_link.return_value = "https://pay.example.com/INV-001"

    handler = CreateDealHandler(mock_repo, mock_invoice, mock_notify)
    command = CreateDealCommand("cli-0001", "Test Deal", 1000.00, "USD")

    deal_id = handler.handle(command)

    assert deal_id.startswith("D-2026-")
    assert mock_repo.save.call_count == 2
    mock_invoice.create_invoice.assert_called_once()

  def test_create_deal_invalid_amount_raises_error(self):
    handler = CreateDealHandler(Mock(), Mock(), Mock())

    with pytest.raises(ValueError, match="positive"):
      command = CreateDealCommand("cli-0001", "Test", -100.00, "USD")
      handler.handle(command)
