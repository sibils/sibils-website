---
description: >-
  Question-Answering (QA) answers questions written in natural language from MEDLINE, PMC
  and Plazi treatments, with the documents each answer is based on.
---

# Question-Answering

Question-Answering (QA) answers a question written in natural language from MEDLINE, PMC and Plazi treatments: it either extracts the passage that answers it or writes a short answer, and lists the documents each answer is based on.
{ .lead }

[Ask a question](https://qa.sibils.org/){ .btn .btn-primary }
[API documentation](../api/biodiversitypmc/qa.md){ .btn }

<div class="facts" markdown>

Web application
:   [qa.sibils.org](https://qa.sibils.org/)

API
:   REST API at `https://qa.sibils.org/api`, see the [Question-Answering API](../api/biodiversitypmc/qa.md)

Collections
:   MEDLINE, PMC, Plazi treatments (API ids `medline`, `pmc`, `plazi`)

Output
:   Answers with their source documents (PMID, PMCID or Plazi treatment id) and passages, extractive answers with a confidence score; export as JSON or CSV in the web application

Reference
:   No dedicated publication yet; see Caucheteur et al., Database 2026 [@caucheteur2026sibils] and the milestone report of Flament et al., 2026 [@flament2026qademonstrator]

</div>

## What it does

Ask a question such as [What diseases are transmitted by ticks?](https://qa.sibils.org/?q=What%20diseases%20are%20transmitted%20by%20ticks%3F) and the service searches the literature for documents that are relevant to the question, then builds answers from those documents only. The web application shows the results in one tab per collection (MEDLINE, PMC+, Plazi). Each answer links to the document it was taken from, so it can be checked against its source.

Question-Answering works on three SIBiLS collections: MEDLINE abstracts, PMC full-text articles and Plazi taxonomic treatments, the latter being of particular interest for biodiversity questions. The other collections (supplementary data, Zenodo) are not available for question answering. See [Collections](../collections/sibils_collections.md) for what each one contains.

## How answers are produced

The service first retrieves documents, then produces answers from them.

1. **Retrieval.** The question is sent as a keyword search to the SIBiLS search engine, in each collection ("sparse" retrieval). With "dense" retrieval, the service adds a semantic search in a small local index (2,398 documents, according to `https://qa.sibils.org/api/retrieval-info` on 22 November 2026). Depending on the question, it uses the keyword search, the semantic search or both, merging the two result lists, then reorders the documents with a reranking model.
2. **Filtering.** Only the most relevant documents are kept (5 per collection by default in the web application).
3. **Answer.** In extractive mode, a BioBERT model finds the passage of each kept document that best answers the question and gives it a confidence score. In generative mode, a large language model writes a short answer from the kept documents.

The web application uses extractive mode with sparse retrieval by default; its advanced options let you switch to generative mode, for which dense retrieval is recommended. On 22 November 2026, the service reported these models (from `https://qa.sibils.org/api/health`): Qwen3-8B (`Qwen/Qwen3-8B-FP8`) for generative mode and BioBERT (`ktrapeznikov/biobert_v1.1_pubmed_squad_v2`) for extractive mode.

!!! note "Check generated answers"
    A generative answer is written by a language model. It can be incomplete or wrong: read it together with the documents it lists.

## API

The [Question-Answering API](../api/biodiversitypmc/qa.md) page documents the endpoints, parameters and response fields, and [how to move](../api/biodiversitypmc/qa.md#migrating-from-the-former-endpoint) from the former endpoint `https://biodiversitypmc.sibils.org/api/QA`.

!!! cite "How to cite"
    There is no dedicated publication for Question-Answering yet. Please cite SIBiLS:

    - Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P (2020). SIB Literature Services: RESTful customizable search engines in biomedical literature, enriched with automatically mapped biomedical concepts. *Nucleic Acids Research* 48(W1):W12–W16. [doi:10.1093/nar/gkaa328](https://doi.org/10.1093/nar/gkaa328) · [PMID 32379317](https://pubmed.ncbi.nlm.nih.gov/32379317/)
    - Caucheteur D, Flament A, Gobeill J, Pasche E, Michel PA, Mottin L, Liyanapathirana J, Mottaz A, Ruch P (2026). Enhancing the SIB Literature Services (SIBiLS) with annotations to support biocuration. *Database* 2026:baag034. [doi:10.1093/database/baag034](https://doi.org/10.1093/database/baag034) · [PMID 42768721](https://pubmed.ncbi.nlm.nih.gov/42768721/)

    The current question answering pipeline is described in a project milestone report:

    - Flament A, Gaillac E, Knafou J, Ruch P (2026). SCIENCE BFSP CoS – WP10 – M10.3: An Agent Based Demonstrator to interact with the literature. ELIXIR (project milestone, KYBELE). Zenodo. [doi:10.5281/zenodo.22864180](https://doi.org/10.5281/zenodo.22864180)
