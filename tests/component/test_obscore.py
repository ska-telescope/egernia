"""ObsCore 1.1 end to end (package 12): the odp bootstrap materialises
ivoa.obscore from the ODP tables, TAP publishes and serves it, the triggers
keep it current, and the declarations a validator reads (capabilities,
/tables) say so."""

import copy

import httpx
import pytest
from ska_src_mm_notification.models.schemas.srcnet_ingestion import (
    SRC_INGESTION_EXAMPLE,
)

pytestmark = pytest.mark.component


def _sync_csv(tap_service: str, adql: str) -> list[str]:
    response = httpx.post(
        f"{tap_service}/sync",
        data={"LANG": "ADQL", "QUERY": adql, "RESPONSEFORMAT": "csv"},
        timeout=30,
    )
    assert response.status_code == 200, response.text
    return response.text.strip().splitlines()


def test_obscore_view_serves_ingested_products(tap_service, api_url):
    payload = copy.deepcopy(SRC_INGESTION_EXAMPLE)
    payload["project_id"] = "obscore-demo"
    product = payload["observations"][0]["scheduling_blocks"][0]["execution_blocks"][0][
        "data_products"
    ][0]
    product["s_region"] = "CIRCLE ICRS 150.0 -30.0 0.5"
    created = httpx.post(f"{api_url}/notifications", json=payload, timeout=30)
    assert created.status_code == 201, created.text

    obs_id = payload["observations"][0]["obs_id"]

    # the REC's name is case-insensitive: ivoa.ObsCore works unquoted
    lines = _sync_csv(
        tap_service,
        "SELECT obs_publisher_did, obs_collection, dataproduct_type, calib_level"
        f" FROM ivoa.ObsCore WHERE obs_id = '{obs_id}'",
    )
    header, rows = lines[0].split(","), lines[1:]
    assert header == ["obs_publisher_did", "obs_collection", "dataproduct_type", "calib_level"]
    assert any(row.startswith(f"ivo://skao.int/~?obscore-demo/{obs_id}/") for row in rows)

    # the geometry companion answers footprint queries on the view itself
    overlap = _sync_csv(
        tap_service,
        "SELECT obs_publisher_did FROM ivoa.obscore"
        " WHERE 1=INTERSECTS(s_region_geom, CIRCLE('ICRS', 150.2, -30.0, 0.1))",
    )
    assert any("obscore-demo" in row for row in overlap[1:])


def test_obscore_declarations_for_validators(tap_service, api_url):
    capabilities = httpx.get(f"{tap_service}/capabilities", timeout=10).text
    assert (
        '<dataModel ivo-id="ivo://ivoa.net/std/ObsCore#core-1.1">ObsCore-1.1</dataModel>'
        in capabilities
    )

    tables = httpx.get(f"{tap_service}/tables", timeout=10).text
    assert "<name>ivoa.obscore</name>" in tables
    assert "<utype>ivo://ivoa.net/std/ObsCore#core-1.1</utype>" in tables
    assert 'extendedType="adql:REGION"' in tables
    assert "<utype>obscore:Curation.publisherDID</utype>" in tables

    listing = httpx.get(f"{api_url}/tables", timeout=10).json()
    obscore = next(t for t in listing["tables"] if t["name"] == "ivoa.obscore")
    assert obscore["utype"] == "ivo://ivoa.net/std/ObsCore#core-1.1"
    names = [c["name"] for c in obscore["columns"]]
    assert names[:5] == [
        "dataproduct_type",
        "calib_level",
        "obs_collection",
        "obs_id",
        "obs_publisher_did",
    ]
    assert "s_region_geom" in names

    examples = httpx.get(f"{tap_service}/examples", timeout=10).text
    assert "ivoa.obscore" in examples


def test_obscore_publisher_did_percent_encodes_the_key_chain(tap_service, api_url):
    """The key columns are free text and a PublisherDID is permanent: a
    product_id carrying a space, a '/' and a '#' must not forge a sixth path
    segment or truncate the identifier at the fragment."""
    payload = copy.deepcopy(SRC_INGESTION_EXAMPLE)
    payload["project_id"] = "obscore-escape"
    product = payload["observations"][0]["scheduling_blocks"][0]["execution_blocks"][0][
        "data_products"
    ][0]
    product["product_id"] = "cube 3/a#1"
    created = httpx.post(f"{api_url}/notifications", json=payload, timeout=30)
    assert created.status_code == 201, created.text

    lines = _sync_csv(
        tap_service,
        "SELECT obs_publisher_did FROM ivoa.obscore"
        " WHERE obs_publisher_did LIKE '%obscore-escape%'",
    )
    dids = lines[1:]
    assert dids, lines
    for did in dids:
        assert did.startswith("ivo://skao.int/~?obscore-escape/")
        assert did.endswith("/cube%203%2Fa%231")
        # the raw characters never reach the identifier
        assert " " not in did and "#" not in did


def test_a_geometry_predicate_over_the_text_column_is_a_usage_error(tap_service):
    """`s_region` is the column every ObsCore tutorial names, and it holds
    STC-S text: the queryable companion is the non-standard `s_region_geom`.

    Translation is pure and consults no schema, so the standard spelling used
    to translate happily and die inside PostgreSQL as
    `operator does not exist: text && scircle` — a 500-shaped answer to what
    is a usage error, naming neither the column at fault nor the one to use.
    """
    response = httpx.post(
        f"{tap_service}/sync",
        data={
            "LANG": "ADQL",
            "QUERY": (
                "SELECT obs_publisher_did FROM ivoa.obscore "
                "WHERE 1 = INTERSECTS(s_region, CIRCLE('ICRS', 150.0, -30.0, 0.5))"
            ),
            "RESPONSEFORMAT": "csv",
        },
        timeout=30,
    )
    assert response.status_code == 400, response.text
    body = response.text
    assert "s_region" in body
    assert "s_region_geom" in body, "the usable column has to be named"
    assert "NULL" in body, "the companion is nullable; a caller must know that"
    # the failure a client used to get, and must not get any more
    assert "operator does not exist" not in body


def test_the_geometry_companion_is_still_accepted(tap_service):
    """The check must refuse only what PostgreSQL would refuse."""
    response = httpx.post(
        f"{tap_service}/sync",
        data={
            "LANG": "ADQL",
            "QUERY": (
                "SELECT obs_publisher_did FROM ivoa.obscore "
                "WHERE 1 = INTERSECTS(s_region_geom, CIRCLE('ICRS', 150.0, -30.0, 0.5))"
            ),
            "RESPONSEFORMAT": "csv",
        },
        timeout=30,
    )
    assert response.status_code == 200, response.text


def _plan(database_url: str, sql: str, *settings: str) -> str:
    import psycopg

    with psycopg.connect(database_url) as conn:
        for setting in settings:
            conn.execute(setting)
        rows = conn.execute(f"EXPLAIN (COSTS OFF) {sql}").fetchall()
    return "\n".join(row[0] for row in rows)


_ONLY_BITMAP_SCANS = (
    "SET enable_seqscan = off",
    "SET enable_indexscan = off",
    "SET enable_indexonlyscan = off",
)


def test_a_did_lookup_can_use_the_trigram_index(tap_service, api_url, database_url):
    """A leading-wildcard LIKE on obs_publisher_did used to evaluate the
    five-way DID expression for every product. The DID is a stored column of
    the materialised relation now, with a pg_trgm index the bootstrap owns.
    Sequential scans, and the filtered scans of another index that stand in
    for one, are switched off because a planner facing a handful of rows
    would rightly prefer either; what is left is the bitmap scan a GIN index
    provides."""
    payload = copy.deepcopy(SRC_INGESTION_EXAMPLE)
    payload["project_id"] = "obscore-lookup"
    created = httpx.post(f"{api_url}/notifications", json=payload, timeout=30)
    assert created.status_code == 201, created.text

    for pattern in ("%obscore-lookup/%", "ivo://skao.int/~?obscore-lookup/%"):
        plan = _plan(
            database_url,
            f"SELECT obs_id FROM ivoa.obscore WHERE obs_publisher_did LIKE '{pattern}'",
            *_ONLY_BITMAP_SCANS,
        )
        assert "obscore_did_trgm" in plan, plan

    # and the rows an index scan yields are the rows: the whole key chain,
    # reachable by equality as well
    observation = payload["observations"][0]
    block = observation["scheduling_blocks"][0]["execution_blocks"][0]
    did = "ivo://skao.int/~?obscore-lookup/{}/{}/{}/{}".format(
        observation["obs_id"],
        observation["scheduling_blocks"][0]["sbd_id"],
        block["eb_id"],
        block["data_products"][0]["product_id"],
    )
    lines = _sync_csv(
        tap_service, f"SELECT obs_publisher_did FROM ivoa.obscore WHERE obs_publisher_did = '{did}'"
    )
    assert lines[1:] == [did], lines
    plan = _plan(
        database_url,
        f"SELECT obs_id FROM ivoa.obscore WHERE obs_publisher_did = '{did}'",
        *_ONLY_BITMAP_SCANS,
    )
    assert "obscore_did_key" in plan, plan  # equality: the unique key itself


# The materialised relation must hold exactly what the projection over the
# ODP tables yields: same rows, same bytes. md5 per row, summed, over every
# column, with the projection evaluated live for the comparison.
def _checksum(conn, relation: str) -> tuple[int, str]:
    return conn.execute(
        f"SELECT count(*), coalesce(sum(('x' || left(md5(t::text), 15))::bit(60)::bigint), 0)::text"
        f" FROM ({relation}) AS t"
    ).fetchone()


def _relation_matches_projection(database_url: str) -> None:
    import psycopg
    from egernia_api.plugins import obscore

    with psycopg.connect(database_url) as conn:
        table = _checksum(conn, "SELECT * FROM ivoa.obscore")
        projection = _checksum(conn, obscore.select_sql())
    assert table == projection, (table, projection)


def test_a_scan_over_the_relation_joins_nothing(tap_service, database_url):
    """What the materialisation buys: an aggregate over the collection, or a
    result that reads access_url, is a scan of one relation — no hash of
    observations against every product, no probe of artifacts per row."""
    for sql in (
        "SELECT obs_collection, dataproduct_type, count(*), min(t_min), max(t_max)"
        " FROM ivoa.obscore WHERE calib_level >= 2 GROUP BY obs_collection, dataproduct_type",
        "SELECT access_url, obs_collection FROM ivoa.obscore WHERE obs_collection = 'x'",
    ):
        plan = _plan(database_url, sql)
        assert "artifacts" not in plan and "observations" not in plan and "Join" not in plan, plan


def test_the_relation_holds_exactly_the_projection_and_follows_every_write(
    tap_service, api_url, database_url
):
    """Read-after-write, in the writer's own transaction: a posted document is
    on ivoa.obscore when the POST returns; an amended artifact or observation
    moves the derived columns; a deleted document takes its rows with it.
    After each step the whole relation checksums identically to the live
    projection."""
    import psycopg

    payload = copy.deepcopy(SRC_INGESTION_EXAMPLE)
    payload["project_id"] = "obscore-sync"
    observation = payload["observations"][0]
    product = observation["scheduling_blocks"][0]["execution_blocks"][0]["data_products"][0]
    did_prefix = f"ivo://skao.int/~?obscore-sync/{observation['obs_id']}/"

    created = httpx.post(f"{api_url}/notifications", json=payload, timeout=30)
    assert created.status_code == 201, created.text
    lines = _sync_csv(
        tap_service,
        "SELECT obs_collection, access_url FROM ivoa.obscore"
        f" WHERE obs_publisher_did LIKE '{did_prefix}%'",
    )
    collection = observation.get("collection") or "unclassified"
    assert len(lines) > 1 and all(line.startswith(f"{collection},") for line in lines[1:])
    science = next(a for a in product["artifacts"] if a["semantics"] == "science")
    assert any(science["access_url"] in line for line in lines[1:])
    _relation_matches_projection(database_url)

    # amend the collection on the observation: every product row follows
    amended = httpx.patch(
        f"{api_url}/notifications/obscore-sync",
        json={
            "table": "observations",
            "match": {"obs_id": observation["obs_id"]},
            "values": {"collection": "cycle-9"},
        },
        timeout=30,
    )
    assert amended.status_code == 200, amended.text
    lines = _sync_csv(
        tap_service,
        "SELECT DISTINCT obs_collection FROM ivoa.obscore"
        f" WHERE obs_publisher_did LIKE '{did_prefix}%'",
    )
    assert lines[1:] == ["cycle-9"], lines
    _relation_matches_projection(database_url)

    # amend the science artifact's URL: the product's access_url follows
    amended = httpx.patch(
        f"{api_url}/notifications/obscore-sync",
        json={
            "table": "artifacts",
            "match": {"artifact_id": science["artifact_id"]},
            "values": {"access_url": "https://example.org/amended.fits"},
        },
        timeout=30,
    )
    assert amended.status_code == 200, amended.text
    lines = _sync_csv(
        tap_service,
        "SELECT access_url FROM ivoa.obscore"
        f" WHERE obs_publisher_did = '{did_prefix}{observation['scheduling_blocks'][0]['sbd_id']}"
        f"/{observation['scheduling_blocks'][0]['execution_blocks'][0]['eb_id']}"
        f"/{product['product_id']}'",
    )
    assert lines[1:] == ["https://example.org/amended.fits"], lines
    _relation_matches_projection(database_url)

    # re-posting the document is idempotent on the relation too
    reposted = httpx.post(f"{api_url}/notifications", json=payload, timeout=30)
    assert reposted.status_code == 201, reposted.text
    _relation_matches_projection(database_url)

    # and a deletion's cascade takes the rows with it
    deleted = httpx.delete(f"{api_url}/notifications/obscore-sync", timeout=30)
    assert deleted.status_code == 200, deleted.text
    lines = _sync_csv(
        tap_service,
        f"SELECT count(*) FROM ivoa.obscore WHERE obs_publisher_did LIKE '{did_prefix}%'",
    )
    assert lines[1:] == ["0"], lines
    _relation_matches_projection(database_url)
    with psycopg.connect(database_url) as conn:
        assert conn.execute("SELECT count(*) FROM ivoa.obscore").fetchone()[0] > 0


def test_the_backfill_join_has_a_foreign_key_to_estimate_from(tap_service, database_url):
    """data_products joins observations two levels up the hierarchy (in the
    backfill and the triggers, and in any ADQL that joins them directly).
    The planner estimates a join from the foreign keys between the two
    relations joined, and with none it multiplied the selectivities of key
    columns that are perfectly correlated — 10,000x low on the comparison
    corpus, enough to sort-and-group where a hash aggregate belonged."""
    import psycopg

    with psycopg.connect(database_url) as conn:
        row = conn.execute(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint"
            " WHERE conrelid = 'srcnet.data_products'::regclass"
            " AND conname = 'data_products_observations_fkey'"
        ).fetchone()
    assert row is not None
    assert row[0].startswith(
        "FOREIGN KEY (project_id, obs_id) REFERENCES srcnet.observations(project_id, obs_id)"
    )


def test_a_deployment_still_serving_the_view_is_migrated_to_the_table(tap_service, database_url):
    """Before this release ivoa.obscore was a view over the ODP tables. Its
    first bootstrap on the new release must swap the table in under the same
    name with every row the view had, without anything but the bootstrap
    running — and leave the triggers behind so the next write is followed."""
    import psycopg
    from egernia_core import bootstrap
    from egernia_core.metadata.plugins import active_plugins

    with psycopg.connect(database_url) as conn:
        before = _checksum(conn, "SELECT * FROM ivoa.obscore")
        assert before[0] > 0
        with conn.transaction():
            conn.execute("CREATE TABLE ivoa.obscore_prev AS SELECT * FROM ivoa.obscore")
            conn.execute("DROP TABLE ivoa.obscore")
            conn.execute("CREATE VIEW ivoa.obscore AS SELECT * FROM ivoa.obscore_prev")
            conn.execute(
                "COMMENT ON VIEW ivoa.obscore IS"
                " 'ObsCore 1.1 over the ODP metadata (definition 6a2b0d29a829f9d4)'"
            )
        with conn.transaction():
            bootstrap.bootstrap(conn, active_plugins())
        kind = conn.execute("SELECT relkind FROM pg_class WHERE oid = 'ivoa.obscore'::regclass")
        assert kind.fetchone()[0] == "r"
        assert _checksum(conn, "SELECT * FROM ivoa.obscore") == before
        indexes = {
            row[0]
            for row in conn.execute(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'ivoa'"
                " AND tablename = 'obscore'"
            )
        }
        assert {"obscore_did_key", "obscore_did_trgm", "obscore_spoint_gist"} <= indexes
        triggers = {
            row[0]
            for row in conn.execute(
                "SELECT tgrelid::regclass::text FROM pg_trigger WHERE tgname LIKE 'obscore_sync_%'"
            )
        }
        assert triggers == {"srcnet.data_products", "srcnet.artifacts", "srcnet.observations"}
        conn.execute("DROP TABLE ivoa.obscore_prev")
        conn.commit()
    _relation_matches_projection(database_url)
