r"""Does the `COPY` fill put the same cells in the temp table the INSERT did?

`create_upload_tables` used to fill an uploaded table with multi-row INSERTs,
500 rows per statement; it now sends one `COPY ... FROM STDIN`. COPY's text
format is a different wire encoding, with its own escapes and its own NULL
marker, so "the same cells" is a claim about bytes and has to be asked of a
real PostgreSQL rather than reasoned about.

The old fill is reproduced here rather than kept in the product: each test
builds one table each way from the *same* rows and compares every cell. The
values are the ones an encoding can eat -- NULL against the empty string, a
literal `\N` (COPY's NULL marker) against a real NULL, tabs and newlines and
backslashes (COPY text's escapes), non-ASCII, non-finite doubles, and a
`timestamp` column, whose cells `_convert` leaves as text for PostgreSQL to
parse.

Two entry points, because they reach different values. The VOTable test is
the real path end to end; the direct-rows test carries what a VOTable cannot
express -- the empty string (an empty `<TD/>` parses as NULL) and the C escapes
that are not XML 1.0 characters.
"""

from __future__ import annotations

import psycopg
import pytest
from egernia_core.query.upload import UploadedTable, create_upload_tables, parse_votable

pytestmark = pytest.mark.component

_INSERT_BATCH = 500  # as the replaced implementation batched


def _insert_fill(conn, upload: UploadedTable) -> None:
    """The fill `create_upload_tables` used to do, verbatim."""
    col_names = ", ".join(col for col, _ in upload.columns)
    row_tpl = "(" + ", ".join(["%s"] * len(upload.columns)) + ")"
    for start in range(0, len(upload.rows), _INSERT_BATCH):
        batch = upload.rows[start : start + _INSERT_BATCH]
        conn.execute(
            f"INSERT INTO {upload.ident} ({col_names}) VALUES " + ", ".join([row_tpl] * len(batch)),
            tuple(value for row in batch for value in row),
        )


def _fill_both_ways(database_url: str, upload: UploadedTable) -> tuple[list, list]:
    """(rows the COPY fill stored, rows the INSERT fill stored), ordered by the
    first column, which every table here makes a row counter."""
    out = []
    for fill in ("copy", "insert"):
        with psycopg.connect(database_url) as conn:
            with conn.transaction():
                if fill == "copy":
                    create_upload_tables(conn, [upload], "tap_reader")
                else:
                    columns = ", ".join(f"{c} {t}" for c, t in upload.columns)
                    conn.execute(
                        f"CREATE TEMP TABLE {upload.ident.split('.', 1)[1]}"
                        f" ({columns}) ON COMMIT DROP"
                    )
                    _insert_fill(conn, upload)
                out.append(conn.execute(f"SELECT * FROM {upload.ident} ORDER BY 1").fetchall())
            conn.rollback()
    return out[0], out[1]


# Cells that exercise an encoding rather than a pleasant value.
TEXT_CELLS = [
    "plain",
    "\\N",  # COPY text's NULL marker, as data
    "\\",  # a lone backslash
    "\\\\N",
    "a\tb",  # COPY text's field separator
    "a\\tb",  # ... and its escape, as data
    "line1\nline2",  # COPY text's row separator
    "cr\rhere",
    "back\\slash\tand\ttabs",
    "  leading and trailing  ",
    "naïve — ✓ 中文 🛰",  # non-ASCII, multi-byte, astral
    "NULL",
    ".",  # COPY's end-of-data marker, alone on a line
    "%s",  # would be a placeholder if anything still interpolated
    "'; DROP TABLE x; --",
]

DOUBLE_CELLS = ["1.5", "0", "-0.0", "1e308", "-1e308", "Inf", "-Inf", "+Inf", "infinity", "5e-324"]

COLUMNS = [
    ("i", "bigint"),
    ("t", "text"),
    ("d", "double precision"),
    ("n", "integer"),
    ("ts", "timestamp"),
]


def _votable(rows: list[tuple[str | None, ...]]) -> bytes:
    """A VOTable over `COLUMNS`; cells are raw TABLEDATA content, `None` for
    `<TD/>`, and `i` is filled in as the row counter."""
    head = (
        '<?xml version="1.0"?>'
        '<VOTABLE version="1.4" xmlns="http://www.ivoa.net/xml/VOTable/v1.3">'
        "<RESOURCE><TABLE>"
        '<FIELD name="i" datatype="long"/>'
        '<FIELD name="t" datatype="char" arraysize="*"/>'
        '<FIELD name="d" datatype="double"/>'
        '<FIELD name="n" datatype="int"><VALUES null="-999"/></FIELD>'
        '<FIELD name="ts" datatype="char" arraysize="*" xtype="timestamp"/>'
        "<DATA><TABLEDATA>"
    )
    body = []
    for i, cells in enumerate(rows):
        markup = "".join(
            "<TD/>" if cell is None else f"<TD>{cell}</TD>" for cell in (str(i), *cells)
        )
        body.append(f"<TR>{markup}</TR>")
    return (head + "".join(body) + "</TABLEDATA></DATA></TABLE></RESOURCE></VOTABLE>").encode()


def _escape(text: str) -> str:
    r"""The cell's content as TABLEDATA markup.

    CR goes as a character reference: XML normalises a literal one to LF, and
    a CR that never reaches the parser cannot test COPY's escape for it. (The
    remaining C escapes COPY spells out -- \b, \f, \v -- are not XML 1.0
    characters at all, so only the direct-rows test can carry them.)
    """
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return escaped.replace("\r", "&#13;")


def test_copy_and_insert_fills_agree_on_an_uploaded_votable(database_url):
    rows: list[tuple[str | None, ...]] = []
    for index in range(max(len(TEXT_CELLS), len(DOUBLE_CELLS))):
        rows.append(
            (
                _escape(TEXT_CELLS[index % len(TEXT_CELLS)]),
                DOUBLE_CELLS[index % len(DOUBLE_CELLS)],
                str(index),
                "2026-01-02T03:04:05.123456",
            )
        )
    all_null = len(rows)
    rows.append((None, None, None, None))  # `<TD/>` everywhere
    sentinel = len(rows)
    rows.append(("", "", "-999", ""))  # empty cells, and the declared sentinel
    rows.append(("&amp;&lt;&gt;", "nan", "0", "2026-12-31T23:59:59"))
    while len(rows) < 1201:  # across the old 500-row batch boundary, twice
        rows.append((_escape(TEXT_CELLS[len(rows) % len(TEXT_CELLS)]), "0.25", "7", "2026-06-01"))

    upload = parse_votable("pos", _votable(rows), max_rows=10_000, max_bytes=1 << 20)
    assert len(upload.rows) == len(rows)

    copied, inserted = _fill_both_ways(database_url, upload)
    assert copied == inserted
    assert len(copied) == len(rows)
    # The comparison is only worth the values in it: check the cases an
    # encoding could have eaten really did survive the round trip.
    stored = {row[0]: row for row in copied}
    assert stored[1][1] == "\\N"  # COPY's NULL marker as data
    assert stored[4][1] == "a\tb"
    assert stored[7][1] == "cr\rhere"
    assert stored[10][1] == "naïve — ✓ 中文 🛰"
    assert stored[all_null] == (all_null, None, None, None, None)
    assert stored[sentinel][3] is None  # the declared sentinel is a NULL
    assert {float("inf"), float("-inf")} <= {row[2] for row in copied}


def test_copy_and_insert_fills_agree_on_values_no_votable_can_carry(database_url):
    """The empty string (`<TD/>` parses as NULL, so the VOTable path cannot
    produce one) and the C escapes XML 1.0 excludes."""
    rows = [
        (0, "", 1.5, 0, "2026-01-02T03:04:05"),
        (1, "\b\f\v", -1.5, None, None),
        (2, "\x00nul-free \x01\x1f", 0.0, -1, "2026-01-02 03:04:05.5".replace("\x00", "")),
        (3, None, float("inf"), 2, None),
        (4, "\N{ZERO WIDTH SPACE}\N{NO-BREAK SPACE}", float("-inf"), 3, None),
    ]
    rows[2] = (2, "\x01\x1f low control bytes", 0.0, -1, "2026-01-02 03:04:05.5")
    upload = UploadedTable(name="pos", columns=COLUMNS, rows=[tuple(r) for r in rows])

    copied, inserted = _fill_both_ways(database_url, upload)
    assert copied == inserted
    assert copied[0][1] == ""  # the empty string, still not NULL
    assert copied[1][1] == "\b\f\v"
    assert copied[3][1] is None


def test_copy_fill_reports_a_bad_cell_as_a_database_error(database_url):
    """A value PostgreSQL refuses fails the transaction, as the INSERT did --
    it does not silently drop the row or leave the connection in COPY state."""
    upload = UploadedTable(
        name="pos",
        columns=[("i", "bigint"), ("ts", "timestamp")],
        rows=[(1, "2026-01-02T03:04:05"), (2, "not a timestamp")],
    )
    with psycopg.connect(database_url) as conn:
        with pytest.raises(psycopg.errors.DataError), conn.transaction():
            create_upload_tables(conn, [upload], "tap_reader")
        # the connection is usable again, so it can go back to the pool
        assert conn.execute("SELECT 1").fetchone() == (1,)
