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
| `refs.bib` | Bibliography: `[@key]` citations and the references of the Publications page are written from it (see *Citations* below). |
| `hooks/sibils_data.py`, `data/` | Collection counts and vocabularies from the SIBiLS API (see below), and the references written from `refs.bib`. |
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

Write references as keys of `refs.bib`, never by hand: the build writes them all in the same
style, so a correction in `refs.bib` reaches every page. Requests to cite are in the How to cite
section of the Publications page and in the *Citation* row of each service page (see *Citations*
below). In its How to cite box, the marker is alone on its line and indented like the box:

```markdown
## How to cite

!!! cite ""

    If you use SIBiLS, its APIs or one of its web applications, please cite both papers:

    <!-- sibils:cite 10_1093_nar_gkaa328 caucheteur2026sibils -->
```

A service page has no box: the *Citation* row of its facts box names the papers to cite, with
author-year citations listed under *References* at the end of the page:

```markdown
Citation
:   Pasche et al. [-@pasche2022variomes], with the SIBiLS papers Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]
```

Other markers: `<!-- sibils:bibtex KEY KEY -->` (a BibTeX block copied from `refs.bib`),
`<!-- sibils:cite-short KEY -->` (*Pasche et al. (2022), [title](link)*, a link to the entry
when the page lists it, else to the DOI) and `<!-- sibils:bibliography GROUP -->` (a group of
the Publications page, see below). A key that is not in `refs.bib` is shown in the page as
**Missing reference: KEY** and logged as a warning, which the deployment does not stop on: run
`mkdocs build --strict` before pushing.

Every author is listed, as in the byline of the publication (PubMed or the journal), group
authors included (`and others` in `refs.bib` prints *et al.*).

### Add a publication to the Publications page

Add one entry to `refs.bib`, with `sibils_group`: the group named by a
`<!-- sibils:bibliography GROUP -->` marker of `docs/publications.md`: `about-papers`
(papers, conference abstracts and posters about SIBiLS), `about-reports` (reports and datasets
on Zenodo) or `work-using` (published work that uses SIBiLS). The group lists its entries newest
first, then by first author, then by title. The two SIBiLS papers have no group: they are in the
How to cite box. A paper that users of a service should cite also goes in the table of the How
to cite section (`<!-- sibils:cite-short KEY -->`), in the BibTeX marker and in the *Citation*
row of the service page (see *Citations* below). Optional fields: `sibils_use`, how the work
uses SIBiLS, printed after the reference (Markdown, for *Work using SIBiLS*); `addendum`,
Markdown after the DOI; `shorttitle`, the title in the table of the page; `comment`, a note for
the maintainers that is never shown. Standard fields are LaTeX: write `\%` for a percent sign (a
bare `%` cuts the field).

For example, the entry already in `refs.bib` for the OLIDA paper (copy it with a new key, or the
build stops on the duplicate):

```bibtex
@article{nachtegael2022olida,
  author = {Nachtegael, Charlotte and Gravel, Barbara and Dillen, Arnau and Smits, Guillaume and Nowé, Ann and Papadimitriou, Sofia and Lenaerts, Tom},
  title = {Scaling up oligogenic diseases research with {OLIDA}: the Oligogenic Diseases Database},
  journal = {Database},
  volume = {2022},
  pages = {baac023},
  year = {2022},
  doi = {10.1093/database/baac023},
  pmid = {35411390},
  pmcid = {PMC9216476},
  sibils_group = {work-using},
  sibils_use = {The curation pipeline runs variants through SynVar to obtain genomic coordinates.},
}
```

### Citations

Cite an entry of `refs.bib` by its key: `[@key]` gives *(Gobeill et al., 2020)*, a link to the
full reference on the same page; `[-@key]` gives *(2020)*, for a sentence that already names the
authors. `[@a] [@b]` or `[@a; @b]` give one parenthesis, in which works of the same authors share
the label: *(Pasche et al., 2023b, 2023c)*. The link text has no-break spaces inside "et al." and
before the year, so that a line never breaks there. Put the citation before the punctuation. A
work that the page lists itself (the How to cite box and the lists of the Publications page) is
linked there; the other cited works are listed under a *References* heading added at the end of
the page.

Nothing else goes inside the brackets: no space, page number or prefix. `[@key, p. 5]` or
`[@ key]` stays in the page as written and logs a warning, so `mkdocs build --strict` stops; a
link whose text starts with `@` (`[@name](url)`) is not a citation. A key is made of letters,
digits and `_`, with `-`, `:`, `.`, `/` or `+` inside. Citations in fenced code blocks (```` ``` ````
or `~~~`) and in code spans are left as written, but not in a code block indented by 4 spaces:
use a fenced block for code that contains `[@`.

```markdown
Caucheteur et al. [-@caucheteur2026sibils] describe how the annotations are made and measure their precision vocabulary by vocabulary.
The 2022 paper describes the first three [@pasche2022variomes]; supplementary materials were added later [@pasche2023supplementary].
```

When several works shown on the site have the same authors' label and year, a letter follows the
year, in the order of their titles: today *Pasche et al., 2023a, 2023b, 2023c*. The letter is in
the citations, the *References* sections, the Publications lists and the table of the How to cite
section, but not in the How to cite box, which users copy into their own papers. A new work with
the same label and year can shift these letters.

Plain footnotes (`[^note]`) are for explanatory notes and are listed under *Notes*:

```markdown
The count includes retracted articles.[^retracted]

[^retracted]: Retracted articles stay in PubMed with a retraction notice.
```

Requests to cite are in the How to cite section of `docs/publications.md` and in the *Citation*
row of each service page. The section has the box of the two SIBiLS papers (the only cite box of
the site, and its only "please ... cite"), the table of the papers of each service, collection
and vocabulary, and the BibTeX. Elsewhere the site points to the section without asking: the
*How to cite* link in the footer of every page, the sentence of the About page next to the
licence. A service page names the papers to cite in the *Citation* row of its facts box, as
author-year citations listed under *References* at the end of the page: the papers of its row of
the table and the two SIBiLS papers. An API guide links its service page (its *Web application*
row), not the papers.

The SIBiLS papers are not cited as the source of what the team states about its own service, such
as the daily updates of the collections or what an annotation records: write such facts without a
citation. Cite them for what only they give, such as the precision of the annotations, measured
vocabulary by vocabulary (Vocabularies page).

The build checks these rules (`check_cite_requests()` in `hooks/sibils_data.py`), with warnings,
so `mkdocs build --strict` stops on:

- a cite box (`<!-- sibils:cite -->` or a `cite` admonition) or a sentence with "please"
  followed by "cite", "cites", "cited" or "citing" on a page other than `docs/publications.md`;
- a page of the *Services* section of `nav` without a *Citation* row in its facts box;
- a *Citation* row whose keys are not those of its service's row in the table of
  `docs/publications.md` together with those of the How to cite box. In the row, a sentence that
  says "described in" gives information, not a paper to cite (the KYBELE report of
  Question-Answering), and "with the Variomes paper" adds the keys of the Variomes row.

A new service page therefore gets its row in the table and its *Citation* row in the same commit.

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
| `<!-- sibils:cite KEY KEY -->`, `bibliography GROUP`, `bibtex KEY KEY`, `cite-short KEY` | References from `refs.bib` (see *How to cite* above) |

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
pybtex (read by `hooks/sibils_data.py`), mkdocs-swagger-ui-tag pinned to 0.6.10, and
beautifulsoup4 (used by the latter) below 5.0.
