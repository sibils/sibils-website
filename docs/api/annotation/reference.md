---
description: >-
  Interactive reference of the SIBiLS annotation and vocabularies (OTF) API, generated from its
  OpenAPI description.
---

# Annotation and vocabularies API reference

This page embeds the interactive reference generated from the [OpenAPI description](https://biodiversitypmc.sibils.org/api/otf/openapi.json) of the annotation and vocabularies API. The same reference is available on the API server, as [Swagger UI](https://biodiversitypmc.sibils.org/api/otf/). The [guide](index.md) explains the endpoints and outputs, with examples.

"Try it out" sends real requests to `https://biodiversitypmc.sibils.org/api/otf`. Known issues of the embedded reference:

- `/concept/url`: set `redirect` to `0` in the form. With the default value `1`, the API answers with a redirect to the page of the concept on another site, which the browser blocks here ("Failed to fetch").
- The "live test" link in the description below does not work from this site. The live annotation demo is at [biodiversitypmc.sibils.org/api/otf/live/](https://biodiversitypmc.sibils.org/api/otf/live/).

<swagger-ui src="https://biodiversitypmc.sibils.org/api/otf/openapi.json"/>
