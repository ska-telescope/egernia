"""The lowered DISTANCE predicate returns exactly the rows the unlowered one
did, on a real PostgreSQL with pg_sphere.

`DISTANCE(p, q) < r` translates to a pgsphere containment (which an index
serves) conjoined with the original degree comparison. Containment includes
the boundary and carries pgsphere's floating-point epsilon, so it is a
*superset* filter; this test is the evidence that the conjunction puts the
row set back exactly where it was — over a sample built to hit the cases a
spherical rewrite gets wrong: both poles, RA wrapping through zero, and
companions at exactly the comparison radius.
"""

import math

import psycopg
import pytest
from egernia_core.config import GEOMETRY_BACKENDS, _choose
from egernia_core.query.adql import adql_to_postgresql

pytestmark = [
    pytest.mark.component,
    # The lowering is the pg_sphere translation's: skycell plans
    # `distance(...) < r` as its indexed cone without one.
    pytest.mark.skipif(
        _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) != "pgsphere",
        reason="DISTANCE lowering applies to the pgsphere backend only",
    ),
]

SCHEMA = "xm_test"
RADII = (1.0 / 3600.0, 60.0 / 3600.0, 1.0)

#: The emission the translator produced before the lowering, and still
#: produces as the second conjunct of it. Asserted to be a substring of the
#: translated query, so the reference below cannot silently drift away from
#: what the lowering claims to be equivalent to.
UNLOWERED = (
    "DEGREES(spoint(RADIANS(a.s_ra), RADIANS(a.s_dec)) <-> "
    "spoint(RADIANS(b.s_ra), RADIANS(b.s_dec))) {op} {r!r}"
)

XMATCH_ADQL = (
    "SELECT a.id, b.id FROM {schema}.pts AS a JOIN {schema}.pts AS b "
    "ON DISTANCE(POINT('ICRS', a.s_ra, a.s_dec), POINT('ICRS', b.s_ra, b.s_dec)) {op} {r!r} "
    "WHERE a.id < b.id"
)


def _awkward_positions():
    """Positions where a spherical rewrite goes wrong if it is wrong at all.

    Around each base position, companions at half, exactly, and one and a
    half times each test radius — offset along a meridian, where the
    declination offset *is* the angular separation, and across it, where the
    RA offset has to be divided by cos(dec). The exactly-at-the-radius
    companions are the boundary cases: `@` includes them and `<` must not.
    """
    bases = [
        (0.0, 0.0),
        (180.0, 0.0),
        (359.9999, 0.0),  # RA wrapping through zero
        (0.0002, 0.0),
        (359.99, 60.0),
        (0.01, 60.0),
        (10.0, 89.999),  # north pole
        (0.0, 90.0),
        (123.4, -89.999),  # south pole
        (0.0, -90.0),
        (200.0, 45.0),
    ]
    points = []
    for ra, dec in bases:
        points.append((ra, dec))
        for radius in RADII:
            for factor in (0.5, 1.0, 1.5):
                offset = radius * factor
                points.append((ra, dec - offset if dec > 0 else dec + offset))
                if abs(dec) < 89.0:
                    step = offset / math.cos(math.radians(dec))
                    points.append(((ra + step) % 360.0, dec))
    return points


@pytest.fixture(scope="module")
def corpus(database_url):
    """A small catalogue with a GiST index on the point expression, plus the
    awkward positions. 4k rows: big enough that the planner prefers the index
    once the predicate is lowered, small enough that the unlowered reference
    query — 16M pair-wise distance computations, no index possible — still
    finishes in seconds."""
    with psycopg.connect(database_url, autocommit=True) as conn:
        if not conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_sphere'").fetchone():
            pytest.skip("pg_sphere is not installed in the component database")
        conn.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
        conn.execute(f"CREATE SCHEMA {SCHEMA}")
        conn.execute(
            f"CREATE TABLE {SCHEMA}.pts "
            "(id bigint PRIMARY KEY, s_ra double precision, s_dec double precision)"
        )
        # A deterministic spread over the whole sky: equal-area in dec, so
        # the density (and therefore the fan-out per probe) is uniform.
        conn.execute(
            f"INSERT INTO {SCHEMA}.pts (id, s_ra, s_dec) SELECT g, "
            "360.0 * ((g * 7919) % 1000003) / 1000003.0, "
            "degrees(asin(2.0 * ((g * 104729) % 999983) / 999983.0 - 1.0)) "
            "FROM generate_series(1, 4000) AS g"
        )
        with conn.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {SCHEMA}.pts (id, s_ra, s_dec) VALUES (%s, %s, %s)",
                [(1_000_000 + i, ra, dec) for i, (ra, dec) in enumerate(_awkward_positions())],
            )
        conn.execute(
            f"CREATE INDEX pts_spoint_gist ON {SCHEMA}.pts "
            "USING gist (spoint(radians(s_ra), radians(s_dec)))"
        )
        conn.execute(f"ANALYZE {SCHEMA}.pts")
        yield conn
        conn.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")


@pytest.mark.parametrize("radius", RADII)
@pytest.mark.parametrize("op", ["<", "<="])
def test_lowered_cross_match_returns_the_same_rows(corpus, radius, op):
    lowered = adql_to_postgresql(XMATCH_ADQL.format(schema=SCHEMA, op=op, r=radius)).rstrip(";")
    reference_predicate = UNLOWERED.format(op=op, r=radius)
    assert " @ scircle(" in lowered, "the predicate was not lowered at all"
    assert reference_predicate in lowered, "the recheck is not the old emission"

    unlowered = (
        f"SELECT a.id, b.id FROM {SCHEMA}.pts AS a JOIN {SCHEMA}.pts AS b "
        f"ON {reference_predicate} WHERE a.id < b.id"
    )
    with corpus.cursor() as cur:
        rows = sorted(cur.execute(lowered).fetchall())
        # No index can serve the unlowered form, so this is the sequential
        # scan the lowering exists to avoid — affordable only at 4k rows.
        assert rows == sorted(cur.execute(unlowered).fetchall())
    # The sample is built to match at every radius; an empty result would
    # make the equality above vacuous.
    assert rows


def test_lowered_cross_match_uses_the_index(corpus):
    """The point of the rewrite: the planner can reach the GiST index."""
    lowered = adql_to_postgresql(XMATCH_ADQL.format(schema=SCHEMA, op="<", r=1.0 / 3600.0)).rstrip(
        ";"
    )
    with corpus.cursor() as cur:
        plan = "\n".join(row[0] for row in cur.execute(f"EXPLAIN {lowered}").fetchall())
    assert "pts_spoint_gist" in plan, plan
