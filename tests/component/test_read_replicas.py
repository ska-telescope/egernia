"""A stack whose query path has its own pool (TAP_QUERY_DATABASE_URL).

There is no standby here: the second pool points at the same server under a
different DSN, which is enough to prove what a standby cannot be relied on to
prove in CI — that the services boot with the setting, that the sync query
really leaves through the query pool while an upload-bearing one does not (the
per-pool metrics say which), that an async job still completes, and that the
URL the abort path pins is one libpq accepts. Replication itself is verified
by hand against benchmarks/tap-compare/scaling-replicas; see the PR.
"""

from dataclasses import replace

import httpx
import psycopg
import pytest
import pyvo
from egernia_core import db

from .conftest import running_services

pytestmark = pytest.mark.component

QUERY = "SELECT source_id, source_name FROM ska.continuum_sources"
UPLOAD_VOTABLE = b"""<?xml version="1.0"?>
<VOTABLE version="1.4" xmlns="http://www.ivoa.net/xml/VOTable/v1.3">
<RESOURCE><TABLE>
<FIELD name="source_name" datatype="char" arraysize="*"/>
<DATA><TABLEDATA><TR><TD>SKA-CS J1959+4044</TD></TR></TABLEDATA></DATA>
</TABLE></RESOURCE></VOTABLE>"""


@pytest.fixture(scope="module")
def query_url(database_url):
    """The same database under a second DSN, so it gets its own pool.

    application_name also makes the pool's connections recognisable in
    pg_stat_activity, which is how an operator checks the routing in the
    field.
    """
    return f"{database_url}?application_name=tap-query"


@pytest.fixture(scope="module")
def split_service(database_url, query_url, tmp_path_factory):
    with running_services(
        database_url,
        tmp_path_factory.mktemp("results-replicas"),
        log_tag="-replicas",
        TAP_QUERY_DATABASE_URL=query_url,
    ) as base_url:
        yield base_url


def _waits(base_url: str) -> dict[str, float]:
    """Per-pool connection acquisitions, from the API's own metrics."""
    text = httpx.get(base_url.rsplit("/tap", 1)[0] + "/metrics", timeout=10).text
    # a histogram child exists only once something has used that pool
    counts = {"primary": 0.0, "query": 0.0}
    for line in text.splitlines():
        if line.startswith("tap_db_pool_wait_seconds_count"):
            role = line.split('pool="', 1)[1].split('"', 1)[0]
            counts[role] = float(line.split()[-1])
    return counts


def test_a_sync_query_leaves_through_the_query_pool(split_service):
    before = _waits(split_service)
    response = httpx.post(
        f"{split_service}/sync",
        data={"QUERY": QUERY, "LANG": "ADQL", "RESPONSEFORMAT": "csv"},
        timeout=30,
    )
    assert response.status_code == 200, response.text
    assert "source_name" in response.text
    after = _waits(split_service)
    assert after["query"] > before["query"]


def test_an_upload_query_stays_on_the_primary(split_service):
    """Its temp tables are a write, which a standby refuses."""
    before = _waits(split_service)
    response = httpx.post(
        f"{split_service}/sync",
        data={
            "QUERY": "SELECT u.source_name FROM TAP_UPLOAD.mine AS u",
            "LANG": "ADQL",
            "UPLOAD": "mine,param:mine",
            "RESPONSEFORMAT": "csv",
        },
        files={"mine": ("mine.vot", UPLOAD_VOTABLE, "application/x-votable+xml")},
        timeout=30,
    )
    assert response.status_code == 200, response.text
    assert "SKA-CS J1959+4044" in response.text
    after = _waits(split_service)
    assert after["query"] == before["query"]
    assert after["primary"] > before["primary"]


def test_an_async_job_completes_with_a_split_query_path(split_service):
    job = pyvo.dal.TAPService(split_service).submit_job(QUERY)
    job.run()
    job.wait(phases=["COMPLETED", "ERROR", "ABORTED"], timeout=60)
    assert job.phase == "COMPLETED"
    assert len(job.fetch_result().to_table()) == 8
    job.delete()


def test_the_pinned_abort_url_is_one_libpq_accepts(query_url, monkeypatch):
    """The executor builds this URL to cancel a statement on the server that
    is running it; a URL libpq cannot parse would only surface on an abort."""
    monkeypatch.setattr(db, "settings", replace(db.settings, query_database_url=query_url))
    with psycopg.connect(query_url) as conn:
        pinned = db.pinned_url(conn)
    with psycopg.connect(pinned) as pinned_conn:
        assert pinned_conn.execute("SELECT 1").fetchone() == (1,)
