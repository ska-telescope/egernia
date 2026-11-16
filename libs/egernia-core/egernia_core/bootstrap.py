"""Startup schema handling shared by both services, and the explicit
pre-deploy bootstrap command.

By default every service replica ensures the schema at startup (idempotent,
advisory-locked DDL), which is what a rolling upgrade relies on: whichever
new pod touches the database first migrates it forward. A deployment that
would rather keep DDL away from the runtime credentials runs

    python -m egernia_core.bootstrap

once against the database before deploying (with credentials that may own
schema changes) and sets TAP_SCHEMA_BOOTSTRAP_ON_STARTUP=false, after which
the services only *verify* the schema at startup and fail fast — naming this
command — when it is missing or outdated.
"""

import logging
import time

import psycopg

from . import uws
from .config import geometry_backend, settings
from .db import close_pool
from .db import connection as db_connection
from .geometry import SupportFunction
from .metadata import ingest
from .metadata.plugins import MetadataPlugin

log = logging.getLogger("egernia_core")

BOOTSTRAP_COMMAND = "python -m egernia_core.bootstrap"


def bootstrap(conn, plugins: list[MetadataPlugin]) -> None:
    """All the DDL the services need: the uws.jobs forward migration plus
    each plugin's generated tables and TAP_SCHEMA registration."""
    uws.ensure_job_columns(conn)
    ensure_tap_schema_self(conn)
    ensure_geometry_functions(conn)
    for plugin in plugins:
        ingest.ensure_schema(conn, plugin)


def missing_geometry_functions(conn) -> list[SupportFunction]:
    """The SQL functions the geometry backend's translation calls, its
    extension does not define (geometry.py, support_functions), and this
    database lacks. None while the extension itself is missing: there is no
    geometry to translate for then, and db/init lets a database start so."""
    backend = geometry_backend()
    if not backend.support_functions:
        return []
    installed = conn.execute(
        "SELECT 1 FROM pg_extension WHERE extname = %s", (backend.extension,)
    ).fetchone()
    if installed is None:
        return []
    return [
        function
        for function in backend.support_functions
        if conn.execute("SELECT to_regprocedure(%s)", (function.signature,)).fetchone()[0] is None
    ]


def ensure_geometry_functions(conn) -> None:
    """Create the missing support functions (db/init creates them on a fresh
    database; this covers one that predates them).

    Under the advisory lock the schema DDL takes, so replicas starting
    together do not race to create them. In a savepoint, and a refusal --
    most likely a role that may not create in the public schema, which
    PostgreSQL 15 and later deny by default -- is a warning, not a failed
    start: the service then behaves as before these functions existed, where
    only a geometry in a select list fails.
    """
    conn.execute("SELECT pg_advisory_xact_lock(%s)", (ingest.ADVISORY_LOCK_KEY,))
    missing = missing_geometry_functions(conn)
    if not missing:
        return
    try:
        with conn.transaction():
            for function in missing:
                conn.execute(function.definition)
    except psycopg.Error as exc:
        log.warning(
            "geometry functions %s not created (%s): a POINT, CIRCLE or POLYGON in a select"
            " list fails until they are; db/init/01_extensions.sql creates them, as does"
            " `%s` run as a role that may create in the public schema",
            ", ".join(f.signature for f in missing),
            str(exc).strip(),
            BOOTSTRAP_COMMAND,
        )


def ensure_tap_schema_self(conn) -> None:
    """Forward-migrate TAP_SCHEMA's description of itself (fresh databases
    get this from db/init/02_tap_schema.sql).

    Two TAP 1.1 conformance points, both found by stilts taplint: the
    deprecated-but-required ``"size"`` column must be registered delimited
    (SIZE is an ADQL reserved word), and TAP_SCHEMA must declare its own
    standard foreign keys so a client can join the metadata tables.
    """
    conn.execute(
        "UPDATE tap_schema.columns SET column_name = '\"size\"'"
        " WHERE table_name = 'tap_schema.columns' AND column_name = 'size'"
    )
    conn.execute(
        """
        INSERT INTO tap_schema.keys (key_id, from_table, target_table, description) VALUES
            ('tap_schema:tables_schema', 'tap_schema.tables', 'tap_schema.schemas',
             'table membership'),
            ('tap_schema:columns_table', 'tap_schema.columns', 'tap_schema.tables',
             'column membership'),
            ('tap_schema:keys_from_table', 'tap_schema.keys', 'tap_schema.tables',
             'referencing table'),
            ('tap_schema:keys_target_table', 'tap_schema.keys', 'tap_schema.tables',
             'referenced table'),
            ('tap_schema:key_columns_key', 'tap_schema.key_columns', 'tap_schema.keys',
             'key membership')
        ON CONFLICT (key_id) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO tap_schema.key_columns (key_id, from_column, target_column)
        SELECT v.key_id, v.from_column, v.target_column FROM (VALUES
            ('tap_schema:tables_schema', 'schema_name', 'schema_name'),
            ('tap_schema:columns_table', 'table_name', 'table_name'),
            ('tap_schema:keys_from_table', 'from_table', 'table_name'),
            ('tap_schema:keys_target_table', 'target_table', 'table_name'),
            ('tap_schema:key_columns_key', 'key_id', 'key_id')
        ) AS v(key_id, from_column, target_column)
        WHERE NOT EXISTS (
            SELECT 1 FROM tap_schema.key_columns k WHERE k.key_id = v.key_id
        )
        """
    )


def check_ready(conn, plugins: list[MetadataPlugin]) -> None:
    """Read-only verification that a bootstrap already ran.

    Selects every column the services rely on (zero rows), so a missing
    table and a table an older bootstrap left without a newer model's
    columns both fail here — at startup, with the remedy named — rather
    than later as a 500 on the endpoints that touch them.
    """
    try:
        conn.execute(f"SELECT {uws.JOB_COLUMNS_SQL} FROM uws.jobs WHERE false")
        for plugin in plugins:
            for table in plugin.tables:
                columns = ", ".join(c.name for c in table.columns)
                conn.execute(f"SELECT {columns} FROM {table.qualified} WHERE false")
    except Exception as exc:
        raise RuntimeError(
            "schema is missing or outdated and startup DDL is disabled"
            f" (TAP_SCHEMA_BOOTSTRAP_ON_STARTUP=false); run `{BOOTSTRAP_COMMAND}`"
            " against this database before deploying"
        ) from exc
    # outside the try: a footprint column of the other backend's type is not
    # fixed by running the bootstrap, and the error says what is
    for plugin in plugins:
        ingest.check_geometry_types(conn, plugin.tables)
    # a database the bootstrap has not been re-run on since these functions
    # were added: everything but a geometry in a select list works, as before
    missing = missing_geometry_functions(conn)
    if missing:
        log.warning(
            "geometry functions %s are missing: a POINT, CIRCLE or POLYGON in a select list"
            " fails until `%s` is run against this database",
            ", ".join(f.signature for f in missing),
            BOOTSTRAP_COMMAND,
        )


def startup(plugins: list[MetadataPlugin], attempts: int = 5, delay_s: float = 2.0) -> None:
    """Prepare — or, with startup DDL disabled, verify — the schema at
    service start, retrying while the database comes up."""
    if settings.schema_bootstrap_on_startup:
        step, what = bootstrap, "bootstrap"
    else:
        step, what = check_ready, "readiness check"
        log.info("startup schema DDL disabled; verifying a pre-deploy bootstrap ran")
    _run_with_retry(step, plugins, attempts, delay_s, what)


def _run_with_retry(step, plugins, attempts: int, delay_s: float, what: str) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with db_connection() as conn, conn.transaction():
                step(conn, plugins)
            return
        except Exception as exc:
            if attempt == attempts:
                # Fail fast: a half-initialized service would only surface
                # confusing errors later on the metadata endpoints and
                # generated-schema queries; the orchestrator should restart us.
                raise RuntimeError(f"schema {what} failed after {attempts} attempts") from exc
            log.warning("schema %s attempt %d failed (%s), retrying", what, attempt, exc)
            time.sleep(delay_s)


def main() -> None:
    """The explicit pre-deploy bootstrap: ensure everything, once, and exit."""
    from .metadata.plugins import active_plugins
    from .observability import configure_logging

    configure_logging("schema-bootstrap")
    plugins = active_plugins()
    log.info("bootstrapping schema (plugins: %s)", ", ".join(p.name for p in plugins) or "none")
    try:
        # generous retries: a fresh environment's database may still be starting
        _run_with_retry(bootstrap, plugins, attempts=30, delay_s=2.0, what="bootstrap")
        with db_connection() as conn:
            ingest.warn_tap_schema_divergence(conn)
    finally:
        close_pool()
    log.info("schema bootstrap complete")


if __name__ == "__main__":
    main()
