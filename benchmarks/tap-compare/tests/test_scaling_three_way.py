"""The three-server resource-scaling protocol (scaling-three-way/PROTOCOL.md):
three tiers, three servers, each sized by its own documented rule, and a grid
narrow enough to feed a figure."""

import pathlib
import re

import pytest
import yaml
from tap_compare import publish

SUITE = pathlib.Path(__file__).resolve().parents[1]
S3 = SUITE / "scaling-three-way"
SCALING = SUITE / "scaling"
TIERS = (8, 16, 24)
GIB = 2**30
POOL = 8  # connections per process (config.dbPoolMax), unchanged
PER_GATHER = 2
GENERATOR_CORES = set(range(24, 30))
# tier 8 puts the three servers side by side; above it each is measured alone
CPUSETS = {
    8: {"egernia": "0-7", "argus": "8-15", "dachs": "16-23"},
    16: {"egernia": "0-15", "argus": "0-15", "dachs": "0-15"},
    24: {"egernia": "0-23", "argus": "0-23", "dachs": "0-23"},
}
_UNITS = {"GB": GIB, "MB": 2**20, "g": GIB}


def _bytes(value: str) -> int:
    for suffix, scale in _UNITS.items():
        if value.endswith(suffix):
            return int(value.removesuffix(suffix)) * scale
    raise AssertionError(f"{value!r}: unknown unit")


def _services(name: str) -> dict:
    return yaml.safe_load((S3 / "pins" / f"{name}.yml").read_text())["services"]


def _flags(service: dict) -> dict:
    return dict(kv.split("=", 1) for kv in service["command"][2::2])


def _cores(spec: str) -> set[int]:
    lo, hi = spec.split("-")
    return set(range(int(lo), int(hi) + 1))


def test_scenarios_keep_the_parity_workload_and_the_scaling_windows():
    parity = yaml.safe_load((SUITE / "config" / "scenarios.yaml").read_text())
    scaling = yaml.safe_load((SCALING / "scenarios.yaml").read_text())
    s3 = yaml.safe_load((S3 / "scenarios.yaml").read_text())
    for block in ("corpus", "mix", "guards"):
        assert s3[block] == parity[block]
    grid = s3["scenarios"]["scaling3"]
    assert grid["per_class"] and grid["repetitions"] == 3
    assert grid["response_formats"] == parity["scenarios"]["compare"]["response_formats"]
    assert grid["maxrec"] == parity["scenarios"]["compare"]["maxrec"]
    for key in ("warmup_seconds", "measure_seconds", "generator_processes"):
        assert grid[key] == scaling["scenarios"]["scaling"][key]
    # the ladder stops at 32: c=64 was below c=32 at every tier of the
    # published scaling run, so it buys a point beneath the one beside it
    assert grid["ladder"] == [8, 32]
    # 5 entries x 2 formats x 2 concurrencies x 3 repetitions, 9 blocks
    rungs = 9 * 5 * len(grid["response_formats"]) * len(grid["ladder"]) * grid["repetitions"]
    assert rungs == 540
    assert 12 < rungs * 85.7 / 3600 < 13.5  # PROTOCOL.md's arithmetic


@pytest.mark.parametrize("tier", TIERS)
def test_egernia_pins_are_the_published_scaling_runs_verbatim(tier):
    """Same sizing rule as the run this one replaces, so the two remain
    comparable — and so the rule is not quietly re-derived here."""
    assert (S3 / "pins" / f"egernia-{tier}.yml").read_text() == (
        SCALING / "pins" / f"egernia-{tier}.yml"
    ).read_text()
    services = _services(f"egernia-{tier}")
    memory = {name: _bytes(s["mem_limit"]) for name, s in services.items()}
    assert sum(memory.values()) == tier * GIB and memory["db"] == tier * GIB // 2
    tuning = _flags(services["db"])
    workers = int(services["tap-api"]["environment"]["TAP_API_WORKERS"])
    assert workers == {8: 1, 16: 2, 24: 4}[tier]
    # the connection budget stays inside PostgreSQL's default max_connections
    assert (workers + 1) * POOL < 100
    assert int(tuning["max_parallel_workers"]) >= (workers + 1) * POOL * PER_GATHER
    assert _bytes(tuning["shared_buffers"]) == memory["db"] // 4
    assert _bytes(tuning["effective_cache_size"]) == memory["db"] * 3 // 4


@pytest.mark.parametrize("tier", TIERS)
def test_dachs_gets_the_quarter_rule_and_egernias_parallel_budget(tier):
    dachs = _services(f"dachs-{tier}")["dachs"]
    assert dachs["cpus"] == tier and _bytes(dachs["mem_limit"]) == tier * GIB
    # the drop-in is the published run's verbatim; only the cpuset differs
    assert (S3 / "pins" / f"dachs-postgres-{tier}.conf").read_text() == (
        SCALING / "pins" / f"dachs-postgres-{tier}.conf"
    ).read_text()
    conf = dict(
        line.replace(" ", "").split("=", 1)
        for line in (S3 / "pins" / f"dachs-postgres-{tier}.conf").read_text().splitlines()
        if line and not line.startswith("#")
    )
    assert _bytes(conf["shared_buffers"]) == tier * GIB // 4
    assert _bytes(conf["effective_cache_size"]) == tier * GIB * 3 // 4
    egernia_db = _flags(_services(f"egernia-{tier}")["db"])
    for setting in ("max_parallel_workers", "max_worker_processes"):
        assert conf[setting] == egernia_db[setting]
    (mount,) = [v for v in dachs["volumes"] if f"dachs-postgres-{tier}.conf" in v]
    assert mount.startswith("./scaling-three-way/pins/")  # not the other protocol's file
    assert mount.endswith("/conf.d/90-tier.conf:ro")


@pytest.mark.parametrize("tier", TIERS)
def test_argus_holds_its_shape_and_sizes_postgresql_by_the_same_rule(tier):
    services = _services(f"argus-{tier}")
    assert set(services) == {"argus", "argus-db"}
    tomcat = _bytes(services["argus"]["mem_limit"])
    database = _bytes(services["argus-db"]["mem_limit"])
    assert tomcat + database == tier * GIB
    assert tomcat == tier * GIB * 3 // 8 and database == tier * GIB * 5 // 8  # tier 8's split
    tuning = _flags(services["argus-db"])
    assert _bytes(tuning["shared_buffers"]) == database // 4
    assert _bytes(tuning["effective_cache_size"]) == database * 3 // 4
    egernia_db = _flags(_services(f"egernia-{tier}")["db"])
    for setting in ("max_parallel_workers", "max_worker_processes"):
        assert tuning[setting] == egernia_db[setting]
    # the vendor JVM default is untouched at every tier: no -Xmx anywhere
    assert "environment" not in services["argus"]


@pytest.mark.parametrize("tier", TIERS)
def test_no_target_ever_shares_a_cpuset_and_the_generator_keeps_its_cores(tier):
    """argus keeps draining its queue after the generator leaves, so a shared
    cpuset is unsound at any tier (argus-equal-cpu/PROTOCOL.md, amendment 1)."""
    pinned = {}
    for server, expected in CPUSETS[tier].items():
        services = _services(f"{server}-{tier}")
        cpusets = {s["cpuset"] for s in services.values()}
        assert cpusets == {expected}, f"{server} at tier {tier}"
        pinned[server] = _cores(expected)
        assert len(pinned[server]) == tier
        assert not (pinned[server] & GENERATOR_CORES)
    if tier == 8:
        # all three up at once: disjoint, and they fill the host with the generator
        assert not (pinned["egernia"] & pinned["argus"])
        assert not (pinned["egernia"] & pinned["dachs"])
        assert not (pinned["argus"] & pinned["dachs"])
        assert len(set().union(*pinned.values()) | GENERATOR_CORES) == 30
    else:
        # measured one at a time, so the same cores are offered to each in turn
        assert pinned["egernia"] == pinned["argus"] == pinned["dachs"]


def test_the_driver_matches_the_protocol_and_keeps_the_final_runs_discipline():
    script = (S3 / "run.sh").read_text()
    assert re.search(r"^EXPECTED_CORPUS_SHA=bc4110500860", script, re.M)
    assert re.search(r"^EXPECTED_ROWS=500096$", script, re.M)
    assert re.search(r"^CLASSES=\$\{CLASSES:-Q01 Q05 Q11 Q13 mix\}$", script, re.M)
    assert re.search(r"^TIERS=\$\{TIERS:-8 16 24\}$", script, re.M)
    for needle in (
        "another tap-compare measurement",  # the interlock
        "truncate uws.jobdetail, uws.job",  # a fresh job store per block
        "egernia-tap-executor-1",  # PR #161 inert in both query-serving containers
        "TAP_QUERY_DATABASE_URL",
        "relkind",  # PR #160's ivoa.obscore is a table
        "work_mem",
        "record_host",
        "stop_sampler",
        "--gates-only",
        "--classes",
    ):
        assert needle in script, needle
    # the interlock excludes by identity and neutralises pgrep's empty exit
    interlock = script[script.index("# The interlock") : script.index('log "PROGRESS start')]
    assert "|| true; }" in interlock
    assert "ps -o ppid=" in interlock and "ps -o sid=" in interlock
    # tier 8 interleaves; above it the others are stopped, not left idle
    assert 'if [ "$tier" = 8 ]' in script and "down_server" in script
    # the generator's affinity is validated before the first stack is touched
    assert script.index("GEN_CORES=$(") < script.index('log "PROGRESS start')


def test_the_report_names_this_protocol_not_the_other_one():
    # every scenario this protocol defines, the shake-out included: publishing
    # a smoke run must not attribute it to the protocol it is not
    for scenario in ("scaling3", "scaling3-smoke"):
        assert "scaling-three-way/PROTOCOL.md" in "\n".join(publish.scaling_intro(scenario))
    for scenario in ("scaling", "scaling-smoke"):
        assert "scaling-three-way" not in "\n".join(publish.scaling_intro(scenario))
    # a tiered run from before the mapping still names the original protocol
    assert "scaling/PROTOCOL.md" in "\n".join(publish.scaling_intro(None))
    # nothing this protocol can run is missing from the map
    scenarios = yaml.safe_load((S3 / "scenarios.yaml").read_text())["scenarios"]
    for scenario in scenarios:
        if scenario != "warm":  # the warm pass is a discard, never published
            assert scenario in publish.SCALING_PROTOCOLS


def test_argus_starts_every_measured_block_on_an_empty_job_store():
    """The gates' probes and the warm pass are synchronous requests, and argus
    persists a UWS job for each — so truncating only at `up` would leave a
    different history on each tier's blocks and put it on the tier axis."""
    script = (S3 / "run.sh").read_text()
    assert script.count("truncate_argus_jobs_if_up") == 3  # the definition and both call sites
    # each measured block truncates immediately before `compare`, never after it
    for block in script.split("truncate_argus_jobs_if_up")[1:]:
        head = block[: block.index("tap compare")] if "tap compare" in block else block
        assert "--classes" not in head
    # and it is a no-op when argus is stopped, which is every non-argus block
    # above tier 8
    assert "State.Running" in script
