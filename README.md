# sibils.org

Source of [sibils.org](https://sibils.org/), the documentation site of SIBiLS (SIB Literature
Services). The pages are Markdown files in `docs/`, built with [MkDocs](https://www.mkdocs.org/)
and a theme of our own in `theme/`. Every push to `master` publishes the site.

## Edit a page

**On GitHub.** Open the file under `docs/` (for example `docs/biotxplorer/index.md`), click the
pencil icon, edit, check the *Preview* tab, then *Commit changes* to `master`. The site updates
a few minutes later.

**On your computer.**

```sh
git clone git@github.com:sibils/sibils-website.git
cd sibils-website
./serve                        # Linux and macOS; on Windows: serve.bat
```

Then open <http://127.0.0.1:8000/>; the page reloads when you save a file in `docs/`, `theme/`,
`hooks/` or `data/`, `refs.bib` or `mkdocs.yml`. If port 8000 is taken, choose another one:
`./serve -a 127.0.0.1:8001`. The first run creates `./venv` and installs `requirements.txt`
(Python 3.9 or later); `./serve` reinstalls when that file changes.

Before pushing, run a strict build: it turns every warning (a broken link or anchor, an unknown
citation key or an unknown `<!-- sibils:... -->` marker) into an error. The deployment does not
run in strict mode, so these mistakes would otherwise reach sibils.org; after an edit made on
GitHub, check the warnings in the log of the *Actions* tab.

```sh
./venv/bin/mkdocs build --strict   # output in site/, ignored by git
git add -A && git commit && git push
```

## Where things are

| Path | What |
|------|------|
| `docs/` | The pages. The URL follows the path: `docs/sparql/index.md` is `/sparql/`, `docs/vocabularies.md` is `/vocabularies/`. Keep existing paths: other sites link to them. |
| `docs/assets/` | Images and files used by the pages (external sites also link to the logos here). |
| `mkdocs.yml` | Site settings: the navigation (`nav`), the SIBiLS apps given as service channels in the home page's structured data (`extra.apps`, see `theme/partials/jsonld.html`), footer logos (`extra.partners`), contact, licence, Matomo. |
| `refs.bib` | Bibliography for `[@key]` citations. |
| `hooks/sibils_data.py`, `data/` | Collection counts and vocabularies from the SIBiLS API (see below). |
| `theme/` | The theme: templates, CSS, JavaScript, fonts, images. See [theme/README.md](theme/README.md). |
| `.github/workflows/publish.yml` | Build and deployment. |

### Add a page

1. Create the Markdown file under `docs/`, starting with a `# Title`.
2. Add it to `nav` in `mkdocs.yml`. The six top-level entries (Overview, Services, Data, API,
   Publications, About) are the sections of the sub-bar; the left sidebar lists the pages of the
   current section. A section whose first entry has no title, such as
   `- api/biodiversitypmc/index.md`, uses that page as its landing page.
3. Link pages with relative paths to the `.md` file, for example
   `[Fetch](../api/biodiversitypmc/fetch.md)`, so that the build checks the link.

### Front matter

Optional keys at the top of a page:

```yaml
---
description: One sentence for search engines and link previews (default: the lead paragraph).
hide:
  - toc          # no "On this page" column
wide: true       # no "On this page" column and a wider main column; pages that embed
                 # <swagger-ui ...> are wide by default (set "wide: false" to opt out)
---
```

The home page (`docs/index.md`) uses its own template and keys:

```yaml
---
template: home.html
title: SIB Literature Services           # browser title and H1
description: ...                         # meta description
hero_lead: One plain sentence.
hero_actions:
  - {label: Search BiodiversityPMC, url: "https://biodiversitypmc.sibils.org/", primary: true}
  - {label: API documentation, url: api/index.md}
  - {label: How to cite, url: publications.md}
---
```

Relative `url` values point to Markdown files and are turned into page URLs.

## Writing

Plain, factual sentences in the present tense; sentence case headings ("Search API", not
"Search Api" or "SEARCH API"); no emoji and no exclamation marks. Give a source and a date for
every number: a citation, or the API data inserted by the hook. Test every example URL and command
before publishing it.

## Component cheat sheet

The Markdown extensions are listed under `markdown_extensions` in `mkdocs.yml`. Copy and adapt.

### Lead paragraph

```markdown
BiodiversityPMC is a search engine over the SIBiLS literature collections.
{ .lead }
```

### Buttons

Several buttons in one paragraph wrap on small screens. The old `.md-button` and
`.md-button--primary` classes still work.

```markdown
[Open BiotXplorer](https://biotxplorer.sibils.org/){ .btn .btn-primary } [API reference](../api/biodiversitypmc/index.md){ .btn }
```

### Facts box

A definition list in a box, at the top of service pages.

```markdown
<div class="facts" markdown>

Web application
:   [biotxplorer.sibils.org](https://biotxplorer.sibils.org/)

Data
:   MEDLINE, PMC, supplementary data, Plazi

</div>
```

### Cards

Each item of the list is a card (one to three columns depending on the width).

```markdown
<div class="cards" markdown>

- ### BiodiversityPMC

    Search engine over MEDLINE, PMC, supplementary data, Plazi and Zenodo.

    [Open](https://biodiversitypmc.sibils.org/) · [Documentation](biodiversitypmc/index.md) · [API](api/biodiversitypmc/index.md)

- ### Variomes

    Literature triage for genomic variants.

    [Open](https://variomes.sibils.org/) · [Documentation](variomes/index.md)

</div>
```

### Notes and warnings

Types: `note`, `info`, `tip`, `warning`, `danger`, `example`. Use them sparingly. `???` makes a
collapsed block, `???+` an expanded one.

```markdown
!!! warning "Rate limit"
    Send at most one request per second.

??? note "Response example"
    Content shown when the reader opens the block.
```

### How to cite

```markdown
!!! cite "How to cite"
    Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P. SIB Literature Services:
    RESTful customizable search engines in biomedical literature, enriched with automatically
    mapped biomedical concepts. *Nucleic Acids Research* 48(W1):W12–W16, 2020.
    [doi:10.1093/nar/gkaa328](https://doi.org/10.1093/nar/gkaa328)
```

### Citations

Cite an entry of `refs.bib` by its key; the references are listed at the end of the page.

```markdown
SIBiLS is described in the 2020 web server issue of Nucleic Acids Research [@10_1093_nar_gkaa328].
```

Plain footnotes use the same list:

```markdown
The count includes retracted articles.[^retracted]

[^retracted]: Retracted articles stay in PubMed with a retraction notice.
```

### Code

A copy button appears on every code block. `title` adds a file name above the block.

````markdown
```bash
curl 'https://biodiversitypmc.sibils.org/api/fetch?ids=14691011&col=medline'
```

```sparql title="publications.sparql"
SELECT ?s WHERE { ?s ?p ?o } LIMIT 10
```
````

### Tabs

````markdown
=== "curl"

    ```bash
    curl 'https://biodiversitypmc.sibils.org/api/search?q=pangolin&col=medline'
    ```

=== "Python"

    ```python
    import requests
    r = requests.get("https://biodiversitypmc.sibils.org/api/search",
                     params={"q": "pangolin", "col": "medline"}, timeout=60)
    ```
````

### Tables

Wide tables scroll sideways on small screens.

```markdown
| Parameter | Required | Description |
|-----------|----------|-------------|
| `ids`     | yes      | Document ids, separated by commas |
| `col`     | yes      | Collection: `medline`, `pmc`, `suppdata`, `plazi` |
```

### Figures

```markdown
<figure markdown>
  ![Architecture of SIBiLS](../assets/graphical_abstract.png){ loading=lazy }
  <figcaption>Architecture of SIBiLS, from the 2020 paper.</figcaption>
</figure>
```

### Video

16:9 and full width. For YouTube, use the `youtube-nocookie.com` address.

```html
<div class="video"><video controls preload="none" poster="../assets/video-poster.png"><source src="https://candy.text-analytics.ch/Speech.mp4" type="video/mp4"></video></div>

<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/VIDEO_ID" title="Title of the video" allowfullscreen></iframe></div>
```

### Interactive API reference (Swagger UI)

```html
<swagger-ui src="https://biodiversitypmc.sibils.org/api/openapi.json"/>
```

### Other

```markdown
- [x] Task list item, done
- [ ] Task list item, open

Term
:   Definition list.

The API returns JSON.

*[JSON]: JavaScript Object Notation
```

Keyboard keys: `<kbd>Ctrl</kbd>`. Every `##` and `###` heading gets a link anchor, shown on hover.

## Collection counts and vocabularies

`hooks/sibils_data.py` runs during every build. It reads the document counts
(`https://biodiversitypmc.sibils.org/api/count`) and the vocabulary list
(`https://biodiversitypmc.sibils.org/api/otf/terminologies`) from the SIBiLS API; if the API does
not answer, it uses the snapshots committed in `data/`. The build log says which one it used.

The data feeds the counts on the home page and replaces these markers in the pages:

| Marker | Replaced by |
|--------|-------------|
| `<!-- sibils:vocabularies -->` | The vocabulary tables (`docs/vocabularies.md`) |
| `<!-- sibils:collection-counts -->` | The table of documents per collection |
| `<!-- sibils:release -->` | The SIBiLS release, for example 5.1.5.10 |
| `<!-- sibils:date -->` | The build day, or the day the snapshot in `data/` was saved (the API gives no date, so this is not the day the SIBiLS data changed) |

```sh
SIBILS_OFFLINE=1 ./serve                            # do not call the API, use data/
SIBILS_API_BASE=https://example.org/api ./serve     # read another API base URL (default https://biodiversitypmc.sibils.org/api)
./venv/bin/python hooks/sibils_data.py --refresh    # update the snapshots in data/, then commit them
./venv/bin/python hooks/sibils_data.py --selftest   # check the snapshots, the fallback and the rendering
```

`--refresh` rewrites the snapshots only when both endpoints answer correctly. The module
docstring of `hooks/sibils_data.py` documents every key of `config.extra.sibils`.

The API gives no date for its counts: the date on the Collections page is the day of the build
(or the day the snapshot was saved), and the page says so. The home page shows no date. It is
built with a round lower bound of each count (two significant digits, rounded down: 41,438,260
becomes 41,000,000), in grey; in the browser, `theme/js/counts.js` reads
`https://biodiversitypmc.sibils.org/api/count` (the same URL as the build, so `SIBILS_API_BASE`
changes both) and writes the exact numbers in place. If the API does not answer within 3 seconds,
answers with an error, or gives a count below half the round number, the grey round numbers
stay; they remain true as long as the collections grow.

## Theme

The theme is plain Jinja templates, one CSS file and three small JavaScript files, with no
dependency on Material for MkDocs or on any CDN:

```
theme/
  main.html  home.html  404.html     page templates
  partials/                          header, sub-bar, sidebar, search, footer, ...
  css/sibils.css  css/pygments.css   styles, light and dark
  js/theme.js  js/search.js          theme toggle, menu, copy buttons, search
  js/counts.js                       current collection counts on the home page
  fonts/                             DM Sans (OFL licence)
  img/                               wordmarks, favicon, social card, partner logos
  tools/build_pygments_css.py        regenerates css/pygments.css
```

Light and dark follow the system setting; the button in the sub-bar switches and remembers the
choice. Search uses the index of the MkDocs `search` plugin. Details in
[theme/README.md](theme/README.md).

## Deployment

On every push to `master`, `.github/workflows/publish.yml` installs `requirements.txt`, runs
`mkdocs gh-deploy --force` (build, then push to the `gh-pages` branch; build warnings appear in
the log but do not stop it) and calls the deployment service that publishes `gh-pages` on sibils.org. Matomo statistics are only sent from sibils.org,
not from local previews.

Dependencies (`requirements.txt`): MkDocs 1.6 (below 2.0), pymdown-extensions, Pygments,
mkdocs-bibtex, mkdocs-swagger-ui-tag pinned to 0.6.10, and beautifulsoup4 (used by the latter)
below 5.0.
