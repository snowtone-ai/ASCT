from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import (
    Company,
    Event,
    Inventory,
    InventoryPolicy,
    Location,
    Product,
    SalesHistory,
    Signal,
    Supplier,
)
from src.seed.generate import BASE_DATE, generate_seed


def make_session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_seed_generates_expected_counts():
    session = make_session()
    generate_seed(session)

    assert session.query(Company).count() == 2
    assert session.query(Location).count() == 6
    assert session.query(Product).count() == 10
    assert session.query(Supplier).count() == 7
    assert session.query(InventoryPolicy).count() == 30
    assert session.query(Inventory).count() == 30
    assert session.query(SalesHistory).count() == 900
    assert session.query(Event).count() == 12
    assert session.query(Signal).count() == 12


def test_seed_foreign_keys_are_valid():
    session = make_session()
    generate_seed(session)

    rows = session.query(Inventory).all()
    assert rows
    assert all(row.product is not None and row.location is not None for row in rows)


def test_sales_history_spans_30_days():
    session = make_session()
    generate_seed(session)

    dates = [row.date for row in session.query(SalesHistory).all()]
    assert min(dates).toordinal() == BASE_DATE.toordinal() - 29
    assert max(dates) == BASE_DATE
    assert len(set(dates)) == 30


def test_inventory_quantities_are_non_negative():
    session = make_session()
    generate_seed(session)

    assert all(row.quantity >= 0 for row in session.query(Inventory).all())
