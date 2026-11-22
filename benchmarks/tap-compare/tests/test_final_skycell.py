"""The skycell rerun (final-skycell/PROTOCOL.md): the final and scaling
protocols again with egernia's geometry on skycell, plus a backend A/B.

Every check reads the drivers; none runs one (final/PROTOCOL.md,
amendment 1: a script whose purpose is to recreate containers is not a unit
under test).
"""

import json
import pathlib
import re
import subprocess

import yaml
from tap_compare import publish
from test_scaling import _resource_run

SUITE = pathlib.Path(__file__).resolve().parents[1]
HERE = SUITE / "final-skycell"
COMMIT = "0d998bd928e026da05631e6f0e9b3b6dbab7570d"  # skycell v0.58
DRIVERS = ("run.sh", "scaling.sh", "ab.sh")


class _ComposeLoader(yaml.SafeLoader):
    """Reads compose's `!override` tag (replace, don't merge) as its value."""


_ComposeLoader.add_constructor("!override", lambda loader, node: loader.construct_sequence(node))


def _yaml(path: pathlib.Path) -> dict:
    return yaml.load(path.read_text(), Loader=_ComposeLoader)


def test_every_borrowed_pins_file_is_a_byte_copy():
    own = {"skycell.yml", "egernia-ab-pgsphere.yml", "dachs-as-gavo.yml", "dachs-as-gavo.sh"}
    borrowed = sorted(p.name for p in (HERE / "pins").iterdir() if p.name not in own)
    sources = {
        p.name: p for d in ("final", "scaling-three-way") for p in (SUITE / d / "pins").iterdir()
    }
    assert borrowed == sorted(sources)
    for name in borrowed:
        assert (HERE / "pins" / name).read_bytes() == sources[name].read_bytes(), name


def test_the_workload_is_the_base_protocols_verbatim():
    final = _yaml(SUITE / "final" / "scenarios.yaml")
    three = _yaml(SUITE / "scaling-three-way" / "scenarios.yaml")
    mine = _yaml(HERE / "scenarios.yaml")
    for block in ("corpus", "mix", "guards"):
        assert mine[block] == final[block]
    for name in ("final", "warm", "final-smoke"):
        assert mine["scenarios"][name] == final["scenarios"][name]
    assert mine["scenarios"]["warm"] == three["scenarios"]["warm"]
    assert mine["scenarios"]["scaling3-skycell"] == three["scenarios"]["scaling3"]
    assert mine["scenarios"]["scaling3-skycell-smoke"] == three["scenarios"]["scaling3-smoke"]


def test_the_ab_grid_is_the_final_rung_over_seven_classes():
    scenarios = _yaml(HERE / "scenarios.yaml")["scenarios"]
    ab, final = scenarios["backend-ab"], scenarios["final"]
    assert ab == final  # the same rung shape, ladder, formats and generator
    (classes,) = re.findall(r'^CLASSES="([^"]+)"', (HERE / "ab.sh").read_text(), re.M)
    assert classes.split() == ["Q03", "Q05", "Q06", "Q07", "Q12", "Q13", "mix"]
    rungs = 2 * 7 * len(ab["response_formats"]) * len(ab["ladder"]) * ab["repetitions"]
    assert rungs == 336
    assert "--classes $CLASSES" in (HERE / "ab.sh").read_text()


def test_skycell_is_set_on_both_query_serving_containers():
    services = _yaml(HERE / "pins" / "skycell.yml")["services"]
    assert set(services) == {"tap-api", "tap-executor"}
    for service in services.values():
        assert service["environment"] == {"TAP_GEOMETRY_BACKEND": "skycell"}


def test_every_skycell_compose_call_carries_the_overlay():
    for name in ("run.sh", "scaling.sh"):
        (body,) = re.findall(r"compose_egernia\(\) \{\n(.*?)\n\}", (HERE / name).read_text(), re.S)
        assert '-f "$HERE/pins/skycell.yml"' in body, name
    ab = (HERE / "ab.sh").read_text()
    (sky,) = re.findall(r"compose_sky\(\) \{\n(.*?)\n\}", ab, re.S)
    (pgs,) = re.findall(r"compose_pgs\(\) \{\n(.*?)\n\}", ab, re.S)
    assert "skycell.yml" in sky and "skycell.yml" not in pgs


def test_every_driver_verifies_the_backend_before_timing():
    for name in DRIVERS:
        text = (HERE / name).read_text()
        assert '. "$HERE/backend.sh"' in text, name
        verified = text.index("check_backend" if name != "ab.sh" else "verify $SKY_CONTAINERS")
        assert verified < text.index("--gates-only"), name
    assert (
        "check_backend egernia-db-1 egernia-tap-api-1 egernia-tap-executor-1 skycell"
        in (HERE / "run.sh").read_text()
    )
    ab = (HERE / "ab.sh").read_text()
    assert "verify $SKY_CONTAINERS $SKY_CPUSET skycell" in ab
    assert "verify $PGS_CONTAINERS $PGS_CPUSET pgsphere" in ab


def test_one_skycell_commit_everywhere():
    backend = (HERE / "backend.sh").read_text()
    assert f"SKYCELL_COMMIT={COMMIT}" in backend
    assert "SKYCELL_EXTVERSION=0.50" in backend
    assert COMMIT in (HERE / "pins" / "skycell.yml").read_text()
    assert COMMIT in (HERE / "PROTOCOL.md").read_text()


def test_the_pgsphere_stack_is_phase_a_on_other_cores_and_ports():
    w1 = _yaml(HERE / "pins" / "egernia-w1.yml")["services"]
    pgs = _yaml(HERE / "pins" / "egernia-ab-pgsphere.yml")["services"]
    targets = {t["name"]: t for t in _yaml(HERE / "targets.yaml")["targets"]}
    for name in ("db", "tap-api", "tap-executor"):
        assert pgs[name]["mem_limit"] == w1[name]["mem_limit"]
        assert pgs[name]["cpuset"] == "8-15" and w1[name]["cpuset"] == "0-7"
    assert pgs["tap-api"]["environment"]["TAP_API_WORKERS"] == "1"
    for name in ("tap-api", "tap-executor"):
        assert pgs[name]["environment"]["TAP_GEOMETRY_BACKEND"] == "pgsphere"
        assert (
            pgs[name]["environment"]["TAP_BASE_URL"] == targets["egernia-ab-pgsphere"]["base_url"]
        )
    assert targets["egernia-ab-pgsphere"]["base_url"] == "http://localhost:18080/tap"


def test_the_ab_and_three_way_stacks_refuse_each_other():
    # the A/B's pg_sphere stack takes argus's cores 8-15
    assert "tap-compare-argus-1 tap-compare-argus-db-1" in (HERE / "ab.sh").read_text()
    for name in ("run.sh", "scaling.sh"):
        assert "egernia-pgs-db-1 egernia-pgs-tap-api-1" in (HERE / name).read_text(), name


def test_the_publisher_names_every_egernia_target_by_its_own_pins():
    targets = [t["name"] for t in _yaml(HERE / "targets.yaml")["targets"]]
    for name in (
        "egernia-skycell-w1",
        "egernia-skycell-w8",
        "egernia-ab-skycell",
        "egernia-ab-pgsphere",
    ):
        assert name in targets
        assert "final-skycell" in publish.STACKS[name][0]
    assert publish.SCALING_PROTOCOLS["scaling3-skycell"] == "final-skycell/PROTOCOL.md"
    for name in DRIVERS:
        for target in re.findall(r"egernia-(?:skycell|ab)-[\w-]+", (HERE / name).read_text()):
            assert target in targets, (name, target)


def test_the_pgsphere_stacks_resources_are_its_own(tmp_path):
    """The A/B's second egernia is attributed its own containers, and the
    worker count is read from its own API container."""
    run_dir, row = _resource_run(tmp_path)
    row = {**row, "target": "egernia-ab-pgsphere"}
    samples = run_dir / "samples"
    (old,) = samples.iterdir()
    old.rename(samples / old.name.replace("egernia-local", "egernia-ab-pgsphere"))
    lines = (run_dir / "resources.jsonl").read_text().splitlines()
    renamed = []
    for line in lines:
        rec = json.loads(line)
        rec["container"] = rec["container"].replace("egernia-", "egernia-pgs-")
        renamed.append(json.dumps(rec))
    (run_dir / "resources.jsonl").write_text("\n".join(renamed) + "\n")
    (res,) = publish.resources(run_dir, [row]).values()
    assert res["api_workers"] == 2
    assert res["cpu_cores"] > 2.9
    # the skycell target, with a rung of its own, sees none of the pg_sphere
    # stack's samples: its containers (egernia-*) were never sampled here
    (pgs,) = samples.iterdir()
    (samples / pgs.name.replace("egernia-ab-pgsphere", "egernia-ab-skycell")).write_bytes(
        pgs.read_bytes()
    )
    assert publish.resources(run_dir, [{**row, "target": "egernia-ab-skycell"}]) == {}


# -- amendment 1: the review of PR #220 ------------------------------------


def _refuse(tmp_path, gates: dict | None) -> subprocess.CompletedProcess:
    """Run backend.sh's refuse_cone_disagreement alone: a pure function over
    a gate record, sourced with the drivers' log/fail, recreating nothing."""
    path = tmp_path / "gates.json"
    if gates is not None:
        path.write_text(json.dumps(gates))
    script = (
        'log() { echo "$*"; }; fail() { echo "FAIL $*"; exit 1; }; '
        f'. "{HERE / "backend.sh"}"; refuse_cone_disagreement "{path}"'
    )
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=False)


def test_a_cone_class_disagreement_stops_the_experiment(tmp_path):
    for cone in ("Q05", "Q06", "Q07", "Q12"):
        out = _refuse(tmp_path, {"agreement": {"agreed": [], "disagreed": ["Q03", cone]}})
        assert out.returncode == 1 and cone in out.stdout, cone


def test_other_disagreements_keep_the_base_protocols_exclusion(tmp_path):
    out = _refuse(tmp_path, {"agreement": {"agreed": ["Q05"], "disagreed": ["Q03", "Q11"]}})
    assert out.returncode == 0, out.stdout


def test_a_missing_or_verdictless_gate_record_stops_the_experiment(tmp_path):
    assert _refuse(tmp_path, None).returncode == 1
    assert _refuse(tmp_path, {"targets": {}}).returncode == 1


def test_every_driver_refuses_cone_disagreement_before_timing():
    for name, record in (
        ("run.sh", "gates.json"),
        ("ab.sh", "gates.json"),
        ("scaling.sh", "gates.json"),
    ):
        text = (HERE / name).read_text()
        refuse = text.index('refuse_cone_disagreement "$SUITE/results/$RUN_NAME/')
        assert record in text[refuse : text.index("\n", refuse)], name
        assert text.rindex("--gates-only") < refuse < text.index("--scenario warm"), name
    assert '/t$tier-gates.json"' in (HERE / "scaling.sh").read_text()


def test_smoke_scenarios_are_driven_over_the_mix_only():
    scenarios = _yaml(HERE / "scenarios.yaml")["scenarios"]
    for smoke, driver in (("backend-ab-smoke", "ab.sh"), ("scaling3-skycell-smoke", "scaling.sh")):
        assert not scenarios[smoke].get("per_class"), smoke  # the mix is all it runs
        text = (HERE / driver).read_text()
        assert re.search(
            rf'if \[ "\$SCENARIO" = {smoke} \]; then CLASSES=(\$\{{CLASSES:-)?mix', text
        )


def test_the_pgsphere_reproduction_starts_no_second_prometheus():
    command = publish.STACKS["egernia-ab-pgsphere"][1]
    assert command.rstrip().endswith("up -d db tap-api tap-executor")


# -- amendment 2: DaCHS stopped answering mid phase B ------------------------

MEASURERS = ("run.sh", "scaling.sh")  # experiments 2 and 3; the A/B is done


def test_every_dachs_bringup_starts_from_an_empty_job_table():
    for name in MEASURERS:
        (body,) = re.findall(r"up_dachs\(\) \{\n(.*?)\n\}", (HERE / name).read_text(), re.S)
        assert body.rstrip().endswith("clear_dachs_jobs  # amendment 2"), name
    assert "delete from tap_schema.tapjobs" in (HERE / "backend.sh").read_text()


def test_every_measuring_compare_carries_the_abort_ceiling():
    assert "ABORT_ERROR_FRACTION=0.5" in (HERE / "backend.sh").read_text()
    for name in MEASURERS:
        calls = re.findall(r"^\s*tap compare .*?(?<!\\)\n", (HERE / name).read_text(), re.S | re.M)
        measuring = [c for c in calls if "--gates-only" not in c]
        assert measuring, name
        for call in measuring:
            assert '--abort-error-fraction "$ABORT_ERROR_FRACTION"' in call, (name, call)


def test_a_stopped_run_keeps_its_servers_logs():
    for name in MEASURERS:
        text = (HERE / name).read_text()
        sourced = text.index('. "$HERE/backend.sh"')
        trap = text.index("trap stop_and_keep_logs EXIT INT TERM")
        assert sourced < trap < text.index("--gates-only"), name


class _Run:
    def __init__(self, path):
        self.path = path

    def write_json(self, name, payload):
        (self.path / name).parent.mkdir(parents=True, exist_ok=True)
        (self.path / name).write_text(json.dumps(payload))


def test_a_failing_rung_stops_the_run_with_a_probe(tmp_path, monkeypatch):
    import httpx
    import pytest
    from tap_compare import cli
    from tap_compare.corpus import CorpusEntry
    from tap_compare.targets import Target

    sent = {}

    def post(url, data, timeout):
        sent.update(url=url, data=data)
        return httpx.Response(500, text="<VOTABLE>pool exhausted</VOTABLE>")

    monkeypatch.setattr(httpx, "post", post)
    entries = [CorpusEntry("a", "Q01", "SELECT 1"), CorpusEntry("b", "Q11", "SELECT 11")]
    target = Target("dachs-final", "dachs", "http://localhost:8081/tap")
    summary = {"error_fraction": 1.0, "requests": 10}
    with pytest.raises(SystemExit, match="over the abort ceiling"):
        cli._abort_failing_rung(
            _Run(tmp_path),
            "dachs-final-votable-Q11-c8-r3",
            summary,
            target,
            entries,
            "Q11",
            "votable",
            10000,
        )
    assert sent["url"] == "http://localhost:8081/tap/sync"
    assert sent["data"]["QUERY"] == "SELECT 11" and sent["data"]["MAXREC"] == "10000"
    record = json.loads((tmp_path / "aborted" / "dachs-final-votable-Q11-c8-r3.json").read_text())
    assert record["probe"]["status"] == 500 and "pool exhausted" in record["probe"]["body"]
    assert not (tmp_path / "summaries").exists()


def test_an_aborted_rung_is_never_marked_done():
    source = (SUITE / "tap_compare" / "cli.py").read_text()
    loop = source[source.index("def cmd_compare") : source.index("def _abort_failing_rung")]
    abort = loop.index("_abort_failing_rung(")
    assert abort < loop.index('run.write_json(f"summaries/') < loop.index("run.mark_done(key")


# -- amendment 3: DaCHS serves as gavo, not root ------------------------------


def test_every_dachs_compose_call_serves_as_gavo():
    for name in MEASURERS:
        (body,) = re.findall(r"compose_dachs\(\) \{\n(.*?)\n\}", (HERE / name).read_text(), re.S)
        assert '-f "$HERE/pins/dachs-as-gavo.yml"' in body, name
    overlay = _yaml(HERE / "pins" / "dachs-as-gavo.yml")["services"]["dachs"]
    assert overlay["entrypoint"] == ["/bin/bash", "/dachs-as-gavo.sh"]
    assert overlay["volumes"] == ["./final-skycell/pins/dachs-as-gavo.sh:/dachs-as-gavo.sh:ro"]
    assert (SUITE / "final-skycell" / "pins" / "dachs-as-gavo.sh").is_file()


def test_the_dachs_user_is_checked_before_the_job_table_is_cleared():
    for name in MEASURERS:
        (body,) = re.findall(r"up_dachs\(\) \{\n(.*?)\n\}", (HERE / name).read_text(), re.S)
        assert body.index("check_dachs_user") < body.index("clear_dachs_jobs"), name
    assert (
        '"$(docker exec tap-compare-dachs-1 ps -o user= -p 1' in (HERE / "backend.sh").read_text()
    )


def test_the_wrapper_changes_only_the_images_last_line(tmp_path):
    """The wrapper's sed, run over the image's entrypoint: exactly one line
    differs, and it is the serve line, now under setpriv as gavo."""
    wrapper = (HERE / "pins" / "dachs-as-gavo.sh").read_text()
    (expr,) = re.findall(r"sed '([^']+)'", wrapper)
    source = SUITE / "targets" / "dachs" / "entrypoint.sh"
    out = subprocess.run(["sed", expr, str(source)], capture_output=True, text=True, check=True)
    before, after = source.read_text().splitlines(), out.stdout.splitlines()
    changed = [(a, b) for a, b in zip(before, after, strict=True) if a != b]
    assert changed == [
        (
            "exec dachs serve debug",
            "exec setpriv --reuid=gavo --regid=gavo --init-groups dachs serve debug",
        )
    ]
    assert "grep -qx 'exec setpriv --reuid=gavo" in wrapper  # refuses a changed image
