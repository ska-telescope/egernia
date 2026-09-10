"""PostgreSQL access via a shared psycopg3 connection pool."""

import contextlib

import psycopg
from psycopg import conninfo
from psycopg_pool import ConnectionPool

from .config import settings
from .observability import DB_CONNECTIONS_IN_USE, pool_wait_timer

_pool: ConnectionPool | None = None
_query_pool: ConnectionPool | None = None

# The two roles always exist as series, whether or not a deployment has
# replicas, so a dashboard reads 0 rather than "no data" while a path is idle.
PRIMARY, QUERY = "primary", "query"
for _role in (PRIMARY, QUERY):
    DB_CONNECTIONS_IN_USE.labels(pool=_role)


def _open(url: str) -> ConnectionPool:
    return ConnectionPool(
        url,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        # bound the wait, so exhaustion is a quick answer rather than a
        # request that hangs for psycopg's 30s default and then 500s
        timeout=settings.db_pool_timeout_s,
        open=True,
    )


def pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = _open(settings.database_url)
    return _pool


def query_pool() -> ConnectionPool:
    """The pool user queries execute on: the read replicas, if there are any.

    ``TAP_QUERY_DATABASE_URL`` unset — or set to the same URL — hands back the
    primary's own pool rather than opening a second one to the same server, so
    a deployment that has not asked for replicas keeps one pool of exactly the
    size, and the connection budget, it had.
    """
    global _query_pool
    url = settings.query_database_url
    if not url or url == settings.database_url:
        return pool()
    if _query_pool is None:
        _query_pool = _open(url)
    return _query_pool


@contextlib.contextmanager
def connection(*, replica_ok: bool = False):
    """A pooled connection, with the wait for it measured.

    Prefer this to ``pool().connection()``: waiting for a connection is the
    service's real backpressure signal, and it must stay visible.

    ``replica_ok`` marks the work that may run on a streaming-replication
    standby: executing a user query, which runs read-only under
    ``TAP_QUERY_ROLE``. It is opt-in per call site rather than the default
    because most of what this service does cannot go to a standby — the UWS
    job table, ingest and bootstrap all write, a query carrying a TAP_UPLOAD
    creates temp tables, and a read that has to see what this instant just
    wrote (the published-table list right after publishing one) would race
    replication lag.

    Only the acquisition is timed, never the held time. Timing the whole
    block — which is what a combined ``with`` does, since the caller's work
    happens at the yield — would add query and streaming time to the wait
    (a sync query holds its connection for the length of the client's
    download), turning the one metric that reports backpressure into a
    slow-response metric.
    """
    chosen, role = (query_pool, QUERY) if replica_ok else (pool, PRIMARY)
    with contextlib.ExitStack() as stack:
        with pool_wait_timer(role):
            conn = stack.enter_context(chosen().connection())
        DB_CONNECTIONS_IN_USE.labels(pool=role).inc()
        try:
            yield conn
        finally:
            DB_CONNECTIONS_IN_USE.labels(pool=role).dec()


def pinned_url(conn) -> str:
    """The query URL, pinned to the one server ``conn`` is connected to.

    Cancelling a statement is local to a PostgreSQL instance: with the query
    path on standbys, ``pg_cancel_backend()`` on the primary finds nothing to
    cancel, and a second connection from a load-balanced URL lands on
    whichever host comes next rather than the one running the statement. The
    executor's abort path signals that backend, so it needs a URL that can
    only reach that server.
    """
    return conninfo.make_conninfo(
        settings.query_database_url or settings.database_url,
        host=conn.info.host,
        port=conn.info.port,
    )


@contextlib.contextmanager
def pinned_connection(url: str):
    """A short-lived connection to exactly the server ``url`` names.

    Unpooled on purpose. It exists for the abort path, which is rare, has to
    reach one specific server, and must not queue behind a pool that may be
    full of the very query it was asked to cancel.
    """
    with psycopg.connect(url, autocommit=True) as conn:
        yield conn


def close_pool() -> None:
    global _pool, _query_pool
    for existing in (_pool, _query_pool):
        if existing is not None:
            existing.close()
    _pool = _query_pool = None


_NO_ROW = object()


class StreamedRows:
    """Rows from a query executed as a plain streamed statement.

    Deliberately not a named (DECLARE'd) cursor, though one would also keep
    memory flat: PostgreSQL never parallelises a cursor's query, and
    ``cursor_tuple_fraction`` biases the planner toward fast-start plans on
    the assumption that the client will stop reading early — an assumption
    that is always false here, because the service reads every result to
    MAXREC + 1.

    ``Cursor.stream()`` keeps the flat memory profile — rows arrive in
    server-side chunks and are yielded one at a time, and psycopg reads the
    socket only when the consumer asks for more, so a slow reader stalls the
    server through TCP backpressure instead of buffering — while the
    statement is planned as what it is: a plain query, read to the end, free
    to use parallel workers.

    Construction sends the query and waits for the first chunk, so the
    cursor's ``description`` is populated before any row is consumed, for an
    empty result too. The connection is busy until the rows are exhausted or
    ``close()`` is called; close cancels the statement and drains what
    already arrived, so an abandoned stream (MAXREC overflow, a client that
    disconnected mid-download) hands back a reusable connection. Callers
    wrap it in ``contextlib.closing``.

    ``statement_timeout`` bounds the whole statement, production and delivery
    both. For a service timeout that is the honest meaning — "the sync query
    may take this long" — rather than a bound on each internal fetch.
    """

    def __init__(self, cur, sql: str, chunk_rows: int):
        # chunked retrieval needs libpq 17+; older builds fall back to
        # row-by-row, which is correct and merely chattier
        size = chunk_rows if psycopg.capabilities.has_stream_chunked() else 1
        self._gen = cur.stream(sql, size=size)
        self._first = next(self._gen, _NO_ROW)
        if self._first is _NO_ROW and cur.description is None:
            # A zero-row stream finishes without ever exposing the row
            # description, and an empty result still needs its columns — an
            # empty VOTable carries its FIELDs. Recover them with a LIMIT 0
            # probe, which parses and plans but never pulls a row from its
            # child plan, so the query's work is not paid twice.
            probe = sql.rstrip().rstrip(";")
            cur.execute(f"SELECT * FROM ({probe}) AS empty_result LIMIT 0")

    def __iter__(self):
        if self._first is not _NO_ROW:
            first, self._first = self._first, _NO_ROW
            yield first
        yield from self._gen

    def close(self) -> None:
        self._gen.close()
