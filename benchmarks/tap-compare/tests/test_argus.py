"""The egernia-vs-argus comparison (argus/PROTOCOL.md): the config directory
is the parity protocol with argus in DaCHS's seat, and the argus stack holds
the DaCHS budget under the pre-registered sizing rules."""

import pathlib

import yaml
from tap_compare import publish

SUITE = pathlib.Path(__file__).resolve().parents[1]
ARGUS = SUITE / "argus"
GIB = 2**30
_UNITS = {"GB": GIB, "MB": 2**20, "g": GIB}


def _bytes(value: str) -> int:
    for suffix, scale in _UNITS.items():
        if value.endswith(suffix):
            return int(value.removesuffix(suffix)) * scale
    raise AssertionError(f"{value!r}: unknown unit")


def _settings(command: list[str]) -> dict[str, str]:
    return dict(kv.split("=", 1) for kv in command[2::2])


def test_argus_config_is_the_parity_protocol_against_argus():
    assert (ARGUS / "scenarios.yaml").read_text() == (
        SUITE / "config" / "scenarios.yaml"
    ).read_text()
    targets = {
        t["name"]: t for t in yaml.safe_load((ARGUS / "targets.yaml").read_text())["targets"]
    }
    parity = {
        t["name"]: t
        for t in yaml.safe_load((SUITE / "config" / "targets.yaml").read_text())["targets"]
    }
    assert set(targets) == {"egernia-local", "argus-local"}
    assert targets["egernia-local"] == parity["egernia-local"]
    assert targets["argus-local"]["server"] == "argus"
    assert targets["argus-local"]["base_url"] == "http://localhost:8082/argus"
    assert targets["argus-local"]["portable_only"]


def test_argus_stack_holds_the_dachs_budget():
    services = yaml.safe_load((SUITE / "docker-compose.argus.yml").read_text())["services"]
    assert set(services) == {"argus", "argus-db"}
    assert {s["cpuset"] for s in services.values()} == {"0-7"}
    memory = {name: _bytes(s["mem_limit"]) for name, s in services.items()}
    assert sum(memory.values()) == 8 * GIB
    assert services["argus"]["image"].startswith("images.opencadc.org/caom2/argus:1.0.27@sha256:")
    assert services["argus"]["ports"] == ["8082:8080"]
    # the database sized to its share by the same rule as egernia's and the
    # scaling run's DaCHS: 1/4, 3/4, and egernia's parallel budget
    tuning = _settings(services["argus-db"]["command"])
    assert _bytes(tuning["shared_buffers"]) == memory["argus-db"] // 4
    assert _bytes(tuning["effective_cache_size"]) == memory["argus-db"] * 3 // 4
    compose = yaml.safe_load((SUITE.parents[1] / "docker-compose.yml").read_text())["services"]
    egernia_db = _settings(compose["db"]["command"])
    for setting in ("max_parallel_workers", "max_worker_processes"):
        assert tuning[setting] == egernia_db[setting]


def test_argus_pools_are_one_connection_per_pinned_core():
    props = dict(
        line.split("=", 1)
        for line in (SUITE / "targets" / "argus" / "config" / "catalina.properties")
        .read_text()
        .splitlines()
        if line and not line.startswith("#")
    )
    assert {
        props[f"org.opencadc.argus.{pool}.maxActive"] for pool in ("uws", "tapadm", "query")
    } == {"8"}
    assert props["tomcat.connector.scheme"] == "http"
    assert props["tomcat.connector.proxyPort"] == "8082"
    assert "ca.nrc.cadc.auth.IdentityManager" not in props  # anonymous


def test_publisher_describes_the_stacks_actually_compared():
    intro = "\n".join(publish.parity_intro(["argus", "egernia"]))
    assert "docker-compose.argus.yml" in intro and "egernia-pins" in intro
    assert "dachs" not in intro.lower()
    assert "tap-compare-argus-db-1" in publish.SERVER_CONTAINERS["argus"]
