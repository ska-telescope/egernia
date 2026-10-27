"""The skycell geometry backend (TAP_GEOMETRY_BACKEND=skycell).

ADQL geometry translated for skycell rather than pg_sphere, the footprint
companion column and the position index built for it, and the setting that
chooses. The SQL is pinned exactly; that skycell answers it the way pg_sphere
answers its own translation is a property of the database, checked against a
real server.
"""

import contextlib
import logging
import pathlib
import sys
from xml.etree import ElementTree as ET

import pytest
import yaml
from egernia_core.config import GEOMETRY_BACKENDS, _choose, settings
from egernia_core.geometry import PGSPHERE, SKYCELL
from egernia_core.metadata import ingest
from egernia_core.metadata.regions import (
    POSITION_RADIUS_DEG,
    UnsupportedRegion,
    stcs_to_skyregion,
)
from egernia_core.metadata.schema_gen import (
    build_tables,
    ddl_statements,
    position_index_definition,
    position_index_name,
    position_index_statements,
)
from egernia_core.query._adql import ADQLQueryTranslator
from egernia_core.query.adql import GEOMETRY_VISITORS, translate
from queryparser.exceptions import QueryError


@pytest.fixture
def skycell():
    """Run one test with TAP_GEOMETRY_BACKEND=skycell (Settings is frozen)."""
    original = settings.geometry_backend
    object.__setattr__(settings, "geometry_backend", "skycell")
    yield
    object.__setattr__(settings, "geometry_backend", original)


def sql(adql: str) -> str:
    return ADQLQueryTranslator(adql).to_postgresql(*GEOMETRY_VISITORS["skycell"])


# -- the setting ---------------------------------------------------------------


def test_backends_and_default(monkeypatch):
    assert GEOMETRY_BACKENDS == ("pgsphere", "skycell")
    monkeypatch.delenv("TAP_GEOMETRY_BACKEND", raising=False)
    assert _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) == "pgsphere"


def test_backend_setting_refuses_anything_else(monkeypatch):
    monkeypatch.setenv("TAP_GEOMETRY_BACKEND", "SkyCell ")
    assert _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) == "skycell"
    monkeypatch.setenv("TAP_GEOMETRY_BACKEND", "")
    assert _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) == "pgsphere"
    monkeypatch.setenv("TAP_GEOMETRY_BACKEND", "q3c")
    with pytest.raises(ValueError, match="TAP_GEOMETRY_BACKEND"):
        _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS)


def test_every_backend_setting_has_its_visitors():
    # the setting refuses anything else at startup, so this lookup cannot miss
    assert set(GEOMETRY_VISITORS) == set(GEOMETRY_BACKENDS)


# -- translation ---------------------------------------------------------------


def test_intersects_writes_a_point_constructor_first():
    # skycell defines intersects(skypos, skyregion) and not the reverse;
    # ADQL's INTERSECTS is symmetric, so the point goes first
    assert sql("SELECT * FROM t WHERE 1 = INTERSECTS(s_region_geom, POINT('ICRS', 10, 20))") == (
        "SELECT * FROM t WHERE intersects(skycell_point(10.0, 20.0), s_region_geom) = 1;"
    )
    assert sql("SELECT * FROM t WHERE INTERSECTS(POINT('ICRS', 10, 20), s_region_geom) = 0") == (
        "SELECT * FROM t WHERE intersects(skycell_point(10.0, 20.0), s_region_geom) = 0;"
    )
    # two regions keep the order they were written in
    assert sql(
        "SELECT * FROM t WHERE 1 = INTERSECTS(s_region_geom, CIRCLE('ICRS', 10, 20, 1))"
    ) == ("SELECT * FROM t WHERE intersects(s_region_geom, skycell_circle(10.0, 20.0, 1.0)) = 1;")


def test_coord_functions_record_their_column_as_a_geometry(monkeypatch):
    from egernia_api.queries import query as query_module
    from egernia_core.errors import UsageError

    translator = ADQLQueryTranslator(
        "SELECT COORD1(s_region), CENTROID(o.s_region) FROM ivoa.obscore AS o"
        " WHERE COORD2(POINT('ICRS', 1, 2)) > 0"
    )
    translator.to_postgresql(*GEOMETRY_VISITORS["skycell"])
    assert translator.geometry_columns == {"s_region", "o.s_region"}
    # so a text column there is a usage error, not a database fault
    monkeypatch.setattr(
        query_module,
        "_column_is_geometry",
        lambda: {"ivoa.obscore.s_region": False, "ivoa.obscore.s_region_geom": True},
    )
    with pytest.raises(UsageError, match="s_region_geom"):
        query_module._reject_text_geometry(
            translator.geometry_columns, frozenset({"ivoa.obscore"}), set()
        )


def test_cone_is_contains_compared_with_one():
    assert sql(
        "SELECT * FROM t WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 10, 20, 0.5)) = 1"
    ) == (
        "SELECT * FROM t WHERE"
        " contains(skycell_point(ra, dec), skycell_circle(10.0, 20.0, 0.5)) = 1;"
    )


def test_reversed_cone_and_left_hand_comparison_are_kept_as_written():
    # a constant point inside a circle around each row, as the Gaia archive
    # writes cone searches: skycell plans it as the cone, so it stays as is
    assert sql(
        "SELECT * FROM t WHERE 1 = CONTAINS(POINT('ICRS', 1, 2), CIRCLE('ICRS', ra, dec, 0.1))"
    ) == (
        "SELECT * FROM t WHERE contains(skycell_point(1.0, 2.0), skycell_circle(ra, dec, 0.1)) = 1;"
    )


def test_not_contained_and_intersects():
    assert sql(
        "SELECT * FROM t WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 1, 2, 3)) = 0"
    ).endswith("contains(skycell_point(ra, dec), skycell_circle(1.0, 2.0, 3.0)) = 0;")
    assert sql(
        "SELECT * FROM t WHERE INTERSECTS(s_region_geom, CIRCLE('ICRS', 1, 2, 3)) = 1"
    ).endswith("intersects(s_region_geom, skycell_circle(1.0, 2.0, 3.0)) = 1;")


def test_cross_match():
    assert sql(
        "SELECT h.id FROM h JOIN g"
        " ON CONTAINS(POINT('ICRS', g.ra, g.dec), CIRCLE('ICRS', h.ra, h.dec, 0.001)) = 1"
    ) == (
        "SELECT h.id FROM h JOIN g ON"
        " contains(skycell_point(g.ra, g.dec), skycell_circle(h.ra, h.dec, 0.001)) = 1;"
    )


def test_polygon():
    assert sql(
        "SELECT * FROM t WHERE CONTAINS(POINT('ICRS', ra, dec),"
        " POLYGON('ICRS', 10, 20, 12, 20, 12, 22)) = 1"
    ).endswith("skycell_polygon(10.0, 20.0, 12.0, 20.0, 12.0, 22.0)) = 1;")


def test_box_is_the_coordinate_range_pg_sphere_gives_it():
    # the same RA/Dec corners as the pg_sphere translation's sbox, so a BOX
    # means the same under either backend
    assert sql(
        "SELECT * FROM t WHERE CONTAINS(POINT('ICRS', ra, dec), BOX('ICRS', 11, 21, 2, 4)) = 1"
    ).endswith(
        "skycell_polygon(10.000000000000, 19.000000000000, 12.000000000000, 19.000000000000,"
        " 12.000000000000, 23.000000000000, 10.000000000000, 23.000000000000)) = 1;"
    )


def test_distance_both_forms_in_degrees():
    assert sql(
        "SELECT * FROM t WHERE DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', 1, 2)) < 0.1"
    ) == ("SELECT * FROM t WHERE distance(skycell_point(ra, dec), skycell_point(1.0, 2.0)) < 0.1;")
    assert sql("SELECT DISTANCE(ra, dec, 1, 2) FROM t") == (
        "SELECT distance(ra, dec, 1.0, 2.0) AS distance FROM t;"
    )


def test_distance_bounds_are_not_lowered_to_pgsphere_containment():
    # The pg_sphere translation rewrites these into `@ scircle(...)`;
    # skycell indexes the comparison as written.
    assert sql(
        "SELECT * FROM t WHERE 0.1 > DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', 1, 2))"
    ) == ("SELECT * FROM t WHERE 0.1 > distance(skycell_point(ra, dec), skycell_point(1.0, 2.0));")
    assert sql("SELECT * FROM t WHERE DISTANCE(ra, dec, 1, 2) <= 0.1") == (
        "SELECT * FROM t WHERE distance(ra, dec, 1.0, 2.0) <= 0.1;"
    )


def test_select_list_geometry_is_an_array_of_doubles_in_degrees():
    # the shape the pg_sphere translation returns (spoint_to_array_deg and
    # friends, geometry.py): [ra, dec], [ra, dec, radius], [ra1, dec1, ...]
    assert sql(
        "SELECT AREA(s_region_geom), POINT('ICRS', ra, dec), CIRCLE('ICRS', ra, dec, 1) AS c,"
        " POLYGON('ICRS', 10, 20, 11, 20, 11, 21) FROM t"
    ) == (
        "SELECT area(s_region_geom) AS adql_area,"
        " ARRAY[coord1(skycell_point(ra, dec)), coord2(skycell_point(ra, dec))] AS adql_point,"
        " ARRAY[coord1(skycell_point(ra, dec)), coord2(skycell_point(ra, dec)), 1.0] AS c,"
        " ARRAY[coord1(skycell_point(10.0, 20.0)), coord2(skycell_point(10.0, 20.0)),"
        " coord1(skycell_point(11.0, 20.0)), coord2(skycell_point(11.0, 20.0)),"
        " coord1(skycell_point(11.0, 21.0)), coord2(skycell_point(11.0, 21.0))]"
        " AS adql_polygon FROM t;"
    )
    # a constructor inside an expression stays a geometry
    assert sql("SELECT DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', 1, 2)) FROM t") == (
        "SELECT distance(skycell_point(ra, dec), skycell_point(1.0, 2.0)) AS distance FROM t;"
    )


def test_a_selected_centroid_is_a_point_array():
    assert sql(
        "SELECT CENTROID(s_region_geom), obs_id FROM t WHERE COORD1(CENTROID(s_region_geom)) > 3"
    ) == (
        "SELECT ARRAY[coord1(centroid(s_region_geom)), coord2(centroid(s_region_geom))]"
        " AS centroid, obs_id FROM t WHERE COORD1(CENTROID(s_region_geom)) > 3;"
    )


@pytest.mark.parametrize(
    ("box", "vertices"),
    [
        # crossing RA 0: RA normalised into [0, 360)
        ((0, 0, 2, 2), "359.0, -1.0, 1.0, -1.0, 1.0, 1.0, 359.0, 1.0"),
        # past the north pole: Dec clamped, the polar corners merged into the pole
        ((0, 89, 10, 6), "355.0, 86.0, 5.0, 86.0, 0.0, 90.0"),
        ((180, -89, 10, 6), "180.0, -90.0, 185.0, -86.0, 175.0, -86.0"),
    ],
)
def test_box_corners_are_on_the_sphere(box, vertices):
    args = ", ".join(map(str, box))
    translated = sql(
        f"SELECT * FROM t WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), BOX('ICRS', {args}))"
    )
    polygon = translated.split("skycell_polygon(")[1].split(")")[0]
    assert [round(float(v), 9) for v in polygon.split(",")] == [
        float(v) for v in vertices.split(",")
    ]


@pytest.mark.parametrize(
    "box",
    [
        "0, 0, 0, 1",  # no width
        "0, 0, 1, 0",  # no height
        "0, 0, 180, 1",  # 180 degrees wide
        "0, 120, 1, 2",  # beyond a pole
        "10, 0, 20, 200",  # past both poles: two corners, no polygon
    ],
)
def test_a_box_with_no_convex_polygon_is_a_query_error(box):
    with pytest.raises(QueryError):
        sql(f"SELECT * FROM t WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), BOX('ICRS', {box}))")


def test_geometry_columns_are_recorded():
    translator = ADQLQueryTranslator("SELECT * FROM t WHERE CONTAINS(pos, CIRCLE(centre, 0.1)) = 1")
    assert translator.to_postgresql(*GEOMETRY_VISITORS["skycell"]) == (
        "SELECT * FROM t WHERE"
        " contains(pos, skycell_circle(coord1(centre), coord2(centre), 0.1)) = 1;"
    )
    assert translator.geometry_columns == {"pos", "centre"}


def test_the_translation_cache_is_keyed_by_backend(skycell):
    query = "SELECT * FROM t WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 1, 2, 3)) = 1"
    assert "skycell_point" in translate(query).sql
    object.__setattr__(settings, "geometry_backend", "pgsphere")
    assert "spoint" in translate(query).sql


# -- user-defined functions ----------------------------------------------------

_PROP = "ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv, 2016, 2026)"


def test_a_position_function_is_a_point_in_the_predicates():
    # what an epoch-propagated search is written as: the propagated position
    # in CONTAINS, INTERSECTS and DISTANCE, where a POINT goes
    assert sql(f"SELECT * FROM t WHERE 1 = CONTAINS({_PROP}, CIRCLE('ICRS', 10, 20, 0.5))") == (
        "SELECT * FROM t WHERE contains(ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv,"
        " 2016, 2026), skycell_circle(10.0, 20.0, 0.5)) = 1;"
    )
    assert sql(
        "SELECT * FROM t WHERE 1 = INTERSECTS(CIRCLE('ICRS', 10, 20, 0.5),"
        " ivo_healpix_center(5, 7))"
    ) == (
        "SELECT * FROM t WHERE intersects(skycell_circle(10.0, 20.0, 0.5),"
        " ivo_healpix_center(5, 7)) = 1;"
    )
    assert sql(f"SELECT DISTANCE({_PROP}, POINT('ICRS', ra, dec)) AS moved FROM t") == (
        "SELECT distance(ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv, 2016, 2026),"
        " skycell_point(ra, dec)) AS moved FROM t;"
    )


def test_a_position_function_can_centre_a_circle():
    assert sql(
        "SELECT * FROM t WHERE 1 = CONTAINS(POINT('ICRS', ra, dec),"
        " CIRCLE(ivo_healpix_center(5, 7), 1))"
    ) == (
        "SELECT * FROM t WHERE contains(skycell_point(ra, dec),"
        " skycell_circle(coord1(ivo_healpix_center(5, 7)), coord2(ivo_healpix_center(5, 7)),"
        " 1.0)) = 1;"
    )


def test_a_position_function_in_the_select_list_is_ra_dec_like_a_point():
    assert sql(f"SELECT {_PROP}, ivo_healpix_center(5, 100) AS centre FROM t") == (
        "SELECT ARRAY[coord1(ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv, 2016, 2026)),"
        " coord2(ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv, 2016, 2026))]"
        " AS ivo_epoch_prop_pos,"
        " ARRAY[coord1(ivo_healpix_center(5, 100)), coord2(ivo_healpix_center(5, 100))]"
        " AS centre FROM t;"
    )


def test_other_user_functions_pass_through():
    # not a position: a number or an array, already what a client expects;
    # and a position inside an expression is left to that expression
    assert sql("SELECT ivo_epoch_prop(ra, dec, 1, 2, 3, 4, 2016, 2026) FROM t") == (
        "SELECT ivo_epoch_prop(ra, dec, 1, 2, 3, 4, 2016, 2026) FROM t;"
    )
    assert sql("SELECT ivo_healpix_index(5, POINT('ICRS', ra, dec)) FROM t") == (
        "SELECT ivo_healpix_index(5, skycell_point(ra, dec)) FROM t;"
    )
    assert sql(f"SELECT COORD1({_PROP}) FROM t") == (
        "SELECT COORD1(ivo_epoch_prop_pos(ra, dec, plx, pmra, pmdec, rv, 2016, 2026)) FROM t;"
    )


def test_an_undeclared_function_is_still_no_geometry():
    with pytest.raises(QueryError, match="unsupported geometry argument"):
        sql("SELECT * FROM t WHERE 1 = CONTAINS(my_point(ra, dec), CIRCLE('ICRS', 1, 2, 3))")


def test_the_declared_functions_name_their_point_results():
    names = {f.name for f in SKYCELL.user_functions}
    assert names == {
        "ivo_epoch_prop",
        "ivo_epoch_prop_pos",
        "ivo_healpix_index",
        "ivo_healpix_center",
    }
    assert SKYCELL.position_functions() == {"ivo_epoch_prop_pos", "ivo_healpix_center"}
    assert PGSPHERE.user_functions == ()


# -- footprints ----------------------------------------------------------------


def test_skyregion_circle_and_position():
    assert stcs_to_skyregion(None) is None
    assert stcs_to_skyregion("CIRCLE ICRS 10 20 0.5") == (
        "CIRCLE ICRS 10.000000000000 20.000000000000 0.500000000000"
    )
    # the frame is optional in the source and always written for skycell
    assert stcs_to_skyregion("CIRCLE 10 20 0.5") == stcs_to_skyregion("CIRCLE ICRS 10 20 0.5")
    assert stcs_to_skyregion("POSITION ICRS 10 20") == (
        f"CIRCLE ICRS 10.000000000000 20.000000000000 {POSITION_RADIUS_DEG:.12f}"
    )


def test_skyregion_polygon_either_winding_and_closing_vertex():
    square = "POLYGON ICRS 10.000000000000 20.000000000000 11.000000000000 20.000000000000"
    square += " 11.000000000000 21.000000000000 10.000000000000 21.000000000000"
    assert stcs_to_skyregion("POLYGON 10 20 11 20 11 21 10 21") == square
    assert stcs_to_skyregion("POLYGON 10 20 11 20 11 21 10 21 10 20") == square
    assert stcs_to_skyregion("POLYGON 10 21 11 21 11 20 10 20").startswith("POLYGON ICRS")


@pytest.mark.parametrize(
    "region",
    [
        "POLYGON ICRS 0 0 2 0 1 0.2 2 2 0 2",  # a notch
        "POLYGON ICRS 0 0 2 2 2 0 0 2",  # self-crossing
    ],
)
def test_skyregion_refuses_what_skycell_cannot_store(region):
    with pytest.raises(UnsupportedRegion, match="convex"):
        stcs_to_skyregion(region)


@pytest.mark.parametrize(
    ("region", "reason"),
    [
        ("POLYGON ICRS 10 20 11 20 10 20", "at least 3 distinct"),
        ("POLYGON ICRS 10 20 11 20 10 20 11 21", "repeated"),
        ("POLYGON ICRS 10 0 11 0 12 0", "one great circle"),
        ("POLYGON ICRS 0 0 120 0 240 0", "one great circle"),
    ],
)
def test_a_malformed_polygon_is_the_callers_mistake_not_a_null(region, reason):
    # not UnsupportedRegion, which ingest stores as NULL: a usage error
    with pytest.raises(ValueError, match=reason) as excinfo:
        stcs_to_skyregion(region)
    assert not isinstance(excinfo.value, UnsupportedRegion)


def test_a_vertex_repeated_in_a_row_is_dropped_as_pg_sphere_stores_it():
    assert stcs_to_skyregion("POLYGON ICRS 10 20 11 20 11 20 11 21") == (
        stcs_to_skyregion("POLYGON ICRS 10 20 11 20 11 21")
    )


def test_a_circle_wider_than_a_hemisphere_passes_through():
    # skycell holds a cap up to 180 degrees as one, and answers it the same
    # with and without its index (checked against the database)
    assert stcs_to_skyregion("CIRCLE ICRS 10 20 150") == (
        "CIRCLE ICRS 10.000000000000 20.000000000000 150.000000000000"
    )


def test_skyregion_still_validates_like_the_spoly_conversion():
    with pytest.raises(ValueError, match="Dec"):
        stcs_to_skyregion("CIRCLE ICRS 10 95 1")


def test_an_unsupported_footprint_is_ingested_as_null(caplog):
    column = next(
        c for c in _skycell_tables()["data_products"].columns if c.name == "s_region_geom"
    )
    with caplog.at_level(logging.WARNING, logger="egernia_core"):
        assert ingest._derive(column, "POLYGON ICRS 0 0 2 0 1 0.2 2 2 0 2") is None
    assert "s_region_geom left NULL" in caplog.text
    # anything malformed is still the caller's mistake, a degenerate polygon too
    from egernia_core.errors import UsageError

    with pytest.raises(UsageError):
        ingest._derive(column, "CIRCLE ICRS 10 95 1")
    with pytest.raises(UsageError, match="at least 3 distinct"):
        ingest._derive(column, "POLYGON ICRS 10 20 11 20 10 20")


# -- schema --------------------------------------------------------------------


def _skycell_tables():
    from ska_src_mm_notification.models.schemas.srcnet_ingestion import (
        SRCIngestionNotification,
    )

    original = settings.geometry_backend
    object.__setattr__(settings, "geometry_backend", "skycell")
    try:
        tables = build_tables(SRCIngestionNotification, "srcnet", "projects")
    finally:
        object.__setattr__(settings, "geometry_backend", original)
    return {t.name: t for t in tables}


def test_footprint_companion_is_a_skyregion_with_a_gist_index():
    column = next(
        c for c in _skycell_tables()["data_products"].columns if c.name == "s_region_geom"
    )
    assert column.sql_type == "skyregion"
    assert column.index == "gist"
    assert column.description.startswith("skycell footprint")


def test_position_index_is_the_skycell_cell_btree(skycell):
    assert position_index_statements("data_products", "srcnet.data_products") == [
        (
            "CREATE INDEX IF NOT EXISTS data_products_skycell_cell"
            " ON srcnet.data_products (skycell_ang2cell(s_ra, s_dec)) INCLUDE (s_ra, s_dec)"
        ),
        # only when the target is not 1000 already: no DDL on an unchanged bootstrap
        (
            "DO $do$ BEGIN IF (SELECT attstattarget FROM pg_attribute"
            " WHERE attrelid = 'srcnet.data_products_skycell_cell'::regclass AND attnum = 1)"
            " IS DISTINCT FROM 1000 THEN ALTER INDEX srcnet.data_products_skycell_cell"
            " ALTER COLUMN 1 SET STATISTICS 1000; END IF; END $do$"
        ),
    ]
    ddl = ddl_statements(list(_skycell_tables().values()), "tap_reader")
    assert not any("spoint" in s for s in ddl)
    assert any(
        "srcnet.data_products (skycell_ang2cell(s_ra, s_dec)) INCLUDE (s_ra, s_dec)" in s
        for s in ddl
    )


def test_obscore_position_index_is_the_generated_tables_one():
    from egernia_api.plugins import obscore

    # the default deployment keeps its pg_sphere index under its old name and
    # definition, so the relation's fingerprint does not change on upgrade
    assert obscore.position_index() == "obscore_spoint_gist"
    assert obscore.index_sql("obscore_spoint_gist") == (
        "CREATE INDEX obscore_spoint_gist ON ivoa.obscore"
        " USING gist (spoint(RADIANS(s_ra), RADIANS(s_dec)))"
    )


def test_obscore_position_index_under_skycell(skycell):
    from egernia_api.plugins import obscore

    # one definition (geometry.py), formatted for ivoa.obscore
    assert position_index_name("obscore") == "obscore_skycell_cell"
    assert position_index_definition("ivoa.obscore") == (
        "ON ivoa.obscore (skycell_ang2cell(s_ra, s_dec)) INCLUDE (s_ra, s_dec)"
    )
    # read when used, so it follows the setting rather than the import
    assert obscore.position_index() == "obscore_skycell_cell"
    assert obscore.index_sql("obscore_skycell_cell", obscore.BUILD, "_build") == (
        "CREATE INDEX obscore_skycell_cell_build ON ivoa.obscore_build"
        " (skycell_ang2cell(s_ra, s_dec)) INCLUDE (s_ra, s_dec)"
    )


def test_dataset_generator_writes_the_footprint_type_the_column_has():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "dataset"))
    from egernia_dataset import generate

    class Conn:
        def __init__(self, udt):
            self.udt = udt

        def execute(self, *_):
            return self

        def fetchone(self):
            return (self.udt,)

    data_products = dict(generate.LEVELS)["data_product"]
    assert generate._SPOLY_FOOTPRINT in data_products
    assert generate._levels(Conn("spoly")) == generate.LEVELS
    skycell_levels = dict(generate._levels(Conn("skyregion")))
    assert generate._SKYREGION_FOOTPRINT in skycell_levels["data_product"]
    assert generate._SPOLY_FOOTPRINT not in skycell_levels["data_product"]


def test_the_seeder_writes_the_footprint_type_the_column_has():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "dataset"))
    from egernia_dataset import seed

    class Conn:
        """Answers the column-type and resume-point lookups; records the rest."""

        def __init__(self):
            self.statements = []

        def execute(self, sql, *_):
            self.row = ("skyregion",) if "udt_name" in sql else (0,)
            return self

        def fetchone(self):
            return self.row

        def cursor(self):
            conn = self

            class Cursor:
                def __enter__(self):
                    return self

                def __exit__(self, *_):
                    return False

                def execute(self, sql, *_):
                    conn.statements.append(sql)

            return Cursor()

        def commit(self):
            pass

    conn = Conn()
    cfg = yaml.safe_load((seed.ROOT / "config" / "datasets.yaml").read_text())
    seed.grow_products_to(conn, cfg, seed.PRODUCTS_PER_PROJECT, 1)
    written = "\n".join(conn.statements)
    assert "skycell_circle(sky.ra, sky.dec" in written
    assert "circle_spoly" not in written


def test_a_footprint_column_of_the_other_backend_refuses_to_start(skycell):
    class Conn:
        def execute(self, sql, params):
            self.params = params
            return self

        def fetchone(self):
            # the column as a pg_sphere deployment created it
            return ("spoly",) if self.params[2] == "s_region_geom" else None

    tables = list(_skycell_tables().values())
    with pytest.raises(RuntimeError, match="is spoly, but TAP_GEOMETRY_BACKEND=skycell needs"):
        ingest.check_geometry_types(Conn(), tables)


def test_a_footprint_column_not_created_yet_is_left_to_the_ddl(skycell):
    class Conn:
        def execute(self, *_):
            return self

        def fetchone(self):
            return None

    ingest.check_geometry_types(Conn(), list(_skycell_tables().values()))  # no raise


# -- capabilities --------------------------------------------------------------


def test_capabilities_name_the_backend_and_its_extra_functions(client, skycell):
    body = client.get("/tap/capabilities").text
    assert "ADQL translated to PostgreSQL/skycell" in body
    for form in ("CENTROID", "COORD1", "COORD2"):
        assert f"<feature><form>{form}</form></feature>" in body


def test_capabilities_declare_the_user_functions(client, skycell):
    root = ET.fromstring(client.get("/tap/capabilities").text)
    (udfs,) = [
        lf
        for lf in root.iter("languageFeatures")
        if lf.get("type") == "ivo://ivoa.net/std/TAPRegExt#features-udf"
    ]
    forms = {f.findtext("form"): f.findtext("description") for f in udfs.findall("feature")}
    assert len(forms) == len(SKYCELL.user_functions)
    assert (
        "ivo_healpix_center(hpxOrder INTEGER, hpxIndex BIGINT) -> POINT" in forms
    )  # the arrow survives the XML
    assert all(forms.values())


def test_capabilities_under_pg_sphere_are_unchanged(client):
    body = client.get("/tap/capabilities").text
    assert "ADQL translated to PostgreSQL/pg_sphere" in body
    assert "<form>COORD1</form>" not in body
    assert "features-udf" not in body


# -- geometry support functions (pg_sphere) ------------------------------------


def test_db_init_creates_the_same_support_functions():
    """db/init and geometry.py hold one text, so a fresh database and the
    bootstrap's catch-up create the same functions."""
    from egernia_core.geometry import PGSPHERE

    init = (pathlib.Path(__file__).resolve().parents[2] / "db/init/01_extensions.sql").read_text()
    init = " ".join(init.split())
    for function in PGSPHERE.support_functions:
        definition = " ".join(function.definition.split())
        assert definition.replace("CREATE FUNCTION", "CREATE OR REPLACE FUNCTION", 1) in init


class _SupportConn:
    """A connection to a database with pg_sphere and none of its support
    functions, whose CREATE FUNCTION raises ``refuse`` (if given)."""

    def __init__(self, refuse=None, extension=True):
        self.refuse, self.extension, self.sql = refuse, extension, []

    def execute(self, sql, params=()):
        self.sql.append(sql)
        if sql.startswith("CREATE FUNCTION") and self.refuse is not None:
            raise self.refuse
        self.row = (1,) if "pg_extension" in sql and self.extension else None
        if "to_regprocedure" in sql:
            self.row = (None,)
        return self

    def fetchone(self):
        return self.row

    def transaction(self):
        return contextlib.nullcontext()


def test_support_functions_are_created_under_the_schema_lock():
    from egernia_core import bootstrap

    conn = _SupportConn()
    bootstrap.ensure_geometry_functions(conn)
    # the advisory lock the schema DDL takes, first: replicas do not race
    assert conn.sql[0] == "SELECT pg_advisory_xact_lock(%s)"
    assert sum(s.startswith("CREATE FUNCTION") for s in conn.sql) == 3


def test_a_refused_support_function_is_a_warning_not_a_failed_start(caplog):
    import psycopg
    from egernia_core import bootstrap

    conn = _SupportConn(refuse=psycopg.errors.InsufficientPrivilege("permission denied"))
    with caplog.at_level(logging.WARNING, logger="egernia_core"):
        bootstrap.ensure_geometry_functions(conn)  # no raise
    assert "spoint_to_array_deg(spoint)" in caplog.text
    assert "permission denied" in caplog.text


def test_no_support_functions_without_the_extension():
    from egernia_core import bootstrap

    assert bootstrap.missing_geometry_functions(_SupportConn(extension=False)) == []


def test_skycell_needs_no_support_functions(skycell):
    from egernia_core import bootstrap

    assert bootstrap.missing_geometry_functions(_SupportConn()) == []


def test_readiness_warns_about_missing_support_functions(monkeypatch, caplog):
    from egernia_core import bootstrap
    from egernia_core.geometry import PGSPHERE

    class Conn:
        def execute(self, *_):
            return self

    monkeypatch.setattr(
        bootstrap, "missing_geometry_functions", lambda conn: [PGSPHERE.support_functions[0]]
    )
    monkeypatch.setattr(ingest, "check_geometry_types", lambda conn, tables: None)
    with caplog.at_level(logging.WARNING, logger="egernia_core"):
        bootstrap.check_ready(Conn(), [])  # starts: a warning, as main behaves without them
    assert "spoint_to_array_deg(spoint) are missing" in caplog.text


def test_only_the_active_backends_types_are_geometries(monkeypatch):
    from egernia_api.queries import query as query_module

    class Conn:
        def execute(self, *_):
            return self

        def fetchall(self):
            return [("s", "t", "fp_spoly", "spoly"), ("s", "t", "fp_skyregion", "skyregion")]

    monkeypatch.setattr(query_module, "db_connection", lambda: contextlib.nullcontext(Conn()))
    query_module._column_is_geometry.cache_clear()
    try:
        assert query_module._column_is_geometry() == {
            "s.t.fp_spoly": True,
            "s.t.fp_skyregion": False,
        }
    finally:
        query_module._column_is_geometry.cache_clear()
