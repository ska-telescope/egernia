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

# The CAOM2 DDL argus's TAP_SCHEMA describes (caom2.Observation, Plane,
# Artifact, Part, Chunk, ObservationMember, ProvenanceInput, HarvestState,
# HarvestSkipURI, SIAv1), vendored from the argus source tree — opencadc/caom2
# main at 733b4cd (2026-07-20, argus/VERSION 1.0.27) — and pinned by checksum.
# init/01-caom2.sh creates them empty; init/02-obscore.sql puts the corpus in
# caom2.ObsCore, the table argus rewrites ivoa.ObsCore to.
ARG CAOM2_SQL=https://raw.githubusercontent.com/opencadc/caom2/733b4cd87c9005215b7cdfeba1240607e8f2be12/caom2persistence/src/main/resources/postgresql
ADD --checksum=sha256:3e4f6d8e1321abb881a0b24aa4c45475041bfacdc0cdc213946553b89dbcc6fb ${CAOM2_SQL}/caom2.Observation.sql /caom2-sql/
ADD --checksum=sha256:bc422cf1473ac9f4905350b8affb493f56a9071372103480b38a0053b5fe7385 ${CAOM2_SQL}/caom2.Plane.sql /caom2-sql/
ADD --checksum=sha256:98e86407b2baf0bbdc29545420d2414cfc601c2c9c9b5b247597cafe35489d1f ${CAOM2_SQL}/caom2.Artifact.sql /caom2-sql/
ADD --checksum=sha256:15c0c5f03cdb582ac884941e94812bc074a8ec59ee43e79148c26c125277ef85 ${CAOM2_SQL}/caom2.Part.sql /caom2-sql/
ADD --checksum=sha256:25dc513f5fc357bbf13d202dd67dabc565000a18d1028bd4f0cc5691df69d13a ${CAOM2_SQL}/caom2.Chunk.sql /caom2-sql/
ADD --checksum=sha256:544ddf14d8a974cfc341b77f2ecd0dd13efca8bf1f8478214d54c17e0255098c ${CAOM2_SQL}/caom2.HarvestState.sql /caom2-sql/
ADD --checksum=sha256:b14b424664419b4e689261640d707ccc47492b408cb16d542816cd6e50d9ac27 ${CAOM2_SQL}/caom2.HarvestSkipURI.sql /caom2-sql/
ADD --checksum=sha256:9151bc95687457a467012a7c50fd4d21476260b0390d7459de1cccb9ed2118c5 ${CAOM2_SQL}/caom2.SIAv1.sql /caom2-sql/

COPY init/ /docker-entrypoint-initdb.d/
