# API

## URL

<https://synvar.sibils.org/generate/literature/fromMutation>

## Parameters

* **ref**: Gene name or chromosome number or name (e.g. `JAK2`, `BRAF`, `9`, `X`). Optional if an identifier is given in the variant parameter.

* **variant**: Variant description, COSMIC id, or dbSNP id (e.g. `V617F`, `Val600Glu`, `rs113488022`, `COSM476`). 

* **level**: Level of the provided variant description (`protein`, `transcript`, `genome`, `dbsnp` or `cosmic`).

## Optional parameters

* **iso**: Validate on and generate synonyms for isoforms: `false` (default) or `true`.
* **map**: Output syntactic variations even if the variant could not be mapped on genome: `false` (default) or `true`.
* **format**: Output format: `xml` (default) or `beacon` (json).

## Examples

* <https://synvar.sibils.org/generate/literature/fromMutation?ref=BRAF&variant=V600E&level=protein>

* <https://synvar.sibils.org/generate/literature/fromMutation?ref=BRAF&variant=V600E&level=protein&format=beacon&iso=true>

* <https://synvar.sibils.org/generate/literature/fromMutation?variant=5279C%3EA&ref=BRCA2&level=transcript>

* <https://synvar.sibils.org/generate/literature/fromMutation?ref=&variant=rs113488022&level=dbsnp>

* <https://synvar.sibils.org/generate/literature/fromMutation?ref=&variant=COSM476&level=cosmic>

* <https://synvar.sibils.org/generate/literature/fromMutation?ref=BRAF&variant=V600K&level=protein&map=false>
