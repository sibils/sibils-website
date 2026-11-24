---
description: >-
  The SIBiLS REST APIs: fetch, search and count documents, annotate texts with the SIBiLS
  vocabularies and answer questions, free and without an API key.
---

# APIs

SIBiLS offers three REST APIs over its collections: the BiodiversityPMC API to fetch, search and count documents, the Question-Answering (QA) API, and the annotation and vocabularies API to annotate your own texts. They are free and need no API key.
{ .lead }

SynVar, Variomes, CellTriage, BiotXplorer and the SPARQL endpoint also have their own APIs, listed under [Other SIBiLS APIs](#other-sibils-apis).

## The three APIs

| API | Base URL | Interactive reference |
|---|---|---|
| [BiodiversityPMC](biodiversitypmc/index.md) | `https://biodiversitypmc.sibils.org/api` | [Swagger UI](https://biodiversitypmc.sibils.org/api/) · [OpenAPI](https://biodiversitypmc.sibils.org/api/openapi.json) · [on this site](biodiversitypmc/reference.md) |
| [Question-Answering (QA)](qa/index.md) | `https://qa.sibils.org/api` | [Swagger UI](https://qa.sibils.org/api/) · [OpenAPI](https://qa.sibils.org/api/openapi.json) · [on this site](qa/reference.md) |
| [Annotation and vocabularies (OTF)](annotation/index.md) | `https://biodiversitypmc.sibils.org/api/otf` | [Swagger UI](https://biodiversitypmc.sibils.org/api/otf/) · [OpenAPI](https://biodiversitypmc.sibils.org/api/otf/openapi.json) · [on this site](annotation/reference.md) |

The base URL is the prefix of every endpoint path, for example `https://biodiversitypmc.sibils.org/api/fetch`; it is not a page itself. To browse an API, open its Swagger UI link above, which ends with a slash.

## What each API does

The BiodiversityPMC and QA APIs work on the SIBiLS collections, selected with the `col` parameter. Operations available for each collection:

| `col` | Fetch | Search | Query player | Count | Id mapping | QA |
|---|---|---|---|---|---|---|
| `medline` | yes | yes | yes | yes | yes | yes |
| `pmc` | yes | yes | yes | yes | `/pmid2pmcid` | yes |
| `suppdata` | yes | yes | yes | yes | no | no |
| `plazi` | yes | yes | yes | yes | no | yes |
| `zenodo` | yes | yes | yes | yes | no | no |

The annotation API is not tied to a collection: it works on the text you send.

| Operation | Endpoint | Limits |
|---|---|---|
| Fetch parsed and annotated documents by id | [`/fetch`](biodiversitypmc/fetch.md) | Up to 1,000 ids per request recommended |
| Search with free text (`q`) or an Elasticsearch query (`jq`) | [`/search`](biodiversitypmc/search.md) | 1 to 1,000 documents per request; `from` + `n` up to 10,000 |
| Query player: ranked documents with snippets, counts per field value, most frequent concepts | [`/query_player`](biodiversitypmc/query-player.md) | 1 to 10,000 documents per request |
| Count the documents of each collection | [`/count`](biodiversitypmc/index.md#collection-sizes) | |
| Id mapping: PMIDs to DOIs or PMCIDs, DOIs to PMIDs | [`/pmid2doi`, `/pmid2pmcid`, `/doi2pmid`](biodiversitypmc/mapping.md) | 1,000 ids per request |
| Question-Answering (QA) | [`/qa`, `/QA`, `/batch`](qa/index.md) | `POST` endpoints: 1 to 100 documents retrieved per collection |
| Annotate a text with the SIBiLS vocabularies | [`/otf/annotations`](annotation/index.md#annotate-a-text) | |
| Look up concepts, list the vocabularies | [`/otf/concept`, `/otf/terminologies`](annotation/index.md#look-up-concepts) | Autocomplete: 10 concepts |

The [BiodiversityPMC API](biodiversitypmc/index.md#collections) page lists the document ids of each collection, and the [Collections](../data/collections.md) page describes their content. The annotation API also lists the vocabularies and looks up their concepts: see [Vocabularies](../data/vocabularies.md). The output format of each endpoint is listed in [BiodiversityPMC output formats](biodiversitypmc/index.md#output-formats).

## Responses

Most responses are JSON objects that start with `sibils_version`, `success`, `error` and `warning`. The three APIs do not fill these fields in the same way. Always check `success` as well as the HTTP status:

| Item | BiodiversityPMC | Annotation (OTF) | Question-Answering |
|---|---|---|---|
| `sibils_version` | `v5.1.5.10` (with a `v`) | `5.1.5.10` | `biomoqa-2.0`, the version of the QA service |
| `warning` | Present, except in `/count` and `/query_player` | Present | Absent |
| Missing or invalid parameter | HTTP 422, same fields, `sibils_version` `5.1.5.10` | HTTP 422, same fields, `sibils_version` `1.0.0` | HTTP 422, FastAPI format `{"detail": [...]}` |
| Error while processing a valid request | HTTP 200 with `"success": false` | HTTP 404 for an unknown concept | HTTP 200 with `"success": false` (`GET /QA`) |
| Responses without these fields | | `/metrics` (Prometheus text), `/concept/url` with `redirect=1` (HTTP 307) | `POST /qa`, `/qa/multi`, `/batch`, `/health`, `/retrieval-info` |

Values observed on 22 November 2026, with SIBiLS release 5.1.5.10.

## Other SIBiLS APIs

| Service | API | Documentation |
|---|---|---|
| SynVar | Generates the synonyms of a genomic variant, or its normalized representations | [SynVar API](synvar/index.md) |
| Variomes | Ranks the publications that mention a genomic variant | [Variomes API](variomes/index.md) |
| CellTriage | Scores articles for Cellosaurus curation | [CellTriage API](celltriage/index.md) |
| BiotXplorer | Searches the literature for pairs of taxa that could have a biotic relationship | [BiotXplorer API](biotxplorer/index.md) |
| SPARQL endpoint | Queries the SIBiLS RDF: publications cited by SIB resources, with their annotations | [SPARQL API](sparql/index.md) |

## Using the APIs

- No registration or API key is needed, and the APIs do not send rate-limit headers. Keep requests within the limits above and avoid sending many requests in parallel.
- Use `POST` for long id lists and long queries, which can exceed URL length limits. Each guide shows how to send the parameters.
- Set a client timeout. Most requests answer in less than a few seconds; generative question answering and large `/fetch` requests can take longer.
