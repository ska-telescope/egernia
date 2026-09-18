# API reference

All resources live under the TAP base URL (default
`http://localhost:8080/tap`). Parameters follow DALI conventions:
case-insensitive names, sent via query string (GET) or form body (POST).
Errors are returned as DALI VOTable documents with
`INFO name="QUERY_STATUS" value="ERROR"` and HTTP status 400/404.

## Synchronous queries

| Method | Resource | Description |
|---|---|---|
| GET/POST | `/sync` | Execute an ADQL query; results spool before delivery and are limited by `TAP_SYNC_MAX_BYTES` |

Parameters:

| Name | Required | Description |
|---|---|---|
| `QUERY` | yes | The ADQL query |
| `LANG` | no (defaults to `ADQL`) | `ADQL`, `ADQL-2.0`, or `ADQL-2.1` |
| `RESPONSEFORMAT` (or `FORMAT`) | no | `votable` (default), `csv`, `tsv`, `json`, `parquet`, `arrow`, or the equivalent MIME types |
| `MAXREC` | no | Row limit; `0` returns metadata only; overflow is flagged with `QUERY_STATUS=OVERFLOW` |
| `REQUEST` | no | `doQuery` accepted for TAP 1.0 compatibility |
| `UPLOAD` | no | Table upload: repeatable `name,uri` pairs separated by `;`. Use `param:<part>` for inline multipart VOTables. HTTP(S) sources are disabled unless their exact hosts are listed in `TAP_UPLOAD_ALLOWED_HOSTS`. Tables are queried as `TAP_UPLOAD.<name>`; the TABLEDATA and BINARY serializations are accepted (BINARY2 and FITS are not). Limits: `TAP_UPLOAD_MAX_ROWS` (100000), `TAP_UPLOAD_MAX_BYTES` (32 MiB per source), `TAP_UPLOAD_MAX_TOTAL_BYTES` (32 MiB total), and `TAP_UPLOAD_MAX_SOURCES` (8). |

### Uploads and the row limit

`MAXREC` is what truncates an upload query, and it truncates silently unless
the client looks. A request that sends no `MAXREC` gets the server default,
`TAP_DEFAULT_MAXREC`, which is **10,000** — so a positional cross-match of a
100,000-row uploaded table returns 10,000 rows, not because the join found
10,000 but because the response stopped there. The uploaded table is not the
limit: `TAP_UPLOAD_MAX_ROWS` (100,000) caps what goes *in*, `MAXREC` caps what
comes *out*, and the two are unrelated.

Send `MAXREC` explicitly on any query whose result you intend to be complete.
The server clamps it to `TAP_HARD_MAXREC` (1,000,000) without saying so, so a
`MAXREC` above the hard cap is not an error — it is a truncation at 1,000,000.
A result that needs more rows than that has to be split, or narrowed in ADQL.

Truncation is reported per DALI as `QUERY_STATUS=OVERFLOW`, but where that
indicator lives — and whether it exists at all — depends on
`RESPONSEFORMAT`:

| Format | Overflow indicator |
|---|---|
| `votable` | a second `<INFO name="QUERY_STATUS" value="OVERFLOW"/>`, after `</TABLE>`. Every response carries an `OK` INFO *before* the table, overflowed or not, so it is the trailing INFO that means anything — a parser that reads only the first one never sees a truncation |
| `json` | the top-level `"status"` field, `"OVERFLOW"` instead of `"OK"` |
| `parquet` | file key-value metadata, `IVOA.VOTable.QUERY_STATUS` = `OVERFLOW` |
| `csv`, `tsv` | **none** — the body has nowhere to carry one |
| `arrow` | **none** |

There is no HTTP header and no non-200 status in any format: an overflowed
response is a normal `200`. In `csv`, `tsv` and `arrow` a truncated result is
therefore indistinguishable from a complete one, so a client using those
formats should either send a `MAXREC` it knows exceeds the result, or compare
the row count it received against the `MAXREC` it asked for — equality means
the result may have been cut. `MAXREC=0` returns the columns and no rows (flagged
`OVERFLOW`, since rows were withheld), which is the cheap way to check a
query's shape before running it.

## Asynchronous queries (UWS 1.1)

| Method | Resource | Description |
|---|---|---|
| GET | `/async` | Job list (`PHASE` filter, `LAST` limit, `AFTER` ISO-8601 creation-time filter); returns `<uws:jobs>` with 100 jobs by default and at most 1,000 |
| POST | `/async` | Create a job from the same parameters as `/sync`; add `PHASE=RUN` to queue immediately; 303 → job URI |
| GET | `/async/{id}` | Job summary `<uws:job>` document; `WAIT=<s>` (or `-1` for the server maximum, `TAP_WAIT_MAX`) blocks until the phase changes, optionally with `PHASE=<phase>` as the reference phase |
| POST | `/async/{id}` | `ACTION=DELETE` destroys the job |
| DELETE | `/async/{id}` | Destroys the job; 303 → job list |
| GET/POST | `/async/{id}/phase` | Read phase (supports `WAIT`/`PHASE` blocking) / `PHASE=RUN` or `PHASE=ABORT`; ABORT cancels the running statement (`pg_cancel_backend`) |
| GET/POST | `/async/{id}/executionduration` | Per-job execution time limit (seconds), settable while `PENDING` |
| GET/POST | `/async/{id}/destruction` | Destruction time; expired jobs are garbage-collected |
| GET | `/async/{id}/quote` | Estimated completion time (nil in this draft) |
| GET | `/async/{id}/owner` | Job owner (anonymous in this draft) |
| GET/POST | `/async/{id}/parameters` | Read parameters / update them while `PENDING` |
| GET | `/async/{id}/results` | Result list; a completed job exposes one result named `result` |
| GET | `/async/{id}/results/result` | The result file, in the format requested at submission |
| GET | `/async/{id}/error` | VOTable error document for `ERROR` jobs |

Job phases: `PENDING → QUEUED → EXECUTING → COMPLETED | ERROR | ABORTED`
(`HELD`, `SUSPENDED`, `ARCHIVED` are accepted values per UWS).

## VOSI & metadata

| Method | Resource | Description |
|---|---|---|
| GET | `/capabilities` | TAPRegExt capability document: languages, output formats, limits |
| GET | `/availability` | Liveness (checks database connectivity) |
| GET | `/tables` | VODataService tableset generated from `TAP_SCHEMA` |
| GET | `/examples` | DALI-examples RDFa document |

`TAP_SCHEMA.schemas`, `.tables`, `.columns`, `.keys` and `.key_columns` are
regular published tables — query them via ADQL, e.g.

```sql
SELECT table_name, description FROM tap_schema.tables
```
