---
description: >-
  The /query_player endpoint of the BiodiversityPMC API returns ranked documents with snippets,
  counts per field value, or the most frequent concepts for an Elasticsearch query.
---

# Query player

`/query_player` runs an Elasticsearch JSON query on a collection, in one of three modes: ranked documents with snippets, counts per field value, or the most frequent concepts of a vocabulary.
{ .lead }

<div class="facts" markdown>

Endpoint
:   `GET` or `POST` `https://biodiversitypmc.sibils.org/api/query_player`

Reference
:   [OpenAPI reference](reference.md) · [Swagger UI](https://biodiversitypmc.sibils.org/api/)

Examples checked
:   22 November 2026, SIBiLS release 5.1.5.10

</div>

| `mode` | Result |
|---|---|
| `ir` | Ranked documents, as with [`/search`](search.md), with optional highlighted snippets and an exact hit count |
| `aggs` | Number of matching documents per value of a field, for example per publication year |
| `anns` | Most frequent concepts of a vocabulary in the matching documents |

## Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `jq` | yes | | Elasticsearch JSON query, as a JSON string. See [Search](search.md#elasticsearch-json-queries) |
| `col` | yes | | Collection: `medline`, `pmc`, `suppdata`, `plazi` or `zenodo` |
| `mode` | yes | | `ir`, `aggs` or `anns` |
| `n` | no | `10` | `ir`: number of documents, 1 to 10,000 |
| `from` | no | `0` | `ir`: offset of the first document. `from` + `n` cannot exceed 10,000 |
| `highlights` | no | `false` | `ir`: add a highlighted snippet to each hit |
| `snippet_size` | no | `250` | `ir`: snippet size in characters, 1 to 1,000 |
| `total_hits` | no | `false` | `ir`: count all matching documents. Otherwise the count stops at 10,000 |
| `aggs_field` | in `aggs` mode | | `aggs`: field to count values of. It must be a keyword or numeric field, such as `pubyear`, `interpreted.document_type`, `subset` (pmc), `type` (suppdata) or `communities` (zenodo). Text fields such as `journal` return an error |
| `aggs_size` | no | `10` | `aggs`: number of values to return, 1 to 10,000 |
| `anns_term` | in `anns` mode | | `anns`: vocabulary code, such as `mesh`, `ncbitaxon_full` or `covocorganism`. See [Vocabularies](../../vocabularies.md) |
| `anns_size` | no | `10` | `anns`: number of concepts to return, 1 to 10,000 |
| `anns_limit` | no | `10000` | `anns`: number of most frequent concepts, all vocabularies together, from which the concepts of `anns_term` are selected |

There is no `source` parameter. To limit the content returned in `ir` mode, add a list of fields to `jq`, such as `"_source": ["title", "pubyear"]`. `"_source": false` also works, except with `col=zenodo`, where it currently returns HTTP 500.

## Ranked documents with highlights

```bash
curl -G 'https://biodiversitypmc.sibils.org/api/query_player' \
  --data-urlencode 'jq={"_source": ["title", "pubyear"],
                       "query": {"match": {"abstract": "pangolin"}}}' \
  --data-urlencode 'col=medline' \
  --data-urlencode 'mode=ir' \
  --data-urlencode 'n=3' \
  --data-urlencode 'highlights=true' \
  --data-urlencode 'snippet_size=100'
```

Each hit has a `highlight` object, in which the matching terms are enclosed in `<em>` tags:

```json
"highlight": {"abstract": ["the four <em>pangolin</em> seizures."]}
```

The snippet is taken from one field, which depends on the collection:

| `col` | Field of the snippet |
|---|---|
| `medline` | `abstract` |
| `pmc` | `full_text` |
| `suppdata`, `plazi`, `zenodo` | `text` |

## Counts per field value

Publication years of the MEDLINE abstracts that mention pangolins:

```bash
curl -G 'https://biodiversitypmc.sibils.org/api/query_player' \
  --data-urlencode 'jq={"query": {"match": {"abstract": "pangolin"}}}' \
  --data-urlencode 'col=medline' \
  --data-urlencode 'mode=aggs' \
  --data-urlencode 'aggs_field=pubyear' \
  --data-urlencode 'aggs_size=3'
```

Response:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "collection": "medline",
  "json_query": {
    "query": {"match": {"abstract": "pangolin"}},
    "size": 0,
    "aggs": {"keyword_count": {"terms": {"field": "pubyear", "size": 3}}}
  },
  "elastic_output": {
    "hits": {"total": {"value": 796, "relation": "eq"}, "max_score": null, "hits": []},
    "aggregations": {
      "keyword_count": {
        "doc_count_error_upper_bound": 7,
        "sum_other_doc_count": 462,
        "buckets": [
          {"key": 2021, "doc_count": 137},
          {"key": 2020, "doc_count": 99},
          {"key": 2022, "doc_count": 98}
        ]
      }
    }
  }
}
```

## Most frequent concepts

Species most often mapped in the MEDLINE abstracts that mention pangolins:

```bash
curl -G 'https://biodiversitypmc.sibils.org/api/query_player' \
  --data-urlencode 'jq={"query": {"match": {"abstract": "pangolin"}}}' \
  --data-urlencode 'col=medline' \
  --data-urlencode 'mode=anns' \
  --data-urlencode 'anns_term=covocorganism' \
  --data-urlencode 'anns_size=3' \
  --data-urlencode 'anns_limit=50'
```

Excerpt of the response:

```json
"buckets": [
  {"key": "covocorganism|SP_14|Manidae", "doc_count": 796},
  {"key": "covocorganism|SP_6|COVID-19", "doc_count": 382},
  {"key": "covocorganism|SP_5|Coronavirus", "doc_count": 287}
]
```

Each `key` is a `vocabulary|concept_id|preferred_term` value, and `doc_count` is the number of matching documents in which the concept is mapped.

## Response {#output}

The response contains `sibils_version`, `success`, `error`, `collection`, `json_query` (the query sent to Elasticsearch) and `elastic_output` (the native Elasticsearch response). There is no `warning` field. In `aggs` and `anns` modes, the counts are in `elastic_output.aggregations.keyword_count.buckets`.
