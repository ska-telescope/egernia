"""The read-replica tier's pins: same budget as the published tier 24, one
primary plus three standbys inside it, each server sized by the documented
rule — and a class list the driver can actually run."""

import pathlib
import re

import yaml
from tap_compare import corpus

SUITE = pathlib.Path(__file__).resolve().parents[1]
REPLICAS = SUITE / "scaling-replicas"
GIB = 2**30
POOL = 8  # connections per process (config.dbPoolMax)
PER_GATHER = 2
STANDBYS = ("db-standby-1", "db-standby-2", "db-standby-3")

_UNITS = {"GB": GIB, "MB": 2**20, "g": GIB}


def _bytes(value: str) -> int:
    for suffix, scale in _UNITS.items():
        if value.endswith(suffix):
            return int(value.removesuffix(suffix)) * scale
    raise AssertionError(f"{value!r}: unknown unit")


def _services(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text())["services"]


def _pg_flags(service: dict) -> dict[str, str]:
    """The `-c name=value` server settings, however the service starts postgres.

    The primary passes them as compose command arguments; a standby starts
    from a shell script that clones the primary first, so there they are text.
    """
    return dict(re.findall(r"-c\s+(\w+)=(\S+)", " ".join(service["command"])))


def _tier_24() -> dict:
    return _services(SUITE / "scaling" / "pins" / "egernia-24.yml")


def test_the_replica_tier_holds_the_tier_24_budget():
    services = _services(REPLICAS / "pins" / "egernia-24r.yml")
    tier24 = _tier_24()
    assert {s["cpuset"] for s in services.values()} == {"0-23"}
    memory = {name: _bytes(s["mem_limit"]) for name, s in services.items()}
    assert sum(memory.values()) == 24 * GIB
    # the API and executor are held identical, so the comparison is about the
    # database; the database's 12 GiB is what gets divided four ways
    assert memory["tap-api"] == _bytes(tier24["tap-api"]["mem_limit"])
    assert memory["tap-executor"] == _bytes(tier24["tap-executor"]["mem_limit"])
    assert memory["db"] + sum(memory[s] for s in STANDBYS) == _bytes(tier24["db"]["mem_limit"])


def test_every_replica_tier_server_is_sized_to_its_container():
    services = _services(REPLICAS / "pins" / "egernia-24r.yml")
    workers = int(services["tap-api"]["environment"]["TAP_API_WORKERS"])
    pools = (workers + 1) * POOL  # API workers + one executor
    primary = _pg_flags(services["db"])
    for name in ("db", *STANDBYS):
        limit = _bytes(services[name]["mem_limit"])
        flags = _pg_flags(services[name])
        assert _bytes(flags["shared_buffers"]) == limit // 4, name
        assert _bytes(flags["effective_cache_size"]) == limit * 3 // 4, name
    for name in STANDBYS:
        flags = _pg_flags(services[name])
        # a standby may receive the whole query pool: libpq balances at random
        assert int(flags["max_parallel_workers"]) >= pools * PER_GATHER, name
        assert int(flags["max_worker_processes"]) == int(flags["max_parallel_workers"]) + 8, name
        # PostgreSQL refuses to start a standby whose slots are fewer than the
        # primary's
        assert int(flags["max_worker_processes"]) >= int(primary["max_worker_processes"]), name
        # a long TAP scan must not lose to a vacuum on the primary
        assert flags["hot_standby_feedback"] == "on", name


def test_the_replica_tier_points_the_query_path_at_every_standby():
    services = _services(REPLICAS / "pins" / "egernia-24r.yml")
    for name in ("tap-api", "tap-executor"):
        url = services[name]["environment"]["TAP_QUERY_DATABASE_URL"]
        assert "target_session_attrs=read-only" in url, name
        assert "load_balance_hosts=random" in url, name
        for standby in STANDBYS:
            assert f"{standby}:5432" in url, (name, standby)
        assert "@db:" not in url, name  # never the primary


def test_the_worker_control_differs_from_tier_24_in_workers_alone():
    """24w exists to tell more workers apart from more databases, so it must be
    the published tier-24 shape with nothing else moved."""
    control = _services(REPLICAS / "pins" / "egernia-24w.yml")
    tier24 = _tier_24()
    assert {s["cpuset"] for s in control.values()} == {"0-23"}
    for name, service in tier24.items():
        assert control[name]["mem_limit"] == service["mem_limit"], name
    assert control["tap-api"]["environment"]["TAP_API_WORKERS"] == "8"
    flags, published = _pg_flags(control["db"]), _pg_flags(tier24["db"])
    workers = int(control["tap-api"]["environment"]["TAP_API_WORKERS"])
    pools = (workers + 1) * POOL
    assert int(flags["max_parallel_workers"]) >= pools * PER_GATHER
    assert int(flags["max_worker_processes"]) == int(flags["max_parallel_workers"]) + 8
    # everything the worker count does not decide stays as tier 24 had it
    for setting in ("shared_buffers", "effective_cache_size", "work_mem"):
        assert flags[setting] == published[setting], setting


def test_the_driver_runs_classes_the_corpus_has():
    """A typo in CLASSES aborts the run hours in, when --classes refuses it."""
    script = (REPLICAS / "run.sh").read_text()
    known = set(corpus.CLASSES) | {"mix"}
    for name in ("CLASSES", "CONTROL_CLASSES"):
        listed = re.search(rf'^{name}="([^"]+)"', script, re.M)
        assert listed, name
        classes = set(listed.group(1).split())
        assert classes <= known, (name, classes - known)
        # the mixed workload is the headline of every rung of this protocol
        assert "mix" in classes, name
