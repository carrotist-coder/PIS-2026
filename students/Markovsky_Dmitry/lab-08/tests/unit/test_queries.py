from unittest.mock import Mock

from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from src.application.query.get_deal_by_id_query import GetDealByIdQuery
from src.application.query.handlers.get_deal_by_id_handler import GetDealByIdHandler
from src.domain.models.deal import Deal
from src.domain.models.money import Money


class TestGetDealByIdHandler:
  def test_get_deal_found(self):
    mock_repo = Mock()
    client_id = ClientId("cli-0001")
    title = DealTitle("Test Deal")
    amount = Money(1000, "USD")
    deal = Deal("D-001", str(client_id), str(title), amount)

    mock_repo.find_by_id.return_value = deal
    handler = GetDealByIdHandler(mock_repo)
    query = GetDealByIdQuery("D-001")

    result = handler.handle(query)

    assert result is not None
    assert result.id == "D-001"
    assert result.client_id == "cli-0001"
    assert result.title == "Test Deal"
    assert result.amount == 1000.0

  def test_get_deal_not_found(self):
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None
    handler = GetDealByIdHandler(mock_repo)
    query = GetDealByIdQuery("D-999")

    result = handler.handle(query)

    assert result is None
