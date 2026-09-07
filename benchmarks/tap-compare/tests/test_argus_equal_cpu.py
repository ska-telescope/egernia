"""The equal-CPU variant (argus-equal-cpu/PROTOCOL.md): the parity protocol
and the argus target verbatim, egernia at one API worker per pinned core with
PostgreSQL's parallel budget re-derived by the documented rule."""

import pathlib

import yaml
from tap_compare import publish

SUITE = pathlib.Path(__file__).resolve().parents[1]
VARIANT = SUITE / "argus-equal-cpu"
GIB = 2**30
POOL = 8  # TAP_DB_POOL_MAX default, unchanged
PER_GATHER = 2
_UNITS = {"GB": GIB, "MB": 2**20, "g": GIB}


def _bytes(value: str) -> int:
    for suffix, scale in _UNITS.items():
        if value.endswith(suffix):
            return int(value.removesuffix(suffix)) * scale
    raise AssertionError(f"{value!r}: unknown unit")


def _targets(path):
    return {t["name"]: t for t in yaml.safe_load(path.read_text())["targets"]}


def test_variant_changes_only_egernias_workers():
    assert (VARIANT / "scenarios.yaml").read_text() == (
        SUITE / "config" / "scenarios.yaml"
    ).read_text()
    targets = _targets(VARIANT / "targets.yaml")
    assert set(targets) == {"egernia-local-equalcpu", "argus-local"}
    assert targets["argus-local"] == _targets(SUITE / "argus" / "targets.yaml")["argus-local"]
    egernia = targets["egernia-local-equalcpu"]
    assert egernia["server"] == "egernia" and egernia["base_url"] == "http://localhost:8080/tap"


def test_equalcpu_pins_are_the_parity_pins_plus_eight_workers():
    parity = yaml.safe_load((SUITE / "docker-compose.egernia-pins.yml").read_text())["services"]
    pins = yaml.safe_load((VARIANT / "egernia-equalcpu.yml").read_text())["services"]
    assert set(pins) == set(parity)
    for name, service in parity.items():
        assert pins[name]["cpuset"] == service["cpuset"] == "0-7"
        assert pins[name]["mem_limit"] == service["mem_limit"]  # memory split unchanged
    workers = int(pins["tap-api"]["environment"]["TAP_API_WORKERS"])
    assert workers == 8  # one per pinned core
    assert "TAP_DB_POOL_MAX" not in pins["tap-api"].get("environment", {})
    # docs/postgres-performance.md's rule for the new pool total; the rest of
    # the db command is docker-compose.yml's
    compose = yaml.safe_load((SUITE.parents[1] / "docker-compose.yml").read_text())["services"]
    base = dict(kv.split("=", 1) for kv in compose["db"]["command"][2::2])
    tuning = dict(kv.split("=", 1) for kv in pins["db"]["command"][2::2])
    pools = (workers + 1) * POOL  # API workers + one executor
    assert pools < 100  # PostgreSQL's default max_connections
    assert int(tuning["max_parallel_workers"]) == pools * PER_GATHER == 144
    assert int(tuning["max_worker_processes"]) == int(tuning["max_parallel_workers"]) + 8
    for setting in ("shared_buffers", "effective_cache_size", "work_mem"):
        assert tuning[setting] == base[setting]
    assert _bytes(tuning["shared_buffers"]) == _bytes(pins["db"]["mem_limit"]) // 4
    # the documented memory floor fits the API's share
    assert 140 * workers + workers * POOL * 2.5 < _bytes(pins["tap-api"]["mem_limit"]) / 2**20


def test_publisher_names_the_variants_own_pins():
    rows = [
        {"target": "egernia-local-equalcpu", "server": "egernia"},
        {"target": "argus-local", "server": "argus"},
    ]
    keys = publish.stack_keys(rows)
    assert keys == ["argus", "egernia-local-equalcpu"]
    intro = "\n".join(publish.parity_intro(keys))
    assert "egernia-equalcpu.yml" in intro and "egernia-pins" not in intro
    assert publish.stack_keys([{"target": "egernia-local", "server": "egernia"}]) == ["egernia"]
