-- The ObsCore corpus as argus serves it.
--
-- argus rewrites every reference to ivoa.ObsCore into caom2.ObsCore
-- (CaomAdqlQuery's TableNameConverter); at CADC that is a view over
-- caom2.Observation JOIN caom2.Plane (caom2persistence caom2.ObsCore.sql).
-- Here it is a plain table with the view's column list — the same names,
-- types and order, including the columns the view keeps out of TAP_SCHEMA —
-- so everything argus does to a result finds what it expects:
--   * s_region is double precision[] (the view's p.position_bounds), which
--     PositionBoundsRegionFormat renders as an STC-S circle when it holds
--     three numbers; the corpus's "CIRCLE ra dec r" text becomes [ra,dec,r];
--   * CaomReadAccessConverter appends "metaRelease < <now>" to the WHERE of
--     every caom2.ObsCore query — a release date in the past makes every
--     row public, which is what the corpus is;
--   * position_bounds_center is the spoint CENTROID() would use.
-- The ObsCore 1.1 column metadata (utypes, UCDs, units, xtypes) is written
-- into TAP_SCHEMA by argus itself at startup (ivoa.tap_schema_content11.sql);
-- nothing here duplicates it.
create table caom2.ObsCore (
    dataproduct_type      varchar,
    calib_level           integer,
    obs_collection        varchar,
    facility_name         varchar,
    instrument_name       varchar,
    obs_id                varchar,
    obs_publisher_did     varchar,
    obs_release_date      timestamp,
    access_url            varchar,
    access_format         varchar,
    access_estsize        bigint,
    target_name           varchar,
    s_ra                  double precision,
    s_dec                 double precision,
    s_fov                 double precision,
    s_region              double precision[],
    s_resolution          double precision,
    s_xel1                bigint,
    s_xel2                bigint,
    position_bounds_center spoint,
    position_bounds_area  double precision,
    t_min                 double precision,
    t_max                 double precision,
    t_exptime             double precision,
    t_resolution          double precision,
    t_xel                 bigint,
    em_min                double precision,
    em_max                double precision,
    em_res_power          double precision,
    em_xel                bigint,
    em_ucd                varchar,
    pol_states            varchar,
    pol_xel               integer,
    o_ucd                 varchar,
    lastModified          timestamp,
    -- hidden columns (not in tap_schema)
    position_bounds_spoly spoly,
    -- for CAOM access control
    dataRelease           timestamp,
    dataReadAccessGroups  tsvector,
    planeID               uuid,
    metaRelease           timestamp,
    metaReadAccessGroups  tsvector
);

-- The export, column for column (corpus/dataset.json: the 30 ObsCore 1.1
-- mandatory columns; SQL NULL rendered as the empty field, which CSV COPY
-- reads back as NULL).
create temp table obscore_csv (
    dataproduct_type text, calib_level integer, obs_collection text, obs_id text,
    obs_publisher_did text, access_url text, access_format text, access_estsize bigint,
    target_name text, s_ra double precision, s_dec double precision, s_fov double precision,
    s_region text, s_resolution double precision, s_xel1 bigint, s_xel2 bigint,
    t_min double precision, t_max double precision, t_exptime double precision,
    t_resolution double precision, t_xel bigint, em_min double precision,
    em_max double precision, em_res_power double precision, em_xel bigint,
    o_ucd text, pol_states text, pol_xel integer, facility_name text, instrument_name text
);
copy obscore_csv from '/corpus/obscore.csv' with (format csv, header true);

insert into caom2.ObsCore (
    dataproduct_type, calib_level, obs_collection, facility_name, instrument_name, obs_id,
    obs_publisher_did, access_url, access_format, access_estsize, target_name,
    s_ra, s_dec, s_fov, s_region, s_resolution, s_xel1, s_xel2, position_bounds_center,
    t_min, t_max, t_exptime, t_resolution, t_xel, em_min, em_max, em_res_power, em_xel,
    pol_states, pol_xel, o_ucd, lastModified, dataRelease, metaRelease)
select
    dataproduct_type, calib_level, obs_collection, facility_name, instrument_name, obs_id,
    obs_publisher_did, access_url, access_format, access_estsize, target_name,
    s_ra, s_dec, s_fov,
    (string_to_array(s_region, ' '))[2:4]::double precision[],  -- "CIRCLE ra dec r"
    s_resolution, s_xel1, s_xel2,
    spoint(radians(s_ra), radians(s_dec)),
    t_min, t_max, t_exptime, t_resolution, t_xel, em_min, em_max, em_res_power, em_xel,
    pol_states, pol_xel, o_ucd,
    now(), timestamp '2000-01-01', timestamp '2000-01-01'
from obscore_csv;

-- CADC's indexes on the columns the view draws from (caom2persistence
-- caom2.Plane.sql, caom2.Observation.sql, caom2.extra_indices.sql), one for
-- one on the flat table. Not carried over: the GiST index on
-- position_bounds_spoly and the dataRelease index (both columns are NULL
-- here — the corpus has no release date, and pgsphere has no circle-to-
-- polygon cast; nothing in the benchmark's query classes touches either),
-- and Plane's clustering on obsID (no such column).
create unique index ObsCore_i_publisherID on caom2.ObsCore (obs_publisher_did);
create index ObsCore_i_observationID on caom2.ObsCore (obs_collection, obs_id);
create index ObsCore_i_observationID_lower on caom2.ObsCore (lower(obs_id));
create index ObsCore_i_observationID_lower_pattern on caom2.ObsCore (lower(obs_id) text_pattern_ops);
create index ObsCore_i_targ_lower on caom2.ObsCore (lower(target_name)) where target_name is not null;
create index ObsCore_i_targ_lower_pattern on caom2.ObsCore (lower(target_name) text_pattern_ops)
    where target_name is not null;
create index ObsCore_i_collection_instrument on caom2.ObsCore (obs_collection, instrument_name);
create index ObsCore_i_telescope_instrument on caom2.ObsCore (facility_name, instrument_name);
create index ObsCore_i_instrument on caom2.ObsCore (instrument_name);
create index ObsCore_i_instrument_pattern on caom2.ObsCore (instrument_name varchar_pattern_ops);
create index ObsCore_i_telescope on caom2.ObsCore (facility_name);
create index ObsCore_time_ib1 on caom2.ObsCore (t_min);
create index ObsCore_time_ib2 on caom2.ObsCore (t_max);
create index ObsCore_energy_ib1 on caom2.ObsCore (em_min);
create index ObsCore_energy_ib2 on caom2.ObsCore (em_max);
create index ObsCore_pol_states_pattern on caom2.ObsCore (pol_states varchar_pattern_ops)
    where pol_states is not null;
create index ObsCore_i_maxLastModified on caom2.ObsCore (lastModified);

analyze caom2.ObsCore;
