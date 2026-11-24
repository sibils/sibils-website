---
description: >-
  The CellTriage API scores articles, given by PMID, for their relevance to Cellosaurus curation.
---

# CellTriage API

The CellTriage API scores articles for their relevance to Cellosaurus curation. You submit a list of PMIDs as a job, then read the score of each article when the job is done.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://celltriage.sibils.org/api/v1`

Interactive reference
:   [Swagger UI](https://celltriage.sibils.org/docs)

OpenAPI description
:   [celltriage.sibils.org/api/v1/openapi.json](https://celltriage.sibils.org/api/v1/openapi.json)

Web application
:   [triage.sibils.org/celltriage](https://triage.sibils.org/celltriage), described in [Triage](../../services/triage/index.md)

Authentication
:   None

</div>

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/jobs` | Create a job with a list of PMIDs to score |
| `GET` | `/jobs/{job_id}/status` | Status of a job |
| `GET` | `/jobs/{job_id}` | Job with the score of each article; `include_text=true` adds the text that was scored |
| `GET` | `/healthz`, `/readyz` | Liveness and readiness of the service |

The text of each article is fetched from the [BiodiversityPMC API](../biodiversitypmc/fetch.md). By default (`use_fulltext` false), the abstract is scored. With `"use_fulltext": true`, the PMC full text is used when it is available, otherwise the abstract; `text_source` (`fulltext` or `abstract`) shows which text was scored. The description of `POST /jobs` in the Swagger UI says that full text is the default, but on 22 November 2026 a job without `use_fulltext` scored the abstract of PMID 41892333, which has a PMC full text (PMC13025826).

## Example

Create a job with two PMIDs:

```bash
curl -X POST 'https://celltriage.sibils.org/api/v1/jobs' \
  -H 'Content-Type: application/json' \
  -d '{"article_set": [{"pmid": 41892333}, {"pmid": 41888353}], "use_fulltext": false}'
```

The response contains the job `id`, with `"status": "pending"`. Poll `/jobs/{id}/status` until the status is no longer `pending` or `in progress`, then get the results with `GET /jobs/{id}`. On 22 November 2026, this job was done after 11 seconds, with one score per article:

```json
{
  "status": "done",
  "n_submitted": 2,
  "n_scored": 2,
  "sibils_version": "v5.1.5.10",
  "article_set": [
    {"pmid": 41892333, "score": 1.0, "pmcid": "PMC13025826", "entrez_date": "2026-03-27", "error": null, "text_status": "ok", "text_source": "abstract"},
    {"pmid": 41888353, "score": 1.0, "pmcid": "PMC13172412", "entrez_date": "2026-03-27", "error": null, "text_status": "ok", "text_source": "abstract"}
  ]
}
```

A job is `done` when every article is scored, `partial` when some are not, and `failed` when none is. An article without a score has `score: null` and an `error` that gives the reason: see the [Swagger UI](https://celltriage.sibils.org/docs) for details.
