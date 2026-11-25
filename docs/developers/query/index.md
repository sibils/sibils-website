---
description: >-
  The query parser API turns a query written in the SIBiLS query syntax into the Elasticsearch
  query that the search endpoint of the BiodiversityPMC API runs.
---

# Query parser API

The query parser API turns a query written in the SIBiLS query syntax, such as `TITLE:pangolin coronavirus`, into the Elasticsearch query of each collection, adding the concepts of the SIBiLS vocabularies that match its terms. The [search endpoint](../biodiversitypmc/search.md) of the BiodiversityPMC API runs that Elasticsearch query.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://biodiversitypmc.sibils.org/api/query`

Interactive reference
:   [Swagger UI](https://biodiversitypmc.sibils.org/api/query/) · [ReDoc](https://biodiversitypmc.sibils.org/api/query/redoc)

OpenAPI description
:   [biodiversitypmc.sibils.org/api/query/openapi.json](https://biodiversitypmc.sibils.org/api/query/openapi.json) (OpenAPI 3.1)

Query syntax
:   [SIBiLS Query Syntax](https://biodiversitypmc.sibils.org/api/query/documentation/), with its field reference

Live test
:   [biodiversitypmc.sibils.org/api/query/live/](https://biodiversitypmc.sibils.org/api/query/live/)

Authentication
:   None

Examples checked
:   24 November 2026, SIBiLS release 5.1.5.10

</div>

The syntax is based on the Apache Lucene query syntax: words, `"phrases"`, fields (`TITLE:covid`, `PUB_YEAR:[2020 TO 2024]`, `HAS_DOI:y`), fuzzy and proximity searches, boosts, `AND`, `OR`, `NOT` and parentheses. It adds concepts of the SIBiLS [vocabularies](../../data/vocabularies.md), written `[concept_source:concept_id]`, for example `[mesh:D002415]`. The parser removes stop words from unquoted text, finds the concepts whose names match each term, and writes the query in several forms.

## Endpoints

| Method and path | Returns |
|---|---|
| `GET /parse` | The query, parsed: see the parameters and the response below |
| `POST /parse` | The same, from a query already in the JSON form that `json_query` returns; the parameters other than `query` and `json` are the same |
| `GET /fields` | The 30 fields of the syntax (`name`, `type`, `category`, `label`, `supports_annotations`, `allowed_terminologies`, `collections`, `description`, `examples`), their 9 categories and the 5 collections |
| `GET /search-syntax` | The syntax documentation, in Markdown, in `search_syntax` |
| `GET /metrics` | Metrics of the server in the Prometheus text format, for monitoring |

Parameters of `GET /parse`:

| Parameter | Default | Description |
|---|---|---|
| `query` | (required) | The query, 1 to 4,096 characters |
| `es` | none | Collections for which to write the Elasticsearch query: `medline`, `pmc`, `suppdata`, `plazi` or `zenodo`; repeat the parameter for several (`es=medline&es=plazi`). Without it, `es_queries` is `null` |
| `query_type` | `normal` | `QA` removes more stop words, for queries written as questions |
| `normalized` | `true` | Return `normalized_query` |
| `json` | `true` | Return `json_query` |
| `text_parts` | `true` | Return `text_parts` |

A field applies only to the collections listed for it by `/fields`: `MESH` to `medline`, `TAXON` to `plazi`, `TITLE` to all five.

## Response

| Field | Content |
|---|---|
| `success`, `error`, `warning` | `false` and a message when the query cannot be parsed |
| `normalized_query` | The query as the parser understood it, with the concepts it added, for example ``TITLE:`pangolin` OR TITLE:[mesh:D000086642]`` |
| `es_queries` | For each collection of `es`, the Elasticsearch query: pass it as `jq` to the [search endpoint](../biodiversitypmc/search.md#elasticsearch-json-queries) |
| `json_query` | The parsed query as a JSON tree, which `POST /parse` accepts |
| `text_parts` | The words and phrases of the query and the names of its concepts, preferred terms and synonyms, sorted: the words to highlight in the results |
| `highlights` | The parts of the query string, with their type and position (`token_type`, `start_index`, `end_index`) |
| `timings` | Time spent in each step, in milliseconds; also in the `Server-Timing` header |

## Example

Parse a query and write its Elasticsearch query for MEDLINE:

=== "curl"

    ```bash
    curl -G 'https://biodiversitypmc.sibils.org/api/query/parse' \
      --data-urlencode 'query=TITLE:pangolin coronavirus' \
      --data-urlencode 'es=medline'
    ```

`normalized_query` shows the concepts added to each term:

```text
(TITLE:`pangolin` OR TITLE:[covocorganism:SP_14] OR TITLE:[mesh:D000086642] OR TITLE:[ott:644247]) (`coronavirus` OR [covocbiomed:BMV_34] OR [covocorganism:SP_5] OR [mesh:D017934])
```

and `es_queries.medline` is the Elasticsearch query, shortened here:

```json
{"query": {"bool": {"must": [
  {"dis_max": {"queries": [
    {"match": {"title": "pangolin"}},
    {"term": {"annotations.title": "covocorganism|SP_14|Manidae"}},
    {"term": {"annotations.title": "mesh|D000086642|Pangolins"}},
    {"term": {"annotations.title": "ott|644247|Manis"}}
  ], "tie_breaker": 0.5}},
  {"dis_max": {"queries": [
    {"multi_match": {"query": "coronavirus", "fields": ["title", "abstract", "keywords", "mesh_terms", "sup_mesh_terms", "chemicals"]}},
    {"term": {"annotations.all": "mesh|D017934|Coronavirus"}},
    "..."
  ], "tie_breaker": 0.5}}
]}}}
```

Then run it with the search endpoint:

=== "Python"

    ```python
    import json
    import requests  # pip install requests

    API = "https://biodiversitypmc.sibils.org/api"

    # 1. Turn the query into an Elasticsearch query for MEDLINE
    parsed = requests.get(f"{API}/query/parse",
                          params={"query": "TITLE:pangolin coronavirus", "es": "medline"},
                          timeout=60).json()
    if not parsed["success"]:
        raise SystemExit(parsed["error"])
    print(parsed["normalized_query"])

    # 2. Run it with the search endpoint of the BiodiversityPMC API
    r = requests.post(f"{API}/search",
                      data={"col": "medline", "n": 3,
                            "jq": json.dumps(parsed["es_queries"]["medline"])},
                      timeout=60)
    r.raise_for_status()
    hits = r.json()["elastic_output"]["hits"]
    print(hits["total"]["value"], "documents")
    for hit in hits["hits"]:
        print(hit["_id"], hit["_source"]["title"])
    ```

Output on 24 November 2026, after the normalized query:

```text
82 documents
37749253 Zoonotic potential of a pangolin coronavirus.
36803601 Pangolin merbecovirus gets down to (poly)basics.
32511310 Evidence of recombination in coronaviruses implicating pangolin origins of nCoV-2019.
```

## Errors

- A query that cannot be parsed returns HTTP 400 with `"success": false`, an `error` such as `Unexpected end of input` (for `TITLE:(pangolin`) or `Unexpected token`, and `highlights` with an `error` token at the place of the problem.
- A query of spaces returns HTTP 400 with `"error": "Query cannot be empty"`.
- An empty `query`, or an unknown value of `es` or `query_type`, returns HTTP 422 in the FastAPI format, `{"detail": [...]}`.
