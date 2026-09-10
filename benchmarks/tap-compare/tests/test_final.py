"""The final three-way comparison (final/PROTOCOL.md): the parity workload on
three servers pinned to disjoint cores, in two phases that differ only in
egernia's worker count — and the two things three targets need from the
harness, a unanimous agreement gate and a verdict over more than two.
"""

import json
import pathlib
import re

import pytest
import yaml
from tap_compare import corpus as corpus_mod
from tap_compare import publish, validate

SUITE = pathlib.Path(__file__).resolve().parents[1]
FINAL = SUITE / "final"
GIB = 2**30
POOL = 8  # connections per process (config.dbPoolMax), unchanged
PER_GATHER = 2
CORPUS_SHA = "bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007"
CPUSETS = {"egernia": "0-7", "argus": "8-15", "dachs": "16-23"}
GENERATOR_CORES = set(range(24, 30))

_UNITS = {"GB": GIB, "MB": 2**20, "g": GIB}


def _bytes(value: str) -> int:
    for suffix, scale in _UNITS.items():
        if value.endswith(suffix):
            return int(value.removesuffix(suffix)) * scale
    raise AssertionError(f"{value!r}: unknown unit")


def _services(name: str) -> dict:
    return yaml.safe_load((FINAL / "pins" / f"{name}.yml").read_text())["services"]


def _cores(spec: str) -> set[int]:
    lo, hi = spec.split("-")
    return set(range(int(lo), int(hi) + 1))


def _flags(service: dict) -> dict:
    """The `postgres -c name=value` settings of a compose service's command."""
    return dict(kv.split("=", 1) for kv in service["command"][2::2])


# -- the protocol: workload, cores, shapes -----------------------------------


def test_final_scenarios_keep_the_parity_workload():
    parity = yaml.safe_load((SUITE / "config" / "scenarios.yaml").read_text())
    final = yaml.safe_load((FINAL / "scenarios.yaml").read_text())
    for block in ("corpus", "mix", "guards"):
        assert final[block] == parity[block]
    grid = final["scenarios"]["final"]
    compare = parity["scenarios"]["compare"]
    assert grid["per_class"] and grid["repetitions"] == compare["repetitions"] == 3
    assert grid["response_formats"] == compare["response_formats"]
    assert grid["maxrec"] == compare["maxrec"]
    # the reduction: a subset of the parity ladder, and the scaling protocol's
    # windows (PROTOCOL.md, "The grid and its wall-clock")
    assert grid["ladder"] == [1, 4, 8, 32]
    assert set(grid["ladder"]) < set(compare["ladder"])
    scaling = yaml.safe_load((SUITE / "scaling" / "scenarios.yaml").read_text())
    for key in ("warmup_seconds", "measure_seconds"):
        assert grid[key] == scaling["scenarios"]["scaling"][key]
    # 3 targets x 12 classes x 2 formats x 4 concurrencies x 3 repetitions
    rungs = 3 * 12 * len(grid["response_formats"]) * len(grid["ladder"]) * grid["repetitions"]
    assert rungs == 864
    per_rung = grid["warmup_seconds"] + grid["measure_seconds"]
    assert 2 * rungs * (per_rung + 6) / 3600 < 50  # both phases inside the budget


def test_the_three_stacks_run_on_disjoint_cores_and_leave_the_generator_alone():
    stacks = {
        "egernia": _services("egernia-w1"),
        "egernia-b": _services("egernia-w8"),
        "argus": _services("argus"),
        "dachs": _services("dachs"),
    }
    cores = {}
    for stack, services in stacks.items():
        pinned = {s["cpuset"] for s in services.values()}
        assert len(pinned) == 1, f"{stack}: its containers must share one cpuset"
        cores[stack] = _cores(pinned.pop())
        assert len(cores[stack]) == 8  # the same core budget for every server
        assert not (cores[stack] & GENERATOR_CORES)
    assert cores["egernia"] == cores["egernia-b"] == _cores(CPUSETS["egernia"])
    assert cores["argus"] == _cores(CPUSETS["argus"])
    assert cores["dachs"] == _cores(CPUSETS["dachs"])
    assert not (cores["egernia"] & cores["argus"])
    assert not (cores["egernia"] & cores["dachs"])
    assert not (cores["argus"] & cores["dachs"])
    # 24 server cores + 6 generator cores = the host
    assert len(cores["egernia"] | cores["argus"] | cores["dachs"] | GENERATOR_CORES) == 30


def test_phase_a_is_the_published_parity_shape_with_the_worker_count_written_down():
    parity = yaml.safe_load((SUITE / "docker-compose.egernia-pins.yml").read_text())["services"]
    phase_a = _services("egernia-w1")
    assert set(phase_a) == set(parity)
    for name, service in parity.items():
        assert phase_a[name]["cpuset"] == service["cpuset"]
        assert phase_a[name]["mem_limit"] == service["mem_limit"]
    assert phase_a["tap-api"]["environment"]["TAP_API_WORKERS"] == "1"
    # the database is docker-compose.yml's: phase A overrides no PostgreSQL setting
    assert "command" not in phase_a["db"]


def test_phase_b_is_phase_a_plus_eight_workers_by_the_documented_rules():
    phase_a, phase_b = _services("egernia-w1"), _services("egernia-w8")
    assert set(phase_a) == set(phase_b)
    for name in phase_a:
        assert phase_b[name]["cpuset"] == phase_a[name]["cpuset"]
        assert phase_b[name]["mem_limit"] == phase_a[name]["mem_limit"]  # split unchanged
    workers = int(phase_b["tap-api"]["environment"]["TAP_API_WORKERS"])
    assert workers == 8  # one per pinned core
    assert "TAP_DB_POOL_MAX" not in phase_b["tap-api"].get("environment", {})
    # docs/postgres-performance.md's rule for the resulting pool total; the
    # rest of the db command is docker-compose.yml's
    compose = yaml.safe_load((SUITE.parents[1] / "docker-compose.yml").read_text())["services"]
    base, tuning = _flags(compose["db"]), _flags(phase_b["db"])
    pools = (workers + 1) * POOL  # API workers + one executor
    assert pools < 100  # PostgreSQL's default max_connections
    assert int(tuning["max_parallel_workers"]) == pools * PER_GATHER == 144
    assert int(tuning["max_worker_processes"]) == int(tuning["max_parallel_workers"]) + 8
    for setting in ("shared_buffers", "effective_cache_size", "work_mem"):
        assert tuning[setting] == base[setting]
    assert _bytes(tuning["shared_buffers"]) == _bytes(phase_b["db"]["mem_limit"]) // 4
    # the documented memory floor fits the API's unchanged share
    assert 140 * workers + workers * POOL * 2.5 < _bytes(phase_b["tap-api"]["mem_limit"]) / 2**20
    # this is argus-equal-cpu's rule, reused rather than re-derived
    equalcpu = yaml.safe_load((SUITE / "argus-equal-cpu" / "egernia-equalcpu.yml").read_text())
    assert _flags(equalcpu["services"]["db"]) == tuning
    assert equalcpu["services"]["tap-api"]["environment"] == phase_b["tap-api"]["environment"]


def test_dachs_keeps_its_budget_and_gets_the_quarter_rule():
    parity = yaml.safe_load((SUITE / "docker-compose.dachs.yml").read_text())["services"]["dachs"]
    dachs = _services("dachs")["dachs"]
    assert dachs["cpus"] == parity["cpus"] == 8
    assert _bytes(dachs["mem_limit"]) == _bytes(parity["mem_limit"]) == 8 * GIB
    conf = dict(
        line.replace(" ", "").split("=", 1)
        for line in (FINAL / "pins" / "dachs-postgres.conf").read_text().splitlines()
        if line and not line.startswith("#")
    )
    assert _bytes(conf["shared_buffers"]) == 8 * GIB // 4
    assert _bytes(conf["effective_cache_size"]) == 8 * GIB * 3 // 4
    # the same parallel budget egernia's and argus's databases get at this budget
    argus_db = yaml.safe_load((SUITE / "docker-compose.argus.yml").read_text())
    for setting in ("max_parallel_workers", "max_worker_processes"):
        assert conf[setting] == _flags(argus_db["services"]["argus-db"])[setting]
    (mount,) = [v for v in dachs["volumes"] if "dachs-postgres.conf" in v]
    assert mount.endswith("/conf.d/90-final.conf:ro")


def test_argus_pins_are_the_equal_cpu_amendments_disjoint_cores():
    assert (
        _services("argus")
        == yaml.safe_load((SUITE / "argus-equal-cpu" / "argus-disjoint.yml").read_text())[
            "services"
        ]
    )


def test_targets_are_three_servers_in_four_shapes():
    targets = {
        t["name"]: t for t in yaml.safe_load((FINAL / "targets.yaml").read_text())["targets"]
    }
    assert set(targets) == {"egernia-final-w1", "egernia-final-w8", "dachs-final", "argus-final"}
    assert [t["server"] for t in targets.values()].count("egernia") == 2
    assert all(t["portable_only"] for t in targets.values())
    # the two egernia shapes are the same deployment at the same URL
    assert targets["egernia-final-w1"]["base_url"] == targets["egernia-final-w8"]["base_url"]
    # the opponents' URLs are the ones their own protocols established
    assert targets["dachs-final"]["base_url"] == "http://localhost:8081/tap"
    assert targets["argus-final"]["base_url"] == "http://localhost/argus"


def test_the_driver_and_the_pins_agree_on_every_placement():
    """The driver refuses to measure a stack that is not where the protocol
    put it — so its expectations must be the pins' own."""
    script = (FINAL / "run.sh").read_text()

    def setting(name):
        return re.search(rf"^{name}=(\S+)$", script, re.M).group(1)

    for server, cpuset in CPUSETS.items():
        assert setting(f"{server.upper()}_CPUSET") == cpuset
    assert setting("EXPECTED_CORPUS_SHA") == CORPUS_SHA
    assert setting("EXPECTED_ROWS") == "500096"
    assert setting("GEN_CPUS") == "${GEN_CPUS:-24-29}"
    # both phases, and the checks that make a phase trustworthy
    for needle in (
        "pins/egernia-w1.yml",
        "pins/egernia-w8.yml",
        "truncate uws.jobdetail, uws.job",  # argus starts each phase fresh
        "egernia-tap-executor-1",  # PR #161 routes queries in both containers
        "TAP_QUERY_DATABASE_URL",  # one database: PR #161 must be inert
        "relkind",  # PR #160's ivoa.obscore is a table
        "work_mem",  # every setting the pins promise, not just most of them
        "record_host",  # the override and the neighbours reach the report
        "stop_sampler",  # the sampler loops forever: one phase, one sampler
        "--gates-only",
    ):
        assert needle in script


def test_the_driver_validates_the_generator_affinity_before_anything_else():
    """A generator on a measured stack's cores would report its own
    contention as the server's, so the driver expands GEN_CPUS and refuses an
    overlap. Checked statically and never by executing run.sh: the script's
    job is to recreate containers, so a test must not run it (learned the
    hard way on 2026-09-10 — see PROTOCOL.md's amendment 1)."""
    script = (FINAL / "run.sh").read_text()
    validator = script[script.index("GEN_CORES=$(") : script.index("|| fail_early")]
    assert "EGERNIA_CPUSET" in validator and "ARGUS_CPUSET" in validator
    assert "DACHS_CPUSET" in validator
    assert "generator & servers" in validator  # the overlap is what refuses
    # it runs before the main body — nothing is created or timed until it has
    assert script.index("GEN_CORES=$(") < script.index('log "PROGRESS start')
    # and the driver refuses to start while another measurement holds the box
    assert "another tap-compare measurement" in script


# -- the harness: a unanimous gate and a three-way verdict -------------------


def _entries():
    return [
        corpus_mod.CorpusEntry("q-Q05-1", "Q05", "SELECT TOP 10 obs_publisher_did FROM x"),
        corpus_mod.CorpusEntry("q-Q01-1", "Q01", "SELECT table_name FROM tap_schema.tables"),
    ]


THREE = {"egernia-final-w1": "http://e", "dachs-final": "http://d", "argus-final": "http://a"}


def _agreement(answers, monkeypatch):
    """Run the gate over three targets, ``answers`` mapping url -> csv text."""
    monkeypatch.setattr(validate, "probe", lambda url, adql, maxrec, **kw: answers[url](adql))
    return validate.agreement(THREE, _entries(), maxrec=100)


def test_three_targets_agree_only_unanimously(monkeypatch):
    same = validate.fingerprint("obs_publisher_did\nivo://x/1\nivo://x/2\n")
    listing = validate.fingerprint("table_name\ntap_schema.tables\n")

    def answer(adql):
        return listing if "tap_schema" in adql else same

    verdict = _agreement(dict.fromkeys(THREE.values(), answer), monkeypatch)
    assert verdict["agreed"] == ["Q01", "Q05"] and verdict["disagreed"] == []


@pytest.mark.parametrize("dissenter", sorted(THREE.values()))
def test_one_dissenter_out_of_three_fails_the_class(monkeypatch, dissenter):
    """No target is the reference: any one of the three disagreeing excludes
    the class, and the other two agreeing does not rescue it."""
    same = validate.fingerprint("obs_publisher_did\nivo://x/1\nivo://x/2\n")
    short = validate.fingerprint("obs_publisher_did\nivo://x/1\n")
    listing = validate.fingerprint("table_name\ntap_schema.tables\n")
    answers = {
        url: (
            lambda adql, url=url: (
                listing if "tap_schema" in adql else (short if url == dissenter else same)
            )
        )
        for url in THREE.values()
    }
    verdict = _agreement(answers, monkeypatch)
    assert verdict["disagreed"] == ["Q05"] and verdict["agreed"] == ["Q01"]


def test_an_error_from_any_of_the_three_fails_the_class(monkeypatch):
    same = validate.fingerprint("obs_publisher_did\nivo://x/1\n")
    answers = {url: (lambda adql: same) for url in THREE.values()}
    answers["http://a"] = lambda adql: {"error": "HTTP 500", "body": ""}
    verdict = _agreement(answers, monkeypatch)
    assert verdict["disagreed"] == ["Q01", "Q05"]  # Q01 is status-only, and it errored


def _cell(rps, errors=0.0, guard_ok=True, spread=0.5):
    return {
        "rps": {"mean": rps, "ci95_low": rps - spread, "ci95_high": rps + spread},
        "p95": {"mean": 0.1, "ci95_low": 0.09, "ci95_high": 0.11},
        "errors": errors,
        "guard_ok": guard_ok,
        "reps": 3,
    }


def _keys(*names):
    return tuple(("Q05", "votable", 8, name) for name in names)


def test_a_three_way_winner_must_beat_every_other_target():
    keys = _keys("egernia-final-w1", "dachs-final", "argus-final")
    cells = dict(zip(keys, [_cell(200.0), _cell(10.0), _cell(150.0)], strict=True))
    assert publish.verdict(cells, *keys) == "egernia-final-w1"
    # the runner-up within the 10% floor: the leading group is indistinguishable
    cells[keys[2]] = _cell(190.0)
    assert publish.verdict(cells, *keys) == "tie"


def test_three_way_ties_and_invalid_cells_follow_the_parity_rule():
    keys = _keys("egernia-final-w1", "dachs-final", "argus-final")
    # a target erroring beyond the ceiling cannot win, but a clean one still can
    cells = dict(zip(keys, [_cell(500.0, errors=0.5), _cell(10.0), _cell(150.0)], strict=True))
    assert publish.verdict(cells, *keys) == "argus-final"
    # every target erroring, or any tripped generator guard, voids the cell
    cells = dict(
        zip(
            keys,
            [_cell(500.0, errors=0.5), _cell(10.0, errors=0.5), _cell(150.0, errors=0.5)],
            strict=True,
        )
    )
    assert publish.verdict(cells, *keys) == "invalid"
    cells = dict(zip(keys, [_cell(200.0), _cell(10.0), _cell(150.0, guard_ok=False)], strict=True))
    assert publish.verdict(cells, *keys) == "invalid"


def test_the_publisher_names_the_final_pins():
    rows = [
        {"target": "egernia-final-w8", "server": "egernia"},
        {"target": "dachs-final", "server": "dachs"},
        {"target": "argus-final", "server": "argus"},
    ]
    keys = publish.stack_keys(rows)
    assert keys == ["argus-final", "dachs-final", "egernia-final-w8"]
    intro = "\n".join(publish.parity_intro(keys))
    assert "egernia-w8.yml" in intro and "TAP_API_WORKERS=8" in intro
    assert "final/pins/dachs.yml" in intro and "final/pins/argus.yml" in intro


def test_a_three_target_report_still_names_a_winner_per_cell(tmp_path):
    """The regression this run needed: the publisher used to print `—` in the
    verdict column for anything but exactly two targets."""
    run_dir = tmp_path / "20260910T000000Z-abc12345-tap-compare"
    run_dir.mkdir()
    rows = []
    for rep, (e, d, a) in enumerate([(200, 10, 150), (201, 11, 151), (199, 10, 149)], start=1):
        for target, server, rps in (
            ("egernia-final-w1", "egernia", e),
            ("dachs-final", "dachs", d),
            ("argus-final", "argus", a),
        ):
            rows.append(
                {
                    "target": target,
                    "server": server,
                    "query_class": "Q05",
                    "response_format": "csv",
                    "concurrency": 8,
                    "repetition": rep,
                    "requests": 100,
                    "error_fraction": 0.0,
                    "rps": float(rps),
                    "latency": {"p50_s": 0.05, "p95_s": 0.1},
                    "ttfb": {"p95_s": 0.03},
                    "mean_response_bytes": 1000.0,
                    "generator_cpu_peak": 0.2,
                    "generator_guard_ok": True,
                }
            )
    (run_dir / "summary.json").write_text(json.dumps(rows))
    (run_dir / "environment.json").write_text(
        json.dumps({"git": {"sha": "abc12345dead"}, "seed": 424242, "corpus_sha256": "c" * 64})
    )
    (run_dir / "gates.json").write_text(
        json.dumps(
            {
                "targets": {
                    name: {
                        "vosi": {"tap_versions": ["1.1"], "maxrec_default": 10000},
                        "taplint": {"passed": True, "errors_total": 0},
                    }
                    for name in ("egernia-final-w1", "dachs-final", "argus-final")
                },
                "agreement": {"agreed": ["Q05"], "disagreed": []},
            }
        )
    )
    text = publish.render(run_dir, tmp_path / "docs").read_text()
    assert "| Q05 | 8 |" in text and "egernia-final-w1 |" in text
    # all three servers in the table, one verdict column
    for name in ("egernia-final-w1", "dachs-final", "argus-final"):
        assert f"{name} rps" in text
    (row,) = [line for line in text.splitlines() if line.startswith("| Q05 | 8 |")]
    assert row.rstrip().endswith("| egernia-final-w1 |")
