# Publishing releases to Zenodo

The **Publish to Zenodo** GitHub Actions workflow archives the source of each
published, stable GitHub release. It uses the authors, title, abstract, licence
and keywords from `CITATION.cff` **at the release tag**, and the version and date
from the GitHub release. The ZIP is generated with `git archive` from the tagged
commit; it contains tracked source files, not containers, datasets generated at
runtime or release attachments.

## One-time setup

1. Create the GitHub environments `zenodo-sandbox` and `zenodo` under the
   repository's **Settings → Environments**. Restrict deployment branches/tags
   to the refs maintainers use for releases. Required reviewers can be enabled
   for production if the project wants an approval before a DOI is published.
2. Create separate personal access tokens at
   [Zenodo Sandbox](https://sandbox.zenodo.org/account/settings/applications/)
   and [Zenodo](https://zenodo.org/account/settings/applications/), with
   `deposit:write` and `deposit:actions` scopes. Add each as the environment
   secret `ZENODO_TOKEN` in its matching GitHub environment. Use the same Zenodo
   account for every release so previous deposits remain accessible.
3. Review `CITATION.cff` before tagging, especially the author list and licence.
   No DOI, existing deposit ID or repository write token is needed to start.

Use this workflow as the sole publisher for this repository: leave Zenodo's
separate GitHub integration disabled to avoid two deposits for each release.
If Egernia already has deposits created outside this workflow, reconcile them
before enabling it. Discovery uses an exact repository URL with the
`isSupplementTo` relation in the authenticated account's deposit metadata.
Records without that marker or owned by another account cannot be discovered.

## First release and sandbox check

Merge the workflow, then create a tag and a GitHub release containing that
commit. Publishing a stable release automatically runs the production workflow;
configure production credentials first if you want it to publish immediately.
Draft releases and prereleases are skipped.

For a sandbox check, select **Actions → Publish to Zenodo → Run workflow**, run
from `main`, enter an existing stable release tag, select `zenodo-sandbox`, and
leave **publish** unchecked. This creates an unpublished sandbox draft. Inspect
the archive and metadata using the link in the run summary. Run again with
**publish** checked to test DOI publication in the sandbox. Sandbox tokens and
records are separate from production.

The manual workflow also supports `zenodo` for creating a production draft or
retrying a release. It requires an existing published, non-prerelease GitHub
release; a tag alone is insufficient. Publishing in production makes the record
public and mints a DOI. After the first publication, add the concept DOI to
`CITATION.cff` for a citation that covers all versions.

## Subsequent releases and recovery

Later releases create a new version of the latest Egernia deposit, preserving
the concept DOI while assigning each version its own DOI. Inherited files are
removed before uploading the new source ZIP. Runs are serialized per target.
GitHub concurrency can replace a pending run if several releases arrive while
one is running; rerun any skipped release manually, in release order.

Rerunning a published tag returns its existing record without republishing it.
An interrupted upload resumes its draft, replaces incomplete files and retries
publication. A draft for another release or multiple DOI families causes a
failure rather than selecting an arbitrary record. Finish or remove conflicting
unpublished drafts in Zenodo before retrying. Do not edit published records into
draft mode while the workflow is running. HTTP failures fail the job; check
token scopes, environment configuration and Zenodo availability, then rerun.

The workflow records the target, source commit, record URL and concept record ID
in the Actions summary. No Zenodo credentials are available to pull-request
tests. API behavior is covered by mocked tests; a real sandbox run is still
needed to verify the account and token setup.

See the [Zenodo deposition API](https://developers.zenodo.org/) for the upload,
versioning and publication endpoints used by the script.
