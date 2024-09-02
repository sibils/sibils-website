---
hide:
  - navigation
  - toc
---

# Variomes

<p style="text-align: center" markdown>
  [Variomes](https://variomes.sibils.org/){ .md-button .md-button--primary .sibils-service }
</p>

<figure style="margin-bottom: 3em; margin-top: 2em">
    <iframe width="800" height="454" src="https://www.youtube.com/embed/ovhu5U0EKHQ?si=W6HVdTnLuTYbT3KA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    <figcaption></figcaption>
</figure>

## Introduction

Precision oncology relies on the use of treatments targeting specific genetic variants. However, identifying clinically actionable variants as well as relevant information likely to be used to treat a patient with a given cancer is a labor-intensive task, which includes searching the literature for a large set of variants. The lack of universally adopted standard nomenclature for variants requires the development of variant-specific literature search engines. We develop a system to perform triage of publications relevant to support an evidence-based decision. Together with providing a ranked list of articles for a given variant, the system is also able to prioritize variants, as found in a Variant Calling Format, assuming that the clinical actionability of a genetic variant is correlated with the volume of literature published about the variant. Our system [@pasche2021variomes] searches within four pre-annotated document collections: MEDLINE abstracts, PubMed Central full-text articles, supplementary materials associated with publications, and ClinicalTrials.gov clinical trials. A variant synonym generator is used to increase the comprehensiveness of the set of retrieved documents. We then apply different strategies to rank the publications.

## API

See [the dedicated page](https://variomes.sibils.org/apis)
