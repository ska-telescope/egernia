"""ADQL geometry translated for skycell instead of pg_sphere.

skycell (https://github.com/jesusjuansalgado/skycell) is a PostgreSQL
extension whose geometry functions carry ADQL's own names and units, so the
translation is close to the identity:

- POINT, CIRCLE and POLYGON become ``skycell_point``, ``skycell_circle`` and
  ``skycell_polygon`` -- the prefixed aliases, because PostgreSQL's own
  ``point``/``circle``/``polygon`` would otherwise win the name lookup --
  with coordinates in degrees, as written;
- BOX becomes the polygon with corners at the centre plus and minus half the
  width in RA and half the height in Dec. Its edges are great circles, as
  ADQL 2.0 meant a BOX (a shortcut for a POLYGON, consistent with STC), where
  pg_sphere's ``sbox`` keeps its Dec edges at constant Dec; ADQL 2.1
  deprecates BOX for that ambiguity. So the backends agree only for small
  boxes: they differ in slivers along the Dec edges (a couple of arcseconds
  for a 1-degree box at Dec -70), and for a wide box by far more, as a great
  circle bows towards the pole (the top edge of a 120-degree-wide box from
  Dec 0 to 30 rises to Dec 49 at its middle). skycell's own ``box()`` reads
  the width as an angle on the sky instead, which opens out in RA by
  1/cos(dec);
- CONTAINS and INTERSECTS stay the ADQL functions, compared with 1 or 0 as
  the query compares them. skycell plans ``contains(...) = 1`` as its
  indexed operator, whichever argument is the column and whichever way
  round the query is written, so no operator choice is made here. One
  exception: skycell defines ``intersects(skypos, skyregion)`` but not the
  reverse, so an INTERSECTS whose second argument is a POINT constructor is
  written point first (ADQL's INTERSECTS is symmetric). As in the pg_sphere
  translation, a constructor is the only argument whose type is known here;
  a point-typed column (ADQL 2.1) keeps the order it was written in;
- DISTANCE becomes ``distance()``, in degrees, in both of its forms. Compared
  with a radius in a WHERE or JOIN ON it is planned as the same indexed cone;
- AREA becomes ``area()``, already in square degrees;
- COORD1, COORD2 and CENTROID pass through untranslated, as they do for
  pg_sphere -- but under skycell they name its own functions and work. A
  column they take is recorded as a geometry column, like one in CONTAINS or
  INTERSECTS, so a text column there is refused as a usage error before
  the query reaches the database.

The values are skycell's ``skypos``/``skyregion`` types, so a geometry column
(ADQL 2.1) is one of those, and a stored footprint is a ``skyregion`` (see
metadata/regions.py, ``stcs_to_skyregion``).

skycell's polygons must be convex; a non-convex ADQL POLYGON is an error in
the database rather than here.
"""

from queryparser.exceptions import QueryError

from .ADQLParser import ADQLParser
from .translator import (
    ADQLFunctionsTranslationVisitor,
    ADQLGeometryTranslationVisitor,
    _aliased,
    _convert_values,
    _is_point,
    _point_coords,
    _remove_children,
    _select_item,
)

# ADQL functions that reach skycell unchanged and take a geometry
_PASSTHROUGH_GEOMETRY_FUNCTIONS = frozenset({"COORD1", "COORD2", "CENTROID"})


def _bare_column(ctx):
    """The column reference ctx consists of, or None if it is anything else."""
    while ctx.getChildCount() == 1 and not isinstance(ctx, ADQLParser.Column_referenceContext):
        ctx = ctx.getChild(0)
    return ctx if isinstance(ctx, ADQLParser.Column_referenceContext) else None


def _bare_select_item(ctx):
    """The select-list item ctx is the whole expression of, or None."""
    while (
        ctx.parentCtx is not None
        and not isinstance(ctx.parentCtx, ADQLParser.Derived_columnContext)
        and ctx.parentCtx.getChildCount() == 1
    ):
        ctx = ctx.parentCtx
    parent = ctx.parentCtx
    return parent if isinstance(parent, ADQLParser.Derived_columnContext) else None


def _position(ra, dec):
    """``ra, dec`` of a position as skycell holds it (RA in [0, 360))."""
    point = f"skycell_point({ra}, {dec})"
    return f"coord1({point}), coord2({point})"


class SkycellGeometryTranslationVisitor(ADQLGeometryTranslationVisitor):
    """The geometry constructors, as skycell functions in degrees.

    In the select list a constructor is a DALI array of doubles in degrees,
    as the pg_sphere translation returns it (``spoint_to_array_deg`` and
    friends): ``[ra, dec]`` for a POINT, ``[ra, dec, radius]`` for a CIRCLE
    and ``[ra1, dec1, ...]`` for a POLYGON.
    """

    def __init__(self):
        super().__init__(conunits="")

    def visitPoint(self, ctx):
        ra, dec = _point_coords(ctx)
        ctx_text = f"skycell_point({ra}, {dec})"
        item = _select_item(ctx, 3)
        if item is not None:
            ctx_text = _aliased(f"ARRAY[{_position(ra, dec)}]", item, "adql_point")
        _remove_children(ctx)
        self.contexts[ctx] = ctx_text

    def visitBox(self, ctx):
        s = 4 if len(ctx.children) > 8 else 2
        pars = []
        for j in (s, s + 2, s + 4):
            pars.extend(self._convert_values(ctx, j))
        if len(pars) != 4:
            raise QueryError("BOX needs a centre, a width and a height")
        try:
            ra, dec, width, height = (float(p) for p in pars)
        except ValueError:
            # the pg_sphere translation takes numbers only, too
            raise QueryError("sbox values incorrect") from None
        ctx_text = f"skycell_polygon({_box_vertices(ra, dec, width, height)})"
        _remove_children(ctx)
        self.contexts[ctx] = ctx_text

    def visitCircle(self, ctx):
        s = 4 if isinstance(ctx.children[2], ADQLParser.Coord_sysContext) else 2
        radius = self._convert_values(ctx, s + 2)[0]
        circle_center = ctx.children[s]
        if isinstance(circle_center.children[0], ADQLParser.CoordinatesContext):
            ra, dec = self._convert_values(circle_center, 0)[:2]
        elif isinstance(circle_center.children[0].children[0], ADQLParser.Column_referenceContext):
            # ADQL 2.1: a POINT-typed (skypos) column as the circle centre.
            column = circle_center.children[0].getText()
            self.geometry_columns.add(column)
            ra, dec = f"coord1({column})", f"coord2({column})"
        else:
            point_ctx = circle_center.children[0].children[0].children[0]
            if not isinstance(point_ctx, ADQLParser.PointContext):
                raise QueryError(
                    "In the current implementation, circle allows only explicitly"
                    " defined point or a point column as the circle center. For"
                    " instance, CIRCLE(POINT(t.ra, t.dec), 0.1)"
                )
            ra, dec = _point_coords(point_ctx)
        ctx_text = f"skycell_circle({ra}, {dec}, {radius})"
        item = _select_item(ctx, 3)
        if item is not None:
            ctx_text = _aliased(f"ARRAY[{_position(ra, dec)}, {radius}]", item, "circle")
        _remove_children(ctx)
        self.contexts[ctx] = ctx_text

    def visitPolygon(self, ctx):
        coords = []
        for j in range(2, len(ctx.children), 2):
            par = self._convert_values(ctx, j)
            # only coordinate pairs (ctx.children[2] can be the deprecated
            # coordinate system)
            if len(par) > 1:
                coords.extend(par[:2])
        ctx_text = f"skycell_polygon({', '.join(str(c) for c in coords)})"
        item = _select_item(ctx, 3)
        if item is not None:
            vertices = ", ".join(
                _position(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)
            )
            ctx_text = _aliased(f"ARRAY[{vertices}]", item, "adql_polygon")
        _remove_children(ctx)
        self.contexts[ctx] = ctx_text


def _box_vertices(ra, dec, width, height):
    """The skycell_polygon arguments for a BOX: its corners, joined by great
    circles (see the module docstring for how that differs from pg_sphere).

    RA is normalised into [0, 360) and Dec clamped to [-90, 90], so a box
    reaching past a pole means the cap of the RA range above (or below) its
    other edge -- the two corners that would both sit on the pole become the
    pole itself, which skycell needs (it refuses a repeated vertex). A box
    with no area, as wide as 180 degrees or more, or reaching past both
    poles (two corners left, which is no polygon) is refused.
    """
    if width <= 0 or height <= 0:
        raise QueryError("BOX needs a positive width and height")
    if width >= 180:
        raise QueryError(
            "BOX must be narrower than 180 degrees in RA under the skycell backend:"
            " a wider coordinate range is not a convex polygon"
        )
    lo_ra, hi_ra = (ra - width / 2) % 360, (ra + width / 2) % 360
    lo_dec, hi_dec = max(dec - height / 2, -90.0), min(dec + height / 2, 90.0)
    if lo_dec >= hi_dec:
        raise QueryError("BOX has no area: its Dec range lies beyond a pole")
    if lo_dec == -90.0 and hi_dec == 90.0:
        raise QueryError("BOX reaching past both poles is not a polygon under the skycell backend")
    corners = [(lo_ra, lo_dec), (hi_ra, lo_dec), (hi_ra, hi_dec), (lo_ra, hi_dec)]
    if hi_dec == 90.0:
        corners[2:] = [(ra % 360, 90.0)]
    if lo_dec == -90.0:
        corners[:2] = [(ra % 360, -90.0)]
    return ", ".join(f"{a:.12f}, {d:.12f}" for a, d in corners)


class SkycellFunctionsTranslationVisitor(ADQLFunctionsTranslationVisitor):
    """The geometry functions and predicates, as skycell's ADQL-named ones."""

    def __init__(self, contexts):
        super().__init__(contexts, conunits="")

    def _lower_distance(self, ctx):
        # The pg_sphere translation rewrites `DISTANCE(p, q) < r` into the
        # `@ scircle` containment its GiST index serves. skycell plans the
        # comparison itself as the indexed cone (see the module docstring),
        # and scircle is pg_sphere's: the comparison stays as written.
        return None

    def visitArea(self, ctx):
        arg = self._geometry_argument(ctx.children[2])
        ctx_text = _aliased(f"area({arg})", _select_item(ctx, 9), "adql_area")
        _remove_children(ctx)
        self.contexts[ctx] = ctx_text

    def _predicate(self, ctx, name):
        """``name(a, b) = 1`` or ``= 0``, from either side of the comparison."""
        left = ctx.children[0].getText()
        right = ctx.children[2].getText()
        if left in ("0", "1"):
            function, value, reverse = ctx.children[2], left, False
        elif right in ("0", "1"):
            function, value, reverse = ctx.children[0], right, True
        else:
            raise QueryError(f"The function {name.upper()} allows comparison to 1 or 0 only.")
        self._function(function, name)
        ctx_text = f"{self.contexts[function]} = {value}"
        _remove_children(ctx, reverse=reverse)
        self.contexts[ctx] = ctx_text

    def _function(self, ctx, name):
        left = self._geometry_argument(ctx.children[2])
        right = self._geometry_argument(ctx.children[4])
        if (
            name == "intersects"
            and _is_point(right, "skycell_point")
            and not _is_point(left, "skycell_point")
        ):
            left, right = right, left
        _remove_children(ctx)
        self.contexts[ctx] = f"{name}({left}, {right})"

    def visitContains_predicate(self, ctx):
        self._predicate(ctx, "contains")

    def visitContains(self, ctx):
        self._function(ctx, "contains")

    def visitIntersects_predicate(self, ctx):
        self._predicate(ctx, "intersects")

    def visitIntersects(self, ctx):
        self._function(ctx, "intersects")

    def visitUser_defined_function(self, ctx):
        # COORD1/COORD2/CENTROID parse as user-defined functions; their
        # column argument is a geometry column all the same
        name = ctx.getChild(0).getText().upper()
        params = ctx.getTypedRuleContexts(ADQLParser.User_defined_function_paramContext)
        if name in _PASSTHROUGH_GEOMETRY_FUNCTIONS:
            for param in params:
                column = _bare_column(param)
                if column is not None:
                    self.geometry_columns.add(column.getText())
        result = self.visitChildren(ctx)
        # a CENTROID that is a select item is a POINT there: [ra, dec]
        if name == "CENTROID" and len(params) == 1 and _bare_select_item(ctx) is not None:
            argument = self._sql_of(params[0])
            if argument is not None:
                centre = f"centroid({argument})"
                text = _aliased(
                    f"ARRAY[coord1({centre}), coord2({centre})]",
                    _bare_select_item(ctx),
                    "centroid",
                )
                # printed through the one token left, the function's "(": a
                # token of the name would be glued to the next one
                ctx.children = [ctx.getChild(1)]
                self.contexts[ctx] = text
        return result

    def _sql_of(self, ctx):
        """The SQL for an argument that is a column or a translated
        constructor, or None for anything else."""
        while True:
            if ctx in self.contexts:
                return self.contexts[ctx]
            if isinstance(ctx, ADQLParser.Column_referenceContext):
                return ctx.getText()
            if ctx.getChildCount() != 1:
                return None
            ctx = ctx.getChild(0)

    def visitDistance(self, ctx):
        if isinstance(ctx.children[2], ADQLParser.Coord_valueContext):
            args = (
                self._point_argument(ctx.children[2]),
                self._point_argument(ctx.children[4]),
            )
        else:
            args = tuple(_convert_values(ctx, i)[0] for i in (2, 4, 6, 8))
        ctx_text = f"distance({', '.join(str(a) for a in args)})"
        ctx_text = _aliased(ctx_text, _select_item(ctx, 9), "distance")
        for _ in range(ctx.getChildCount() - 1):
            ctx.removeLastChild()
        self.contexts[ctx] = ctx_text
