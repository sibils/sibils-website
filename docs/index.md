---
hide:
  - navigation
  - toc
---

<script type="application/ld+json">
{
  "@context": {
    "@vocab": "https://schema.org/"
  },
  "@type": [
    "Service",
    "ResearchProject"
  ],
  "name": "SIBiLS",
  "url": "https://sibils.org",
  "description": "Swiss Institute of Bioinformatics Literature Services",
  "sameAs": [
    "https://sibils.text-analytics.ch/",
  ],
  "logo": {
    "@type": "ImageObject",
    "url": "https://sibils.org/assets/SIBiLS_logo_red.png"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "name": "Julien Gobeill",
    "email": "julien.gobeill@hesge.ch",
    "contactType": "contact"
  },
  "parentOrganization": {
    "@type": "Organization",
    "@id": "http://sib.swiss",
    "legalName": "Swiss Institute of Bioinformatics",
    "name": "SIB",
    "url": "http://sib.swiss"
  },
  "availableChannel": [
    {
      "@type": "ServiceChannel",
      "serviceUrl": "https://biodiversitypmc.sibils.org/",
      "providesService": {
        "@type": "Service",
        "name": "Biodiversity PMC",
      }
    },
    {
      "@type": "ServiceChannel",
      "serviceUrl": "https://biotxplorer.sibils.org/",
      "providesService": {
        "@type": "Service",
        "name": "BiotXplorer",
      }
    },
    {
      "@type": "ServiceChannel",
      "serviceUrl": "https://variomes.sibils.org/",
      "providesService": {
        "@type": "Service",
        "name": "Variomes",
      },
    },
    {
      "@type": "ServiceChannel",
      "serviceUrl": "https://celltriage.sibils.org/",
      "providesService": {
        "@type": "Service",
        "name": "Celltriage",
      },
    },
    {
      "@type": "ServiceChannel",
      "serviceUrl": "https://sparql.sibils.org/",
      "providesService": {
        "@type": "Service",
        "name": "SIBiLS SPARQL endpoint",
      },
    }
  ]
}
</script>
<style>
  .md-typeset h1 {
    color: black;
    text-align: center;
    font-variant: small-caps;
    font-family: 'HelveticaNeue-Light', Arial, Verdana, Tahoma, sans-serif;
    font-weight: bold;
    font-size: 2.2em;
    margin-bottom: 40px;
  }

  .md-typeset h1 img {
    display: block;
    margin: 1.5rem auto 2.5rem auto;
  }
</style>

<h1><img src="assets/SIBiLS_logo_red.png" alt="SIBiLS" style="magin-bottom: 3rem"></h1>

<p style="text-align: center" markdown>
  [Biodiversity PMC](https://biodiversitypmc.sibils.org/){ .md-button .md-button--primary .sibils-service }

  [BiotXplorer](https://biotxplorer.sibils.org/){ .md-button .md-button--primary .sibils-service }

  [Variomes](https://variomes.sibils.org/){ .md-button .md-button--primary .sibils-service }

  [Celltriage](https://celltriage.sibils.org/){ .md-button .md-button--primary .sibils-service }

  [SPARQL endpoint](https://sparql.sibils.org/){ .md-button .md-button--primary .sibils-service }
</p>

## Introduction

This page provides a description of SIBiLS (Swiss Institute of Bioinformatics Literature Services). SIBiLS provide **personalized Information Retrieval** in the biological literature. Indeed, SIBiLS allow **fully customizable search** in **semantically enriched contents**, based on keywords and/or mapped biomedical entities from a growing set of standardized and legacy vocabularies. The services have been used and favourably evaluated to assist the curation of genes and gene products, by delivering **customized literature triage** engines to different curation teams. SIBiLS are freely accessible via **REST APIs** and are **ready to empower any curation workflow**, built on modern technologies scalable with big data: MongoDB and Elasticsearch.

<ul class="partners">
  <li itemscope itemtype="https://schema.org/Organization">
    <a href="https://sib.swiss/" target="_blank" itemprop="url">
      <span itemprop="name">SIB</span>
        <img src="assets/logo_sib.png" alt="SIB">
    </a>
  </li>
  <li itemscope itemtype="https://schema.org/Organization">
    <a href="https://www.elixir-europe.org/" target="_blank" itemprop="url">
      <span itemprop="name">Exlir</span>
        <img class="bigger" src="assets/logo_elixir.png" alt="Elixir">
    </a>
  </li>
  <li itemscope itemtype="https://schema.org/Organization">
    <a href="https://www.hesge.ch/heg/" target="_blank" itemprop="url">
      <span itemprop="name">Haute Ecole de Gestion, Genève</span>
        <img class="bigger" src="assets/logo_heg.png" alt="Haute Ecole de Gestion, Genève">
    </a>
  </li>
  <li itemscope itemtype="https://schema.org/Organization">
    <a href="https://www.swissuniversities.ch/" target="_blank" itemprop="url">
      <span itemprop="name">swissuniversities</span>
        <img class="bigger" src="assets/logo_swissuniversities.png" alt="swissuniversities">
    </a>
  </li>
  <li itemscope itemtype="https://schema.org/Organization">
    <a href="https://www.hes-so.ch/en/homepage" target="_blank" itemprop="url">
      <span itemprop="name">HES-SO</span>
        <img src="assets/logo_hesso.png" alt="HES-SO">
    </a>
  </li>
</ul>
