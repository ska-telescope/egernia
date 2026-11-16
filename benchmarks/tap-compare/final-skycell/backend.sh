# Sourced by every driver in this directory (PROTOCOL.md, "What is verified").
# check_backend <db container> <api container> <executor container> <backend>
# refuses unless the stack is really on <backend>: the variable in both
# query-serving containers, the skycell build pinned by commit and version,
# ivoa.obscore's footprint column of that backend's type, and the cone index
# of that backend on ivoa.obscore. Needs the drivers' `expect` and `fail`.

# skycell release v0.58. Its SQL extension version is not the release tag
# (v0.58 installs extension version 0.50, which several releases may share),
# so the build is identified by the commit db/Dockerfile records in the
# image, and the extension version is checked beside it.
SKYCELL_COMMIT=0d998bd928e026da05631e6f0e9b3b6dbab7570d
SKYCELL_EXTVERSION=0.50

check_backend() {
    local db=$1 api=$2 executor=$3 backend=$4 container
    local psql=(docker exec "$db" psql -U tap -d tap -Atc)
    for container in "$api" "$executor"; do
        expect "$container TAP_GEOMETRY_BACKEND" \
            "$(docker inspect "$container" --format '{{join .Config.Env "\n"}}' \
                | sed -n 's/^TAP_GEOMETRY_BACKEND=//p')" "$backend"
    done
    local column cone
    column=$("${psql[@]}" "select format_type(atttypid, atttypmod) from pg_attribute \
        where attrelid = 'ivoa.obscore'::regclass and attname = 's_region_geom'")
    case $backend in
        skycell)
            expect "$db skycell commit" \
                "$(docker exec "$db" cat /usr/share/skycell/COMMIT)" "$SKYCELL_COMMIT"
            expect "$db skycell extension version" \
                "$("${psql[@]}" "select extversion from pg_extension where extname = 'skycell'")" \
                "$SKYCELL_EXTVERSION"
            expect "$db ivoa.obscore.s_region_geom type" "$column" skyregion
            # the HEALPix cell B-tree that holds the position (docs/deployment.md)
            cone=$("${psql[@]}" "select count(*) from pg_indexes where schemaname = 'ivoa' \
                and tablename = 'obscore' and indexdef ilike '%skycell_ang2cell%'")
            ;;
        pgsphere)
            expect "$db ivoa.obscore.s_region_geom type" "$column" spoly
            cone=$("${psql[@]}" "select count(*) from pg_indexes where schemaname = 'ivoa' \
                and tablename = 'obscore' and indexdef ilike '%gist%spoint%'")
            ;;
        *) fail "unknown backend '$backend'" ;;
    esac
    [ "$cone" -ge 1 ] || fail "$db: no $backend cone index on ivoa.obscore"
}

# refuse_cone_disagreement <gates.json>: the cone classes are what this rerun
# exists to measure, so a disagreement on any of them stops the experiment
# (PROTOCOL.md, "Pre-flight"; amendment 1). `compare --gates-only` itself
# fails only on taplint: a class that fails agreement is excluded and the
# rest measured, which is the base protocols' rule and stays theirs for every
# other class.
CONE_CLASSES="Q05 Q06 Q07 Q12"
refuse_cone_disagreement() {
    local gates=$1 disagreed
    [ -f "$gates" ] || fail "no gate record at $gates"
    disagreed=$(python3 -c '
import json, sys
gates = json.load(open(sys.argv[1]))
if "agreement" not in gates:
    sys.exit("no agreement verdict in " + sys.argv[1])
print(" ".join(sorted(set(gates["agreement"]["disagreed"]) & set(sys.argv[2:]))))
' "$gates" $CONE_CLASSES) || fail "cannot read the agreement verdict in $gates"
    [ -z "$disagreed" ] || fail "cone classes disagree across targets: $disagreed" \
        "($gates) - a skycell correctness finding; nothing is measured (PROTOCOL.md)"
    log "PROGRESS cone classes agree ($CONE_CLASSES)"
}
