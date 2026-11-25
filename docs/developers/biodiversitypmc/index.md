---
description: >-
  The BiodiversityPMC API retrieves, searches and counts parsed and annotated documents and maps
  identifiers, over MEDLINE, PMC+, supplementary data, Plazi and Zenodo.
---

# BiodiversityPMC API

The BiodiversityPMC API is the core REST API of SIBiLS. It retrieves parsed and annotated documents, runs Elasticsearch searches and aggregations, counts documents and maps identifiers, over MEDLINE, PMC+, supplementary data, Plazi treatments and Zenodo.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://biodiversitypmc.sibils.org/api`

Interactive reference
:   [Swagger UI](https://biodiversitypmc.sibils.org/api/) · [on this site](reference.md)

OpenAPI description
:   [biodiversitypmc.sibils.org/api/openapi.json](https://biodiversitypmc.sibils.org/api/openapi.json) (OpenAPI 3.1)

Web application
:   [biodiversitypmc.sibils.org](https://biodiversitypmc.sibils.org/), described in [BiodiversityPMC](../../services/biodiversitypmc/index.md)

Authentication
:   None

</div>

Documents are parsed, then annotated with concepts from reference vocabularies (see [Vocabularies](../../data/vocabularies.md)). The OpenAPI description lists the endpoints and parameters; the guides below add the explanations, limits and examples.

## Endpoints

| Endpoint | Purpose | Guide |
|---|---|---|
| `/fetch` | Retrieve parsed and annotated documents by id, in JSON or BioC format | [Fetch](fetch.md) |
| `/search` | Search a collection with a free-text query (`q`) or an Elasticsearch JSON query (`jq`) | [Search](search.md) |
| `/query_player` | Run an Elasticsearch JSON query in one of three modes: ranked documents with highlights, counts per field value, or most frequent concepts | [Query player](query-player.md) |
| `/count` | Number of documents per collection and per partition | [Collection sizes](#collection-sizes) |
| `/pmid2doi` | Map PMIDs to DOIs | [Identifier mapping](mapping.md#pmids-to-dois) |
| `/pmid2pmcid` | Map PMIDs to PMCIDs | [Identifier mapping](mapping.md#pmids-to-pmcids) |
| `/doi2pmid` | Map DOIs to PMIDs | [Identifier mapping](mapping.md#dois-to-pmids) |

Question-Answering is a separate API, hosted at `qa.sibils.org`: see [Question-Answering API](../qa/index.md).

## Collections

The `col` parameter selects the collection. [SIBiLS collections](../../data/collections.md) describes the content of each one.

| `col` | Content | Document id | Example id |
|---|---|---|---|
| `medline` | MEDLINE citations | PMID | `14691011` |
| `pmc` | PMC+: PMC open-access subset, PMC author manuscripts, and the PMC+ subset (biodiversity articles that are not in PMC, such as Pensoft articles) | PMCID with the `PMC` prefix; DOI for the PMC+ subset | `PMC2196267`, `10.3389/fevo.2023.1081385` |
| `suppdata` | PMC supplementary files and manuscript figures, with the text extracted from tables, documents and images | PMCID, underscore, file name | `PMC10838014_gyad114_suppl_supplementary_data_sd3.xlsx` |
| `plazi` | Plazi taxonomic treatments | Plazi treatment id | `8F0287F93576FFAF381A50CBFA9A0B55` |
| `zenodo` | Biodiversity Literature Repository (BLR) and related Zenodo communities (`biosyslit`, `bhl-blr`, `batlit`, `taxodros`). Records are split into chunks | Zenodo record id, underscore, chunk number | `15935589_0` |

Ids are case sensitive: `PMC2196267` is found, `pmc2196267` is not. A Zenodo record id without its chunk number is reported as missing.

### Collection sizes

`/count` returns the number of documents in each collection, with a breakdown by partition: PMC subsets, supplementary data types and Zenodo communities. It takes no parameters.

```bash
curl 'https://biodiversitypmc.sibils.org/api/count'
```

Response on 22 November 2026:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "count": {
    "_id": "count_5.1.5.10",
    "medline": {"all": 41435461, "partition": {}},
    "pmc": {"all": 9331692, "partition": {"PMC OA Subset": 8241558, "PMC Author Manuscripts": 1047030, "PMC+ subset": 43104}},
    "suppdata": {"all": 34562768, "partition": {"manuscript figure": 23745336, "supplementary data": 10817432}},
    "plazi": {"all": 1101077, "partition": {}},
    "zenodo": {"all": 433314, "partition": {"batlit": 26874, "biosyslit": 433314, "taxodros": 24580, "bhl-blr": 381811}}
  }
}
```

A Zenodo record can belong to several communities, so the partition counts of `zenodo` overlap. The [SIBiLS collections](../../data/collections.md) page shows the current numbers.

## Making requests

- Every endpoint accepts `GET` and `POST` with the same parameters.
- With `POST`, send the parameters as a form-encoded body (`application/x-www-form-urlencoded`: `data=` in Python `requests`, `--data-urlencode` in curl) or in the query string. JSON request bodies are not accepted: they return HTTP 422.
- Use `POST` with a form body for long id lists and long JSON queries, which can exceed URL length limits.
- Separate the ids in a list with commas and no spaces: `ids=14691011,25190367`. A space after a comma becomes part of the next id, which is then reported as missing.

## Responses

All responses are JSON objects that share these fields:

| Field | Content |
|---|---|
| `sibils_version` | SIBiLS release that answered, for example `v5.1.5.10` |
| `success` | `true` or `false` |
| `error` | Error message when `success` is `false` |
| `warning` | Non-fatal messages, for example `missing ids:99999999999` for ids that were not found. Not returned by `/count` and `/query_player` |

Each guide describes the other fields.

Always check `success`. Errors raised while processing a valid request, for example an invalid Elasticsearch query, are returned with HTTP status 200 and `"success": false`. Missing or invalid parameters return HTTP status 422 with the same fields:

```json
{"sibils_version": "5.1.5.10", "success": false, "error": "query/n: Input should be less than or equal to 1000", "warning": ""}
```

The *Responses* section of the [APIs](../index.md#responses) page compares these fields with the other SIBiLS APIs.

## Output formats

| Endpoint | Output |
|---|---|
| `/fetch` | `json` (SIBiLS JSON, default) or `bioc` (BioC JSON). See [Fetch](fetch.md#output) |
| `/search`, `/query_player` | The native Elasticsearch response in `elastic_output`, with the query that was run |
| `/count`, `/pmid2doi`, `/pmid2pmcid`, `/doi2pmid` | JSON |

## Limits

| Limit | Value |
|---|---|
| Ids per `/fetch` request | 1,000 recommended; requests with 10,000 or more are rejected |
| Ids per `/pmid2doi`, `/pmid2pmcid` or `/doi2pmid` request | 1,000 |
| Documents per `/search` request (`n`) | 1 to 1,000, default 10 |
| Documents per `/query_player` request (`n`) | 1 to 10,000, default 10 |
| Deepest result reachable by paging (`from` + `n`) | 10,000 |
| Hit count (`hits.total`) | Exact up to 10,000, then `{"value": 10000, "relation": "gte"}`. Use `/query_player` with `total_hits=true` for an exact count |

The API does not use API keys or rate-limit headers. Keep requests within these limits and avoid sending many requests in parallel.
