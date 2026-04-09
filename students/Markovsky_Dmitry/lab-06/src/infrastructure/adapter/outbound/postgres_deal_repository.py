"""PostgreSQL implementation of DealRepository (outbound adapter)."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.value_objects.client_id import ClientId
from domain.value_objects.deal_title import DealTitle
from src.application.port.outbound.deal_repository import DealRepository
from src.domain.models.deal import Deal
from src.infrastructure.models import DealModel, Base


class PostgresDealRepository(DealRepository):
    """Repository using PostgreSQL and SQLAlchemy."""

    def __init__(self, db_url: str):
        """
        Args:
            db_url: SQLAlchemy database URL, e.g. "postgresql://user:pass@localhost/db"
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def save(self, deal: Deal) -> None:
        """Save or update a deal."""
        session = self._get_session()
        try:
            existing = session.query(DealModel).filter(DealModel.id == deal.id).first()
            if existing:
                # update
                existing.client_id = deal.client_id.value
                existing.title = deal.title.value
                existing.amount = deal.amount.amount
                existing.currency = deal.amount.currency
                existing.status = deal.status.value
                existing.updated_at = deal.updated_at
            else:
                # insert
                model = DealModel.from_domain(deal)
                session.add(model)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_by_id(self, deal_id: str) -> Optional[Deal]:
        session = self._get_session()
        try:
            model = session.query(DealModel).filter(DealModel.id == deal_id).first()
            if not model:
                return None
            deal = model.to_domain()
            deal._client_id = ClientId(model.client_id)
            deal._title = DealTitle(model.title)
            return deal
        finally:
            session.close()

    def update_status(self, deal_id: str, status) -> None:
        session = self._get_session()
        try:
            session.query(DealModel).filter(DealModel.id == deal_id).update(
                {"status": status.value, "updated_at": datetime.now()}
            )
            session.commit()
        finally:
            session.close()

    def _get_idempotency_table(self):
        from sqlalchemy import Table, Column, String, MetaData
        metadata = MetaData()
        idempotency_table = Table(
            "idempotency_keys",
            metadata,
            Column("key", String(128), primary_key=True),
            Column("response", String(50), nullable=False)
        )
        metadata.create_all(self.engine)
        return idempotency_table

    def exists_by_idempotency_key(self, key: str) -> bool:
        session = self._get_session()
        try:
            id_table = self._get_idempotency_table()
            result = session.execute(id_table.select().where(id_table.c.key == key)).first()
            return result is not None
        finally:
            session.close()

    def save_idempotency_key(self, key: str, response: str) -> None:
        session = self._get_session()
        try:
            id_table = self._get_idempotency_table()
            session.execute(id_table.insert().values(key=key, response=response))
            session.commit()
        finally:
            session.close()

    def get_cached_response(self, key: str) -> Optional[str]:
        session = self._get_session()
        try:
            id_table = self._get_idempotency_table()
            result = session.execute(id_table.select().where(id_table.c.key == key)).first()
            return result.response if result else None
        finally:
            session.close()
