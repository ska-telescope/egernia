"""Release publishing tests never contact Zenodo or require credentials."""

import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError

import pytest
import yaml

from scripts import publish_zenodo as zenodo

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def release():
    return {
        "tagName": "v0.1.0",
        "publishedAt": "2026-09-19T12:00:00Z",
        "isDraft": False,
        "isPrerelease": False,
        "url": f"{zenodo.REPOSITORY}/releases/tag/v0.1.0",
    }


@pytest.fixture
def metadata(release):
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    return zenodo.metadata_for(citation, release)


@pytest.fixture
def archive(tmp_path):
    path = tmp_path / "egernia.zip"
    path.write_bytes(b"test archive")
    return path


def record(metadata, *, id=10, submitted=False, version=None, concept=1):
    return {
        "id": id,
        "conceptrecid": concept,
        "submitted": submitted,
        "metadata": {**metadata, "version": version or metadata["version"]},
        "files": [],
        "links": {
            "bucket": "https://sandbox.zenodo.org/api/files/bucket",
            "html": f"https://sandbox.zenodo.org/records/{id}",
        },
    }


def test_metadata_uses_citation_and_release(metadata):
    assert metadata["creators"] == [
        {"name": "Delli Veneri, Michele", "affiliation": "SKA Observatory"}
    ]
    assert metadata["license"] == "mit"
    assert metadata["upload_type"] == "software"
    assert metadata["version"] == "v0.1.0"
    assert metadata["publication_date"] == "2026-09-19"


@pytest.mark.parametrize(
    "change",
    [{"isDraft": True}, {"isPrerelease": True}, {"publishedAt": None}, {"url": "https://other"}],
)
def test_invalid_release_is_rejected(release, change):
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    with pytest.raises(ValueError):
        zenodo.metadata_for(citation, release | change)


def test_first_release_publishes_only_after_upload(metadata, archive):
    draft = record(metadata)
    published = record(metadata, submitted=True)
    client = Mock()
    client.deposits.return_value = []
    client.request.side_effect = [draft, draft, {}, published]
    assert zenodo.deposit_release(client, metadata, archive, publish=True) == published
    calls = client.request.call_args_list
    assert calls[0].args == ("POST", "/api/deposit/depositions")
    assert calls[0].kwargs["payload"]["metadata"] == metadata
    assert calls[2].args == ("PUT", draft["links"]["bucket"] + "/egernia.zip")
    assert calls[3].args == ("POST", "/api/deposit/depositions/10/actions/publish")


def test_manual_draft_does_not_publish(metadata, archive):
    draft = record(metadata)
    client = Mock()
    client.deposits.return_value = []
    client.request.side_effect = [draft, draft, {}, draft]
    assert zenodo.deposit_release(client, metadata, archive, publish=False) == draft
    assert not any("/actions/publish" in call.args[1] for call in client.request.call_args_list)


def test_published_retry_is_noop_even_with_later_versions(metadata, archive):
    published = record(metadata, submitted=True)
    client = Mock()
    client.deposits.return_value = [
        published,
        record(metadata, id=11, submitted=True, version="v0.2.0"),
    ]
    assert zenodo.deposit_release(client, metadata, archive, publish=True) == published
    client.request.assert_not_called()


def test_new_version_uses_latest_draft_and_removes_inherited_files(metadata, archive):
    old = record(metadata, id=9, submitted=True, version="v0.0.9")
    draft = record(metadata)
    draft["files"] = [{"id": "old-source"}]
    client = Mock()
    client.deposits.return_value = [old]
    client.request.side_effect = [
        {"links": {"latest_draft": "https://sandbox.zenodo.org/api/deposit/depositions/10"}},
        draft,
        draft,
        None,
        {},
        record(metadata, submitted=True),
    ]
    zenodo.deposit_release(client, metadata, archive, publish=True)
    calls = client.request.call_args_list
    assert calls[0].args == ("POST", "/api/deposit/depositions/9/actions/newversion")
    assert calls[1].args == ("GET", "https://sandbox.zenodo.org/api/deposit/depositions/10")
    assert calls[3].args == ("DELETE", "/api/deposit/depositions/10/files/old-source")
    assert calls[-1].args == ("POST", "/api/deposit/depositions/10/actions/publish")


@pytest.mark.parametrize("inherited", [False, True])
def test_retry_resumes_draft(metadata, archive, inherited):
    old = record(metadata, id=9, submitted=True, version="v0.0.9")
    draft = record(metadata, version="v0.0.9" if inherited else None)
    draft["files"] = [{"id": "partial"}]
    client = Mock()
    client.deposits.return_value = [old, draft]
    client.request.side_effect = [draft, None, {}, draft]
    zenodo.deposit_release(client, metadata, archive, publish=False)
    assert client.request.call_args_list[0].args == ("PUT", "/api/deposit/depositions/10")
    assert not any(call.args[0] == "POST" for call in client.request.call_args_list)


@pytest.mark.parametrize("conflict", ["families", "drafts", "other-release"])
def test_ambiguous_deposits_fail_before_writes(metadata, archive, conflict):
    first = record(metadata)
    second = record(metadata, id=11, concept=2 if conflict == "families" else 1)
    deposits = [first, second]
    if conflict == "other-release":
        deposits = [record(metadata, version="v9.9.9")]
    client = Mock()
    client.deposits.return_value = deposits
    with pytest.raises(ValueError):
        zenodo.deposit_release(client, metadata, archive, publish=True)
    client.request.assert_not_called()


def test_upload_failure_cannot_publish(metadata, archive):
    client = Mock()
    client.deposits.return_value = []
    client.request.side_effect = [record(metadata), {}, RuntimeError("upload failed")]
    with pytest.raises(RuntimeError, match="upload failed"):
        zenodo.deposit_release(client, metadata, archive, publish=True)
    assert not any("/actions/publish" in call.args[1] for call in client.request.call_args_list)


def test_pagination_includes_all_versions():
    client = zenodo.Zenodo("zenodo-sandbox", "test-token")
    client.request = Mock(side_effect=[[{"id": i} for i in range(100)], [{"id": 100}]])
    assert len(list(client.deposits())) == 101
    assert "page=2" in client.request.call_args.args[1]
    assert "all_versions=true" in client.request.call_args.args[1]


def test_token_stays_on_selected_host():
    client = zenodo.Zenodo("zenodo-sandbox", "test-token")
    with pytest.raises(ValueError, match="different host"):
        client.request("GET", "https://zenodo.org/api/deposit/depositions/1")


def test_http_failure_does_not_disclose_token(monkeypatch):
    client = zenodo.Zenodo("zenodo-sandbox", "test-token")
    error = HTTPError("https://sandbox.zenodo.org", 401, "test-token", {}, io.BytesIO())
    monkeypatch.setattr(zenodo, "urlopen", Mock(side_effect=error))
    with pytest.raises(RuntimeError, match="HTTP 401") as caught:
        client.request("GET", "/api/deposit/depositions")
    assert "test-token" not in str(caught.value)


def test_file_upload_sends_binary_stream_headers(monkeypatch, archive):
    client = zenodo.Zenodo("zenodo-sandbox", "test-token")

    def accept_upload(request, *, timeout):
        assert request.get_method() == "PUT"
        assert request.get_header("Content-type") == "application/octet-stream"
        assert request.get_header("Content-length") == str(archive.stat().st_size)
        assert request.get_header("Authorization") == "Bearer test-token"
        assert request.get_header("Transfer-encoding") is None
        assert request.data.read() == archive.read_bytes()
        assert timeout == 120
        return io.BytesIO(b'{"key": "egernia.zip"}')

    monkeypatch.setattr(zenodo, "urlopen", accept_upload)
    with archive.open("rb") as stream:
        result = client.request("PUT", "/api/files/bucket/egernia.zip", file=stream)
    assert result == {"key": "egernia.zip"}


def test_metadata_request_keeps_json_content_type(monkeypatch, metadata):
    client = zenodo.Zenodo("zenodo-sandbox", "test-token")

    def accept_metadata(request, *, timeout):
        assert request.get_header("Content-type") == "application/json"
        assert json.loads(request.data) == {"metadata": metadata}
        return io.BytesIO(b"{}")

    monkeypatch.setattr(zenodo, "urlopen", accept_metadata)
    client.request("PUT", "/api/deposit/depositions/10", payload={"metadata": metadata})


def test_main_archives_tagged_source_and_citation(tmp_path, monkeypatch, release):
    """A dirty checkout must not alter either the metadata or the uploaded ZIP."""
    monkeypatch.chdir(tmp_path)

    def git(*args):
        return subprocess.check_output(["git", *args], text=True).strip()

    git("init", "-q")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.org")
    citation = (ROOT / "CITATION.cff").read_text()
    Path("CITATION.cff").write_text(citation)
    Path("source.txt").write_text("tagged source")
    git("add", ".")
    git("commit", "-qm", "Release")
    git("tag", release["tagName"])
    Path("CITATION.cff").write_text("invalid working tree citation")
    Path("source.txt").write_text("dirty checkout")
    Path("release.json").write_text(json.dumps(release))
    monkeypatch.setattr(sys, "argv", ["publish_zenodo.py", "--release", "release.json"])
    monkeypatch.setenv("ZENODO_TOKEN", "test-token")
    monkeypatch.setenv("ZENODO_TARGET", "zenodo-sandbox")
    monkeypatch.setenv("ZENODO_PUBLISH", "false")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary.md"))

    def inspect(client, metadata, archive, *, publish):
        assert not publish
        assert metadata["title"] == yaml.safe_load(citation)["title"]
        with zipfile.ZipFile(archive) as contents:
            assert contents.read("egernia/source.txt") == b"tagged source"
            assert "egernia/release.json" not in contents.namelist()
        return record(metadata)

    monkeypatch.setattr(zenodo, "deposit_release", inspect)
    zenodo.main()
    assert "Draft (not published)" in Path("summary.md").read_text()
