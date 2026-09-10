"""ObsCore 1.1 (`ivoa.obscore`) over the ODP metadata.

The SRCNet ODP model is ObsCore-derived, so compliance is a *projection*:
`srcnet.data_products` already carries most of the mandatory columns under
their exact ObsCore names, `srcnet.observations` has the collection and
provenance names, and `srcnet.artifacts` the access columns. That projection
used to be a view, and the join it carried was what a scan-heavy ADQL query
paid: a GROUP BY over the collection hashed observations against every
product, and a result that read ``access_url`` probed artifacts once per
row. So the projection is materialised — ``ivoa.obscore`` is a real table
with exactly the projection's columns, built once at bootstrap from the ODP
tables and kept current by statement-level triggers on them (see
``trigger_sql``), in the same transaction as the write. A row is visible on
``ivoa.obscore`` the moment its notification's ingest commits; there is no
refresh and no lag. The table is created by the odp plugin's bootstrap
(`MetadataPlugin.post_ensure`), so it exists exactly when its source tables
do, and rebuilt when its definition changes (see ``ensure_obscore``).

Column metadata is transcribed from REC-ObsCore-v1.1-20170509 Table 6 (the
TAP_SCHEMA values for the mandatory fields); utypes carry the ``obscore:``
prefix the table's caption says it omits. One non-standard column rides
along: ``s_region_geom``, the pgsphere footprint the ingest pipeline
derives from ``s_region``, registered with ``std = 0`` so ADQL
``INTERSECTS``/``CONTAINS`` work on the table too.

Mapping decisions (each visible in the SQL below):

- ``dataproduct_type = 'table'`` is in the srcnet CHECK but not the ObsCore
  vocabulary; it maps to ``'measurements'``.
- ``obs_collection`` honours the REC's NOT NULL with
  ``COALESCE(collection, 'unclassified')``.
- ``obs_publisher_did`` is a configurable prefix (``TAP_OBSCORE_DID_PREFIX``)
  plus the primary-key chain — a DID must be permanent, so its shape is the
  hierarchy's identity and nothing derived — with each key component
  percent-encoded (see ``_did_component``). It is the table's unique key and
  carries a pg_trgm index, so a lookup by DID — equality, a prefix, or a
  ``LIKE '%<project>/%'`` — is an index scan.
- ``calib_level`` is passed through untranslated; srcnet's declared meaning
  and ObsCore 1.1's disagree at level 1 (see ``docs/obscore.md``).
- ``access_*`` come from one representative science artifact per product:
  the first by ``artifact_id``; a NULL ``access_url`` is spec-legal.
- ``access_estsize`` converts the model's bytes to the REC's kbyte.
- ``s_resolution`` is the synthesized beam size (already arcseconds).
- ``t_resolution`` and ``em_res_power`` are NULL: the model does not carry
  them, and NULL is permitted.
"""

import hashlib
import logging
import re
from typing import NamedTuple

from egernia_core.config import settings

log = logging.getLogger("tap-api")


class ObsCoreColumn(NamedTuple):
    """One ivoa.obscore column: its TAP_SCHEMA registration and the view
    expression that produces it, in REC Table 6 order.

    arraysize is derived rather than stored — VOTable wants "*" for char
    and nothing for the fixed-width types, which held for all 31 columns when
    they were spelled out. Everything ObsCore makes near-universal
    (``principal``, ``std``) defaults to the standard value, so only the one
    non-standard column has to say otherwise.
    """

    name: str
    datatype: str  # the VOTable name TAP_SCHEMA uses
    ucd: str
    utype: str | None
    description: str
    expression: str | None  # None: the publisher DID, built by view_sql()
    unit: str | None = None
    xtype: str | None = None
    principal: int = 1
    std: int = 1

    @property
    def arraysize(self) -> str | None:
        return "*" if self.datatype == "char" else None


OBSCORE_COLUMNS: list[ObsCoreColumn] = [
    ObsCoreColumn(
        "dataproduct_type",
        "char",
        # meta.code.class, not meta.id: changed by ObsCore 1.1 Erratum 1
        "meta.code.class",
        "obscore:ObsDataset.dataProductType",
        "Data product (file content) primary type",
        "CASE p.dataproduct_type WHEN 'table' THEN 'measurements' ELSE p.dataproduct_type END",
    ),
    # ObsCore 1.1 Table 6 reads calib_level as 0=raw, 1=instrumental,
    # 2=calibrated, 3=derived; srcnet declares 0=raw, 1=calibrated,
    # 2=science-ready, 3=analysis (docs/model-schemas.md), and the view hands
    # the value over unchanged. Relabelling real calibration levels is a
    # data-model decision, not a view one, so the description states what the
    # column holds rather than what ObsCore would like it to hold;
    # docs/obscore.md records the discrepancy.
    ObsCoreColumn(
        "calib_level",
        "int",
        "meta.code;obs.calib",
        "obscore:ObsDataset.calibLevel",
        "Calibration level as declared by the SRCNet producer, passed through"
        " untranslated (srcnet: 0=raw, 1=calibrated, 2=science-ready, 3=analysis)",
        "p.calib_level::integer",
    ),
    ObsCoreColumn(
        "obs_collection",
        "char",
        "meta.id",
        "obscore:DataID.collection",
        "Name of the data collection",
        "COALESCE(o.collection, 'unclassified')",
    ),
    ObsCoreColumn(
        "obs_id",
        "char",
        "meta.id",
        "obscore:DataID.observationID",
        "Internal ID given by the ObsTAP service",
        "p.obs_id",
    ),
    ObsCoreColumn(
        "obs_publisher_did",
        "char",
        # meta.ref.ivoid, not meta.ref.uri;meta.curation: ObsCore 1.1 Erratum
        "meta.ref.ivoid",
        "obscore:Curation.publisherDID",
        "ID for the Dataset given by the publisher",
        None,
    ),
    ObsCoreColumn(
        "access_url",
        "char",
        "meta.ref.url",
        "obscore:Access.reference",
        "URL used to access the dataset",
        "a.access_url",
    ),
    ObsCoreColumn(
        "access_format",
        "char",
        "meta.code.mime",
        "obscore:Access.format",
        "Content format of the dataset",
        "a.access_format",
    ),
    ObsCoreColumn(
        "access_estsize",
        "long",
        "phys.size;meta.file",
        "obscore:Access.size",
        "Estimated size of the dataset in kilobytes",
        "round(a.access_estsize / 1000.0)::bigint",
        unit="kbyte",
    ),
    ObsCoreColumn(
        "target_name",
        "char",
        "meta.id;src",
        "obscore:Target.name",
        "Object of interest",
        "p.target_name",
    ),
    ObsCoreColumn(
        "s_ra",
        "double",
        "pos.eq.ra",
        "obscore:Char.SpatialAxis.Coverage.Location.Coord.Position2D.Value2.C1",
        "Central spatial position in ICRS: right ascension",
        "p.s_ra",
        unit="deg",
    ),
    ObsCoreColumn(
        "s_dec",
        "double",
        "pos.eq.dec",
        "obscore:Char.SpatialAxis.Coverage.Location.Coord.Position2D.Value2.C2",
        "Central spatial position in ICRS: declination",
        "p.s_dec",
        unit="deg",
    ),
    ObsCoreColumn(
        "s_fov",
        "double",
        "phys.angSize;instr.fov",
        "obscore:Char.SpatialAxis.Coverage.Bounds.Extent.diameter",
        "Estimated size of the covered region (diameter)",
        "p.s_fov",
        unit="deg",
    ),
    ObsCoreColumn(
        "s_region",
        "char",
        "pos.outline;obs.field",
        "obscore:Char.SpatialAxis.Coverage.Support.Area",
        "Sky region covered by the data product (STC-S)",
        "p.s_region",
        xtype="adql:REGION",
    ),
    ObsCoreColumn(
        "s_resolution",
        "double",
        "pos.angResolution",
        "obscore:Char.SpatialAxis.Resolution.Refval.value",
        "Spatial resolution of the data (FWHM)",
        "p.beam_size",
        unit="arcsec",
    ),
    ObsCoreColumn(
        "s_xel1",
        "long",
        "meta.number",
        "obscore:Char.SpatialAxis.numBins1",
        "Number of elements along the first coordinate of the spatial axis",
        "p.s_xel1",
    ),
    ObsCoreColumn(
        "s_xel2",
        "long",
        "meta.number",
        "obscore:Char.SpatialAxis.numBins2",
        "Number of elements along the second coordinate of the spatial axis",
        "p.s_xel2",
    ),
    ObsCoreColumn(
        "t_min",
        "double",
        "time.start;obs.exposure",
        "obscore:Char.TimeAxis.Coverage.Bounds.Limits.StartTime",
        "Start time in MJD",
        "p.t_min",
        unit="d",
    ),
    ObsCoreColumn(
        "t_max",
        "double",
        "time.end;obs.exposure",
        "obscore:Char.TimeAxis.Coverage.Bounds.Limits.StopTime",
        "Stop time in MJD",
        "p.t_max",
        unit="d",
    ),
    ObsCoreColumn(
        "t_exptime",
        "double",
        "time.duration;obs.exposure",
        "obscore:Char.TimeAxis.Coverage.Support.Extent",
        "Total exposure time",
        "p.t_exptime",
        unit="s",
    ),
    ObsCoreColumn(
        "t_resolution",
        "double",
        "time.resolution",
        "obscore:Char.TimeAxis.Resolution.Refval.value",
        "Temporal resolution (FWHM)",
        "NULL::double precision",
        unit="s",
    ),
    ObsCoreColumn(
        "t_xel",
        "long",
        "meta.number",
        "obscore:Char.TimeAxis.numBins",
        "Number of elements along the time axis",
        "p.t_xel",
    ),
    ObsCoreColumn(
        "em_min",
        "double",
        "em.wl;stat.min",
        "obscore:Char.SpectralAxis.Coverage.Bounds.Limits.LoLimit",
        "Start in spectral coordinates (vacuum wavelength)",
        "p.em_min",
        unit="m",
    ),
    ObsCoreColumn(
        "em_max",
        "double",
        "em.wl;stat.max",
        "obscore:Char.SpectralAxis.Coverage.Bounds.Limits.HiLimit",
        "Stop in spectral coordinates (vacuum wavelength)",
        "p.em_max",
        unit="m",
    ),
    ObsCoreColumn(
        "em_res_power",
        "double",
        "spect.resolution",
        "obscore:Char.SpectralAxis.Resolution.ResolPower.refVal",
        "Spectral resolving power",
        "NULL::double precision",
    ),
    ObsCoreColumn(
        "em_xel",
        "long",
        "meta.number",
        "obscore:Char.SpectralAxis.numBins",
        "Number of elements along the spectral axis",
        "p.em_xel",
    ),
    ObsCoreColumn(
        "o_ucd",
        "char",
        "meta.ucd",
        "obscore:Char.ObservableAxis.ucd",
        "Nature of the observable axis",
        "p.o_ucd",
    ),
    ObsCoreColumn(
        "pol_states",
        "char",
        "meta.code;phys.polarization",
        "obscore:Char.PolarizationAxis.stateList",
        "List of polarization states or NULL if not applicable",
        "p.pol_states",
    ),
    ObsCoreColumn(
        "pol_xel",
        "long",
        "meta.number",
        "obscore:Char.PolarizationAxis.numBins",
        "Number of polarization samples",
        "p.pol_xel",
    ),
    ObsCoreColumn(
        "facility_name",
        "char",
        "meta.id;instr.tel",
        "obscore:Provenance.ObsConfig.Facility.name",
        "Name of the facility used for this observation",
        "o.facility_name",
    ),
    ObsCoreColumn(
        "instrument_name",
        "char",
        "meta.id;instr",
        "obscore:Provenance.ObsConfig.Instrument.name",
        "Name of the instrument used for this observation",
        "o.instrument_name",
    ),
    # Non-standard companion: the pgsphere footprint derived from s_region.
    # std = 0 says it plainly; it exists so INTERSECTS/CONTAINS work directly
    # on the view.
    ObsCoreColumn(
        "s_region_geom",
        "char",
        "pos.outline;obs.field",
        None,
        "pgsphere footprint derived from s_region at ingestion (non-standard);"
        " query it with INTERSECTS/CONTAINS",
        "p.s_region_geom",
        principal=0,
        std=0,
    ),
]

# doubles as the obscore table's utype in TAP_SCHEMA
DATAMODEL_IVOID = "ivo://ivoa.net/std/ObsCore#core-1.1"

TABLE = "ivoa.obscore"
# built beside the live relation, swapped in by rename once complete
BUILD = "ivoa.obscore_build"
COMMENT_PREFIX = "ObsCore 1.1 over the ODP metadata"

# A PublisherDID lands inside a SQL string literal in the table definition,
# so its alphabet is closed: IVOA identifier characters only, quotes and
# whitespace impossible by construction.
_DID_PREFIX_RE = re.compile(r"^[A-Za-z0-9:/~?._#+-]+$")


def did_prefix() -> str:
    prefix = settings.obscore_did_prefix
    if not _DID_PREFIX_RE.match(prefix):
        raise ValueError(
            f"TAP_OBSCORE_DID_PREFIX {prefix!r} contains characters outside"
            " the IVOA identifier alphabet"
        )
    return prefix


# The DID path is built from five free-``text`` primary-key columns. RFC 3986
# unreserved is the safe core of the IVOA identifier alphabet; anything else
# in a key would either forge a path segment ('/'), truncate the identifier
# ('#', '?'), or make it unparseable (a space, a stray '%') — and a
# PublisherDID is a permanent promise, so an ambiguous one cannot be taken
# back later. Encoding every other character also makes the DID injective
# over the key chain, which is what lets it be the table's unique key.
DID_SAFE_CLASS = "A-Za-z0-9._~-"

# A configured column name is interpolated into DDL, where no parameter can
# be bound, so the alphabet is closed to plain lower-case SQL identifiers.
# Anything else — a quote, a space, a parenthesis — is refused first.
_DID_COLUMN_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


def did_key_columns() -> tuple[str, ...]:
    """The data_products columns whose values form the DID path, in order.

    Configured (``TAP_OBSCORE_DID_COLUMNS``, dot-separated) because a
    deployment whose ODP model nests differently has a different identity
    chain. Two things are the operator's to get right: the chain has to
    identify a data product *uniquely* — the table's unique key is the DID,
    so a chain that does not fails the bootstrap's backfill with a duplicate
    key rather than publishing two products under one identifier — and
    changing it changes every DID this service has ever published, which a
    permanent identifier is not supposed to do.

    A column that does not exist on srcnet.data_products fails at bootstrap,
    where PostgreSQL names it.
    """
    raw = settings.obscore_did_columns
    columns = tuple(part.strip() for part in raw.split(".") if part.strip())
    if not columns:
        raise ValueError("TAP_OBSCORE_DID_COLUMNS is empty; a DID needs at least one column")
    for column in columns:
        if not _DID_COLUMN_RE.match(column):
            raise ValueError(
                f"TAP_OBSCORE_DID_COLUMNS component {column!r} is not a plain SQL"
                " identifier (lower-case letters, digits and underscores)"
            )
    return columns


# The percent-encoder is a function rather than an inline subquery: inline,
# a correlated SubPlan was parallel-restricted and unindexable, and the
# planner had no statistics for it. As a function the expression is a plain
# call, and never evaluated for the common row at all (see ``_did_component``).
DID_ENCODE_FUNCTION = "ivoa.did_encode"


def did_encode_sql() -> str:
    """DDL for the percent-encoder of one DID component.

    ``regexp_replace`` cannot compute a per-match replacement, so the
    encoding is a fold over the characters: unreserved ones survive,
    everything else becomes ``%XX`` per UTF-8 byte (upper-case hex, as RFC
    3986 recommends). ``convert_to``, ``encode`` and the ``regexp_*``
    functions are all IMMUTABLE and PARALLEL SAFE, so the function is too.
    STRICT: a NULL component is a NULL DID, as ``||`` would make it anyway.
    """
    return (
        f"CREATE OR REPLACE FUNCTION {DID_ENCODE_FUNCTION}(component text) RETURNS text\n"
        "LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT\n"
        "RETURN (SELECT string_agg("
        f"CASE WHEN ch ~ '^[{DID_SAFE_CLASS}]$' THEN ch"
        " ELSE regexp_replace(upper(encode(convert_to(ch, 'UTF8'), 'hex')),"
        " '(..)', '%\\1', 'g') END, '' ORDER BY n)"
        " FROM regexp_split_to_table(component, '') WITH ORDINALITY AS c(ch, n))"
    )


def _did_component(column: str) -> str:
    """SQL for one percent-encoded component of the DID path.

    The guard in front is not decoration: the encoder splits the string
    into one row per character. Real identifiers are already clean, so the
    common row pays one anchored regexp match and never calls the function.
    """
    return (
        f"CASE WHEN {column} ~ '^[{DID_SAFE_CLASS}]*$' THEN {column}"
        f" ELSE {DID_ENCODE_FUNCTION}({column}) END"
    )


def did_sql(alias: str = "") -> str:
    """The obs_publisher_did expression over the data_products key columns,
    qualified with ``alias`` when given. One builder for the backfill and
    the triggers, so every row's DID is computed by the same text."""
    prefix = f"{alias}." if alias else ""
    return f"'{did_prefix()}' || " + " || '/' || ".join(
        _did_component(f"{prefix}{column}") for column in did_key_columns()
    )


# The first science artifact by id, as an aggregate: the rows are the same
# as ``ORDER BY artifact_id LIMIT 1``, and an aggregate without GROUP BY is
# provably one row, so a LEFT JOIN to it is one the planner can drop.
ACCESS_JOIN = (
    "LEFT JOIN LATERAL (\n"
    "    SELECT (array_agg(art.access_url ORDER BY art.artifact_id))[1] AS access_url,\n"
    "           (array_agg(art.access_format ORDER BY art.artifact_id))[1] AS access_format,\n"
    "           (array_agg(art.access_estsize ORDER BY art.artifact_id))[1] AS access_estsize\n"
    "    FROM srcnet.artifacts AS art\n"
    "    WHERE art.project_id = p.project_id AND art.obs_id = p.obs_id\n"
    "      AND art.sbd_id = p.sbd_id AND art.eb_id = p.eb_id\n"
    "      AND art.product_id = p.product_id AND art.semantics = 'science'\n"
    ") AS a ON true"
)

PRODUCT_KEY = "project_id, obs_id, sbd_id, eb_id, product_id"


def _expression(column: ObsCoreColumn) -> str:
    return column.expression if column.expression is not None else did_sql("p")


def select_sql(products: str = "srcnet.data_products") -> str:
    """The ObsCore rows of ``products`` — the data_products table, or a
    trigger's transition table of just-written data_products rows — in REC
    Table 6 column order. One text for the backfill and the triggers: the
    relation holds what this select yields, and nothing else ever writes it.
    """
    selects = ",\n    ".join(f"{_expression(c)} AS {c.name}" for c in OBSCORE_COLUMNS)
    return (
        f"SELECT\n    {selects}\n"
        f"FROM {products} AS p\n"
        "JOIN srcnet.observations AS o\n"
        "  ON o.project_id = p.project_id AND o.obs_id = p.obs_id\n"
        f"{ACCESS_JOIN}"
    )


# Indexes on the relation, by name. The DID is the unique key (the upsert
# target) and gets a trigram index too, so equality, a prefix and a component
# in the middle (``LIKE '%<project>/%'``) are all index scans; the rest are
# the ObsCore filter columns any client narrows by, and the two GiST indexes
# the ADQL geometry functions translate to (``spoint(RADIANS(s_ra),
# RADIANS(s_dec))`` is the exact expression a cone search becomes, and only an
# index on that expression is considered).
INDEXES: dict[str, str] = {
    "obscore_did_key": "UNIQUE INDEX {name} ON {table} (obs_publisher_did)",
    "obscore_did_trgm": "INDEX {name} ON {table} USING gin (obs_publisher_did gin_trgm_ops)",
    "obscore_collection_idx": "INDEX {name} ON {table} (obs_collection)",
    "obscore_type_calib_idx": "INDEX {name} ON {table} (dataproduct_type, calib_level)",
    "obscore_calib_idx": "INDEX {name} ON {table} (calib_level)",
    "obscore_time_idx": "INDEX {name} ON {table} (t_min, t_max)",
    "obscore_target_idx": "INDEX {name} ON {table} (target_name)",
    "obscore_spoint_gist": (
        "INDEX {name} ON {table} USING gist (spoint(RADIANS(s_ra), RADIANS(s_dec)))"
    ),
    "obscore_s_region_geom_gist": "INDEX {name} ON {table} USING gist (s_region_geom)",
}
# needs pg_trgm, which a role that cannot CREATE EXTENSION may not have
TRGM_INDEX = "obscore_did_trgm"
# the leading column of each index, for TAP_SCHEMA's ``indexed`` flag
INDEXED_COLUMNS = frozenset(
    {"obs_publisher_did", "obs_collection", "dataproduct_type", "calib_level", "t_min",
     "target_name", "s_ra", "s_dec", "s_region_geom"}
)  # fmt: skip


def index_sql(name: str, table: str = TABLE, suffix: str = "") -> str:
    return "CREATE " + INDEXES[name].format(name=f"{name}{suffix}", table=table)


def _set_clause(columns) -> str:
    return ", ".join(
        f"{c.name} = EXCLUDED.{c.name}" for c in columns if c.name != "obs_publisher_did"
    )


def _observation_columns() -> list[ObsCoreColumn]:
    return [c for c in OBSCORE_COLUMNS if c.expression and re.search(r"\bo\.", c.expression)]


def _access_columns() -> list[ObsCoreColumn]:
    return [c for c in OBSCORE_COLUMNS if c.expression and re.search(r"\ba\.", c.expression)]


def trigger_sql() -> list[str]:
    """The functions and statement-level triggers that keep the relation
    current, in the transaction that changes the source rows.

    Statement-level with transition tables rather than row-level: one
    ``INSERT ... SELECT`` per statement, so the JSON API's ``executemany``
    and the dataset seeder's bulk loads pay one join per batch, not one per
    row. Every path the ODP tables change by is covered without any code in
    the ingest module knowing: a document upsert (INSERT and UPDATE on
    data_products; artifacts arrive after their product, so the access
    columns are filled by the artifacts trigger), an amendment (UPDATE on any
    of the three), a document deletion (the FK cascade's DELETEs), and the
    seeder's generated INSERTs. The transition tables are named the same in
    every trigger so one function serves the three events.
    """
    did = did_sql("p")
    key_tuple = f"({PRODUCT_KEY})"
    upsert = (
        f"INSERT INTO {TABLE}\n{select_sql('new_rows')}\n"
        f"ON CONFLICT (obs_publisher_did) DO UPDATE SET {_set_clause(OBSCORE_COLUMNS)}"
    )
    products_fn = f"""CREATE OR REPLACE FUNCTION ivoa.obscore_data_products_changed()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- one statement per branch: a transition table only exists for the
    -- events that declare it, and a statement naming an absent one fails
    -- to parse even on a branch that is not taken
    IF TG_OP = 'DELETE' THEN
        DELETE FROM {TABLE} WHERE obs_publisher_did IN (SELECT {did} FROM old_rows AS p);
    ELSIF TG_OP = 'UPDATE' THEN
        -- re-keyed rows leave their old DID behind
        DELETE FROM {TABLE} WHERE obs_publisher_did IN (SELECT {did} FROM old_rows AS p)
            AND obs_publisher_did NOT IN (SELECT {did} FROM new_rows AS p);
    END IF;
    IF TG_OP <> 'DELETE' THEN
        {upsert.replace(chr(10), chr(10) + "        ")};
    END IF;
    RETURN NULL;
END $$"""
    access_set = ", ".join(f"{c.name} = {c.expression}" for c in _access_columns())

    def access_update(keys: str) -> str:
        return (
            f"UPDATE {TABLE} AS r SET {access_set}\n"
            f"        FROM srcnet.data_products AS p\n"
            f"        {ACCESS_JOIN.replace(chr(10), chr(10) + '        ')}\n"
            f"        WHERE {key_tuple.replace('(', '(p.').replace(', ', ', p.')} IN ({keys})\n"
            f"          AND r.obs_publisher_did = {did}"
        )

    new_keys = f"SELECT {PRODUCT_KEY} FROM new_rows"
    old_keys = f"SELECT {PRODUCT_KEY} FROM old_rows"
    artifacts_fn = f"""CREATE OR REPLACE FUNCTION ivoa.obscore_artifacts_changed()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- recompute the access columns of every product whose artifacts changed;
    -- a product deleted in the same cascade simply matches nothing
    IF TG_OP = 'INSERT' THEN
        {access_update(new_keys)};
    ELSIF TG_OP = 'DELETE' THEN
        {access_update(old_keys)};
    ELSE
        {access_update(f"{new_keys} UNION {old_keys}")};
    END IF;
    RETURN NULL;
END $$"""
    obs_columns = _observation_columns()
    obs_set = ", ".join(f"{c.name} = {c.expression}" for c in obs_columns)
    sources = sorted({m for c in obs_columns for m in re.findall(r"\bo\.(\w+)", c.expression)})
    new_values = ", ".join(f"o.{s}" for s in sources)
    old_values = ", ".join(f"oo.{s}" for s in sources)
    observations_fn = f"""CREATE OR REPLACE FUNCTION ivoa.obscore_observations_changed()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- a re-posted document updates every observation it carries; only one
    -- whose published columns actually moved touches its products
    UPDATE {TABLE} AS r SET {obs_set}
        FROM new_rows AS o
        JOIN old_rows AS oo ON oo.project_id = o.project_id AND oo.obs_id = o.obs_id
        JOIN srcnet.data_products AS p ON p.project_id = o.project_id AND p.obs_id = o.obs_id
        WHERE ({new_values}) IS DISTINCT FROM ({old_values})
          AND r.obs_publisher_did = {did};
    RETURN NULL;
END $$"""
    trigger = (
        "CREATE OR REPLACE TRIGGER obscore_sync_{event} AFTER {event} ON srcnet.{table}"
        " REFERENCING {tables} FOR EACH STATEMENT EXECUTE FUNCTION ivoa.obscore_{table}_changed()"
    )
    tables = {
        "insert": "NEW TABLE AS new_rows",
        "update": "OLD TABLE AS old_rows NEW TABLE AS new_rows",
        "delete": "OLD TABLE AS old_rows",
    }
    return [
        products_fn,
        artifacts_fn,
        observations_fn,
        *(
            trigger.format(event=e, table="data_products", tables=tables[e])
            for e in ("insert", "update", "delete")
        ),
        *(
            trigger.format(event=e, table="artifacts", tables=tables[e])
            for e in ("insert", "update", "delete")
        ),
        trigger.format(event="update", table="observations", tables=tables["update"]),
    ]


def definition_comment() -> str:
    """The relation's comment, carrying a fingerprint of everything that
    produces its rows: the select, the encoder, the triggers and the indexes.
    A comment is read without a relation lock, so a restart that changed
    nothing issues no DDL at all; a changed fingerprint rebuilds the relation
    from scratch, and marks it as this service's to rebuild."""
    definition = "\n".join(
        (select_sql(), did_encode_sql(), *trigger_sql(), *(index_sql(n) for n in INDEXES))
    )
    digest = hashlib.sha256(definition.encode()).hexdigest()[:16]
    return f"{COMMENT_PREFIX} (definition {digest})"


def _create_index(conn, name: str, table: str = TABLE, suffix: str = "") -> None:
    """One index; the trigram one is optional because pg_trgm is (a trusted
    extension the database owner can install without being superuser, but a
    role that cannot loses the index, not the bootstrap)."""
    if name != TRGM_INDEX:
        conn.execute(index_sql(name, table, suffix))
        return
    conn.execute("SAVEPOINT obscore_trgm")
    try:
        conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        conn.execute(index_sql(name, table, suffix))
    except Exception as exc:
        conn.execute("ROLLBACK TO SAVEPOINT obscore_trgm")
        log.warning(
            "ivoa.obscore publisher-DID trigram index not created (%s); LIKE lookups by"
            " obs_publisher_did will scan the relation",
            exc,
        )
    else:
        conn.execute("RELEASE SAVEPOINT obscore_trgm")


def _build(conn, existing_relkind: str | None) -> None:
    """Build the relation beside the live one and swap it in by rename.

    Everything happens in the bootstrap transaction, so ordering is what
    keeps a rolling deployment serving: the source tables are locked in SHARE
    mode (ingest waits, queries do not) so no row written during the backfill
    is missed; the new table is filled and indexed under a scratch name while
    queries keep reading the old view or table; only the final DROP and
    RENAME take the exclusive lock on ``ivoa.obscore``, and that is released
    at commit a few statements later. The old relation's indexes keep their
    names until then, so the new ones are built under a suffix and renamed
    after the swap.
    """
    conn.execute(did_encode_sql())
    conn.execute(
        "LOCK TABLE srcnet.data_products, srcnet.observations, srcnet.artifacts IN SHARE MODE"
    )
    conn.execute(f"DROP TABLE IF EXISTS {BUILD}")
    conn.execute(f"CREATE TABLE {BUILD} AS\n{select_sql()}")
    for name in INDEXES:
        _create_index(conn, name, BUILD, "_build")
    conn.execute(f"ANALYZE {BUILD}")
    for statement in trigger_sql():
        conn.execute(statement)
    if existing_relkind == "v":
        conn.execute(f"DROP VIEW {TABLE}")
    elif existing_relkind is not None:
        conn.execute(f"DROP TABLE {TABLE}")
    conn.execute(f"ALTER TABLE {BUILD} RENAME TO {TABLE.split('.')[1]}")
    for name in INDEXES:
        if conn.execute("SELECT to_regclass(%s)", (f"ivoa.{name}_build",)).fetchone()[0]:
            conn.execute(f"ALTER INDEX ivoa.{name}_build RENAME TO {name}")
    # the expression index the view needed on data_products: the DID is a
    # stored, indexed column now
    conn.execute("DROP INDEX IF EXISTS srcnet.data_products_obscore_did_trgm")
    # COMMENT ON is DDL: Postgres plans no parameters for it, so the
    # fingerprint has to arrive already quoted rather than bound
    literal = conn.execute("SELECT quote_literal(%s)", (definition_comment(),)).fetchone()[0]
    conn.execute(f"COMMENT ON TABLE {TABLE} IS {literal}")


def _ensure_indexes(conn) -> None:
    """Put back any index that is missing on a current relation — the seeder
    sets the GiST ones aside for a bulk load, and pg_trgm may have been
    unavailable at an earlier bootstrap. Checked in the catalogue rather than
    left to IF NOT EXISTS, which locks the table before it looks."""
    missing = [
        name
        for name in INDEXES
        if not conn.execute("SELECT to_regclass(%s)", (f"ivoa.{name}",)).fetchone()[0]
    ]
    for name in missing:
        _create_index(conn, name)
    if missing:
        conn.execute(f"ANALYZE {TABLE}")


def ensure_obscore(conn) -> None:
    """Create or migrate the ivoa.obscore relation and register it (odp
    post_ensure hook). The caller holds the bootstrap's advisory transaction
    lock, so concurrent pods serialise here like they do on the rest of the
    schema."""
    existing = conn.execute(
        "SELECT c.relkind, obj_description(c.oid, 'pg_class') FROM pg_class c"
        " JOIN pg_namespace n ON n.oid = c.relnamespace"
        " WHERE n.nspname = 'ivoa' AND c.relname = 'obscore'"
    ).fetchone()
    relkind, comment = existing if existing else (None, None)
    ours = relkind == "v" or (relkind == "r" and (comment or "").startswith(COMMENT_PREFIX))
    if existing and not ours:
        # A deployment that already has an ivoa.obscore of its own (its own
        # archive, or a test harness's synthetic table) is publishing its
        # own ObsCore: replacing it would destroy data the service does not
        # own, and crashing on it would take the whole bootstrap down.
        log.warning(
            "ivoa.obscore already exists and is not this service's; leaving it in"
            " place and skipping the ODP-derived relation"
        )
        return
    conn.execute("CREATE SCHEMA IF NOT EXISTS ivoa")
    if comment != definition_comment():
        log.info("building ivoa.obscore from the ODP tables")
        _build(conn, relkind)
    else:
        _ensure_indexes(conn)
    conn.execute(f"GRANT USAGE ON SCHEMA ivoa TO {settings.query_role}")
    conn.execute(f"GRANT SELECT ON {TABLE} TO {settings.query_role}")
    conn.execute(
        "INSERT INTO tap_schema.schemas (schema_name, description, schema_index)"
        " VALUES ('ivoa', 'IVOA standard tables', 50)"
        " ON CONFLICT (schema_name) DO UPDATE SET description = EXCLUDED.description"
    )
    conn.execute(
        "INSERT INTO tap_schema.tables (schema_name, table_name, table_type, utype,"
        " description, table_index)"
        " VALUES ('ivoa', 'ivoa.obscore', 'table', %s,"
        " 'ObsCore 1.1: one row per data product of the ingested ODP metadata', 1)"
        " ON CONFLICT (table_name) DO UPDATE"
        " SET table_type = EXCLUDED.table_type, utype = EXCLUDED.utype,"
        " description = EXCLUDED.description",
        (DATAMODEL_IVOID,),
    )
    for index, column in enumerate(OBSCORE_COLUMNS, start=1):
        conn.execute(
            "INSERT INTO tap_schema.columns (table_name, column_name, datatype,"
            " arraysize, xtype, unit, ucd, utype, description, indexed, principal,"
            " std, column_index)"
            " VALUES ('ivoa.obscore', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (table_name, column_name) DO UPDATE SET"
            " datatype = EXCLUDED.datatype, arraysize = EXCLUDED.arraysize,"
            " xtype = EXCLUDED.xtype, unit = EXCLUDED.unit, ucd = EXCLUDED.ucd,"
            " utype = EXCLUDED.utype, description = EXCLUDED.description,"
            " indexed = EXCLUDED.indexed, principal = EXCLUDED.principal,"
            " std = EXCLUDED.std, column_index = EXCLUDED.column_index",
            (
                column.name,
                column.datatype,
                column.arraysize,
                column.xtype,
                column.unit,
                column.ucd,
                column.utype,
                column.description,
                int(column.name in INDEXED_COLUMNS),
                column.principal,
                column.std,
                index,
            ),
        )
