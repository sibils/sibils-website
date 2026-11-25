---
description: >-
  Search a SIBiLS collection with a free-text query or an Elasticsearch JSON query, with the
  /search endpoint of the BiodiversityPMC API.
---

# Search

`/search` searches the documents of a collection, with a free-text query or an Elasticsearch JSON query. The output is the Elasticsearch result set, ranked by relevance, in its native JSON format: for each document, a relevance score and the indexed content.
{ .lead }

<div class="facts" markdown>

Endpoint
:   `GET` or `POST` `https://biodiversitypmc.sibils.org/api/search`

Reference
:   [OpenAPI reference](reference.md) · [Swagger UI](https://biodiversitypmc.sibils.org/api/)

Examples checked
:   22 November 2026

</div>

## Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `q` | `q` or `jq` | | Free-text query |
| `jq` | `q` or `jq` | | Elasticsearch JSON query, as a JSON string. If both are given, `jq` is used |
| `col` | yes | | Collection: `medline`, `pmc`, `suppdata`, `plazi` or `zenodo` |
| `n` | no | `10` | Number of documents to return, 1 to 1,000 |
| `from` | no | `0` | Offset of the first document to return, for paging. `from` + `n` cannot exceed 10,000 |
| `source` | no | `true` | Include the indexed content (`_source`) of each document. With `false`, each hit only has `_index`, `_id` and `_score` |

Search runs on Elasticsearch, whose JSON query language supports many strategies: keywords or concept identifiers, searches in specified fields, boosting of fields or query parts, Boolean combinations, and queries on the concepts and concept types identified in the documents.

You can query in two ways:

- `q`: a free-text query, interpreted by the SIBiLS query analyzer, which expands the terms with the concepts they map to;
- `jq`: an Elasticsearch JSON query, run as is.

## Free-text queries

Example: MEDLINE documents about *Rhinolophus* and pangolins:

[https://biodiversitypmc.sibils.org/api/search?q=Rhinolophus%20AND%20Pangolin&col=medline](https://biodiversitypmc.sibils.org/api/search?q=Rhinolophus%20AND%20Pangolin&col=medline)

The query analyzer:

- requires all the terms by default: `Rhinolophus Pangolin` returns the same documents as `Rhinolophus AND Pangolin`;
- combines terms with the operators `AND`, `OR` and `NOT`, in upper case. A lower-case word such as `and` is searched as one more required term;
- searches the text between double quotes as a phrase, for example `"pangolin coronavirus"`;
- expands each term with the concepts it maps to: `Pangolin` also matches the documents annotated with `mesh|D000086642|Pangolins` or `covocorganism|SP_14|Manidae`;
- searches the following fields:

| `col` | Fields searched by `q` |
|---|---|
| `medline` | `title`, `abstract`, `keywords`, `mesh_terms`, `sup_mesh_terms`, `chemicals` |
| `pmc` | `title`, `abstract`, `keywords`, `mesh_terms`, `sup_mesh_terms`, `chemicals`, `full_text` |
| `suppdata` | `title`, `text`, `filename` |
| `plazi` | `article-title`, `treatment_title`, `taxon_name`, `text`, `material_citation` |
| `zenodo` | `title`, `text`, `keywords`, `creators`, `zenodo_id` |


The response contains the Elasticsearch query built from `q`, in `transformed_query`. It is a good starting point for writing a `jq` query.

`q` does not support field prefixes such as `title:pangolin`. To search in specific fields, use `jq`.

## Elasticsearch JSON queries

`jq` contains an Elasticsearch query, written in the [Elasticsearch query DSL](https://www.elastic.co/docs/reference/query-languages/query-dsl/full-text-queries).

Example: titles matching "Digitoxin metabolism", ranking first the documents annotated with Gene Ontology concepts:

```json
{"query": {"bool": {
  "must": {"match": {"title": "Digitoxin metabolism"}},
  "should": [
    {"prefix": {"annotations.all": "go_bp|"}},
    {"prefix": {"annotations.all": "go_mf|"}},
    {"prefix": {"annotations.all": "go_cc|"}}
  ]
}}}
```

Example: PMC full texts that mention pangolins in a figure caption:

```json
{"query": {"match": {"figures_captions": "pangolin"}}}
```

Example: pangolins in the PMC+ subset only:

```json
{"query": {"bool": {
  "must": [{"match": {"full_text": "pangolin"}}],
  "filter": [{"term": {"subset": "PMC+ subset"}}]
}}}
```

Example: MEDLINE review articles whose abstract mentions pangolins, using the normalized document type in `interpreted`:

```json
{"query": {"bool": {
  "must": [{"match": {"abstract": "pangolin"}}],
  "filter": [{"term": {"interpreted.document_type": "review_article"}}]
}}}
```

The indexed documents also contain the `interpreted` and `stats` objects described in [Fetch](fetch.md#json-default), which `jq` can query like any other field.

!!! warning "Set the number of results with `n` and `from`"
    Do not put `size` in `jq`: the request fails with `Received multiple values for 'size'`. A `from` value in `jq` is replaced by the `from` parameter. Use the `n`, `from` and `source` parameters instead.

### Searching identified concepts

In the index, the `annotations` field of each document lists the concepts mapped in the document. `annotations.all` holds all of them, as `vocabulary|concept_id|preferred_term` values, for example `nextprot|NX_P51587|BRCA2` or `mesh|D000086642|Pangolins`. The same values are available per field: `annotations.title`, `annotations.abstract`, `annotations.mesh_terms`, etc. for MEDLINE, and `annotations.text`, `annotations.fig_caption`, `annotations.table_caption`, etc. for PMC. [Vocabularies](../../data/vocabularies.md) lists the vocabulary codes. To find a concept id from a name, search for the name in the <!-- sibils:terminology-browser --> and open the concept: its "Terminology" and "ID" values are the vocabulary and the id of a `prefix` query, as in the second example below.

Documents with a given concept:

```json
{"query": {"term": {"annotations.all": "nextprot|NX_P51587|BRCA2"}}}
```

Documents with a given concept id, whatever its preferred term:

```json
{"query": {"prefix": {"annotations.all": "nextprot|NX_P51587|"}}}
```

Documents with at least one concept from a vocabulary, for example any DrugBank drug:

```json
{"query": {"prefix": {"annotations.all": "drugbank|"}}}
```

Documents with a concept in a given field:

```json
{"query": {"term": {"annotations.title": "mesh|D000086642|Pangolins"}}}
```

### Indexed fields

| `col` | Main indexed fields |
|---|---|
| `medline` | `pmid`, `title`, `abstract`, `authors`, `affiliations`, `journal`, `pubyear`, `publication_date`, `entrez_date`, `mesh_terms`, `sup_mesh_terms`, `chemicals`, `publication_types`, `keywords`, `grants`, `pmcid`, `doi`, `coi_statement`, `language`, `annotations`, `interpreted`, `stats` |
| `pmc` | `pmcid`, `pmid`, `doi`, `title`, `abstract`, `full_text`, `figures_captions`, `tables`, `tables_captions`, `authors`, `affiliations`, `journal`, `pubyear`, `publication_date`, `keywords`, `article_type`, `license`, `funding_statement`, `subset`, `annotations`, `interpreted`, `stats` |

`hit["_source"]` in the response shows the indexed fields of any collection.

## Response {#output}

The output is the native Elasticsearch response, in `elastic_output`, with the query that was run. With `q` (response on 22 November 2026, shortened: only the first of the 10 hits is shown, and `transformed_query` and `_source` contain more fields):

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "collection": "medline",
  "ndocs": 10,
  "original_query": "Rhinolophus AND Pangolin",
  "transformed_query": {"query": {"bool": {"must": []}}},
  "elastic_output": {
    "took": 4,
    "timed_out": false,
    "hits": {
      "total": {"value": 160, "relation": "eq"},
      "max_score": 94.87805,
      "hits": [
        {
          "_index": "sibils_med_r1_v5.1.5.10",
          "_id": "42267927",
          "_score": 94.87805,
          "_source": {"title": "Genetic diversity of pangolin coronaviruses reveals a key immuno-evasive substitution at spike residue 519."}
        }
      ]
    }
  }
}
```

`ndocs` is the number of hits returned, and `hits.total` the number of matching documents.

With `jq`, `original_query` and `transformed_query` are replaced by `json_query`, the query sent to Elasticsearch, with the `size`, `from` and `_source` values set from `n`, `from` and `source`.

`hits.total` is exact up to 10,000 documents. Above, it is `{"value": 10000, "relation": "gte"}`. To get the exact number, use [`/query_player`](query-player.md) with `total_hits=true`. To retrieve more than 1,000 documents, page with `from`, up to 10,000 documents in total.

## Python script

A Python script that sends `POST` calls to the API, with several examples of Elasticsearch queries:

```python
import json
import requests  # pip install requests

# queries are written in the Elasticsearch query DSL
# https://www.elastic.co/docs/reference/query-languages/query-dsl/full-text-queries
# do not put "size" in the query: use the n and from parameters

# multi-match query: search several fields, with a general OR (default) or AND
search_fields = ["title", "abstract", "keywords", "mesh_terms"]
# use "title^3" to boost the title score by 3
multi_match_query = {
    "query": {
        "multi_match": {
            "query": "BRCA2 cancer",
            "fields": search_fields,
            # "operator": "and",  # default is "or"
            # "type": "phrase",   # phrase matching (exact expression)
        }
    }
}

# boolean query: must is AND, should is OR, must_not is NOT
# https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query
# ex: ("EML4" OR "ALK" in title) AND ("Lung Cancer" in journal)
bool_query = {
    "query": {
        "bool": {
            "must": [
                {"bool": {"should": [
                    {"match": {"title": "EML4"}},
                    {"match": {"title": "ALK"}},
                ]}},
                {"match": {"journal": "Lung Cancer"}},
            ]
        }
    }
}

# annotations query: annotations.all contains "vocabulary|concept_id|preferred_term" values
# ex: documents with BRCA2 (neXtProt NX_P51587) and at least one DrugBank drug
annotations_query = {
    "query": {
        "bool": {
            "must": [
                {"prefix": {"annotations.all": "nextprot|NX_P51587|"}},
                {"prefix": {"annotations.all": "drugbank|"}},
            ]
        }
    }
}

# call the API
url = "https://biodiversitypmc.sibils.org/api/search"
params = {
    "jq": json.dumps(multi_match_query),  # JSON to string; try bool_query or annotations_query
    "col": "pmc",  # the collection: medline, pmc, suppdata, plazi, zenodo...
    "n": 10,     # number of documents (1 to 1,000)
    "from": 0,   # offset of the first document
}
r = requests.post(url, data=params, timeout=60)

result = r.json()
if not result["success"]:
    raise RuntimeError(result["error"])

hits = result["elastic_output"]["hits"]
print(hits["total"])  # {"value": ..., "relation": "eq"} or "gte" above 10,000
for hit in hits["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["title"])

# save the response
with open("SIBiLS_search.json", "w", encoding="utf-8") as file:
    file.write(r.text)
```
