# PostgreSQL for argus. argus ships no database; its README requires
# PostgreSQL with the citext and pgsphere extensions. CADC's own database
# image (opencadc/docker-base cadc-postgresql-dev) is PostgreSQL 17 +
# pgsphere 1.5.2 on Fedora; this is the official postgres image at the same
# major plus Debian trixie's postgresql-17-pgsphere (1.5.1) — citext is in
# contrib, already present.
FROM postgres:17-trixie@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-17-pgsphere \
    && rm -rf /var/lib/apt/lists/*

# CADC's DDL for the eight files whose tables and views argus's TAP_SCHEMA
# describes in the caom2 schema — Observation (+ ObservationMember), Plane
# (+ ProvenanceInput), Artifact, Part, Chunk, HarvestState, HarvestSkipURI,
# SIAv1 — vendored under caom2-sql/ (PROVENANCE: upstream commit and sha256
# per file). init/01-caom2.sh creates them empty; init/02-obscore.sql puts
# the corpus in caom2.ObsCore, the table argus rewrites ivoa.ObsCore to.
COPY caom2-sql/ /caom2-sql/
COPY init/ /docker-entrypoint-initdb.d/

HEALTHCHECK CMD pg_isready -h 127.0.0.1 -U tap -d argus
