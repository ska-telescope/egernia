#!/bin/bash
# Amendment 3 (PROTOCOL.md): the image's own /entrypoint.sh, unchanged except
# that DaCHS serves as the unprivileged `gavo` user instead of root, as the
# Debian package runs it in production. PostgreSQL is still started as before.
#
# Why: DaCHS 2.11 marks a sync query's job EXECUTING with pid -1. When the
# update that ends the job times out, destroying it calls os.kill(-1, SIGTERM)
# (gavo/protocols/tap.py, TAPJob.prepareForDestruction). As root that signals
# every process in the container: PostgreSQL shuts down and DaCHS, which
# survives as PID 1, answers 500 from then on. As `gavo` the same call reaches
# no process but DaCHS's own, and the kernel never lets kill(-1) hit PID 1.
set -euo pipefail
ep=$(sed 's/^exec dachs serve debug$/exec setpriv --reuid=gavo --regid=gavo --init-groups dachs serve debug/' \
    /entrypoint.sh)
grep -qx 'exec setpriv --reuid=gavo --regid=gavo --init-groups dachs serve debug' <<< "$ep" \
    || { echo "dachs-as-gavo: /entrypoint.sh no longer ends in 'exec dachs serve debug'" >&2; exit 1; }
exec bash -c "$ep"
