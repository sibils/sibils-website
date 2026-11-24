---
description: >-
  Fetch parsed and annotated documents by id from the SIBiLS collections with the BiodiversityPMC
  API, in SIBiLS JSON or BioC JSON format.
---

# Fetch

`/fetch` retrieves annotated documents from a given collection. The input is a list of document ids; send at most 1,000 per request. The output is the set of parsed and annotated documents, in SIBiLS JSON (default) or BioC JSON format.
{ .lead }

<div class="facts" markdown>

Endpoint
:   `GET` or `POST` `https://biodiversitypmc.sibils.org/api/fetch`

Reference
:   [OpenAPI reference](reference.md) · [Swagger UI](https://biodiversitypmc.sibils.org/api/)

Examples checked
:   22 November 2026, SIBiLS release 5.1.5.10

</div>

## Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `ids` | yes | | Document ids, separated by commas without spaces; at most 1,000 per request is recommended. The id format depends on the collection: see [Collections](index.md#collections) |
| `col` | yes | | Collection: `medline`, `pmc`, `suppdata`, `plazi` or `zenodo` |
| `format` | no | `json` | Output format: `json` or `bioc` |

## Examples

Fetch two PMIDs from MEDLINE:

[https://biodiversitypmc.sibils.org/api/fetch?ids=14691011,25190367&col=medline](https://biodiversitypmc.sibils.org/api/fetch?ids=14691011,25190367&col=medline)

Fetch a PMC full text in BioC format:

[https://biodiversitypmc.sibils.org/api/fetch?ids=PMC2196267&col=pmc&format=bioc](https://biodiversitypmc.sibils.org/api/fetch?ids=PMC2196267&col=pmc&format=bioc)

Fetch with `POST`:

=== "curl"

    ```bash
    curl 'https://biodiversitypmc.sibils.org/api/fetch' \
      --data-urlencode 'ids=14691011,25190367' \
      --data-urlencode 'col=medline' \
      -o SIBiLS_fetch.json
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    # document ids to fetch (at most 1,000 recommended), separated by commas
    pmids = "14691011,25190367"

    # call with POST, parameters in a form-encoded body
    url = "https://biodiversitypmc.sibils.org/api/fetch"
    params = {"ids": pmids, "col": "medline"}
    r = requests.post(url, data=params, timeout=60)

    result = r.json()
    if not result["success"]:
        raise RuntimeError(result["error"])
    if result["warning"]:
        print(result["warning"])  # e.g. "missing ids:..."

    for article in result["sibils_article_set"]:
        print(article["_id"], article["document"]["title"])
        print(len(article["annotations"]), "annotations")

    # save the response
    with open("SIBiLS_fetch.json", "w", encoding="utf-8") as file:
        file.write(r.text)
    ```

## Response {#output}

For MEDLINE citations, the delivered and annotated fields include the title, the abstract and the MeSH terms. For PMC full texts, paragraphs are provided with their hierarchical level in the document structure, along with figure and table captions. For supplementary data, the text is extracted from spreadsheets and documents, or obtained by OCR from images. Annotations are delivered with the type of the mapped entity (drug, gene, disease, species...), the vocabulary, the concept identifier and preferred term in this vocabulary, and the character offsets of the mention.

All formats return the documents in `sibils_article_set`:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "collection": "medline",
  "collection_version": "med_r1_v5.10",
  "sibils_article_set": []
}
```

### JSON (default)

Each item of `sibils_article_set` contains:

| Field | Content |
|---|---|
| `_id` | Document id |
| `document` | The parsed document. Its fields depend on the collection, see [Document fields](#document-fields) |
| `interpreted` | Normalized values: `doi`, `license`, `language`, `document_type`, `fabio_expression_class`, `fabio_work_class` |
| `stats` | Number of annotations per vocabulary, and numbers of sentences, characters, figures, tables, references, authors and sections |
| `sentences` | The text split into sentences. Each sentence has `field` (for example `title`, `abstract`, `text`, `fig_caption`), `sentence_number`, `sentence_length` and `sentence`; PMC sentences also have `tag` and `content_id` |
| `annotations` | The mapped concepts, one item per mention |
| `relations` | Extracted relations, often empty |

Each annotation contains:

| Field | Content | Example |
|---|---|---|
| `type` | Entity type of the vocabulary; the example links to the vocabularies of that type | [`species`](../../data/vocabularies.md?type=species) |
| `concept_source` | Vocabulary code, see [Vocabularies](../../data/vocabularies.md) | `covocorganism` |
| `version` | Vocabulary version | `v2.0` |
| `concept_id` | Concept id in the vocabulary | `SP_11` |
| `concept_form` | Text of the mention | `human` |
| `preferred_term` | Preferred term of the concept | `Homo sapiens` |
| `nature` | How the mention matched the concept: `pref_term` (the preferred term), `synonym` (a synonym) or `related-synonym` (a related synonym in the vocabulary, as in GO and Uberon). Other values can occur | `synonym` |
| `field` | Field of the sentence that contains the mention | `title` |
| `sentence_number` | Number of the sentence that contains the mention, as in `sentences[].sentence_number` | `1` |
| `start_index`, `end_index` | Character offsets of the mention in the sentence | `51`, `56` |
| `concept_length` | Length of the mention | `5` |
| `evidence_code` | Evidence code (ECO) | `ECO_0000366` |
| `provenance`, `provider` | Origin of the annotation | `SIBILS`, `SIB` |
| `score` | Annotation score | `0.5` |
| `attributes` | Additional attributes, or `null` | `null` |

To locate a mention, find the sentence whose `sentence_number` equals the annotation's `sentence_number`: the mention is `sentence[start_index:end_index]` of that sentence. Sentence numbers start at 1 and identify a single sentence of the document, so `sentences[sentence_number]` (a list index) gives the wrong sentence. The [annotation API](../annotation/index.md#annotation-fields) uses the same fields, but there `sentence_number` is a list index that starts at 0.

### BioC

With `format=bioc`, each item of `sibils_article_set` is a [BioC](https://bioc.sourceforge.net/) document:

```json
{
  "id": "14691011",
  "infons": {
    "title": "Inhibition of death-receptor mediated apoptosis in human adipocytes by the insulin-like growth factor I (IGF-I)/IGF-I receptor autocrine circuit.",
    "pmid": "14691011",
    "mesh_terms": "D017667:Adipocytes;D000328:Adult;D015703:Antigens, CD;..."
  },
  "passages": [
    {
      "offset": 0,
      "text": "Inhibition of death-receptor mediated apoptosis in human adipocytes by the insulin-like growth factor I (IGF-I)/IGF-I receptor autocrine circuit.",
      "infons": {"field": "title", "sentence_number": 1, "sentence_length": 145},
      "annotations": [
        {
          "id": "0",
          "infons": {
            "type": "species",
            "concept_source": "covocorganism",
            "version": "v2.0",
            "concept_id": "SP_11",
            "preferred_term": "Homo sapiens",
            "nature": "synonym",
            "evidence_code": "ECO_0000366",
            "provenance": "SIBILS",
            "provider": "SIB",
            "score": 0.5,
            "attributes": null
          },
          "text": "human",
          "locations": [{"offset": 51, "length": 5}]
        }
      ],
      "relations": []
    }
  ],
  "relations": []
}
```

- `infons` holds the document metadata. List values are joined with `;`.
- There is one passage per sentence. `infons.field` is the field of the sentence; PMC passages also have `tag` and `content_id`. PMC tables are additional passages, whose infons include `table_id`, `label`, `caption`, `footer`, `section_type`, `xref_url` and `xml`.
- `locations[].offset` is an offset in the document: the passage `offset` plus the position of the mention in the passage `text`.

### Document fields

The main fields of `document`, by collection:

| `col` | Main fields |
|---|---|
| `medline` | `pmid`, `title`, `abstract`, `authors`, `affiliations`, `journal`, `pubyear`, `publication_date`, `mesh_terms`, `sup_mesh_terms`, `chemicals`, `publication_types`, `keywords`, `grants`, `pmcid`, `doi`, `coi_statement`, `language` |
| `pmc` | `pmcid`, `pmid`, `doi`, `title`, `abstract`, `authors`, `affiliations`, `journal`, `publication_date`, `pubyear`, `keywords`, `article_type`, `license_href`, `body_sections`, `float_sections`, `back_sections` (sections with `level`, `title`, `label` and `contents`), numbers of figures and tables |
| `suppdata` | `pmcid`, `filename`, `ext`, `type` (`supplementary data` or `manuscript figure`), `title`, `text`, `licence`, `publication_date` |
| `plazi` | `treatment_title`, `taxon-names`, `article-title`, `publication-doi`, `zenodo-doi`, `treatment-bank-uri`, `source`, `issn`, `text` |
| `zenodo` | `zenodo_id`, `chunk`, `total_chunks`, `doi`, `title`, `abstract`, `text`, `keywords`, `communities`, `resource_type`, `status`, `license`, `nb_pages` |

## Errors

Ids that are not found are listed in `warning` (`missing ids:...`). The other documents are still returned.

Batches of up to 1,000 ids keep responses to a manageable size. The API itself rejects requests with 10,000 ids or more (HTTP 422). With `GET`, the length of the URL limits a request to a few hundred ids: send larger batches with `POST`.
