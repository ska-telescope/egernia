-- Spherical-geometry extension used by ADQL geometry translations
-- (POINT/CIRCLE/CONTAINS -> spoint/scircle/@ operators).
DO $do$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS pg_sphere;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'pg_sphere not available: ADQL geometry functions will fail (%).', SQLERRM;
    END;
END
$do$;

-- The functions that return a select-list geometry as a DALI array of
-- doubles in degrees, which pg_sphere does not define. The same text as
-- egernia_core/geometry.py (a unit test holds them equal); the bootstrap
-- creates them on a database that predates this file.
DO $do$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_sphere') THEN
        RETURN;
    END IF;
    BEGIN
        CREATE OR REPLACE FUNCTION spoint_to_array_deg(p spoint) RETURNS double precision[] LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$ SELECT ARRAY[degrees(long(p)), degrees(lat(p))] $$;
        CREATE OR REPLACE FUNCTION scircle_to_array_deg(c scircle) RETURNS double precision[] LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$ SELECT ARRAY[degrees(long(center(c))), degrees(lat(center(c))), degrees(radius(c))] $$;
        CREATE OR REPLACE FUNCTION spoly_to_array_deg(p spoly) RETURNS double precision[] LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$ SELECT array_agg(v ORDER BY i, j) FROM generate_series(1, npoints(p)) AS i, LATERAL (VALUES (1, degrees(long(spoint(p, i)))), (2, degrees(lat(spoint(p, i))))) AS t(j, v) $$;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'pg_sphere select-list functions not created: SELECT POINT(...) will fail (%).', SQLERRM;
    END;
END
$do$;

-- skycell, the alternative geometry backend (TAP_GEOMETRY_BACKEND=skycell);
-- only present when the image was built with it (db/Dockerfile, SKYCELL_REF).
DO $do$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS skycell;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'skycell not available: TAP_GEOMETRY_BACKEND=skycell will fail (%).', SQLERRM;
    END;
END
$do$;
