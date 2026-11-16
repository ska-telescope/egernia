"""The ADQL geometry backends (TAP_GEOMETRY_BACKEND), in one place.

ADQL geometry is translated for one PostgreSQL extension: pg_sphere
(``spoint``/``scircle``/``@``) or skycell (ADQL's own function names on
``skypos``/``skyregion``, indexed by a HEALPix cell B-tree; see
query/_adql/skycell.py). Everything else that differs between the two is
described here, and the modules that need it read it from the backend in
use: the footprint column's type and how it is derived from STC-S, the
position index, the PostgreSQL types that count as geometries, the ADQL
geometry functions the capabilities list, and the SQL functions the
translation relies on that the extension itself does not define. The ADQL
visitors are the one per-backend piece kept beside the translator
(query/adql.py, GEOMETRY_VISITORS), which checks it covers these.
"""

from collections.abc import Callable
from dataclasses import dataclass

from .metadata import regions


@dataclass(frozen=True)
class SupportFunction:
    """A SQL function a translation calls that its extension lacks."""

    signature: str  # for to_regprocedure, e.g. "spoint_to_array_deg(spoint)"
    definition: str  # CREATE FUNCTION ...


@dataclass(frozen=True)
class GeometryBackend:
    name: str  # the TAP_GEOMETRY_BACKEND value
    extension: str  # the PostgreSQL extension, as the capabilities name it
    # the s_region_geom companion: its type, and the STC-S -> literal derivation
    region_type: str
    derive_region: Callable[[str | None], str | None]
    # the cone-search index on (s_ra, s_dec): name suffix, definition after
    # ``ON <table>``, and the statistics target of its column (None: default)
    position_index_suffix: str
    position_index_definition: str
    position_index_statistics: int | None
    # PostgreSQL types that hold a geometry of this backend
    geometry_types: frozenset[str]
    # the ADQL geometry functions the translation supports (TAPRegExt forms)
    adql_geometry_forms: tuple[str, ...]
    support_functions: tuple[SupportFunction, ...] = ()


_ADQL_GEOMETRY = ("AREA", "BOX", "CIRCLE", "CONTAINS", "DISTANCE", "INTERSECTS", "POINT", "POLYGON")

PGSPHERE = GeometryBackend(
    name="pgsphere",
    extension="pg_sphere",
    region_type="spoly",
    derive_region=regions.stcs_to_spoly,
    # cone searches translate to spoint(RADIANS(s_ra), RADIANS(s_dec)) @
    # scircle(...), and only an index on that *expression* is considered
    position_index_suffix="spoint_gist",
    position_index_definition="USING gist (spoint(RADIANS(s_ra), RADIANS(s_dec)))",
    position_index_statistics=None,
    geometry_types=frozenset({"spoly", "spoint", "scircle", "sbox", "spath", "sline"}),
    # CENTROID/REGION/COORD1/COORD2/COORDSYS have no pg_sphere translations
    adql_geometry_forms=_ADQL_GEOMETRY,
    # a geometry in the select list is returned as a DALI array of doubles
    # in degrees; pg_sphere has no such conversion of its own
    support_functions=(
        SupportFunction(
            "spoint_to_array_deg(spoint)",
            "CREATE FUNCTION spoint_to_array_deg(p spoint) RETURNS double precision[]"
            " LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE"
            " AS $$ SELECT ARRAY[degrees(long(p)), degrees(lat(p))] $$",
        ),
        SupportFunction(
            "scircle_to_array_deg(scircle)",
            "CREATE FUNCTION scircle_to_array_deg(c scircle) RETURNS double precision[]"
            " LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE"
            " AS $$ SELECT ARRAY[degrees(long(center(c))), degrees(lat(center(c))),"
            " degrees(radius(c))] $$",
        ),
        SupportFunction(
            "spoly_to_array_deg(spoly)",
            "CREATE FUNCTION spoly_to_array_deg(p spoly) RETURNS double precision[]"
            " LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE"
            " AS $$ SELECT array_agg(v ORDER BY i, j) FROM generate_series(1, npoints(p)) AS i,"
            " LATERAL (VALUES (1, degrees(long(spoint(p, i)))),"
            " (2, degrees(lat(spoint(p, i))))) AS t(j, v) $$",
        ),
    ),
)

SKYCELL = GeometryBackend(
    name="skycell",
    extension="skycell",
    region_type="skyregion",
    derive_region=regions.stcs_to_skyregion,
    # a B-tree on the position's HEALPix cell, which skycell plans every ADQL
    # spelling of a cone or a cross-match through; its histogram is the
    # density map skycell's coverings are costed from, so it gets a finer
    # statistics target. It also holds the position (INCLUDE): skycell then
    # tests the cone on each index entry and reads from the table only the
    # rows inside it (skycell.index_filter, skycell 0.31); an earlier build
    # uses the index as before
    position_index_suffix="skycell_cell",
    position_index_definition="(skycell_ang2cell(s_ra, s_dec)) INCLUDE (s_ra, s_dec)",
    position_index_statistics=1000,
    geometry_types=frozenset({"skypos", "skyregion"}),
    # COORD1, COORD2 and CENTROID pass through to skycell's own functions
    adql_geometry_forms=tuple(sorted((*_ADQL_GEOMETRY, "CENTROID", "COORD1", "COORD2"))),
)

BACKENDS: dict[str, GeometryBackend] = {b.name: b for b in (PGSPHERE, SKYCELL)}
