import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.adapter.outbound.postgres_deal_repository import PostgresDealRepository
from src.domain.entities.deal import Deal
from src.domain.value_objects.money import Money
from src.domain.value_objects.client_id import ClientId
from src.domain.value_objects.deal_title import DealTitle
from src.infrastructure.models.deal_model import Base


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture
def db_session(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repository(postgres_container):
    url = postgres_container.get_connection_url()
    return PostgresDealRepository(url)


def test_save_and_find_deal(repository):
    client_id = ClientId("cli-test")
    title = DealTitle("Integration Test Deal")
    amount = Money(500, "USD")
    deal = Deal("D-INT-001", client_id, title, amount)

    repository.save(deal)
    found = repository.find_by_id("D-INT-001")

    assert found is not None
    assert found.id == "D-INT-001"
    assert found.title == title
    assert found.amount == amount


def test_update_status(repository):
    client_id = ClientId("cli-test2")
    title = DealTitle("Status Test")
    amount = Money(100, "USD")
    deal = Deal("D-INT-002", client_id, title, amount)
    repository.save(deal)

    deal.mark_as_invoiced("INV-001")
    repository.save(deal)

    updated = repository.find_by_id("D-INT-002")
    assert updated.status.value == "invoiced"
