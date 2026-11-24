"""Archive a stable GitHub release via the Zenodo deposition API.

Uses CITATION.cff and the source tree from the release tag, not the working tree.
See docs/releases.md for environment setup and recovery instructions.
"""

import argparse
import html
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

import yaml

REPOSITORY = "https://github.com/ska-telescope/egernia"
HOSTS = {"zenodo": "https://zenodo.org", "zenodo-sandbox": "https://sandbox.zenodo.org"}


class Zenodo:
    def __init__(self, target, token):
        self.host = HOSTS[target]
        self.token = token

    def request(self, method, path, *, payload=None, file=None):
        url = path if path.startswith("https://") else self.host + path
        if urlsplit(url).netloc != urlsplit(self.host).netloc:
            raise ValueError("Refusing to send the Zenodo token to a different host")
        headers = {"Authorization": f"Bearer {self.token}"}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode()
        if file is not None:
            # The bucket API consumes a raw binary stream, even for ZIP files.
            # Sending the archive's MIME type makes Zenodo reject it with 415.
            headers["Content-Type"] = "application/octet-stream"
            headers["Content-Length"] = str(os.fstat(file.fileno()).st_size)
            data = file
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=120) as response:
                body = response.read()
                return json.loads(body) if body else None
        except HTTPError as error:
            # Do not print request headers or token-bearing exception details.
            raise RuntimeError(f"Zenodo {method} failed with HTTP {error.code}") from None

    def deposits(self):
        page = 1
        while True:
            query = urlencode({"page": page, "size": 100, "all_versions": "true"})
            batch = self.request("GET", f"/api/deposit/depositions?{query}")
            yield from batch
            if len(batch) < 100:
                return
            page += 1


def metadata_for(citation, release):
    if release["isDraft"] or release["isPrerelease"] or not release["publishedAt"]:
        raise ValueError("Only published, stable GitHub releases can be archived")
    tag = release["tagName"]
    if release["url"] != f"{REPOSITORY}/releases/tag/{tag}":
        raise ValueError("Release does not belong to ska-telescope/egernia")
    if citation["repository-code"] != REPOSITORY:
        raise ValueError("CITATION.cff must identify the Egernia repository")
    creators = []
    for author in citation["authors"]:
        creator = {
            "name": author.get("name") or f"{author['family-names']}, {author['given-names']}"
        }
        if author.get("affiliation"):
            creator["affiliation"] = author["affiliation"]
        if author.get("orcid"):
            creator["orcid"] = author["orcid"].removeprefix("https://orcid.org/")
        creators.append(creator)
    if not creators:
        raise ValueError("CITATION.cff must contain at least one author")
    return {
        "title": citation["title"],
        "upload_type": "software",
        "description": html.escape(citation["abstract"]),
        "creators": creators,
        "license": citation["license"].lower(),
        "access_right": "open",
        "keywords": citation.get("keywords", []),
        "version": tag,
        "publication_date": release["publishedAt"][:10],
        "related_identifiers": [
            {"identifier": REPOSITORY, "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": release["url"], "relation": "isIdenticalTo", "scheme": "url"},
        ],
    }


def belongs_to_egernia(deposit):
    return any(
        item["identifier"] == REPOSITORY and item["relation"] == "isSupplementTo"
        for item in deposit.get("metadata", {}).get("related_identifiers", [])
    )


def deposit_release(client, metadata, archive, *, publish):
    deposits = [item for item in client.deposits() if belongs_to_egernia(item)]
    if len({str(item["conceptrecid"]) for item in deposits}) > 1:
        raise ValueError("Multiple Egernia DOI families found; resolve them in Zenodo first")
    published = [item for item in deposits if item["submitted"]]
    for item in published:
        if item["metadata"].get("version") == metadata["version"]:
            return item  # Includes a retry after a successful publish response was lost.
    drafts = [item for item in deposits if not item["submitted"]]
    if len(drafts) > 1:
        raise ValueError("Multiple Egernia drafts found; resolve them in Zenodo first")
    latest = max(published, key=lambda item: int(item["id"])) if published else None
    if drafts:
        draft = drafts[0]
        version = draft["metadata"].get("version")
        # newversion initially inherits the preceding release's metadata. Allow
        # recovery if execution stopped before it could write the new metadata.
        inherited = latest and version == latest["metadata"].get("version")
        if version != metadata["version"] and not inherited:
            raise ValueError("An Egernia draft for another release exists; finish it first")
    elif latest:
        original = client.request(
            "POST", f"/api/deposit/depositions/{latest['id']}/actions/newversion"
        )
        draft = client.request("GET", original["links"]["latest_draft"])
    else:
        # Include the repository/version in the initial request so interrupted
        # first uploads can be discovered and resumed without creating duplicates.
        draft = client.request("POST", "/api/deposit/depositions", payload={"metadata": metadata})
    path = f"/api/deposit/depositions/{draft['id']}"
    client.request("PUT", path, payload={"metadata": metadata})
    # New versions inherit files; replace them so every DOI contains only its
    # own source archive. This also recovers from a partial/failed upload.
    for file in draft["files"]:
        client.request("DELETE", f"{path}/files/{file['id']}")
    with archive.open("rb") as stream:
        client.request("PUT", f"{draft['links']['bucket']}/{quote(archive.name)}", file=stream)
    if publish:
        return client.request("POST", f"{path}/actions/publish")
    return client.request("GET", path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    args = parser.parse_args()
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        raise ValueError("Set the ZENODO_TOKEN secret in the selected GitHub environment")
    target = os.environ.get("ZENODO_TARGET", "zenodo-sandbox")
    client = Zenodo(target, token)
    release = json.loads(args.release.read_text())
    tag = release["tagName"]
    # Resolve a full tag ref to a commit before using it in either git command.
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"], text=True
    ).strip()
    citation = yaml.safe_load(subprocess.check_output(["git", "show", f"{commit}:CITATION.cff"]))
    metadata = metadata_for(citation, release)
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / f"egernia-{commit}.zip"
        subprocess.run(
            ["git", "archive", "--format=zip", "--prefix=egernia/", "-o", str(archive), commit],
            check=True,
        )
        result = deposit_release(
            client, metadata, archive, publish=os.environ.get("ZENODO_PUBLISH") == "true"
        )
    status = "Published" if result["submitted"] else "Draft (not published)"
    summary = (
        f"{status}: {result['links']['html']}\n\n"
        f"Version: `{tag}`; source commit: `{commit}`; environment: `{target}`.\n\n"
        f"Concept record: `{result['conceptrecid']}`.\n"
    )
    print(summary)
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(path).open("a") as stream:
            stream.write(summary)


if __name__ == "__main__":
    main()
