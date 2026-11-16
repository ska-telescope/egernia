"""The skycell rerun (final-skycell/PROTOCOL.md): the final and scaling
protocols again with egernia's geometry on skycell, plus a backend A/B.

Every check reads the drivers; none runs one (final/PROTOCOL.md,
amendment 1: a script whose purpose is to recreate containers is not a unit
under test).
"""

import json
import pathlib
import re

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
    own = {"skycell.yml", "egernia-ab-pgsphere.yml"}
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
