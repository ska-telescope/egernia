"""Provenance on resume: written once, never overwritten, corpus pinned."""

import json

import pytest
from tap_compare import cli, runs


class _Entry:
    def as_dict(self):
        return {"query_class": "Q01", "query_id": "q01-000", "adql": "SELECT 1"}


def _record(run, sha, target=None, scenario_name="compare", scenario=None):
    cli._record_provenance(
        run,
        target or {"name": "egernia-local"},
        {"corpus": {"seed": 1}},
        sha,
        scenario_name,
        scenario or {"ladder": [1]},
        [_Entry()],
    )


def test_provenance_written_once_and_kept_on_resume(tmp_path):
    run = runs.Run(path=tmp_path, scenario="compare")
    _record(run, "aaa111")
    first = (tmp_path / "environment.json").read_text()
    _record(run, "aaa111")  # a resume with the same corpus changes nothing
    assert (tmp_path / "environment.json").read_text() == first
    assert json.loads(first)["corpus_sha256"] == "aaa111"


def test_resume_with_a_different_corpus_is_refused(tmp_path):
    run = runs.Run(path=tmp_path, scenario="compare")
    _record(run, "aaa111")
    with pytest.raises(SystemExit, match="corpus"):
        _record(run, "bbb222")


def test_resume_with_a_different_scenario_is_refused(tmp_path):
    run = runs.Run(path=tmp_path, scenario="compare")
    _record(run, "aaa111")
    with pytest.raises(SystemExit, match="scenario"):
        _record(run, "aaa111", scenario_name="compare-demo")
    with pytest.raises(SystemExit, match="scenario"):
        _record(run, "aaa111", scenario={"ladder": [1, 4]})


def test_resume_under_different_code_is_recorded_not_refused(tmp_path):
    run = runs.Run(path=tmp_path, scenario="compare")
    _record(run, "aaa111")
    env_path = tmp_path / "environment.json"
    recorded = json.loads(env_path.read_text())
    recorded["git"]["sha"] = "somethingelse"  # the run started from other code
    env_path.write_text(json.dumps(recorded))
    _record(run, "aaa111")
    after = json.loads(env_path.read_text())
    assert after["git"]["sha"] == "somethingelse"  # the original record stands
    assert after["resumed"][-1]["sha"] == runs.git_sha()


def test_resume_with_different_targets_is_refused(tmp_path):
    run = runs.Run(path=tmp_path, scenario="compare")
    _record(run, "aaa111")
    with pytest.raises(SystemExit, match="target"):
        _record(run, "aaa111", target={"name": "dachs-local"})


def test_classes_filter_keeps_scenario_order_and_refuses_unknown_names():
    assert cli._select_classes(["Q01", "Q02", "Q03"], None) == ["Q01", "Q02", "Q03"]
    assert cli._select_classes(["Q01", "Q02", "Q03"], ["Q03", "Q01"]) == ["Q01", "Q03"]
    assert cli._select_classes([None], None) == [None]
    with pytest.raises(SystemExit, match="Q99"):
        cli._select_classes(["Q01"], ["Q99"])


def test_a_comparisons_mixed_workload_is_selected_by_the_name_it_is_published_under():
    """A comparison's class list carries the mix as None; on the command line
    and in every rung key and table it is `mix`, so --classes uses that."""
    classes = [None, "Q01", "Q05", "Q11", "Q13"]
    assert cli._select_classes(classes, ["Q01", "Q05", "Q11", "Q13", "mix"]) == classes
    assert cli._select_classes(classes, ["mix"]) == [None]
    assert cli._select_classes(classes, ["Q05"]) == ["Q05"]
    with pytest.raises(SystemExit, match="mix"):  # the offer names it too
        cli._select_classes(classes, ["Q99"])


def test_compare_accepts_the_same_classes_flag_as_run(capsys):
    """The option belongs on both commands that loop over classes, not only
    the one that happened to need it first."""
    for command in ("run", "compare"):
        with pytest.raises(SystemExit):
            cli.main([command, "--help"])
        assert "--classes" in capsys.readouterr().out
