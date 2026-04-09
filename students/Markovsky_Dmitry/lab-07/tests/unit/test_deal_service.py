"""Unit tests for DealService."""

import pytest
from unittest.mock import Mock, patch
from src.application.service.deal_service import DealService
from src.application.port.inbound.create_deal_use_case import CreateDealCommand


class TestDealService:
    """Test suite for DealService."""

    def test_create_deal_calls_repository_save(self):
        """Test that repository.save is called when creating a deal."""
        # Arrange
        mock_repo = Mock()
        mock_invoice = Mock()
        mock_notify = Mock()
        mock_invoice.create_invoice.return_value = "INV-2026-0001"

        service = DealService(mock_repo, mock_invoice, mock_notify)
        command = CreateDealCommand(
            client_id="cli-001",
            title="Test Deal",
            amount=1000.00,
            currency="USD"
        )

        # Act
        with patch('src.application.service.deal_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = "2026-03-24"
            deal_id = service.create_deal(command)

        # Assert
        mock_repo.save.assert_called_once()

    def test_create_deal_validates_positive_amount(self):
        """Test that negative amount raises ValueError."""
        # Arrange
        service = DealService(Mock(), Mock(), Mock())
        command = CreateDealCommand(
            client_id="cli-001",
            title="Test",
            amount=-100.00,
            currency="USD"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="positive"):
            service.create_deal(command)
            pass

    def test_get_deal_returns_none_if_not_found(self):
        """Test that get_deal returns None for non-existent deal."""
        # Arrange
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        service = DealService(mock_repo, Mock(), Mock())

        deal = service.get_deal("non-existent")

        assert deal is None
        pass

    def test_create_deal_generates_unique_id(self):
        """Test that each deal gets a unique ID."""
        # Arrange
        mock_repo = Mock()
        mock_invoice = Mock()
        mock_notify = Mock()
        service = DealService(mock_repo, mock_invoice, mock_notify)
        command = CreateDealCommand("cli-001", "Deal 1", 1000.00)

        # Act
        id1 = service.create_deal(command)
        id2 = service.create_deal(command)

        # Assert
        assert id1 != id2
