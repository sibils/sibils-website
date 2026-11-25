---
description: >-
  Interactive reference of the BiodiversityPMC API, generated from its OpenAPI description, with
  the known issues of the embedded Swagger UI.
---

# BiodiversityPMC API reference

This page embeds the interactive reference generated from the [OpenAPI description](https://biodiversitypmc.sibils.org/api/openapi.json) of the BiodiversityPMC API. The same reference is available on the API server, as [Swagger UI](https://biodiversitypmc.sibils.org/api/). The guides explain the parameters and outputs, with examples: [Fetch](fetch.md), [Search](search.md), [Query player](query-player.md) and [Identifier mapping](mapping.md).

"Try it out" sends real requests to `https://biodiversitypmc.sibils.org/api`. Known issues of the embedded reference:

- Each endpoint appears twice, as `GET` and `POST`. Both entries open together, and "Execute" sends the same request from either; the result is the same. To send a form-encoded `POST` body, use curl or Python as shown in [Making requests](index.md#making-requests).

<swagger-ui src="https://biodiversitypmc.sibils.org/api/openapi.json"/>
