"""Synchronous queries: TAP /sync with DALI parameter and error semantics."""

import json
from xml.etree import ElementTree as ET

import httpx
import pytest
import pyvo
from egernia_core.config import GEOMETRY_BACKENDS, _choose

pytestmark = pytest.mark.component

VOT = {"v": "http://www.ivoa.net/xml/VOTable/v1.3"}


def _query_status(text: str) -> str:
    """The effective QUERY_STATUS: per DALI, a trailing INFO written after
    the table (e.g. OVERFLOW while streaming) overrides the header one."""
    root = ET.fromstring(text)
    values = [
        info.get("value")
        for info in root.iter(f"{{{VOT['v']}}}INFO")
        if info.get("name") == "QUERY_STATUS"
    ]
    if not values:
        raise AssertionError("no QUERY_STATUS INFO in response")
    return values[-1]


def test_sync_select_with_pyvo(tap_service):
    svc = pyvo.dal.TAPService(tap_service)
    table = svc.search(
        "SELECT TOP 3 source_name, flux_int FROM ska.continuum_sources ORDER BY flux_int DESC"
    ).to_table()
    assert len(table) == 3
    assert table["source_name"][0] == "SKA-CS J1959+4044"


def test_sync_geometry_cone_search(tap_service):
    svc = pyvo.dal.TAPService(tap_service)
    table = svc.search(
        "SELECT source_name FROM ska.continuum_sources "
        "WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 62.3, -65.5, 1.0))"
    ).to_table()
    assert len(table) == 3
    assert all(name.startswith("SKA-CS J04") for name in table["source_name"])


def test_select_list_geometry_is_an_array_in_degrees(tap_service):
    """A geometry in the select list comes back as its DALI double array in
    degrees, under either geometry backend: [ra, dec] for a POINT, [ra, dec,
    radius] for a CIRCLE, the vertices in order for a POLYGON."""
    svc = pyvo.dal.TAPService(tap_service)
    table = svc.search(
        "SELECT TOP 1 POINT('ICRS', 10, 20), CIRCLE('ICRS', 10, 20, 1) AS c,"
        " POLYGON('ICRS', 10, 20, 11, 20, 11, 21) FROM ska.continuum_sources"
    ).to_table()
    assert table.colnames == ["adql_point", "c", "adql_polygon"]
    assert str(table["adql_point"][0]) == "[10.0, 20.0]"
    assert str(table["c"][0]) == "[10.0, 20.0, 1.0]"
    assert str(table["adql_polygon"][0]) == "[10.0, 20.0, 11.0, 20.0, 11.0, 21.0]"


def test_tap_schema_queryable_via_adql(tap_service):
    svc = pyvo.dal.TAPService(tap_service)
    tables = svc.search("SELECT table_name FROM tap_schema.tables").to_table()
    assert "ska.continuum_sources" in list(tables["table_name"])
    columns = svc.search(
        "SELECT column_name, unit FROM tap_schema.columns "
        "WHERE table_name = 'ska.continuum_sources'"
    ).to_table()
    assert "flux_int" in list(columns["column_name"])


def test_sync_get_and_post_equivalent(tap_service):
    params = {"LANG": "ADQL", "QUERY": "SELECT source_id FROM ska.continuum_sources"}
    get_response = httpx.get(f"{tap_service}/sync", params=params)
    post_response = httpx.post(f"{tap_service}/sync", data=params)
    assert get_response.status_code == post_response.status_code == 200
    assert _query_status(get_response.text) == _query_status(post_response.text) == "OK"


def test_sync_maxrec_overflow(tap_service):
    response = httpx.get(
        f"{tap_service}/sync",
        params={
            "LANG": "ADQL",
            "QUERY": "SELECT source_id FROM ska.continuum_sources",
            "MAXREC": "2",
        },
    )
    root = ET.fromstring(response.text)
    assert _query_status(response.text) == "OVERFLOW"
    assert len(root.findall(f".//{{{VOT['v']}}}TR")) == 2


def test_sync_maxrec_zero_returns_metadata_only(tap_service):
    response = httpx.get(
        f"{tap_service}/sync",
        params={
            "LANG": "ADQL",
            "QUERY": "SELECT source_id, ra FROM ska.continuum_sources",
            "MAXREC": "0",
        },
    )
    root = ET.fromstring(response.text)
    fields = [f.get("name") for f in root.findall(f".//{{{VOT['v']}}}FIELD")]
    assert fields == ["source_id", "ra"]
    assert root.findall(f".//{{{VOT['v']}}}TR") == []


@pytest.mark.parametrize(
    ("fmt", "mime"),
    [
        ("csv", "text/csv"),
        ("tsv", "text/tab-separated-values"),
        ("json", "application/json"),
        ("votable", "application/x-votable+xml"),
    ],
)
def test_sync_response_formats(tap_service, fmt, mime):
    response = httpx.get(
        f"{tap_service}/sync",
        params={
            "LANG": "ADQL",
            "QUERY": "SELECT TOP 1 source_name FROM ska.continuum_sources",
            "RESPONSEFORMAT": fmt,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(mime)
    if fmt == "json":
        assert json.loads(response.text)["status"] == "OK"
    if fmt == "csv":
        assert response.text.splitlines()[0] == "source_name"


@pytest.mark.parametrize(
    "params",
    [
        {"LANG": "ADQL"},  # missing QUERY
        {"LANG": "SQL", "QUERY": "SELECT 1"},  # unsupported language
        {"LANG": "ADQL", "QUERY": "DROP TABLE ska.continuum_sources"},  # not ADQL
        {"LANG": "ADQL", "QUERY": "SELECT * FROM uws.jobs"},  # unpublished table
        {"LANG": "ADQL", "QUERY": "SELECT 1 FROM tap_schema.tables", "RESPONSEFORMAT": "fits"},
        {"LANG": "ADQL", "QUERY": "SELECT 1 FROM tap_schema.tables", "UPLOAD": "t,http://x/y"},
    ],
)
def test_sync_errors_are_dali_votables(tap_service, params):
    response = httpx.get(f"{tap_service}/sync", params=params)
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/x-votable+xml")
    assert _query_status(response.text) == "ERROR"


_CONE = (
    "SELECT TOP 1 source_name FROM ska.continuum_sources WHERE 1=CONTAINS(POINT('ICRS', ra, dec), "
)
# pg_sphere's limits; skycell draws circles up to 180 degrees and answers
# these. The backend is read as the services read it.
_PGSPHERE_ONLY = pytest.mark.skipif(
    _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) != "pgsphere",
    reason="pg_sphere's circle radius limit",
)


@pytest.mark.parametrize(
    ("query", "fmt", "says"),
    [
        ("SELECT TOP 1 1/0 FROM ska.continuum_sources", "votable", "division by zero"),
        # the CSV path is PostgreSQL's COPY, which fails differently
        ("SELECT TOP 1 1/0 FROM ska.continuum_sources", "csv", "division by zero"),
        # a constant radius pg_sphere cannot draw: refused at translation
        pytest.param(
            _CONE + "CIRCLE('ICRS', 62.3, -65.5, 120))",
            "votable",
            "between 0 and 90 degrees",
            marks=_PGSPHERE_ONLY,
        ),
        # one computed per row: refused by pg_sphere as the query runs
        pytest.param(
            _CONE + "CIRCLE('ICRS', 62.3, -65.5, ra * 10))",
            "votable",
            "radius must not be greater",
            marks=_PGSPHERE_ONLY,
        ),
    ],
)
def test_sync_query_the_database_refuses_is_a_dali_error(tap_service, query, fmt, says):
    """These were internal server errors (500): a query PostgreSQL refuses is
    the client's to fix, and DALI wants it as an error document."""
    response = httpx.post(
        f"{tap_service}/sync",
        data={"REQUEST": "doQuery", "LANG": "ADQL", "QUERY": query, "RESPONSEFORMAT": fmt},
    )
    assert response.status_code == 400, response.text
    assert response.headers["content-type"].startswith("application/x-votable+xml")
    assert _query_status(response.text) == "ERROR"
    assert says in response.text


def test_json_query_the_database_refuses_is_a_json_error(tap_service):
    root = tap_service.rsplit("/tap", 1)[0]
    response = httpx.post(
        f"{root}/api/v1/query", json={"query": "SELECT TOP 1 1/0 FROM ska.continuum_sources"}
    )
    assert response.status_code == 400, response.text
    assert response.json()["error"] == "UsageError"
    assert "division by zero" in response.json()["message"]


def test_sync_case_insensitive_parameters(tap_service):
    response = httpx.get(
        f"{tap_service}/sync",
        params={"lang": "ADQL", "query": "SELECT TOP 1 ra FROM ska.continuum_sources"},
    )
    assert response.status_code == 200
    assert _query_status(response.text) == "OK"
