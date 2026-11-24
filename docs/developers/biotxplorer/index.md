---
description: >-
  The BiotXplorer API searches the literature for pairs of taxa that could have a biotic
  interaction, and returns the passages that support each pair.
---

# BiotXplorer API

The BiotXplorer API searches the literature for pairs of taxa that could have a biotic interaction, such as "preys on" or "host of", and returns the documents and passages that support each pair. The [BiotXplorer](../../services/biotxplorer/index.md) web application uses it.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://biotxplorer.sibils.org/api`

Interactive reference
:   [Swagger UI](https://biotxplorer.sibils.org/api/)

OpenAPI description
:   [biotxplorer.sibils.org/api/openapi.json](https://biotxplorer.sibils.org/api/openapi.json) (OpenAPI 3.1)

Web application
:   [biotxplorer.sibils.org](https://biotxplorer.sibils.org/), described in [BiotXplorer](../../services/biotxplorer/index.md)

Authentication
:   None

Examples checked
:   24 November 2026, SIBiLS release 5.1.5.10

</div>

A result is a triplet: two taxa and an interaction type from the Relation Ontology, found in the same passage of a document, with a score and the number of passages and documents that mention it. Its `triplet_key`, for example `ott:906244;ott:733666;RO_0002439`, identifies it in `/passages`.

## Endpoints

All endpoints use `GET`. `collection` is `medline` (the default), `pmc`, `suppdata`, `plazi` or `zenodo`.

| Path | Returns | Parameters |
|---|---|---|
| `/normalize/taxon` | Taxa whose names match a term, best match first, with their identifiers | `term` (required) |
| `/normalize/interaction` | Interaction types that match a term | `term` (required) |
| `/search` | The triplets that match the taxa and the interaction type, best score first | See below |
| `/facets` | The taxa (`name=taxa`) or the interaction types (`name=interaction`) of the triplets that `/search` returns, with the number of triplets for each, most frequent first | `name` (required), `limit`, and the parameters of `/search` except `sort` |
| `/passages` | The documents of one triplet, best score first, each with its bibliographic data and its passages | `triplet_key`, `collection` |
| `/fetch` | One document, with the triplets found in it and their passages | `doc_id` (required): a PMID in `medline`, a PMCID in `pmc`; `collection` |
| `/stats` | The number of documents and of distinct triplets in each collection | |
| `/metrics` | Metrics of the server in the Prometheus text format, for monitoring (no literature data) | |

Parameters of `/search`; at least one of the first three is required:

| Parameter | Description |
|---|---|
| `taxon1`, `taxon2` | Taxon identifiers as `/normalize/taxon` returns them, for example `ott:644247` (Open Tree of Life) or `ncbitaxon_viruses:2697049` (NCBI Taxonomy). A taxon also matches the taxa below it: `ott:716176` (the genus *Phengaris*) finds the triplets of *Phengaris arion*. With two taxa, a triplet must contain both, in either order |
| `interaction` | Relation Ontology identifier, with or without the `robiext:` prefix that `/normalize/interaction` adds: `RO_0002439` (preys on). A type also matches the more specific types: `RO_0002438` (trophically interacts with) finds "preys on" triplets |
| `collection` | `medline` by default |
| `f_taxa`, `f_interaction` | Identifiers separated by commas, matched exactly (taxa below them are not included): keep the triplets that contain one of them, or, with a `-` before the identifier, drop those that contain it. `f_taxa` takes taxon identifiers as `/normalize/taxon` returns them (`ott:644247`). `f_interaction` takes the Relation Ontology identifier without the `robiext:` prefix, as `/facets` returns it (`RO_0002453`). With the prefix no triplet matches: `/search` returns `[]`, and a `-` filter drops nothing |
| `sort` | `score` (the default), `docs_count` or `passages_count`, largest first |

## Example

Find the identifier of a taxon:

```bash
curl 'https://biotxplorer.sibils.org/api/normalize/taxon?term=pangolin'
```

```json
{"warning": [], "query": {"term": "pangolin", "term_type": 1}, "results": [{"concept_id": "ott:644247", "preferred_term": "Manis"}]}
```

Triplets in which the large blue butterfly (*Phengaris arion*, `ott:906244`) preys on the ant *Myrmica sabuleti* (`ott:733666`), in MEDLINE:

```bash
curl -G 'https://biotxplorer.sibils.org/api/search' \
  --data-urlencode 'taxon1=ott:906244' \
  --data-urlencode 'taxon2=ott:733666' \
  --data-urlencode 'interaction=RO_0002439'
```

```json
[
  {
    "taxon1": {"concept_id": "ott:906244", "preferred_term": "Phengaris arion", "concept_source": "ott"},
    "taxon2": {"concept_id": "ott:733666", "preferred_term": "Myrmica sabuleti", "concept_source": "ott"},
    "interaction": {"concept_id": "RO_0002439", "preferred_term": "preys on", "concept_source": "robiext"},
    "score": 0.5827967479674797,
    "passages_count": 1,
    "docs_count": 1,
    "triplet_key": "ott:906244;ott:733666;RO_0002439"
  }
]
```

The passages of this triplet (the `document` object, shortened here, has the title, abstract, authors, journal, dates, identifiers and MeSH terms of the document):

```bash
curl -G 'https://biotxplorer.sibils.org/api/passages' \
  --data-urlencode 'triplet_key=ott:906244;ott:733666;RO_0002439'
```

```json
{
  "docs_count": 1,
  "passages_count": 1,
  "documents": [
    {
      "score": 0.5161300813008131,
      "passages": [
        {
          "field": "abstract",
          "size": 1,
          "text": "Caterpillars of Maculinea arion are obligate predators of the brood of Myrmica sabuleti ants.",
          "highlight": [["Maculinea arion"], ["Myrmica sabuleti"], ["predators of"]],
          "score": 0.5161300813008131
        }
      ],
      "doc_id": "28313380",
      "document": {"title": "The capacity of a Myrmica ant nest to support a predacious species of Maculinea butterfly.", "pmid": "28313380", "...": "..."}
    }
  ]
}
```

`highlight` gives the words of the passage that name the first taxon, the second taxon and the interaction: here the passage uses *Maculinea arion*, a synonym of *Phengaris arion*.

## Responses and errors

- `/search` and `/facets` return a JSON array, and `/metrics` plain text; the other endpoints return an object. In `/fetch`, the identifier of a taxon has no vocabulary prefix (`906244`, not `ott:906244`): `concept_source` gives the vocabulary.
- A `/search` or `/facets` request without `taxon1`, `taxon2` or `interaction`, or a `/facets` request without `name`, returns HTTP 400 with `{"detail": "..."}`.
- An invalid value, such as `limit=abc`, returns HTTP 422 with `sibils_version` (here the version of BiotXplorer, `2.0.0`), `success` (`false`), `error` and `warning`. An unknown `collection` returns HTTP 500 with the same fields, plus `url` and `args`.
- `/fetch` with an unknown `doc_id` returns HTTP 200 with `{"error": "document not found"}`.
- Open the Swagger UI at the address with the final slash: on 24 November 2026, `https://biotxplorer.sibils.org/api` redirected to `http://biotxplorer.sibils.org:82/api/`, which did not answer.
