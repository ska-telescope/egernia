"""The ivoa.obscore view definition and its declarations (package 12).

Compliance is a list of exact names, units, UCDs and utypes from
REC-ObsCore-v1.1 Table 6 — so the tests are mostly that list, pinned. The
view's SQL semantics run against real PostgreSQL in the component suite;
here the pinned surface is what a validator (taplint, pyvo) would read.
"""

import pytest
from egernia_api.endpoints import vosi
from egernia_api.plugins import obscore

MANDATORY = [
    "dataproduct_type",
    "calib_level",
    "obs_collection",
    "obs_id",
    "obs_publisher_did",
    "access_url",
    "access_format",
    "access_estsize",
    "target_name",
    "s_ra",
    "s_dec",
    "s_fov",
    "s_region",
    "s_resolution",
    "s_xel1",
    "s_xel2",
    "t_min",
    "t_max",
    "t_exptime",
    "t_resolution",
    "t_xel",
    "em_min",
    "em_max",
    "em_res_power",
    "em_xel",
    "o_ucd",
    "pol_states",
    "pol_xel",
    "facility_name",
    "instrument_name",
]


def _by_name():
    return {c.name: c for c in obscore.OBSCORE_COLUMNS}


def test_all_thirty_mandatory_columns_in_rec_order():
    names = [c.name for c in obscore.OBSCORE_COLUMNS]
    assert names[: len(MANDATORY)] == MANDATORY
    # the one extra is the package-7 geometry, declared non-standard
    assert names[len(MANDATORY) :] == ["s_region_geom"]
    std = {c.name: c.std for c in obscore.OBSCORE_COLUMNS}
    assert all(std[name] == 1 for name in MANDATORY)
    assert std["s_region_geom"] == 0


def test_char_columns_declare_a_variable_arraysize():
    """VOTable needs arraysize="*" on char and nothing on the fixed-width
    types; it is derived from the datatype, so this is the rule's test."""
    for column in obscore.OBSCORE_COLUMNS:
        assert column.arraysize == ("*" if column.datatype == "char" else None), column.name


@pytest.mark.parametrize(
    ("name", "unit", "ucd", "utype"),
    [
        ("access_estsize", "kbyte", "phys.size;meta.file", "obscore:Access.size"),
        ("s_ra", "deg", "pos.eq.ra", None),
        ("s_resolution", "arcsec", "pos.angResolution", None),
        ("t_min", "d", "time.start;obs.exposure", None),
        ("t_exptime", "s", "time.duration;obs.exposure", None),
        ("em_min", "m", "em.wl;stat.min", None),
        (
            "obs_publisher_did",
            None,
            "meta.ref.ivoid",
            "obscore:Curation.publisherDID",
        ),
        ("pol_states", None, "meta.code;phys.polarization", None),
    ],
)
def test_units_ucds_and_utypes_match_rec_table_6(name, unit, ucd, utype):
    column = _by_name()[name]
    assert column.unit == unit
    assert column.ucd == ucd
    if utype is not None:
        assert column.utype == utype


def test_s_region_is_declared_a_region():
    assert _by_name()["s_region"].xtype == "adql:REGION"


def test_select_sql_carries_the_mapping_decisions():
    sql = obscore.select_sql()
    assert "WHEN 'table' THEN 'measurements'" in sql
    assert "COALESCE(o.collection, 'unclassified')" in sql
    assert "LEFT JOIN LATERAL" in sql and "art.semantics = 'science'" in sql
    assert "round(a.access_estsize / 1000.0)::bigint" in sql
    assert sql.startswith("SELECT\n")
    assert "FROM srcnet.data_products AS p\n" in sql
    # the same text over a trigger's transition table
    assert "FROM new_rows AS p\n" in obscore.select_sql("new_rows")


def test_the_did_percent_encodes_every_key_component():
    """A PublisherDID is permanent and the five key columns are free text: a
    product_id holding '/' or a space would forge a path segment or produce
    an identifier no client can parse, and two products could collide on
    one DID — which, now that the DID is the table's unique key, would be a
    failed ingest rather than a silent duplicate."""
    sql = obscore.select_sql()
    did = next(line for line in sql.splitlines() if line.endswith(" AS obs_publisher_did,"))
    assert did.lstrip().startswith("'ivo://skao.int/~?' || ")
    # the separators stay literal; the components do not
    assert did.count(" || '/' || ") == 4
    for column in obscore.did_key_columns():
        assert f"ELSE ivoa.did_encode(p.{column}) END" in did, column
        assert f"CASE WHEN p.{column} ~ '^[{obscore.DID_SAFE_CLASS}]*$'" in did, column
    assert "p.project_id ||" not in did  # never interpolated raw
    # the encoder: unreserved characters survive; anything else becomes %XX
    # per UTF-8 byte. IMMUTABLE and PARALLEL SAFE are what let it run in a
    # parallel worker.
    encoder = obscore.did_encode_sql()
    assert encoder.startswith("CREATE OR REPLACE FUNCTION ivoa.did_encode(component text)")
    assert "IMMUTABLE PARALLEL SAFE STRICT" in encoder
    assert "upper(encode(convert_to(ch, 'UTF8'), 'hex'))" in encoder
    assert f"CASE WHEN ch ~ '^[{obscore.DID_SAFE_CLASS}]$' THEN ch" in encoder
    assert "regexp_split_to_table(component, '') WITH ORDINALITY" in encoder


def test_the_did_has_no_subquery_so_it_can_run_in_parallel():
    did = next(
        line
        for line in obscore.select_sql().splitlines()
        if line.endswith(" AS obs_publisher_did,")
    )
    assert "SELECT" not in did
    assert did.count("ivoa.did_encode(") == len(obscore.did_key_columns())


def test_the_access_columns_come_from_the_first_science_artifact():
    lateral = obscore.select_sql().split("LEFT JOIN LATERAL (", 1)[1]
    assert "LIMIT" not in lateral
    for column in ("access_url", "access_format", "access_estsize"):
        assert f"(array_agg(art.{column} ORDER BY art.artifact_id))[1] AS {column}" in lateral


def test_the_triggers_cover_every_write_path_with_one_statement_each():
    """The relation is kept current by the database, not by the ingest
    module: a document upsert (INSERT and UPDATE on data_products, then the
    artifacts that carry the access columns), an amendment of any of the
    three source tables, a deletion's FK cascade and the seeder's bulk loads
    all reach the same statement-level triggers, which pay one join per
    statement rather than one per row."""
    statements = obscore.trigger_sql()
    triggers = [s for s in statements if s.startswith("CREATE OR REPLACE TRIGGER")]
    assert len(triggers) == 7
    covered = {
        (s.split(" AFTER ")[1].split(" ON ")[0], s.split(" ON srcnet.")[1].split(" ")[0])
        for s in triggers
    }
    assert covered == {
        ("insert", "data_products"),
        ("update", "data_products"),
        ("delete", "data_products"),
        ("insert", "artifacts"),
        ("update", "artifacts"),
        ("delete", "artifacts"),
        ("update", "observations"),
    }
    assert all("FOR EACH STATEMENT" in s and "REFERENCING" in s for s in triggers)
    # the same names in every trigger, so one function serves the three events
    assert all("new_rows" in s for s in triggers if "insert" in s or "update" in s)
    assert all("old_rows" in s for s in triggers if "delete" in s or "update" in s)

    products = next(s for s in statements if "obscore_data_products_changed()" in s)
    assert obscore.select_sql("new_rows").replace("\n", "\n        ") in products
    assert "ON CONFLICT (obs_publisher_did) DO UPDATE SET" in products
    assert "DELETE FROM ivoa.obscore WHERE obs_publisher_did IN" in products

    artifacts = next(s for s in statements if "obscore_artifacts_changed()" in s)
    sets = {line.split(" SET ")[1] for line in artifacts.splitlines() if " SET " in line}
    assert sets == {
        "access_url = a.access_url, access_format = a.access_format,"
        " access_estsize = round(a.access_estsize / 1000.0)::bigint"
    }
    assert "FROM new_rows UNION SELECT" in artifacts  # an UPDATE touches both key sets

    observations = next(s for s in statements if "obscore_observations_changed()" in s)
    assert (
        "SET obs_collection = COALESCE(o.collection, 'unclassified'),"
        " facility_name = o.facility_name, instrument_name = o.instrument_name" in observations
    )
    # a re-posted document re-writes its observations unchanged; that must
    # not rewrite every product row
    assert "IS DISTINCT FROM" in observations


def test_the_fingerprint_covers_everything_that_produces_a_row(auth_settings):
    before = obscore.definition_comment()
    assert before.startswith(f"{obscore.COMMENT_PREFIX} (definition ")
    auth_settings(obscore_did_prefix="ivo://other.org/~?")
    assert obscore.definition_comment() != before


def test_every_index_is_an_obscore_filter_column_or_the_key():
    assert set(obscore.INDEXES) >= {
        "obscore_did_key",
        obscore.TRGM_INDEX,
        "obscore_spoint_gist",
        "obscore_s_region_geom_gist",
    }
    assert obscore.index_sql("obscore_did_key") == (
        "CREATE UNIQUE INDEX obscore_did_key ON ivoa.obscore (obs_publisher_did)"
    )
    assert obscore.index_sql("obscore_spoint_gist", obscore.BUILD, "_build") == (
        "CREATE INDEX obscore_spoint_gist_build ON ivoa.obscore_build"
        " USING gist (spoint(RADIANS(s_ra), RADIANS(s_dec)))"
    )


def test_did_prefix_outside_the_identifier_alphabet_is_refused(auth_settings):
    auth_settings(obscore_did_prefix="ivo://x/'; DROP VIEW --")
    with pytest.raises(ValueError, match="identifier alphabet"):
        obscore.select_sql()


def test_capabilities_declare_the_data_model_with_odp_active():
    xml = vosi.capabilities_xml()
    assert '<dataModel ivo-id="ivo://ivoa.net/std/ObsCore#core-1.1">ObsCore-1.1</dataModel>' in xml
    # TAPRegExt order: after the interface, before the language
    assert xml.index("</interface>") < xml.index("<dataModel") < xml.index("<language>")


def test_capabilities_stay_silent_without_the_odp_plugin(monkeypatch):
    monkeypatch.setattr(vosi, "active_plugins", lambda: [])
    assert "dataModel" not in vosi.capabilities_xml()


def test_registry_record_inherits_the_data_model(auth_settings):
    auth_settings(
        registry_enabled=True,
        registry_identifier="ivo://skao.int/srcnet/tap",
        registry_title="t",
        registry_short_name="t",
        registry_description="d",
        registry_reference_url="https://example.org",
        registry_publisher="p",
        registry_creator="c",
        registry_contact_name="n",
        registry_contact_email="e@example.org",
        registry_subjects="radio",
        registry_created="2026-08-23",
    )
    assert "ObsCore-1.1</dataModel>" in vosi.voresource_xml()


class _RecordingConn:
    """Just enough connection for ensure_obscore: records statements, answers
    the relkind/comment, catalogue and quoting probes.

    Params are recorded alongside each statement, not discarded: Postgres
    plans no parameters for DDL, so a statement's *bindability* is part of
    what these tests have to be able to see."""

    def __init__(self, relkind: str | None, comment: str | None = None, index_exists=True):
        self._relkind = relkind
        self._comment = comment
        self._index_exists = index_exists
        self.statements: list[str] = []
        self.calls: list[tuple[str, tuple | None]] = []

    def execute(self, sql, params=None):
        self.statements.append(sql)
        self.calls.append((sql, params))
        relkind, comment = self._relkind, self._comment
        index_exists = self._index_exists

        class Result:
            def fetchone(self):
                if "pg_class" in sql:
                    return (relkind, comment) if relkind else None
                if "to_regclass" in sql:
                    return (12345 if index_exists else None,)
                if "quote_literal" in sql:
                    return ("'" + str(params[0]).replace("'", "''") + "'",)
                return None

        return Result()


def _ddl(conn):
    return [s.split("\n")[0] for s in conn.statements]


def test_calib_level_description_does_not_claim_obscores_vocabulary():
    """srcnet reads level 1 as calibrated where ObsCore 1.1 reads it as
    instrumental, and the view passes the value through untranslated: the
    description has to describe the column, not the standard."""
    description = _by_name()["calib_level"].description
    assert "1=calibrated" in description
    assert "instrumental" not in description
    assert "untranslated" in description


def test_a_preexisting_obscore_table_that_is_not_ours_is_left_alone():
    """The benchmark suite's synthetic ivoa.obscore is a real table, and so
    is any archive's own: the bootstrap must neither destroy it nor crash on
    it — it is that deployment's ObsCore. Ours carries the fingerprint."""
    conn = _RecordingConn("r", comment=None)
    obscore.ensure_obscore(conn)
    assert not any(s.startswith(("DROP", "CREATE", "LOCK", "ALTER")) for s in conn.statements)
    assert not any("tap_schema" in s for s in conn.statements)


def test_a_current_relation_is_not_touched():
    """The bootstrap runs on every pod start, and the swap takes ACCESS
    EXCLUSIVE on ivoa.obscore — so the unchanged case must issue no DDL at
    all beyond the lock-free registration, and find its indexes in the
    catalogue rather than through CREATE INDEX IF NOT EXISTS, which locks
    the table before it looks."""
    conn = _RecordingConn("r", comment=obscore.definition_comment())
    obscore.ensure_obscore(conn)
    assert not any(
        s.startswith(("DROP", "CREATE TABLE", "CREATE OR REPLACE", "CREATE INDEX", "LOCK", "ALTER"))
        for s in conn.statements
    )
    assert "CREATE SCHEMA IF NOT EXISTS ivoa" in conn.statements
    assert any("tap_schema.columns" in s for s in conn.statements)


def test_a_missing_index_is_put_back_on_a_current_relation():
    """The seeder sets the GiST indexes aside for a bulk load, and pg_trgm
    may have been unavailable at an earlier bootstrap."""
    conn = _RecordingConn("r", comment=obscore.definition_comment(), index_exists=False)
    obscore.ensure_obscore(conn)
    created = [s for s in conn.statements if s.startswith("CREATE ") and " INDEX " in s]
    assert created == [obscore.index_sql(name) for name in obscore.INDEXES]
    assert not any(s.startswith(("DROP", "CREATE TABLE", "LOCK")) for s in conn.statements)
    order = _ddl(conn)
    assert order.index("CREATE EXTENSION IF NOT EXISTS pg_trgm") < order.index(
        obscore.index_sql(obscore.TRGM_INDEX)
    )
    assert "RELEASE SAVEPOINT obscore_trgm" in conn.statements
    assert "ANALYZE ivoa.obscore" in conn.statements


def test_an_unavailable_pg_trgm_costs_the_index_not_the_bootstrap(caplog):
    """A role without CREATE on the database cannot install the extension;
    the relation still has to exist, and the failed statement has aborted
    the transaction, so that index runs under its own savepoint."""

    class _NoExtension(_RecordingConn):
        def execute(self, sql, params=None):
            if sql.startswith("CREATE EXTENSION"):
                self.statements.append(sql)
                raise RuntimeError("permission denied to create extension")
            return super().execute(sql, params)

    conn = _NoExtension("r", comment=obscore.definition_comment(), index_exists=False)
    obscore.ensure_obscore(conn)
    assert "ROLLBACK TO SAVEPOINT obscore_trgm" in conn.statements
    created = [s for s in conn.statements if s.startswith("CREATE ") and " INDEX " in s]
    assert created == [
        obscore.index_sql(name) for name in obscore.INDEXES if name != obscore.TRGM_INDEX
    ]
    assert any("tap_schema.columns" in s for s in conn.statements)  # bootstrap went on
    assert "trigram index not created" in caplog.text


def test_a_stale_view_is_rebuilt_beside_itself_and_swapped_in():
    """A deployment migrating from the view, or a mapping change: the source
    tables are locked against writers (never readers) so no row written
    during the backfill is missed, the table is filled and indexed under a
    scratch name while the old relation keeps serving, and only the DROP and
    RENAME at the end take the exclusive lock on ivoa.obscore."""
    conn = _RecordingConn("v", comment="ObsCore 1.1 over the ODP metadata (definition older0)")
    obscore.ensure_obscore(conn)
    order = _ddl(conn)
    lock = order.index(
        "LOCK TABLE srcnet.data_products, srcnet.observations, srcnet.artifacts IN SHARE MODE"
    )
    build = order.index("CREATE TABLE ivoa.obscore_build AS")
    first_index = min(i for i, s in enumerate(order) if s.startswith("CREATE UNIQUE INDEX"))
    trigger = min(i for i, s in enumerate(order) if s.startswith("CREATE OR REPLACE TRIGGER"))
    drop = order.index("DROP VIEW ivoa.obscore")
    rename = order.index("ALTER TABLE ivoa.obscore_build RENAME TO obscore")
    assert lock < build < first_index < trigger < drop < rename
    assert "DROP TABLE ivoa.obscore" not in order
    # every index is built on the scratch table under a scratch name, and
    # renamed once the swap has freed the real one
    built = [s for s in conn.statements if s.startswith("CREATE ") and " INDEX " in s]
    assert built == [obscore.index_sql(n, obscore.BUILD, "_build") for n in obscore.INDEXES]
    for name in obscore.INDEXES:
        assert order.index(f"ALTER INDEX ivoa.{name}_build RENAME TO {name}") > rename
    # the expression index the view needed is gone with it
    assert "DROP INDEX IF EXISTS srcnet.data_products_obscore_did_trgm" in order
    assert "ANALYZE ivoa.obscore_build" in order
    # the encoder before anything that calls it
    assert (
        order.index("CREATE OR REPLACE FUNCTION ivoa.did_encode(component text) RETURNS text")
        < build
    )


def test_a_stale_table_of_ours_is_rebuilt_the_same_way():
    conn = _RecordingConn("r", comment="ObsCore 1.1 over the ODP metadata (definition older0)")
    obscore.ensure_obscore(conn)
    order = _ddl(conn)
    assert "DROP TABLE ivoa.obscore" in order and "DROP VIEW ivoa.obscore" not in order
    assert order.index("DROP TABLE ivoa.obscore") < order.index(
        "ALTER TABLE ivoa.obscore_build RENAME TO obscore"
    )


def test_a_first_creation_drops_nothing():
    conn = _RecordingConn(None)
    obscore.ensure_obscore(conn)
    order = _ddl(conn)
    assert "CREATE TABLE ivoa.obscore_build AS" in order
    assert not any(
        s.startswith("DROP VIEW") or s.startswith("DROP TABLE ivoa.obscore\n") for s in order
    )
    assert not any(s == "DROP TABLE ivoa.obscore" for s in order)


def test_the_comment_is_quoted_into_the_ddl_not_bound_as_a_parameter():
    """COMMENT ON is DDL and Postgres plans no parameters for it: binding the
    fingerprint raises 42601 and takes the whole metadata bootstrap — hence
    every pod's startup — down with it. The comment must reach the statement
    already quoted."""
    conn = _RecordingConn("v", comment="stale")
    obscore.ensure_obscore(conn)
    ddl_keywords = ("COMMENT", "CREATE", "DROP", "GRANT", "ALTER", "LOCK")
    ddl = [(s, p) for s, p in conn.calls if s.startswith(ddl_keywords)]
    assert all(p is None for _, p in ddl), [s for s, p in ddl if p is not None]
    comment_ddl = next(s for s, _ in ddl if s.startswith("COMMENT ON TABLE ivoa.obscore"))
    assert obscore.definition_comment() in comment_ddl
    assert "%s" not in comment_ddl


def test_the_registration_says_table_and_marks_the_indexed_columns():
    conn = _RecordingConn("r", comment=obscore.definition_comment())
    obscore.ensure_obscore(conn)
    tables = next(s for s in conn.statements if "INSERT INTO tap_schema.tables" in s)
    assert "'ivoa', 'ivoa.obscore', 'table'" in tables
    indexed = {p[0] for s, p in conn.calls if "INSERT INTO tap_schema.columns" in s and p[8] == 1}
    assert indexed == obscore.INDEXED_COLUMNS


def test_the_did_chain_is_configurable_from_the_model_hierarchy(auth_settings):
    """A deployment whose ODP model nests differently has a different
    identity chain, so the DID path is configured rather than compiled in."""
    auth_settings(obscore_did_columns="project_id.obs_id.product_id")
    assert obscore.did_key_columns() == ("project_id", "obs_id", "product_id")
    did = next(
        line
        for line in obscore.select_sql().splitlines()
        if line.endswith(" AS obs_publisher_did,")
    )
    assert did.count(" || '/' || ") == 2  # three components, two separators
    assert "p.sbd_id" not in did and "p.eb_id" not in did
    for column in ("project_id", "obs_id", "product_id"):
        # each component still percent-encoded, not interpolated raw
        assert f"ivoa.did_encode(p.{column})" in did


def test_the_default_chain_is_the_data_products_primary_key():
    """The default is not an arbitrary list: it is what makes a DID unique."""
    from egernia_api.plugins.odp import PLUGIN

    data_products = next(t for t in PLUGIN.tables if t.name == "data_products")
    assert obscore.did_key_columns() == tuple(c.name for c in data_products.columns if c.is_key)


@pytest.mark.parametrize(
    "configured",
    [
        "project_id; DROP VIEW ivoa.obscore --",
        "project_id, obs_id",
        "Project_ID",
        "'project_id'",
        "project_id.obs id",
        "",
        "   ",
    ],
)
def test_a_did_column_outside_the_identifier_alphabet_is_refused(auth_settings, configured):
    """These names are interpolated into a CREATE VIEW, where nothing can be
    bound, so the alphabet is closed rather than escaped."""
    auth_settings(obscore_did_columns=configured)
    with pytest.raises(ValueError, match="TAP_OBSCORE_DID_COLUMNS"):
        obscore.select_sql()


def test_a_qualified_name_is_read_as_two_components(auth_settings):
    """The separator is a dot, so `p.project_id` — the spelling the view's own
    SQL uses — is a two-column chain, not one qualified column. It is refused
    by PostgreSQL at bootstrap rather than here, because `p` is a syntactically
    valid column name that simply does not exist."""
    auth_settings(obscore_did_columns="p.project_id")
    assert obscore.did_key_columns() == ("p", "project_id")
