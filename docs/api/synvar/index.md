---
description: >-
  The SynVar API generates the synonyms of a human genomic variant, or its normalized
  representations: HGVS, SPDI, VCF, dbSNP and ClinGen identifiers, and GA4GH VRS.
---

# SynVar API

The SynVar API turns a human variant mention into the synonyms used to find it in the literature (expansion), or into its normalized representations: HGVS, SPDI, VCF, dbSNP and ClinGen identifiers, and GA4GH VRS.
{ .lead }

<div class="facts" markdown>

Endpoint
:   `https://synvar.sibils.org/api` (`GET` or `POST`)

Documentation
:   [Usage guide](https://synvar.sibils.org/resources/info.html) · [interactive API](https://synvar.sibils.org/docs) · [OpenAPI description](https://synvar.sibils.org/openapi.json)

Web application
:   [synvar.sibils.org](https://synvar.sibils.org/), described in [SynVar](../../synvar/index.md)

Authentication
:   None

</div>

The [usage guide](https://synvar.sibils.org/resources/info.html) is the reference for the parameters and the outputs; this page summarizes it. The examples were run on 22 November 2026.

## Parameters

Only `variant` is required.

| Parameter | Required | Default | Description |
|---|---|---|---|
| `variant` | yes | | Variant, identifier or text containing variants, for example `V600E`, `BRAF V600E`, `NM_004333.6:c.1799T>A`, `rs113488022` or `CA123643` |
| `ref` | no | | Gene, sequence accession or chromosome, for example `BRAF`. Not needed when `variant` already contains it |
| `mode` | no | `expand` | `expand`: synonyms for literature search. `normalize`: normalized representations |
| `format` | no | `xml` | `xml`, `json`, or `vrs` (structured JSON with VRS objects; enables normalization) |
| `level` | no | `any` | `any`, `protein`, `transcript` (alias `cdna`), `genome`, `dbsnp`, `clingen` or `all`. `genome38` and `genome37` also select the assembly |
| `assembly` | no | both | `GRCh38` or `GRCh37` (aliases `hg38`, `hg19`) |
| `searchGenes` | no | `true` | Look for gene names in `variant`. Set to `false` to use only the reference you supply |
| `taxon` | no | `9606` | Human only; other species are not supported |
| `iso` | no | `false` | Include additional mapped isoforms |
| `map` | no | `false` | Require a successful genome mapping. Without it, expansion can return syntactic variants with `mapped="false"` |

The usage guide lists further options (`startMet`, `insForDup`, `leftAlign`, `cache`). Boolean options accept `true`/`false` or `on`/`off`.

## Examples

Literature synonyms of BRAF V600E (expansion, XML):

[https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein](https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein)

The same in JSON:

[https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein&format=json](https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein&format=json)

A coding DNA variant, with the gene in `ref`:

[https://synvar.sibils.org/api?variant=5279C%3EA&ref=BRCA2&level=transcript](https://synvar.sibils.org/api?variant=5279C%3EA&ref=BRCA2&level=transcript)

Normalization of BRAF V600E:

=== "curl"

    ```bash
    curl -G 'https://synvar.sibils.org/api' \
      --data-urlencode 'variant=V600E' \
      --data-urlencode 'ref=BRAF' \
      --data-urlencode 'mode=normalize' \
      --data-urlencode 'format=json'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    params = {"variant": "V600E", "ref": "BRAF", "mode": "normalize", "format": "json"}
    r = requests.get("https://synvar.sibils.org/api", params=params, timeout=60)
    r.raise_for_status()
    for variant in r.json()["variant-list"]["variant"]:
        print(variant["gene"], variant["hgvs-genome-grch38"], variant["dbsnp"], variant["clingen"])
    ```

Excerpt of the response (the `hgvs-transcript`, `hgvs-protein`, `vcf` and `vrs` lists are shortened):

```json
{
  "variant-list": {
    "variant": [{
      "@valid": "true",
      "@mapped": "true",
      "gene": "BRAF",
      "hgvs-genome-grch38": "NC_000007.14:g.140753336A>T",
      "hgvs-genome-grch37": "NC_000007.13:g.140453136A>T",
      "hgvs-transcript": [
        {"@type": "mane-select", "value": "NM_004333.6:c.1799T>A"}
      ],
      "hgvs-protein": [
        {"@type": "mane-select", "value": "NP_004324.2:p.Val600Glu"}
      ],
      "spdi": "NC_000007.14:140753335:A:T",
      "dbsnp": "rs113488022",
      "clingen": "CA123643",
      "vcf": [
        {"@assembly": "GRCh38", "@chrom": "7", "@pos": "140753336", "@ref": "A", "@alt": "T", "value": ""}
      ],
      "vrs": [
        {"@target": "genome-grch38", "@id": "ga4gh:VA.Otc5ovrw906Ack087o1fhegB4jDRqCAe", "value": "{...}"}
      ]
    }]
  }
}
```

Other inputs, all normalized to JSON:

- dbSNP identifier: [https://synvar.sibils.org/api?variant=rs113488022&level=dbsnp&mode=normalize&format=json](https://synvar.sibils.org/api?variant=rs113488022&level=dbsnp&mode=normalize&format=json)
- ClinGen identifier: [https://synvar.sibils.org/api?variant=CA123643&level=clingen&mode=normalize&format=json](https://synvar.sibils.org/api?variant=CA123643&level=clingen&mode=normalize&format=json)
- HGVS with its transcript: [https://synvar.sibils.org/api?variant=NM_004333.6%3Ac.1799T%3EA&searchGenes=false&mode=normalize&format=json](https://synvar.sibils.org/api?variant=NM_004333.6%3Ac.1799T%3EA&searchGenes=false&mode=normalize&format=json)
- VRS output: [https://synvar.sibils.org/api?variant=NM_000314.8%3Ac.833del&mode=normalize&format=vrs](https://synvar.sibils.org/api?variant=NM_000314.8%3Ac.833del&mode=normalize&format=vrs)

`POST` takes the same parameters as form fields (`application/x-www-form-urlencoded`), not a JSON body:

```python
import requests  # pip install requests

data = {"variant": "BRAF V600E", "mode": "normalize", "format": "json"}
r = requests.post("https://synvar.sibils.org/api", data=data, timeout=60)
r.raise_for_status()
print(r.json()["variant-list"]["variant"][0]["hgvs-genome-grch38"])
```

An HTTP 200 response can contain several candidate variants, each with `valid` and `mapped` flags: an empty or unmapped result is not a successful mapping. HTTP 400 means a missing input, an invalid request or an unsupported species.

## Former route

The former route `https://synvar.sibils.org/generate/literature/fromMutation` still answers, with the parameters `ref`, `variant`, `level`, `iso`, `map` and `format`, for example:

[https://synvar.sibils.org/generate/literature/fromMutation?ref=BRAF&variant=V600E&level=protein](https://synvar.sibils.org/generate/literature/fromMutation?ref=BRAF&variant=V600E&level=protein)

On this route:

- `level=cosmic` is no longer supported: it returns an error in the response body. The current API does not resolve COSMIC identifiers either (`variant=COSM476` returns an empty result);
- `format=beacon` is ignored and returns XML. Use `format=json` for JSON.

New code should use `https://synvar.sibils.org/api`.
