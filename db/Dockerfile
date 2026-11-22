# PostgreSQL with the pg_sphere extension (spherical geometry used by
# translated ADQL POINT/CIRCLE/CONTAINS expressions). The official postgres
# image ships the PGDG apt repository, so the pgsphere package is available.
#
# The major version appears twice — the base image and the versioned pgsphere
# package — and both must move together: postgresql-<N>-pgsphere only builds
# against server major N. The digest pins the exact base image; refresh it
# with: docker buildx imagetools inspect postgres:18
FROM postgres:18@sha256:06cad38a5d9f5d24b4d83d86def30795d5e4b757fedbf5281172b576dedcd941
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-18-pgsphere \
    && rm -rf /var/lib/apt/lists/*

# skycell (https://github.com/jesusjuansalgado/skycell), the alternative
# geometry backend (TAP_GEOMETRY_BACKEND=skycell), built from source when
# SKYCELL_REF names a commit (preferred: the build is then reproducible), a
# tag or a branch of SKYCELL_REPO. Left out by default. The commit actually
# built is recorded in the image (/usr/share/skycell/COMMIT) and the
# extension's own version in pg_available_extensions, so a deployment can be
# traced to the skycell it runs. The toolchain is removed again so the image
# only gains the extension itself.
ARG SKYCELL_REPO=https://github.com/jesusjuansalgado/skycell
ARG SKYCELL_REF=
RUN if [ -n "$SKYCELL_REF" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            build-essential ca-certificates git postgresql-server-dev-18 \
        && git init -q /tmp/skycell \
        && git -C /tmp/skycell fetch -q --depth 1 "$SKYCELL_REPO" "$SKYCELL_REF" \
        && git -C /tmp/skycell checkout -q FETCH_HEAD \
        && mkdir -p /usr/share/skycell \
        && git -C /tmp/skycell rev-parse HEAD > /usr/share/skycell/COMMIT \
        && make -C /tmp/skycell/ext with_llvm=no install \
        && rm -rf /tmp/skycell \
        && apt-get purge -y --auto-remove build-essential git postgresql-server-dev-18 \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# postgres:18 keeps its data under /var/lib/postgresql/<major>/docker and no
# longer ships /var/lib/postgresql/data. Compose and the Helm chart both put
# PGDATA at /var/lib/postgresql/data/pgdata, so create that mount point with
# postgres ownership: a fresh Docker named volume inherits the directory's
# permissions from the image, and without this the non-root server cannot
# create its data directory.
RUN mkdir -p /var/lib/postgresql/data     && chown postgres:postgres /var/lib/postgresql/data     && chmod 700 /var/lib/postgresql/data

# Run as the postgres user (uid 999) instead of root; the official image
# supports this when the data directory is writable by that user.
USER postgres
