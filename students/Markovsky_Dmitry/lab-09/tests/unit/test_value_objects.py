"""Unit tests for value objects."""

import pytest
from domain.value_objects.money import Money
from domain.value_objects.deal_status import DealStatus
from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle


class TestMoney:
    """Test suite for Money value object."""

    def test_create_money_success(self):
        """Test successful money creation."""
        money = Money(100, "USD")
        assert money.amount == 100
        assert money.currency == "USD"

    def test_create_money_with_negative_amount_raises_error(self):
        """Test that negative amount raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            Money(-100, "USD")

    def test_create_money_with_invalid_currency_raises_error(self):
        """Test that invalid currency raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported"):
            Money(100, "GBP")

    def test_money_equality(self):
        """Test money equality."""
        assert Money(100, "USD") == Money(100, "USD")
        assert Money(100, "USD") != Money(200, "USD")
        assert Money(100, "USD") != Money(100, "EUR")

    def test_money_add_same_currency(self):
        """Test adding money with same currency."""
        m1 = Money(100, "USD")
        m2 = Money(50, "USD")
        result = m1.add(m2)

        assert result.amount == 150
        assert result.currency == "USD"

    def test_money_add_different_currency_raises_error(self):
        """Test that adding different currencies raises error."""
        m1 = Money(100, "USD")
        m2 = Money(50, "EUR")

        with pytest.raises(ValueError, match="different currencies"):
            m1.add(m2)


class TestDealStatus:
    """Test suite for DealStatus enum."""

    def test_status_values(self):
        """Test status string values."""
        assert DealStatus.NEGOTIATION.value == "negotiation"
        assert DealStatus.INVOICED.value == "invoiced"
        assert DealStatus.PAID.value == "paid"

    def test_status_transitions(self):
        """Test allowed status transitions."""
        assert DealStatus.NEGOTIATION.can_transition_to(DealStatus.INVOICED) is True
        assert DealStatus.NEGOTIATION.can_transition_to(DealStatus.CANCELLED) is True
        assert DealStatus.PAID.can_transition_to(DealStatus.INVOICED) is False
        assert DealStatus.CANCELLED.can_transition_to(DealStatus.NEGOTIATION) is False


class TestClientId:
    """Test suite for ClientId value object."""

    def test_create_valid_client_id(self):
        """Test creating valid client ID."""
        client_id = ClientId("cli-1234")
        assert client_id.value == "cli-1234"

    def test_create_empty_client_id_raises_error(self):
        """Test that empty client ID raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ClientId("")

    def test_client_id_equality(self):
        """Test client ID equality."""
        assert ClientId("cli-0001") == ClientId("cli-0001")
        assert ClientId("cli-0001") != ClientId("cli-0002")


class TestDealTitle:
    """Test suite for DealTitle value object."""

    def test_create_valid_title(self):
        """Test creating valid title."""
        title = DealTitle("Valid Title")
        assert title.value == "Valid Title"

    def test_create_empty_title_raises_error(self):
        """Test that empty title raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DealTitle("")

    def test_create_too_short_title_raises_error(self):
        """Test that too short title raises error."""
        with pytest.raises(ValueError, match="too short"):
            DealTitle("AB")

    def test_create_too_long_title_raises_error(self):
        """Test that too long title raises error."""
        long_title = "A" * 101
        with pytest.raises(ValueError, match="too long"):
            DealTitle(long_title)

    def test_title_strips_whitespace(self):
        """Test that title strips whitespace."""
        title = DealTitle("  My Deal  ")
        assert title.value == "My Deal"

    def test_title_equality(self):
        """Test title equality."""
        assert DealTitle("Deal") == DealTitle("Deal")
        assert DealTitle("Deal 1") != DealTitle("Deal 2")
