#!/bin/bash
# What argus expects to find in its database (argus README, "configuration"):
# one database for its three pools; the tap_schema and uws schemas, whose
# tables argus creates and fills itself at startup (InitDatabaseTS "assumes
# that the tap_schema schema exists", InitDatabaseUWS likewise); tap_upload,
# where its availability check creates and drops a table; and caom2, which
# "holds the content" — argus writes a TAP_SCHEMA description of the CAOM2
# tables at startup and its availability check selects from
# caom2.Observation, so the tables exist here, empty, exactly as CADC's DDL
# creates them. The corpus itself goes into caom2.ObsCore (02-obscore.sql).
set -euo pipefail

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
create extension if not exists pg_sphere;
create extension if not exists citext;
create schema tap_schema;
create schema uws;
create schema tap_upload;
create schema caom2;
SQL

# CADC's DDL is schema-agnostic (<schema>); argus hard-codes caom2.
for table in Observation Plane Artifact Part Chunk HarvestState HarvestSkipURI SIAv1; do
    sed 's/<schema>/caom2/g' "/caom2-sql/caom2.${table}.sql" \
        | psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
done
