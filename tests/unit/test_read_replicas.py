"""Which pool each call site takes when TAP_QUERY_DATABASE_URL names replicas.

The routing is the whole feature, and it is one keyword at four call sites, so
these tests assert the decisions rather than the plumbing: a query goes to the
replicas, a query carrying a TAP_UPLOAD does not (its temp tables are a write
a standby refuses), and job bookkeeping never does.
"""

from dataclasses import replace
from types import SimpleNamespace

import pytest
from egernia_api.queries import query as query_mod
from egernia_core import db
from egernia_core.config import settings
from egernia_executor import worker

from .conftest import FakePool

QUERY = "SELECT source_id, ra FROM ska.continuum_sources"
REPLICAS = "postgresql://tap:tap@sb1,sb2,sb3/tap?target_session_attrs=read-only"


class CountingPool(FakePool):
    """A fake pool that says how many connections it handed out."""

    def __init__(self, fake_db):
        super().__init__(fake_db)
        self.checkouts = 0

    def connection(self, timeout=None):
        self.checkouts += 1
        return super().connection(timeout)


@pytest.fixture
def replica_pool(fake_db, monkeypatch):
    """A distinct pool for the query path, as a replica URL produces."""
    pool = CountingPool(fake_db)
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=REPLICAS))
    monkeypatch.setattr(db, "_query_pool", pool)
    return pool


def test_without_a_query_url_there_is_only_one_pool(fake_db, monkeypatch):
    """An existing deployment must keep one pool of the size it had, not gain a
    second one to the same server and double its connection budget."""
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=""))
    assert db.query_pool() is db.pool()
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=settings.database_url))
    assert db.query_pool() is db.pool()


def test_a_query_url_separates_the_two_pools(fake_db, replica_pool):
    with db.connection(replica_ok=True) as conn:
        conn.execute("SELECT 1")
    assert replica_pool.checkouts == 1
    with db.connection() as conn:
        conn.execute("SELECT 1")
    assert replica_pool.checkouts == 1  # the primary's work stayed on the primary


def test_a_sync_query_executes_on_the_replicas(fake_db, replica_pool):
    prepared = query_mod.prepare_query({"QUERY": QUERY, "RESPONSEFORMAT": "csv"})
    body, _mime = query_mod.run_sync(prepared)
    assert b"source_id,ra" in b"".join(body)
    assert replica_pool.checkouts == 1


def test_a_sync_query_with_an_upload_stays_on_the_primary(fake_db, replica_pool):
    prepared = query_mod.prepare_query({"QUERY": QUERY, "RESPONSEFORMAT": "csv"})
    uploads = [SimpleNamespace(name="t1", ident="pg_temp.t1", columns=[], rows=[])]
    body, _mime = query_mod.run_sync(prepared, uploads)
    assert b"source_id,ra" in b"".join(body)
    assert replica_pool.checkouts == 0


def test_the_executor_queries_the_replicas_and_books_the_job_on_the_primary(
    fake_db, results_dir, replica_pool
):
    job = fake_db.add_job(
        phase="QUEUED", parameters={"QUERY": QUERY, "RESPONSEFORMAT": "csv"}, query_sql=QUERY
    )
    claimed = worker.claim_job()  # the claim is a write: primary
    assert claimed is not None
    worker.execute_job(claimed)
    # one checkout, the query's; the claim, the PID publication, the lease
    # renewals and the COMPLETED transition all went to the primary
    assert replica_pool.checkouts == 1
    assert fake_db.jobs[job["job_id"]]["phase"] == "COMPLETED"


def _conn(host, hostaddr, port="5432"):
    return SimpleNamespace(info=SimpleNamespace(host=host, hostaddr=hostaddr, port=port))


def test_the_abort_path_is_pinned_to_the_server_that_ran_the_query(monkeypatch):
    """A cancel only works on the instance running the statement, so the URL
    the executor signals over names exactly the server it connected to."""
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=REPLICAS))
    pinned = db.pinned_url(_conn("sb2", "10.0.0.12"))
    assert "host=sb2" in pinned
    assert "sb1" not in pinned and "sb3" not in pinned
    assert "target_session_attrs=read-only" in pinned


def test_the_pin_is_an_address_and_keeps_the_name_for_tls(monkeypatch):
    """A name is not a pin. A read-only Service — or any name that resolves to
    several standbys — resolves again on the next connection, and the cancel
    would land on whichever standby answered that time. The name still has to
    travel, or sslmode=verify-full would have nothing to verify against."""
    service = "postgresql://tap:tap@tap-db-ro:5432/tap?sslmode=verify-full"
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=service))
    pinned = db.pinned_url(_conn("tap-db-ro", "10.0.0.7"))
    assert "hostaddr=10.0.0.7" in pinned
    assert "host=tap-db-ro" in pinned
    assert "sslmode=verify-full" in pinned


def test_a_unix_socket_connection_pins_to_its_socket_directory(monkeypatch):
    """It reports no address, and an empty hostaddr must not reach libpq."""
    monkeypatch.setattr(db, "settings", replace(settings, query_database_url=""))
    pinned = db.pinned_url(_conn("/var/run/postgresql", ""))
    assert "host=/var/run/postgresql" in pinned
    assert "hostaddr" not in pinned
