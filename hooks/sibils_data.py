#!/usr/bin/env python3
"""SIBiLS data for the website: collection counts, vocabularies, references.

MkDocs hook, registered under ``hooks:`` in mkdocs.yml. It uses the Python
standard library, and pybtex to read refs.bib.

At build time (``on_config``) it reads two endpoints of the SIBiLS API:

- https://biodiversitypmc.sibils.org/api/count (documents per collection)
- https://biodiversitypmc.sibils.org/api/otf/terminologies (vocabularies)

If a request fails, or the answer is not what we expect, it uses the
snapshot committed in data/count.json or data/terminologies.json instead. It
logs one INFO line that says which source was used. It never logs a warning
for a network problem, so ``mkdocs build --strict`` does not fail when the API
is down. The build never writes into the repository.

A few vocabulary labels, descriptions and links returned by the API have typos
or are out of date; TERMINOLOGY_OVERRIDES corrects them on the website.

The data is stored in ``config.extra.sibils`` for the templates::

    counts                 {medline: {all, partition}, pmc: ..., ...}  (API /count)
    count_url              "https://biodiversitypmc.sibils.org/api/count": the
                           home page (theme/js/counts.js) reads the current
                           counts from it in the browser
    release                "5.1.5.10"    SIBiLS release of the counts
    date                   "2026-11-22"  build day (live) or snapshot "saved" date;
                           the API gives no date, so this is not the date
                           of the SIBiLS data
    date_display           "22 November 2026"
    source                 "live" or "snapshot"
    terminologies          [entries of /terminologies, corrected with
                            TERMINOLOGY_OVERRIDES, sorted by label]
    terminologies_release, terminologies_date, terminologies_date_display,
    terminologies_source
    collections            [{id, label, table_label, all, all_display,
                             approx, approx_display, live_min,
                             partitions: [{key, label, url, count, count_display}]}]
                           approx: round lower bound of all (approximate());
                           live_min: smallest current count the home page
                           accepts from the API (half of approx)
    terminology_groups     [{category, title, groups: [{subcategory, title,
                             shared_description, entries}]}]
    terminology_corrections {applied: ["name.field"], stale: [...]}  (TERMINOLOGY_OVERRIDES)
    terminology_browser    {name, url, note} from extra.terminology_browser in
                           mkdocs.yml, url ending with "/"; None when absent
                           (then the vocabulary rows have no browser link)

and these markers are replaced in the Markdown of the pages:

    <!-- sibils:vocabularies -->       vocabulary tables, by category
    <!-- sibils:collection-counts -->  table of documents per collection
    <!-- sibils:release -->            SIBiLS release, for example 5.1.5.10
    <!-- sibils:date -->               build day, or the day the snapshot was saved,
                                       for example 22 November 2026 (the API gives
                                       no date: not the day the SIBiLS data changed)
    <!-- sibils:terminology-browser --> link to the Terminology Browser, then its
                                       note: "Terminology Browser (development
                                       server)" (mkdocs.yml extra.terminology_browser);
                                       the note, in span.browser-note, is not printed

On the page that contains ``sibils:vocabularies``, ``release`` and ``date``
describe the vocabulary data; on all other pages they describe the counts.
An unknown ``sibils:`` marker is reported as a warning (it is a typo in a page).

References are written from refs.bib, in one style (format_reference()), by
these markers; the first three must be alone on their line, indented as the
block they belong to (for example 4 spaces inside ``!!! cite``):

    <!-- sibils:cite KEY KEY... -->        list of references, in this order
    <!-- sibils:bibliography GROUP -->     the entries whose sibils_group is GROUP,
                                           newest first
    <!-- sibils:bibtex KEY KEY... -->      BibTeX code block, copied from refs.bib
    <!-- sibils:cite-short KEY -->         "Pasche et al. (2023), [title](link)": the
                                           link goes to #ref-KEY when the page lists
                                           KEY, else to the DOI

The first entry of a work on a page gets the anchor #ref-KEY; a work printed
twice on a page is reported as a warning.

In-text citations (link_citations()), outside code: [@KEY] gives
"(Gobeill et al., 2020)", [-@KEY] gives "(2020)" for a sentence that already
names the authors, and [@a] [@b] or [@a; @b] give one parenthesis. Each
label links to #ref-KEY: the entry that a marker of the page writes, or the
entry in a "References" section added at the end of the page for the works
that the page does not list. A letter follows the year when several works
shown on the site have the same label and year (Pasche et al., 2023a,
2023b...), in the order of their titles; year_suffixes() computes them from
all the pages.

An unknown key or group is reported as a warning and shown in the page as
"Missing reference: KEY" (an unknown key in a citation stays as written); a
group of refs.bib that no page lists is reported as a warning too.

Requests to cite (check_cite_requests(), when the nav is built) are reported
as warnings when they are not where the site makes them: a cite box
(<!-- sibils:cite --> or a "cite" admonition) or a sentence with "please" ...
"cite", "cites", "cited" or "citing" on a page other than publications.md; a
page of the Services section of the nav without a "Citation" row in its facts
box; a Citation row whose keys are not those of the service's row in the table
of publications.md together with those of its How to cite box.

Environment variables:

    SIBILS_OFFLINE=1      do not call the API, use the snapshots
    SIBILS_API_BASE=URL   API base URL, default https://biodiversitypmc.sibils.org/api
                          (also the one the home page calls in the browser)

Command line, from the repository root:

    ./venv/bin/python hooks/sibils_data.py --refresh    rewrite data/*.json from the API
    ./venv/bin/python hooks/sibils_data.py --selftest   check the snapshots and the rendering
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime
import functools
import html
import json
import logging
import os
import posixpath
import re
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.sibils_data")

DEFAULT_API_BASE = "https://biodiversitypmc.sibils.org/api"
USER_AGENT = "sibils.org-docs-build"
TIMEOUT = 15  # seconds, per request
MAX_BYTES = 10 * 1024 * 1024

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

# name -> (path under the API base, snapshot file)
DATASETS = {
    "count": ("/count", "count.json"),
    "terminologies": ("/otf/terminologies", "terminologies.json"),
}

# Collections of /count, in display order. Partitions are the keys of
# "partition" in /count; unknown collections and partitions are shown with
# their API name.
COLLECTIONS = [
    {"id": "medline", "label": "MEDLINE", "table_label": "MEDLINE", "partitions": {}},
    {
        "id": "pmc",
        "label": "PMC",
        "table_label": "PMC+",
        "partitions": {
            "PMC OA Subset": ("PMC Open Access Subset", None),
            "PMC Author Manuscripts": ("PMC author manuscripts", None),
            "PMC+ subset": ("PMC+ subset (articles not in PMC)", None),
        },
    },
    {
        "id": "suppdata",
        "label": "Supplementary data",
        "table_label": "Supplementary data",
        "partitions": {
            "manuscript figure": ("Author manuscript figures", None),
            "supplementary data": ("Supplementary files", None),
        },
    },
    {"id": "plazi", "label": "Plazi", "table_label": "Plazi treatments", "partitions": {}},
    {
        "id": "zenodo",
        "label": "Zenodo",
        "table_label": "Zenodo",
        "partitions": {
            "biosyslit": (
                "Biodiversity Literature Repository (biosyslit)",
                "https://zenodo.org/communities/biosyslit/",
            ),
            "bhl-blr": ("BHL-BLR (bhl-blr)", "https://zenodo.org/communities/bhl-blr/"),
            "batlit": ("Bat Literature Project (batlit)", "https://zenodo.org/communities/batlit/"),
            "taxodros": ("TaxoDros (taxodros)", "https://zenodo.org/communities/taxodros/"),
        },
    },
]
REQUIRED_COLLECTIONS = [c["id"] for c in COLLECTIONS]

# Vocabulary categories of /terminologies, in display order, with the heading
# used on the page (sentence case). Matching ignores case. Unknown categories
# come after these, alphabetically; entries without a category go to "Other".
CATEGORY_ORDER = [
    ("Health", "Health"),
    ("Genes & Proteins", "Genes and proteins"),
    ("Molecular and cellular Biology", "Molecular and cellular biology"),
    ("Biodiversity", "Biodiversity"),
    ("FAIR", "FAIR"),
]
SUBCATEGORY_ORDER = [
    ("Species", "Species"),
    ("Ecology and Interaction", "Ecology and interaction"),
    ("Chemicals", "Chemicals"),
    ("COVoc", "COVoc"),
]
OTHER_CATEGORY = "Other"

# Corrections applied on top of /otf/terminologies, keyed by name_termino:
# {field: (value returned by the API, corrected value)}. They fix typos,
# official names, broken links and text that contradicts the version. A
# correction applies only while the API still returns the value it replaces
# (the whole value for label and url, its beginning for description, after
# collapsing spaces), so a fix made upstream takes over by itself; the INFO
# line lists the corrections that no longer match, so they can be removed.
# Report them to the API maintainers too, so the endpoint gets fixed.
TERMINOLOGY_OVERRIDES = {
    "agrovoc": {"label": ("Agrovoc", "AGROVOC")},
    "drugbank": {
        "label": ("Drugbank", "DrugBank"),
        "description": (
            "The Drugbank database is a freely accessible resource which includes more than 13,000 records (version 5.1.4",
            "DrugBank is a freely accessible database of drugs and drug targets, with their synonyms and product names.",
        ),
    },
    "flopo": {
        "label": ("Flopo", "FLOPO (Flora Phenotype Ontology)"),
        "description": (
            "The flora phenotype ontology (FLOPO): tool for integrating",
            "The Flora Phenotype Ontology (FLOPO) describes morphological traits and phenotypes of vascular plants,"
            " from trait data extracted from digitized Floras.",
        ),
    },
    "icdo3": {
        "url": (
            "http://www.iacr.com.fr/index.php?option=com_content&view=category&layout=blog&id=100&Itemid=577",
            "https://www.who.int/standards/classifications/other-classifications/"
            "international-classification-of-diseases-for-oncology",
        ),
        "description": (
            "The International Classification of Diseases Oncology (ICD-O) is a biomedical ontology",
            "The International Classification of Diseases for Oncology, third edition (ICD-O-3), maintained by the WHO,"
            " is used mainly in cancer registries to code the site (topography) and the histology (morphology) of"
            " neoplasms.",
        ),
    },
    "lotus": {
        "description": (
            "LOTUS, one of the biggest and best annotated resources for Natural Products occurrences",
            "LOTUS is an open resource of natural product occurrences: documented relationships between chemical"
            " structures and the organisms they were found in.",
        ),
    },
    "mdd": {
        "description": (
            "Mammal species list with synonyms. An initial taxonomy of accepted names + synonyms based on v1.7",
            "Mammal species and their synonyms, from the Mammal Diversity Database (MDD).",
        ),
    },
    "mesh": {
        "description": (
            "The Medical Subject Headings (MeSH), provided by the U.S. National Library of Medicine (NLM), is a"
            " controlled vocabulary thesaurus used for indexing articles for PubMed. In comparison with specialzed",
            "The Medical Subject Headings (MeSH), provided by the U.S. National Library of Medicine (NLM), is a"
            " controlled vocabulary thesaurus used for indexing articles for PubMed. Compared with specialized"
            " ontologies such as the NCIt, MeSH is less granular, and its many synonyms make its terms easier to"
            " identify in text.",
        ),
    },
    "ncit": {
        "description": (
            "The NCI Thesaurus (NCIt) is used for disease mapping. It covers clinical care, translational and basic"
            " research, public information and administrative activities. Provided by the National Cancer Institute,"
            " this terminology is a standard for biomedical coding and reference, used both by public and private"
            " scientific partners worldwide. This NCI's reference terminology contains the NCI_CUI",
            "The NCI Thesaurus (NCIt) is used for disease mapping. It covers clinical care, translational and basic"
            " research, public information and administrative activities. Provided by the National Cancer Institute,"
            " this terminology is a standard for biomedical coding and reference, used both by public and private"
            " scientific partners worldwide. The version used by SIBiLS contains the NCI concept identifier"
            " (NCI_CUI), the semantic type, a preferred term, and some NCI and MeSH synonyms.",
        ),
    },
    "nextprot": {
        "url": ("https://www.nextprot.org/", "https://www.expasy.org/archives/nextprot"),
        "description": (
            "Developed by the SIB (Swiss Institute of Bioinformatics) in 2008, the neXtProt human protein knowledgebase",
            "neXtProt, developed by SIB, was a knowledgebase of more than 20,000 manually annotated human proteins;"
            " its services have ended and its data are archived. SIBiLS uses its protein and gene names and their"
            " synonyms.",
        ),
    },
    "ott": {
        "url": (
            "https://tree.opentreeoflife.org/about/taxonomy-version/ott3.3",
            "https://tree.opentreeoflife.org/about/taxonomy-version",
        ),
        "description": (
            "Open Tree of Life aims to construct a comprehensive, dynamic and digitally-available tree of life by"
            " synthesizing published phylogenetic trees along with taxonomic data. https://doi.org/10.5281/zenodo.3937750",
            "Open Tree of Life aims to construct a comprehensive, dynamic and digitally-available tree of life by"
            " synthesizing published phylogenetic trees along with taxonomic data.",
        ),
    },
    "pubchemmesh": {
        "label": ("Pubchem (Mesh subset)", "PubChem (MeSH subset)"),
        "description": (
            "Pubchem database, only coumpounds with mesh terms associated.",
            "PubChem compounds that have associated MeSH terms.",
        ),
    },
    "uniprot_swissprot": {
        "label": ("UniProtKB/SwissProt", "UniProtKB/Swiss-Prot"),
        "description": (
            "The UniProt Knowledgebase (UniProtKB) is the central hub for the collection of functional information on"
            " proteins, with accurate, consistent and rich annotation. We used",
            "The UniProt Knowledgebase (UniProtKB) collects functional information on proteins. SIBiLS uses a large"
            " part of its reviewed section, UniProtKB/Swiss-Prot, whose entries include information extracted from"
            " the literature and curator-evaluated computational analysis.",
        ),
    },
}

DISPROT_BASE = (
    "Terms of the DisProt ontology (January 2020 release): functions, binding partners, structural"
    " transitions and detection methods of intrinsically disordered proteins."
)
DISPROT_VARIANTS = {
    "disprot_type1": ("Disprot_type1", "Matches the preferred terms only."),
    "disprot_type2": ("Disprot_type2", "Also matches plurals and acronyms, for example NMR or SAXS."),
    "disprot_type3": (
        "Disprot_type3",
        "Matches the same terms as type 2, plus 28 general terms about disorder, such as"
        " \"intrinsically disordered\" or \"conformational changes\".",
    ),
    "disprot_type4": (
        "Disprot",
        "Matches the same terms as type 3, plus broader synonyms, for example \"magnetic resonance"
        " spectroscopy\" for NMR.",
    ),
}
for _name, (_label, _variant) in DISPROT_VARIANTS.items():
    TERMINOLOGY_OVERRIDES[_name] = {
        "label": (_label, f"DisProt (type {_name[-1]})"),
        # Empty in the API: an empty expected value matches only an empty value.
        "url": ("", "https://disprot.org/"),
        "description": ("", f"{DISPROT_BASE} {_variant}"),
    }

# <!-- sibils:NAME --> or <!-- sibils:NAME ARG ARG... -->; "indent" is set when
# the marker starts its line (block markers keep that indentation).
MARKER_RE = re.compile(
    r"(?P<indent>^[ \t]*)?<!--\s*sibils:(?P<name>[A-Za-z0-9_-]+)(?P<args>(?:[ \t]+[^\s<>]+)*)\s*-->",
    re.M,
)


class DataError(Exception):
    """The API answer or a snapshot does not have the expected content."""


# --------------------------------------------------------------------------
# Validation


def _is_count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _release(payload: dict) -> str:
    version = payload.get("sibils_version")
    if not isinstance(version, str) or not version.strip():
        raise DataError("no sibils_version")
    # /count answers "v5.1.5.10", /otf/terminologies "5.1.5.10".
    return version.strip().removeprefix("v")


def _check_success(payload) -> None:
    if not isinstance(payload, dict):
        raise DataError("answer is not a JSON object")
    if payload.get("success") is not True:
        error = payload.get("error") or "no error message"
        raise DataError(f"success is not true ({error})")


def validate_count(payload) -> dict:
    """Check a /count answer and return {release, counts}."""
    _check_success(payload)
    count = payload.get("count")
    if not isinstance(count, dict):
        raise DataError("no 'count' object")
    counts = {}
    for cid, entry in count.items():
        if cid.startswith("_"):  # "_id": "count_5.1.5.10"
            continue
        if not isinstance(entry, dict):
            raise DataError(f"count.{cid} is not an object")
        total = entry.get("all")
        partition = entry.get("partition")
        if not _is_count(total):
            raise DataError(f"count.{cid}.all is not a count")
        if not isinstance(partition, dict) or not all(
            isinstance(k, str) and _is_count(v) for k, v in partition.items()
        ):
            raise DataError(f"count.{cid}.partition is not an object of counts")
        counts[cid] = {"all": total, "partition": dict(partition)}
    missing = [cid for cid in REQUIRED_COLLECTIONS if cid not in counts]
    if missing:
        raise DataError("missing collections: " + ", ".join(missing))
    return {"release": _release(payload), "counts": counts}


TERMINOLOGY_REQUIRED = ("name_termino", "code", "type", "version")
TERMINOLOGY_OPTIONAL = ("label", "date", "file_creation", "url", "description", "category", "subcategory")


def validate_terminologies(payload) -> dict:
    """Check a /otf/terminologies answer and return {release, terminologies}."""
    _check_success(payload)
    terminologies = payload.get("terminologies")
    if not isinstance(terminologies, dict) or not terminologies:
        raise DataError("no 'terminologies' object, or it is empty")
    entries = []
    seen = set()
    for key, entry in terminologies.items():
        if not isinstance(entry, dict):
            raise DataError(f"terminologies.{key} is not an object")
        for field in TERMINOLOGY_REQUIRED:
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise DataError(f"terminologies.{key}.{field} is missing")
        for field in TERMINOLOGY_OPTIONAL:
            if entry.get(field) is not None and not isinstance(entry[field], str):
                raise DataError(f"terminologies.{key}.{field} is not a string")
        name = entry["name_termino"].strip()
        if name in seen:
            raise DataError(f"duplicate name_termino {name}")
        seen.add(name)
        clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in entry.items()}
        entries.append(clean)
    entries.sort(key=lambda e: ((e.get("label") or e["name_termino"]).casefold(), e["name_termino"]))
    return {"release": _release(payload), "terminologies": entries}


VALIDATORS = {"count": validate_count, "terminologies": validate_terminologies}


# --------------------------------------------------------------------------
# Loading


def api_base() -> str:
    return (os.environ.get("SIBILS_API_BASE") or DEFAULT_API_BASE).rstrip("/")


def count_url(base: str | None = None) -> str:
    """URL of /count, for the build and for the home page in the browser."""
    return (base or api_base()) + DATASETS["count"][0]


def offline() -> bool:
    return os.environ.get("SIBILS_OFFLINE", "").strip().lower() in ("1", "true", "yes", "on")


def today() -> str:
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        if response.status != 200:
            raise DataError(f"HTTP {response.status}")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise DataError("answer larger than 10 MB")
    return json.loads(body.decode("utf-8"))


def describe_error(exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, (socket.timeout, TimeoutError)):
            return f"no answer within {TIMEOUT} s"
        return str(reason)
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return f"no answer within {TIMEOUT} s"
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)):
        return "answer is not valid JSON"
    if isinstance(exc, DataError):
        return str(exc)
    return f"{type(exc).__name__}: {exc}"


def fetch_dataset(name: str, base: str) -> dict:
    """Fetch and validate one dataset from the API."""
    path, _ = DATASETS[name]
    url = base + path
    payload = fetch_json(url)
    data = VALIDATORS[name](payload)
    data.update(source="live", date=today(), url=url, payload=payload)
    return data


def load_snapshot(name: str, data_dir: Path = DATA_DIR) -> dict:
    _, filename = DATASETS[name]
    path = data_dir / filename
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, ValueError) as exc:
        raise DataError(f"cannot read snapshot {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DataError(f"snapshot {path} is not a JSON object")
    payload = dict(payload)
    saved = payload.pop("saved", None)
    try:
        saved = datetime.date.fromisoformat(saved).isoformat()
    except (TypeError, ValueError) as exc:
        raise DataError(f"snapshot {path} has no valid 'saved' date") from exc
    try:
        data = VALIDATORS[name](payload)
    except DataError as exc:
        raise DataError(f"snapshot {path}: {exc}") from exc
    data.update(source="snapshot", date=saved, url=str(path), payload=payload)
    return data


def load_datasets(use_network: bool | None = None, base: str | None = None, data_dir: Path = DATA_DIR):
    """Return ({name: dataset}, log message). Falls back to the snapshots."""
    use_network = (not offline()) if use_network is None else use_network
    base = base or api_base()
    reasons = {}
    datasets = {}
    if use_network:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(DATASETS)) as pool:
            futures = {name: pool.submit(fetch_dataset, name, base) for name in DATASETS}
            for name, future in futures.items():
                try:
                    datasets[name] = future.result()
                except Exception as exc:  # any failure: use the snapshot
                    reasons[name] = f"{base}{DATASETS[name][0]}: {describe_error(exc)}"
    else:
        reasons = {name: "SIBILS_OFFLINE is set" for name in DATASETS}
    for name in DATASETS:
        if name not in datasets:
            datasets[name] = load_snapshot(name, data_dir)

    parts = []
    for name in DATASETS:
        ds = datasets[name]
        if ds["source"] == "live":
            parts.append(f"{name} from the API ({ds['url']}, release {ds['release']})")
        else:
            parts.append(
                f"{name} from snapshot data/{DATASETS[name][1]} saved {ds['date']} "
                f"(release {ds['release']}; {reasons[name]})"
            )
    return datasets, "sibils_data: " + "; ".join(parts)


# --------------------------------------------------------------------------
# Data for the templates


def fmt_int(n: int) -> str:
    return f"{n:,}"


APPROX_DIGITS = 2


def approximate(n: int, digits: int = APPROX_DIGITS) -> int:
    """Round lower bound of a count: n rounded down to `digits` significant digits.

    41,438,260 -> 41,000,000; 433,314 -> 430,000; numbers below 10**digits
    are kept. The home page shows it until the browser gets the current count
    from the API, and keeps it if the API does not answer. It has as many
    digits as n (the exact number that replaces it has the same length), it
    is within 10% of n, and it stays true while the collection grows, however
    old the build is.
    """
    if n < 10 ** digits:
        return n
    step = 10 ** (len(str(n)) - digits)
    return n - n % step


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def long_date(iso: str) -> str:
    """2026-11-22 -> 22 November 2026."""
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def build_collections(counts: dict) -> list:
    known = {c["id"]: c for c in COLLECTIONS}
    order = REQUIRED_COLLECTIONS + sorted(cid for cid in counts if cid not in known)
    collections = []
    for cid in order:
        if cid not in counts:
            continue
        info = known.get(cid, {"label": cid, "table_label": cid, "partitions": {}})
        entry = counts[cid]
        approx = approximate(entry["all"])
        partition = entry["partition"]
        keys = [k for k in info["partitions"] if k in partition]
        keys += sorted((k for k in partition if k not in info["partitions"]), key=lambda k: (-partition[k], k))
        parts = []
        for key in keys:
            label, url = info["partitions"].get(key, (key, None))
            parts.append(
                {"key": key, "label": label, "url": url, "count": partition[key],
                 "count_display": fmt_int(partition[key])}
            )
        collections.append(
            {
                "id": cid,
                "label": info["label"],
                "table_label": info["table_label"],
                "all": entry["all"],
                "all_display": fmt_int(entry["all"]),
                "approx": approx,
                "approx_display": fmt_int(approx),
                # A current count below this is not shown (a 0 or a partial
                # count while the API is updated); a small real decrease is.
                "live_min": approx // 2,
                "partitions": parts,
                # Zenodo records can be in several communities.
                "partitions_overlap": sum(p["count"] for p in parts) > entry["all"],
            }
        )
    return collections


def _ordered_titles(values, order):
    """Sort raw names by a preferred order; return [(raw, title)]."""
    lookup = {raw.casefold(): (i, title) for i, (raw, title) in enumerate(order)}
    known = sorted((v for v in values if v.casefold() in lookup), key=lambda v: lookup[v.casefold()][0])
    unknown = sorted((v for v in values if v.casefold() not in lookup), key=str.casefold)
    return [(v, lookup[v.casefold()][1]) for v in known] + [(v, v) for v in unknown]


def group_terminologies(entries: list) -> list:
    by_category = {}
    for entry in entries:
        category = entry.get("category") or OTHER_CATEGORY
        by_category.setdefault(category, []).append(entry)
    other = by_category.pop(OTHER_CATEGORY, None)
    ordered = _ordered_titles(list(by_category), CATEGORY_ORDER)
    if other:
        by_category[OTHER_CATEGORY] = other
        ordered.append((OTHER_CATEGORY, OTHER_CATEGORY))

    result = []
    for category, title in ordered:
        members = by_category[category]
        by_sub = {}
        for entry in members:
            by_sub.setdefault(entry.get("subcategory") or None, []).append(entry)
        groups = []
        if None in by_sub:
            groups.append((None, None, by_sub.pop(None)))
        for sub, sub_title in _ordered_titles(list(by_sub), SUBCATEGORY_ORDER):
            groups.append((sub, sub_title, by_sub[sub]))
        out_groups = []
        for sub, sub_title, items in groups:
            descriptions = {_squash(e.get("description")) for e in items}
            shared = None
            if len(items) > 1 and len(descriptions) == 1:
                shared = descriptions.pop() or None
            out_groups.append(
                {"subcategory": sub, "title": sub_title, "shared_description": shared, "entries": items}
            )
        result.append({"category": category, "title": title, "groups": out_groups})
    return result


def apply_terminology_overrides(entries: list, overrides: dict | None = None):
    """Apply TERMINOLOGY_OVERRIDES; return (entries, applied, stale).

    applied and stale are lists of "name_termino.field". The input entries are
    not modified.
    """
    overrides = TERMINOLOGY_OVERRIDES if overrides is None else overrides
    by_name = {e["name_termino"]: e for e in entries}
    corrected = {name: dict(e) for name, e in by_name.items()}
    applied, stale = [], []
    for name, fields in overrides.items():
        for field, (expected, new) in fields.items():
            current = _squash(by_name.get(name, {}).get(field))
            expected = _squash(expected)
            if field == "description" and expected:
                matches = bool(current) and current.startswith(expected)
            else:
                matches = current == expected
            if matches:
                corrected[name][field] = new
                applied.append(f"{name}.{field}")
            else:
                stale.append(f"{name}.{field}")
    result = [corrected[e["name_termino"]] for e in entries]
    result.sort(key=lambda e: ((e.get("label") or e["name_termino"]).casefold(), e["name_termino"]))
    return result, applied, stale


def build_extra(datasets: dict) -> dict:
    count = datasets["count"]
    termino = datasets["terminologies"]
    terminologies, applied, stale = apply_terminology_overrides(termino["terminologies"])
    return {
        "counts": count["counts"],
        "count_url": count_url(),
        "release": count["release"],
        "date": count["date"],
        "date_display": long_date(count["date"]),
        "source": count["source"],
        "terminologies": terminologies,
        "terminologies_release": termino["release"],
        "terminologies_date": termino["date"],
        "terminologies_date_display": long_date(termino["date"]),
        "terminologies_source": termino["source"],
        "collections": build_collections(count["counts"]),
        "terminology_groups": group_terminologies(terminologies),
        "terminology_corrections": {"applied": applied, "stale": stale},
    }


def browser_settings(value) -> dict | None:
    """extra.terminology_browser of mkdocs.yml, checked: {name, url ending with "/", note}, or None."""
    if not value:
        return None
    url = _http_url(value.get("url")) if isinstance(value, dict) else None
    name = _squash(value.get("name")) if isinstance(value, dict) else ""
    if not url or not name:
        log.warning("sibils_data: extra.terminology_browser in mkdocs.yml needs a name and an http(s) url")
        return None
    return {"name": name, "url": url.rstrip("/") + "/", "note": _squash(value.get("note"))}


# --------------------------------------------------------------------------
# Markdown rendering

_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+!|])")


def _squash(text) -> str:
    return " ".join(str(text).split()) if text else ""


def md_text(text) -> str:
    """Plain text for Markdown: collapse spaces, escape HTML and Markdown."""
    return _MD_SPECIAL.sub(r"\\\1", html.escape(_squash(text), quote=False))


def md_code(text) -> str:
    text = _squash(text)  # a pipe inside a code span does not split a table cell
    return f"`` {text} ``" if "`" in text else f"`{text}`"


def _http_url(url) -> str | None:
    url = (url or "").strip()
    return url if re.match(r"https?://\S+$", url) else None


def _link(label: str, url: str | None) -> str:
    if url:
        return f'<a href="{html.escape(url, quote=True)}">{md_text(label)}</a>'
    return md_text(label)


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"[-\s]+", "-", text).strip("-")


def _anchor(name: str, taken: set) -> str:
    anchor = re.sub(r"[^A-Za-z0-9_-]", "-", name).strip("-") or "vocabulary"
    if anchor in taken:
        anchor = "vocabulary-" + anchor
    taken.add(anchor)
    return anchor


def render_vocabularies(extra: dict, page_markdown: str = "") -> str:
    """Markdown for <!-- sibils:vocabularies -->."""
    groups = extra["terminology_groups"]
    entries = extra["terminologies"]
    browser = extra.get("terminology_browser")
    taken = {_slug(m) for m in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", page_markdown, flags=re.M)}
    for cat in groups:
        taken.add(_slug(cat["title"]))
        taken.update(_slug(g["title"]) for g in cat["groups"] if g["title"])
    taken.add(_slug("Vocabularies by annotation type"))
    anchors = {e["name_termino"]: _anchor(e["name_termino"], taken) for e in entries}

    n_cat = len(groups)
    lines = [
        f"The list has {len(entries)} vocabularies in {n_cat} {'category' if n_cat == 1 else 'categories'}.",
        "",
    ]
    for cat in groups:
        lines += [f"## {cat['title']}", ""]
        for group in cat["groups"]:
            if group["title"]:
                lines += [f"### {group['title']}", ""]
            if group["shared_description"]:
                lines += [md_text(group["shared_description"]), ""]
            # div.vocab-table: on phones the theme hides the Version column and
            # shows span.vocab-version in the meta line instead (sibils.css).
            lines += ['<div class="vocab-table" markdown>', ""]
            lines += ["| Vocabulary | Version |", "|------------|---------|"]
            for e in group["entries"]:
                name = e["name_termino"]
                label = e.get("label") or name
                meta = f"concept_source {md_code(name)} · type {md_code(e['type'])}"
                if _squash(e.get("version")):
                    meta += f'<span class="vocab-version"> · version {md_code(e["version"])}</span>'
                # The vocabulary's page in the Terminology Browser, whose ids are the
                # concept_source values (49 of 49 on 24 November 2026). Hidden in
                # print (sibils.css). The no-break space keeps the "·" with the link
                # when the line wraps on phones.
                if browser:
                    href = f'{browser["url"]}terminology/{urllib.parse.quote(name, safe="")}'
                    meta += (
                        f'<span class="vocab-browse"> ·&nbsp;<a href="{html.escape(href, quote=True)}">browse concepts'
                        f'<span class="visually-hidden"> of {md_text(label)} in the {md_text(browser["name"])}</span></a></span>'
                    )
                cell = (
                    f'<span id="{anchors[name]}"></span>{_link(label, _http_url(e.get("url")))}'
                    f"<br><small>{meta}</small>"
                )
                description = _squash(e.get("description"))
                if description and not group["shared_description"]:
                    cell += f"<br><small>{md_text(description)}</small>"
                # Versions such as 2026-02-04 must not wrap at the hyphens.
                version = f'<span style="white-space: nowrap">{md_text(e["version"])}</span>'
                lines.append(f"| {cell} | {version} |")
            lines += ["", "</div>", ""]

    # Which vocabularies produce each annotation type.
    by_type = {}
    for e in entries:
        by_type.setdefault(e["type"], []).append(e["name_termino"])
    lines += [
        "## Vocabularies by annotation type",
        "",
        "Annotations carry the entity type of their vocabulary in the `type` field.",
        "",
        "| Type | Vocabularies (`concept_source`) |",
        "|------|---------------------------------|",
    ]
    for type_, names in sorted(by_type.items(), key=lambda kv: kv[0].casefold()):
        links = ", ".join(f"[{md_code(n)}](#{anchors[n]})" for n in sorted(names))
        lines.append(f"| {md_code(type_)} | {links} |")
    lines.append("")
    return "\n".join(lines)


def render_collection_counts(extra: dict) -> str:
    """Markdown for <!-- sibils:collection-counts -->."""
    lines = ["| Collection | Documents | Parts |", "|------------|----------:|-------|"]
    overlap = []
    for c in extra["collections"]:
        name = f"{md_text(c['table_label'])}<br><small>{md_code(c['id'])}</small>"
        parts = "<br>".join(f"{_link(p['label'], p['url'])}: {p['count_display']}" for p in c["partitions"])
        lines.append(f"| {name} | {c['all_display']} | {parts} |")
        if c["partitions_overlap"]:
            overlap.append(c)
    lines.append("")
    for c in overlap:
        if c["id"] == "zenodo":
            lines += ["A Zenodo record can belong to several communities, so the parts add up to more than the total.", ""]
        else:
            lines += [f"The parts of {md_text(c['table_label'])} overlap: they add up to more than the total.", ""]
    lines += [counts_date_line(extra), ""]
    return "\n".join(lines)


def counts_date_line(extra: dict) -> str:
    """Date line under the counts table. /count gives no date: the date is the
    day of the build (or the day the snapshot was saved), which must not read as
    the day the SIBiLS data changed."""
    release = md_text(extra["release"])
    if extra["source"] == "live":
        return f"Counts at the last build of this site, {extra['date_display']} (release {release})."
    return (
        f"Counts saved on {extra['date_display']} (release {release}) and used at the last build of this site."
    )


# --------------------------------------------------------------------------
# References (refs.bib)
#
# Every full reference of the site is written from refs.bib, in the style of
# the "How to cite" box of the Publications page:
#
#   Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P (2020). SIB
#   Literature Services: [...]. *Nucleic Acids Research* 48(W1):W12–W16.
#   [doi:10.1093/nar/gkaa328](https://doi.org/10.1093/nar/gkaa328) · [PMID 32379317](...)
#
# Every author is listed, as in the byline of the publication (PubMed or the
# journal), group authors included; "and others" in refs.bib prints "et al.".
# Standard fields are LaTeX (write \% for a percent sign). Fields read
# besides the usual ones:
#
#   note          printed after the journal or the publisher
#   addendum      Markdown, printed after the DOI and the PMID
#   shorttitle    title used by <!-- sibils:cite-short -->
#   sibils_group  group of the Publications page (<!-- sibils:bibliography GROUP -->)
#   sibils_use    Markdown, how the work uses SIBiLS, after the reference
#   comment       for the maintainers, never printed

BIB_FILE = REPO_DIR / "refs.bib"
# Not copied into <!-- sibils:bibtex -->: they mean nothing outside this site.
BIB_PRIVATE_FIELDS = ("sibils_group", "sibils_use", "comment", "addendum")
BLOCK_MARKERS = ("cite", "bibliography", "bibtex")
REF_MARKERS = BLOCK_MARKERS + ("cite-short",)


class Bibliography:
    """refs.bib, parsed by pybtex, with its source text for BibTeX blocks."""

    def __init__(self, path: Path = BIB_FILE):
        from pybtex.database import parse_string

        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.entries = parse_string(self.text, "bibtex").entries
        self.groups_shown: set = set()

    def get(self, key: str, src: str = ""):
        entry = self.entries.get(key)
        if entry is None:
            log.warning("sibils_data: unknown reference key %s in %s (not in %s)", key, src or "a page",
                        self.path.name)
        return entry

    def groups(self) -> dict:
        """{group: [keys]} from the sibils_group fields."""
        result = {}
        for key, entry in self.entries.items():
            group = entry.fields.get("sibils_group", "").strip()
            if group:
                result.setdefault(group, []).append(key)
        return result

    def source(self, key: str) -> str:
        """The entry as written in refs.bib, without BIB_PRIVATE_FIELDS."""
        start = re.search(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,", self.text)
        if start is None:
            raise DataError(f"entry {key} not found in the text of {self.path.name}")
        end = _closing_brace(self.text, self.text.index("{", start.start()))
        body = self.text[start.start():end + 1]
        for field in BIB_PRIVATE_FIELDS:
            m = re.search(r"^[ \t]*" + field + r"\s*=\s*", body, flags=re.M | re.I)
            if m:
                stop = _closing_brace(body, m.end()) + 1 if body[m.end()] == "{" else body.index(",", m.end())
                stop = body.index("\n", stop) + 1
                body = body[:m.start()] + body[stop:]
        return body


def _closing_brace(text: str, start: int) -> int:
    """Index of the brace that closes the one at text[start]."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise DataError(f"unbalanced braces after position {start}")


@functools.lru_cache(maxsize=None)
def _latex(value: str) -> str:
    """LaTeX field value as plain text: {braces} removed, -- as an en dash, ``quotes''."""
    # render(Backend()), not render_as("text"): render_as looks the backend up
    # in the installed packages' entry points at each call (10 ms each).
    from pybtex.backends.plaintext import Backend
    from pybtex.richtext import Text

    return " ".join(Text.from_latex(value).render(Backend()).split())


def _md_inline(text: str) -> str:
    """Plain text for running Markdown: escape what would become markup.

    "|" is escaped too (the tables extension makes "\\|" an escape), so that a
    title can be written in a table cell.
    """
    text = html.escape(text, quote=False)
    text = re.sub(r"([\\`*\[\]|])", r"\\\1", text)
    return re.sub(r"(?<!\w)_|_(?!\w)", r"\\_", text)


def _person_family(person) -> str:
    return _latex(" ".join(person.prelast_names + person.last_names))


def _person_initials(person) -> str:
    names = _latex(" ".join(person.first_names + person.middle_names))
    return "".join(part[0] for part in re.split(r"[\s.\-]+", names) if part)


def format_authors(entry) -> str:
    """'Gobeill J, Caucheteur D, Michel PA': every author; "others" gives "et al."."""
    names = []
    for person in entry.persons.get("author", []):
        family = _person_family(person)
        if family == "others":
            names.append("et al.")
            break
        initials = _person_initials(person)
        names.append(f"{family} {initials}" if initials else family)
    return ", ".join(_md_inline(n) for n in names)


def short_authors(entry) -> str:
    """'Pasche et al.', 'Gobeill and Ruch', 'Caucheteur'."""
    families = [_person_family(p) for p in entry.persons.get("author", [])]
    if len(families) >= 3 or "others" in families:
        return _md_inline(families[0]) + " et al."
    return " and ".join(_md_inline(f) for f in families)


def _sentence(text: str) -> str:
    text = text.strip()
    return text if not text or text[-1] in ".?!" else text + "."


def _container(entry) -> str:
    """Journal, book, report or publisher part, without the final period."""
    f = {k.lower(): _latex(v) for k, v in entry.fields.items()
         if k.lower() in ("journal", "volume", "number", "pages", "booktitle", "series",
                          "howpublished", "institution", "publisher")}
    kind = entry.type.lower()
    if kind == "article":
        where = f"*{_md_inline(f['journal'])}*"
        issue = f.get("volume", "") + (f"({f['number']})" if f.get("number") else "")
        location = ":".join(x for x in (issue, f.get("pages", "")) if x)
        return f"{where} {location}".strip()
    if kind == "incollection" and f.get("series"):
        # *Series* volume:pages (EVENT), EVENT from "Book title (EVENT)"
        event = re.search(r"\(([^()]*)\)\s*$", f.get("booktitle", ""))
        text = f"*{_md_inline(f['series'])}* {f.get('volume', '')}:{f.get('pages', '')}"
        return text + (f" ({_md_inline(event.group(1))})" if event else "")
    if kind in ("inproceedings", "incollection"):
        text = f"*{_md_inline(f.get('booktitle', ''))}*"
        if f.get("series"):
            text += f", {_md_inline(f['series'])}" + (f" {f['number']}" if f.get("number") else "")
        return text
    if kind == "techreport":
        authors = " and ".join(_person_family(p) for p in entry.persons.get("author", []))
        parts = [f.get("institution", ""), f.get("publisher", "")]
        return ". ".join(_md_inline(p) for p in parts if p and p != authors)
    text = f.get("howpublished") or f.get("publisher", "")
    if entry.fields.get("month"):  # a news release: "..., 15 February 2024"
        text += f", {_latex(entry.fields['month'])} {_latex(entry.fields.get('year', ''))}"
    return _md_inline(text)


def _doi_url(doi: str) -> str:
    return "https://doi.org/" + doi.replace("(", "%28").replace(")", "%29").replace(" ", "%20")


def format_identifiers(entry) -> str:
    """[doi:...](https://doi.org/...) · [PMID ...](https://pubmed.ncbi.nlm.nih.gov/.../)"""
    fields = entry.fields
    links = []
    doi = fields.get("doi", "").strip()
    if doi:
        links.append(f"[doi:{_md_inline(doi)}]({_doi_url(doi)})")
    elif fields.get("url"):
        url = fields["url"].strip()
        links.append(f"[{_md_inline(re.sub(r'^https?://', '', url))}]({url})")
    pmid = fields.get("pmid", "").strip()
    if pmid:
        links.append(f"[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    # A no-break space before the dot: a line never starts with "·".
    return "\u00a0· ".join(links)


# {key: "a"}: letters after the year, set by year_suffixes() for the works
# that share their label and year with another work shown on the site.
YEAR_SUFFIX: dict = {}


def format_year(entry, letter: bool = True) -> str:
    """'2020', or '2023b' (YEAR_SUFFIX) unless letter is False."""
    year = _latex(entry.fields.get("year", "n.d."))
    return year + YEAR_SUFFIX.get(entry.key, "") if letter else year


def citation_label(entry) -> str:
    """'Gobeill et al., 2020', 'Gobeill and Ruch, 2026', 'Plazi, 2023'."""
    return f"{short_authors(entry)}, {format_year(entry)}"


def link_label(label: str) -> str:
    """Text of an author-year link: a line may break after the surname, not
    inside "et al." nor before the year ("Gobeill et\u00a0al.,\u00a02020")."""
    label = label.replace(" et al.,", " et\u00a0al.,")
    head, sep, year = label.rpartition(", ")
    return head + ",\u00a0" + year if sep else label


def year_suffixes(bib, keys) -> dict:
    """{key: letter} for the keys that share their label and year with another key."""
    by_label = {}
    for key in sorted(set(keys)):
        entry = bib.entries[key]
        label = (short_authors(entry), _latex(entry.fields.get("year", "n.d.")))
        by_label.setdefault(label, []).append(key)
    suffixes = {}
    for same in by_label.values():
        if len(same) > 1:
            same.sort(key=lambda k: (_latex(bib.entries[k].fields.get("title", "")).casefold(), k))
            suffixes.update({k: "abcdefghijklmnopqrstuvwxyz"[i] for i, k in enumerate(same)})
    return suffixes


def format_reference(entry, letter: bool = True) -> str:
    """One reference in the house style, as Markdown on one line.

    letter=False leaves out the year letter (2023b): the How to cite box is
    copied into papers, where a letter of this site would mean nothing.
    """
    fields = entry.fields
    parts = [
        f"{format_authors(entry)} ({format_year(entry, letter)}).",
        _sentence(_md_inline(_latex(fields.get("title", "")))),
        _sentence(_container(entry)),
    ]
    if fields.get("note"):
        parts.append(_sentence(_md_inline(_latex(fields["note"]))))
    parts.append(format_identifiers(entry))
    if fields.get("addendum"):
        parts.append(" ".join(fields["addendum"].split()))  # Markdown, as written
    return " ".join(p for p in parts if p and p != ".")


def format_short(entry, target: str | None = None) -> str:
    """'Pasche et al. (2023), [Towards “Biodiversity PMC”](link)'.

    The link goes to target (an anchor on the page) or to the DOI.
    """
    fields = entry.fields
    title = _md_inline(_latex(fields.get("shorttitle") or fields.get("title", "")))
    doi = fields.get("doi", "").strip()
    url = target or (_doi_url(doi) if doi else fields.get("url", "").strip())
    link = f"[{title}]({url})" if url else f"*{title}*"
    return f"{short_authors(entry)} ({format_year(entry)}), {link}"


def _sort_key(entry):
    """Newest first, then first author, then title."""
    persons = entry.persons.get("author", [])
    first = _person_family(persons[0]).casefold() if persons else ""
    year = int(re.sub(r"\D", "", entry.fields.get("year", "")) or 0)
    return (-year, first, _latex(entry.fields.get("title", "")).casefold())


def _missing(key: str) -> str:
    """Shown in the page in place of an unknown key, besides the warning."""
    return f"**Missing reference: {_md_inline(key)} (not in refs.bib)**"


def _ref_anchor(key: str, rendered: set, src: str) -> str:
    """<span id="ref-KEY"></span> for the first entry of KEY on the page."""
    if key in rendered:
        log.warning("sibils_data: %s is printed twice on %s", key, src or "a page")
        return ""
    rendered.add(key)
    return f'<span id="ref-{key}"></span>'


def render_cite(bib: Bibliography, keys: list, src: str = "", rendered: set | None = None) -> list:
    """Lines of <!-- sibils:cite KEY... -->: a Markdown list, years without letters."""
    rendered = set() if rendered is None else rendered
    lines = []
    for key in keys:
        entry = bib.get(key, src)
        if entry is None:
            lines.append(f"- {_missing(key)}")
        else:
            lines.append(f"- {_ref_anchor(key, rendered, src)}{format_reference(entry, letter=False)}")
    return lines


def render_bibliography(bib: Bibliography, group: str, src: str = "", rendered: set | None = None) -> list:
    """Lines of <!-- sibils:bibliography GROUP -->: the group, newest first."""
    rendered = set() if rendered is None else rendered
    keys = bib.groups().get(group)
    if not keys:
        log.warning("sibils_data: no entry of refs.bib has sibils_group = {%s} (%s)", group, src or "a page")
        return [f"**Missing group: {_md_inline(group)} (no entry of refs.bib has sibils_group = {{{_md_inline(group)}}})**"]
    bib.groups_shown.add(group)
    lines = ['<div class="biblio" markdown>', ""]
    for key in sorted(keys, key=lambda k: _sort_key(bib.entries[k])):
        entry = bib.entries[key]
        item = f"- {_ref_anchor(key, rendered, src)}{format_reference(entry)}"
        if entry.fields.get("sibils_use"):
            item += '<br><span class="biblio-note">' + " ".join(entry.fields["sibils_use"].split()) + "</span>"
        lines.append(item)
    return lines + ["", "</div>"]


def render_bibtex(bib: Bibliography, keys: list, src: str = "") -> list:
    """Lines of <!-- sibils:bibtex KEY... -->: a fenced code block."""
    blocks = [bib.source(k) if bib.get(k, src) is not None else f"% Missing reference: {k} (not in refs.bib)"
              for k in keys]
    return ["```bibtex", *"\n\n".join(blocks).split("\n"), "```"]


def _anchored_keys(markdown: str, bib: Bibliography) -> set:
    """Keys that a cite or bibliography marker of the page writes with id="ref-KEY"."""
    groups = bib.groups()
    keys = set()
    for m in MARKER_RE.finditer(markdown):
        if m.group("name") == "bibliography":
            for group in m.group("args").split():
                keys.update(groups.get(group, []))
        elif m.group("name") == "cite":
            keys.update(k for k in m.group("args").split() if k in bib.entries)
    return keys


def shown_keys(markdown: str, bib: Bibliography) -> set:
    """Keys of refs.bib that a page shows: cited, or written by a marker."""
    groups = bib.groups()
    keys = set()
    for is_code, text in split_code(markdown):
        if not is_code:
            for run in CITE_RUN_RE.finditer(text):
                keys.update(k for _, k in CITE_KEY_RE.findall(run.group(0)))
    for m in MARKER_RE.finditer(markdown):
        args = m.group("args").split()
        if m.group("name") in ("cite", "cite-short", "bibtex"):
            keys.update(args)
        elif m.group("name") == "bibliography":
            for group in args:
                keys.update(groups.get(group, []))
    return {k for k in keys if k in bib.entries}


# In-text citations: [@KEY], [-@KEY], [@a; @b], [@a] [@b] (one run).
# A key: letters, digits and _, with - : . / + inside (Pandoc's rule,
# without the characters that would break an id or a link: # $ % & ? < > ~).
CITE_KEY = r"\w(?:[\w:./+-]*\w)?"
_CITE_ITEMS = rf"\[-?@{CITE_KEY}(?:\s*;\s*-?@{CITE_KEY})*\]"
CITE_RUN_RE = re.compile(rf"{_CITE_ITEMS}(?:[ \t]{_CITE_ITEMS})*(?!\()")
CITE_KEY_RE = re.compile(rf"(-?)@({CITE_KEY})")
# "[@" or "[-@" up to "]" or the end of the line: what is left of it after
# the citations are linked is a mistake, unless it is the text of a link.
STRAY_CITE_RE = re.compile(r"\[-?@[^\]\n]*\]?")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
# A code span: a run of backticks, up to the same run, within a paragraph.
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(?:(?!\n[ \t]*\n).)+?(?<!`)\1(?!`)", re.S)


def split_code(markdown: str) -> list:
    """[(is_code, text)]: fenced blocks (``` or ~~~, at any indentation) and
    code spans are code; joining the texts gives the page back."""
    blocks, buf, fence = [], [], None
    for line in markdown.splitlines(keepends=True):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                if buf:
                    blocks.append((False, "".join(buf)))
                buf, fence = [line], m.group(1)
            else:
                buf.append(line)
            continue
        buf.append(line)
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                and not line.strip()[len(m.group(1)):].strip():
            blocks.append((True, "".join(buf)))
            buf, fence = [], None
    if buf:
        blocks.append((fence is not None, "".join(buf)))
    parts = []
    for is_code, text in blocks:
        if is_code:
            parts.append((True, text))
            continue
        pos = 0
        for m in CODE_SPAN_RE.finditer(text):
            parts += [(False, text[pos:m.start()]), (True, m.group(0))]
            pos = m.end()
        parts.append((False, text[pos:]))
    return parts


def _check_stray_citations(text: str, src: str) -> None:
    """Warn about the "[@" that are neither a citation nor the text of a link."""
    for m in STRAY_CITE_RE.finditer(text):
        found = m.group(0)
        if found.endswith("]") and text[m.end():m.end() + 1] == "(":
            continue  # [@name](url): a link
        if CITE_RUN_RE.fullmatch(found):
            continue  # an unknown key, already reported
        log.warning("sibils_data: citation not understood in %s: %s (write [@key], [-@key] or [@a; @b], "
                    "with nothing else inside the brackets)", src or "a page", found)


def link_citations(markdown: str, bib: Bibliography, src: str = "", rendered: set = frozenset()) -> str:
    """Author-year links for the citations of a page, and its References section."""
    cited = []

    def run(match):
        items = CITE_KEY_RE.findall(match.group(0))
        unknown = [k for _, k in items if k not in bib.entries]
        if unknown:
            log.warning("sibils_data: unknown citation key %s in %s (not in %s)", ", ".join(unknown),
                        src or "a page", bib.path.name)
            return match.group(0)
        links = {}
        for minus, key in items:
            entry = bib.entries[key]
            links.setdefault(key, (citation_label(entry).casefold(), short_authors(entry), bool(minus), key))
        # Sorted by label; works of the same authors share it: "Pasche et al., 2023b, 2023c".
        parts, previous = [], None
        for _, authors, minus, key in sorted(links.values()):
            entry = bib.entries[key]
            if authors == previous:
                parts.append(f", [{format_year(entry)}](#ref-{key})")
            else:
                text = format_year(entry) if minus else link_label(citation_label(entry))
                parts.append(("; " if parts else "") + f"[{text}](#ref-{key})")
            previous = authors
            if key not in cited:
                cited.append(key)
        return "(" + "".join(parts) + ")"

    def link(text):
        text = CITE_RUN_RE.sub(run, text)
        _check_stray_citations(text, src)
        return text

    markdown = "".join(text if is_code else link(text) for is_code, text in split_code(markdown))
    listed = sorted((k for k in cited if k not in rendered), key=lambda k: citation_label(bib.entries[k]).casefold())
    if listed:
        items = "\n".join(f'- <span id="ref-{k}"></span>{format_reference(bib.entries[k])}' for k in listed)
        markdown += f'\n\n## References\n\n<div class="biblio" markdown>\n\n{items}\n\n</div>\n'
    return markdown


def replace_markers(markdown: str, extra: dict, src: str = "", bib: Bibliography | None = None,
                    rendered: set | None = None) -> str:
    """Replace the <!-- sibils:... --> markers; rendered collects the keys given an id."""
    rendered = set() if rendered is None else rendered
    vocab_page = re.search(r"<!--\s*sibils:vocabularies\s*-->", markdown) is not None
    release = extra["terminologies_release"] if vocab_page else extra["release"]
    date = extra["terminologies_date_display"] if vocab_page else extra["date_display"]
    anchored = _anchored_keys(markdown, bib) if bib is not None else set()

    def block(match, lines):
        indent = match.group("indent")
        rest = markdown[match.end():].split("\n", 1)[0]
        if indent is None or rest.strip():
            log.warning("sibils_data: <!-- sibils:%s --> must be alone on its line in %s",
                        match.group("name"), src or "a page")
            return match.group(0)
        return "\n".join(indent + line if line else "" for line in lines)

    def repl(match):
        name = match.group("name")
        args = match.group("args").split()
        indent = match.group("indent") or ""
        if name in REF_MARKERS:
            if bib is None:
                log.warning("sibils_data: <!-- sibils:%s --> in %s, but refs.bib is not loaded", name, src)
                return match.group(0)
            if not args or (name in ("bibliography", "cite-short") and len(args) != 1):
                log.warning("sibils_data: wrong arguments in <!-- sibils:%s%s --> in %s",
                            name, match.group("args"), src or "a page")
                return match.group(0)
        if name == "cite":
            return block(match, render_cite(bib, args, src, rendered))
        if name == "bibliography":
            return block(match, render_bibliography(bib, args[0], src, rendered))
        if name == "bibtex":
            return block(match, render_bibtex(bib, args, src))
        if name == "cite-short":
            entry = bib.get(args[0], src)
            if entry is None:
                return indent + _missing(args[0])
            return indent + format_short(entry, f"#ref-{args[0]}" if args[0] in anchored else None)
        if args and name in ("vocabularies", "collection-counts", "release", "date", "terminology-browser"):
            log.warning("sibils_data: <!-- sibils:%s --> takes no argument (%s)", name, src or "a page")
            return match.group(0)
        if name == "vocabularies":
            return indent + render_vocabularies(extra, markdown)
        if name == "collection-counts":
            return indent + render_collection_counts(extra)
        if name == "release":
            return indent + md_text(release)
        if name == "date":
            return indent + date
        if name == "terminology-browser":
            browser = extra.get("terminology_browser")
            if not browser:
                log.warning("sibils_data: <!-- sibils:terminology-browser --> in %s, but mkdocs.yml has no "
                            "valid extra.terminology_browser", src or "a page")
                return match.group(0)
            # Print shows the link's address instead of the note (sibils.css).
            note = f'<span class="browser-note"> ({md_text(browser["note"])})</span>' if browser["note"] else ""
            return indent + _link(browser["name"], browser["url"]) + note
        log.warning("sibils_data: unknown marker <!-- sibils:%s --> in %s", name, src or "a page")
        return match.group(0)

    return MARKER_RE.sub(repl, markdown)


# --------------------------------------------------------------------------
# Requests to cite
#
# The site asks to be cited in the How to cite section of CITE_PAGE, with its
# box (the two SIBiLS papers) and its table of the papers of each service, and
# in the "Citation" row of the facts box of each service page (a page of the
# SERVICES_SECTION of the nav), which names the papers to cite as author-year
# citations and without "please": the papers of the service's row of the
# table, with those of the box. In a cell of the table, a sentence that says
# "described in" gives information, not a paper to cite (the KYBELE report of
# Question-Answering), and "with the X paper" brings the papers of the row of
# X (SynVar, with the Variomes paper).

CITE_PAGE = "publications.md"
SERVICES_SECTION = "Services"
CITE_ADMONITION_RE = re.compile(r"^[ \t]*(?:!!!|\?\?\?\+?)[ \t]+cite\b", re.M)
# "please" then "cite", "cites", "cited" or "citing" in the same sentence (and paragraph).
PLEASE_CITE_RE = re.compile(r"\bplease\b(?:(?![.!?]\s|\n[ \t]*\n).)*?\bcit(?:e[sd]?|ing)\b", re.I | re.S)
FACTS_RE = re.compile(r'<div class="facts" markdown>\n(.*?)\n</div>', re.S)
CITATION_ROW_RE = re.compile(r"^Citation[ \t]*\n:[ \t]+(?P<text>[^\n]*(?:\n[ \t]+[^\n]+)*)", re.M)
# A row of the table: | [Name](page.md) ... | cell |
TABLE_ROW_RE = re.compile(r"^\|[ \t]*\[(?P<name>[^\]]+)\]\((?P<link>[^)#\s]+)[^)]*\)[^|\n]*\|(?P<cell>[^\n]*)\|[ \t]*$",
                          re.M)
WITH_PAPER_RE = re.compile(r"\bwith the (?P<name>.+?) paper\b")


def _cell_keys(cell: str, cells: dict | None = None) -> set:
    """Keys of the papers to cite that a cell of the table gives; cells: {name: cell}."""
    keys = set()
    for sentence in re.split(r"(?<=\.)\s+", cell):
        if "described in" in sentence:
            continue
        keys.update(m.group("args").split()[0] for m in MARKER_RE.finditer(sentence)
                    if m.group("name") == "cite-short" and m.group("args").split())
        for m in WITH_PAPER_RE.finditer(sentence):
            if cells and m.group("name") in cells:
                keys |= _cell_keys(cells[m.group("name")])
    return keys


def check_cite_requests(pages: dict, services: list, cite_page: str = CITE_PAGE) -> list:
    """Problems with the requests to cite (see above), as messages.

    pages: {src_uri: Markdown} of every page; services: the src_uri of the
    service pages.
    """
    problems = []
    for src, markdown in sorted(pages.items()):
        if src == cite_page:
            continue
        text = "".join(part for is_code, part in split_code(markdown) if not is_code)
        if CITE_ADMONITION_RE.search(text) or any(m.group("name") == "cite" for m in MARKER_RE.finditer(text)):
            problems.append(f"{src} has a cite box: only {cite_page} asks to be cited")
        for m in PLEASE_CITE_RE.finditer(text):
            problems.append(f"{src} asks to cite (\"{' '.join(m.group(0).split())}\"): only {cite_page} asks to be"
                            " cited; a service page names its papers in the Citation row of its facts box")
    source = pages.get(cite_page)
    if source is None:
        return problems + ([f"no {cite_page}: the Citation rows cannot be checked"] if services else [])
    box = {k for m in MARKER_RE.finditer(source) if m.group("name") == "cite" for k in m.group("args").split()}
    rows = {}
    for m in TABLE_ROW_RE.finditer(source):
        target = posixpath.normpath(posixpath.join(posixpath.dirname(cite_page), m.group("link")))
        rows[target] = (m.group("name"), m.group("cell"))
    cells = dict(rows.values())
    for src in services:
        facts = FACTS_RE.search(pages.get(src, ""))
        row = CITATION_ROW_RE.search(facts.group(1)) if facts else None
        if row is None:
            problems.append(f"{src} has no Citation row in its facts box: a service page names there the papers"
                            f" to cite, as in the table of {cite_page}")
            continue
        if src not in rows:
            problems.append(f"{src} has no row in the table of {cite_page}")
            continue
        keys = {key for run in CITE_RUN_RE.finditer(row.group("text")) for _, key in CITE_KEY_RE.findall(run.group(0))}
        expected = _cell_keys(rows[src][1], cells) | box
        if keys != expected:
            problems.append(f"the Citation row of {src} cites {', '.join(sorted(keys)) or 'nothing'}; the row of"
                            f" {rows[src][0]} in the table of {cite_page}, with its How to cite box, gives"
                            f" {', '.join(sorted(expected))}")
    return problems


# --------------------------------------------------------------------------
# MkDocs events


def on_config(config, **kwargs):
    try:
        datasets, message = load_datasets()
    except DataError as exc:
        from mkdocs.exceptions import PluginError

        raise PluginError(f"sibils_data: no API data and no usable snapshot: {exc}") from exc
    extra = build_extra(datasets)
    extra["terminology_browser"] = browser_settings(config["extra"].get("terminology_browser"))
    corrections = extra["terminology_corrections"]
    message += f"; {len(corrections['applied'])} vocabulary corrections applied"
    if corrections["stale"]:
        message += " (no longer matching the API, remove them: " + ", ".join(corrections["stale"]) + ")"
    log.info(message)
    config["extra"]["sibils"] = extra
    global BIB
    try:
        BIB = Bibliography(Path(config["config_file_path"]).parent / "refs.bib")
    except Exception as exc:  # a syntax error in refs.bib, a missing file
        from mkdocs.exceptions import PluginError

        raise PluginError(f"sibils_data: cannot read refs.bib: {exc}") from exc
    return config


BIB: Bibliography | None = None


def on_files(files, config, **kwargs):
    # Year letters (2023a, 2023b) depend on every work the site shows.
    if BIB is not None:
        keys = set()
        for file in files.documentation_pages():
            keys |= shown_keys(Path(file.abs_src_path).read_text(encoding="utf-8"), BIB)
        YEAR_SUFFIX.clear()
        YEAR_SUFFIX.update(year_suffixes(BIB, keys))
    return files


def on_nav(nav, config, files, **kwargs):
    # Requests to cite: only on publications.md; a Citation row on each service page.
    services = None
    for item in nav.items:
        if item.is_section and item.title == SERVICES_SECTION:
            services = [child.file.src_uri for child in item.children if child.is_page]
    if services is None:
        log.warning("sibils_data: no %s section in the nav, so no service page is checked for its Citation row",
                    SERVICES_SECTION)
    pages = {file.src_uri: Path(file.abs_src_path).read_text(encoding="utf-8")
             for file in files.documentation_pages()}
    for problem in check_cite_requests(pages, services or []):
        log.warning("sibils_data: %s", problem)
    return nav


def on_page_markdown(markdown, page, config, files, **kwargs):
    rendered = set()
    if "sibils:" in markdown:
        markdown = replace_markers(markdown, config["extra"]["sibils"], page.file.src_uri, BIB, rendered)
    if BIB is not None and "@" in markdown:
        markdown = link_citations(markdown, BIB, page.file.src_uri, rendered)
    return markdown


def on_post_build(config, **kwargs):
    if BIB is None:
        return
    for group, keys in sorted(BIB.groups().items()):
        if group not in BIB.groups_shown:
            log.warning("sibils_data: no page has <!-- sibils:bibliography %s -->; not shown: %s",
                        group, ", ".join(keys))


# --------------------------------------------------------------------------
# Command line


def _write_json(path: Path, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    mode = (path.stat().st_mode & 0o777) if path.exists() else 0o644
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def refresh(data_dir: Path = DATA_DIR) -> int:
    base = api_base()
    if offline():
        print("SIBILS_OFFLINE is set; --refresh calls the API anyway.")
    fetched = {}
    for name in DATASETS:
        url = base + DATASETS[name][0]
        try:
            fetched[name] = fetch_dataset(name, base)
        except Exception as exc:
            print(f"error: {url}: {describe_error(exc)}; snapshots not changed", file=sys.stderr)
            return 1
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, ds in fetched.items():
        path = data_dir / DATASETS[name][1]
        _write_json(path, {"saved": ds["date"], **ds["payload"]})
        print(f"wrote {path} (release {ds['release']}, saved {ds['date']})")
    return 0


def selftest() -> int:
    """Check the snapshots, the validation, the fallback and the rendering."""
    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    # 1. Snapshots load and validate.
    datasets = {name: load_snapshot(name) for name in DATASETS}
    extra = build_extra(datasets)
    check(re.fullmatch(r"\d+(\.\d+)+", extra["release"]) is not None, f"release {extra['release']!r}")
    for key in ("counts", "release", "date", "source", "terminologies", "terminologies_release"):
        check(key in extra, f"config.extra.sibils.{key} missing")
    for cid in REQUIRED_COLLECTIONS:
        check(cid in extra["counts"], f"collection {cid} missing")

    # 2. Validators reject broken answers.
    good_count = datasets["count"]["payload"]
    good_termino = datasets["terminologies"]["payload"]
    bad = []
    broken = copy.deepcopy(good_count)
    broken["success"] = False
    bad.append(("count", broken))
    broken = copy.deepcopy(good_count)
    del broken["count"]["pmc"]
    bad.append(("count", broken))
    broken = copy.deepcopy(good_count)
    broken["count"]["medline"]["all"] = "many"
    bad.append(("count", broken))
    broken = copy.deepcopy(good_termino)
    broken["terminologies"] = {}
    bad.append(("terminologies", broken))
    broken = copy.deepcopy(good_termino)
    next(iter(broken["terminologies"].values())).pop("version")
    bad.append(("terminologies", broken))
    bad.append(("terminologies", ["not", "an", "object"]))
    for name, payload in bad:
        try:
            VALIDATORS[name](payload)
            failures.append(f"{name}: broken payload accepted")
        except DataError:
            pass

    # 3. An unreachable API falls back to the snapshots (port 9 refuses connections).
    fallback, message = load_datasets(use_network=True, base="http://127.0.0.1:9/api")
    check(all(ds["source"] == "snapshot" for ds in fallback.values()), "fallback did not use the snapshots")
    check("snapshot" in message, "fallback message")

    # The Terminology Browser setting comes from mkdocs.yml; a fixed value here.
    extra["terminology_browser"] = browser_settings(
        {"name": "Terminology Browser", "url": "https://browser.example/x", "note": "development server"})
    check(extra["terminology_browser"]["url"] == "https://browser.example/x/", "browser url ends with /")
    check(browser_settings({"name": "Terminology Browser", "url": "ftp://x"}) is None, "browser url not http(s)")

    # 4. Rendering.
    vocab_page = (REPO_DIR / "docs" / "vocabularies.md").read_text(encoding="utf-8")
    vocab_md = replace_markers(vocab_page, extra, "vocabularies.md")
    counts_md = replace_markers("<!-- sibils:collection-counts -->", extra, "test")
    check(MARKER_RE.search(vocab_md) is None, "marker left on the vocabularies page")
    for e in extra["terminologies"]:
        check(vocab_md.count(f'<span id="{e["name_termino"]}"></span>') == 1, f"anchor {e['name_termino']}")
    for word in ("None", "null", "xxx"):
        check(re.search(rf"\b{word}\b", vocab_md) is None, f"{word!r} in the vocabularies page")
    rows = [line for line in vocab_md.splitlines() if line.startswith("| <span id=")]
    check(len(rows) == len(extra["terminologies"]), "one row per vocabulary")
    for row in rows:
        check(len(re.findall(r"(?<!\\)\|", row)) == 3, f"cells in row {row[:60]}")
    for e in extra["terminologies"]:
        check(vocab_md.count(f'href="https://browser.example/x/terminology/{e["name_termino"]}"') == 1,
              f"browser link {e['name_termino']}")
    check(replace_markers("the <!-- sibils:terminology-browser -->.", extra, "test")
          == 'the <a href="https://browser.example/x/">Terminology Browser</a>'
          '<span class="browser-note"> (development server)</span>.',
          "terminology-browser marker")
    check(replace_markers("<!-- sibils:terminology-browser -->", {**extra, "terminology_browser": None}, "test")
          .startswith("<!--"), "terminology-browser marker without the mkdocs.yml setting")
    check("vocab-browse" not in render_vocabularies({**extra, "terminology_browser": None}),
          "browser links without the mkdocs.yml setting")
    count_rows = [line for line in counts_md.splitlines() if line.startswith("| ")]
    check(len(count_rows) == len(extra["collections"]) + 1, "one counts row per collection")
    check(extra["release"] in counts_md and extra["date_display"] in counts_md, "as-of line")
    check(long_date("2026-01-05") == "5 January 2026", "long_date")
    # The date is the build's (or the snapshot's), never "from the API on <date>".
    live_md = render_collection_counts({**extra, "source": "live"})
    check(f"Counts at the last build of this site, {extra['date_display']}" in live_md, "date line (live)")
    check(f"Counts saved on {extra['date_display']}" in counts_md, "date line (snapshot)")
    check("from the SIBiLS API on" not in live_md + counts_md, "date line reads as the date of the data")

    # 5. Approximate counts of the home page: round lower bounds with the same
    # number of digits, within 10%.
    examples = {
        41_438_260: 41_000_000, 9_331_692: 9_300_000, 34_562_768: 34_000_000,
        1_101_077: 1_100_000, 433_314: 430_000, 41_435_461: 41_000_000,
        0: 0, 7: 7, 99: 99, 100: 100, 109: 100, 999: 990, 1_000: 1_000, 10_999: 10_000,
    }
    for n, expected in examples.items():
        check(approximate(n) == expected, f"approximate({n}) = {approximate(n)}, expected {expected}")
    for n in list(range(0, 2_000, 7)) + [10**k + d for k in range(2, 12) for d in (-1, 0, 1, 10**k // 3)]:
        a = approximate(n)
        if not (a <= n and len(str(a)) == len(str(n)) and n - a < max(1, n / 10)):
            failures.append(f"approximate({n}) = {a}: not a lower bound with the same digits within 10%")
            break
    for c in extra["collections"]:
        check(c["approx"] == approximate(c["all"]) and c["approx_display"] == fmt_int(c["approx"]),
              f"approx of {c['id']}")
        check(c["live_min"] == c["approx"] // 2 <= c["all"], f"live_min of {c['id']}")
    check(extra["count_url"] == api_base() + "/count", "count_url")
    check(count_url("https://example.org/api") == "https://example.org/api/count", "count_url(base)")

    # 6. Vocabulary corrections: applied to the snapshot, without changing the
    # input; a correction whose API value has changed is reported as stale.
    corrections = extra["terminology_corrections"]
    raw = datasets["terminologies"]["terminologies"]
    raw_copy = copy.deepcopy(raw)
    sample = {"x": {"label": ("Old", "New"), "description": ("Starts", "Fixed.")}, "missing": {"url": ("a", "b")}}
    entries = [{"name_termino": "x", "label": "Old", "description": "Starts  with this", "code": "x", "type": "t", "version": "1"}]
    fixed, applied, stale = apply_terminology_overrides(entries, sample)
    check(fixed[0]["label"] == "New" and fixed[0]["description"] == "Fixed.", "override applied")
    check(entries[0]["label"] == "Old", "override modified its input")
    check(applied == ["x.label", "x.description"] and stale == ["missing.url"], "override applied/stale lists")
    apply_terminology_overrides(raw)
    check(raw == raw_copy, "overrides modified the snapshot entries")
    names = {e["name_termino"] for e in extra["terminologies"]}
    check(all(name in names for name in TERMINOLOGY_OVERRIDES), "override for an unknown vocabulary")

    # 7. References: the house style, the markers, no LaTeX left in the output.
    bib = Bibliography()
    expected = (
        "Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P (2020). SIB Literature Services: RESTful"
        " customizable search engines in biomedical literature, enriched with automatically mapped biomedical"
        " concepts. *Nucleic Acids Research* 48(W1):W12–W16. [doi:10.1093/nar/gkaa328]"
        "(https://doi.org/10.1093/nar/gkaa328)\u00a0· [PMID 32379317](https://pubmed.ncbi.nlm.nih.gov/32379317/)"
    )
    check(format_reference(bib.entries["10_1093_nar_gkaa328"]) == expected, "house style of 10_1093_nar_gkaa328")
    for key, entry in bib.entries.items():
        text = format_reference(entry)
        check(not re.search(r"[{}]|\\[a-z]|--|``", text), f"LaTeX left in the reference {key}: {text[:80]}")
        if entry.fields.get("sibils_group"):
            check(bool(entry.fields.get("doi") or entry.fields.get("url")), f"{key}: listed without a link")
    page = "!!! cite\n    Cite:\n\n    <!-- sibils:cite 10_1093_nar_gkaa328 -->\n"
    check(replace_markers(page, extra, "test", bib)
          == '!!! cite\n    Cite:\n\n    - <span id="ref-10_1093_nar_gkaa328"></span>' + expected + "\n",
          "cite marker keeps the indentation")
    block = render_bibtex(bib, ["10_1093_nar_gkaa328"])
    check(block[0] == "```bibtex" and block[1] == "@article{10_1093_nar_gkaa328," and block[-1] == "```",
          "BibTeX block")
    check(all(not re.search(r"^\s*(sibils_|comment\s*=|addendum\s*=)", bib.source(k), re.M) for k in bib.entries),
          "private fields in a BibTeX block")
    # Every author is listed (no "et al." unless refs.bib says "and others").
    check(format_authors(bib.entries["pasche2023sibils"]).count(", ") == 10, "all 11 authors of pasche2023sibils")
    # An unknown key is shown in the page, not only logged.
    shown = replace_markers("<!-- sibils:cite nosuchkey -->\n", extra, "test", bib)
    check("Missing reference: nosuchkey" in shown, "unknown key in a cite marker is visible")
    check("Missing reference" in replace_markers("x <!-- sibils:cite-short nosuchkey --> y", extra, "test", bib),
          "unknown key in a cite-short marker is visible")
    check("Missing group" in replace_markers("<!-- sibils:bibliography nosuchgroup -->", extra, "test", bib),
          "unknown group is visible")
    # cite-short links to the entry when the page lists it, else to the DOI.
    group, keys = next(iter(bib.groups().items()))
    with_list = replace_markers(f"<!-- sibils:cite-short {keys[0]} -->\n\n<!-- sibils:bibliography {group} -->\n",
                                extra, "test", bib)
    check(f"](#ref-{keys[0]})" in with_list, "cite-short links to the entry listed on the page")
    alone = replace_markers("<!-- sibils:cite-short 10_1093_nar_gkaa328 -->", extra, "test", bib)
    check("](https://doi.org/10.1093/nar/gkaa328)" in alone, "cite-short links to the DOI")
    # A block marker in running text is left as written.
    check(replace_markers("see <!-- sibils:cite 10_1093_nar_gkaa328 -->", extra, "test", bib).endswith("-->"),
          "block marker in running text")

    # 8. In-text citations: labels, year letters, runs, code left alone.
    keys = set()
    for path in (REPO_DIR / "docs").rglob("*.md"):
        keys |= shown_keys(path.read_text(encoding="utf-8"), bib)
    YEAR_SUFFIX.clear()
    YEAR_SUFFIX.update(year_suffixes(bib, keys))
    check({k: v for k, v in YEAR_SUFFIX.items() if k.startswith("pasche2023")}
          == {"pasche2023supplementary": "a", "pasche2023sibils": "b", "pasche2023towards": "c"}, "year letters")
    check(citation_label(bib.entries["10_1093_nar_gkaa328"]) == "Gobeill et al., 2020", "label, 3+ authors")
    check(citation_label(bib.entries["gobeill2026videos"]) == "Gobeill and Ruch, 2026", "label, 2 authors")
    check(citation_label(bib.entries["sib2025sab"]) == "SIB Swiss Institute of Bioinformatics, 2025", "label, organisation")
    cite = lambda md, rendered=frozenset(): link_citations(md, bib, "test", rendered)
    check(link_label("SIB Swiss Institute of Bioinformatics, 2025") == "SIB Swiss Institute of Bioinformatics,\u00a02025"
          and link_label("Gobeill and Ruch, 2026") == "Gobeill and Ruch,\u00a02026", "link text: no break before the year")
    out = cite("Pasche et al. [-@pasche2023towards] [-@pasche2023sibils] x")
    check(out.startswith("Pasche et al. ([2023b](#ref-pasche2023sibils), [2023c](#ref-pasche2023towards)) x"),
          "run of [-@] citations: one parenthesis, sorted by label")
    out = cite("a [@pasche2023towards; @10_1093_nar_gkaa328; @pasche2023sibils]")
    check(out.startswith("a ([Gobeill et\u00a0al.,\u00a02020](#ref-10_1093_nar_gkaa328); [Pasche et\u00a0al.,\u00a02023b]"
                         "(#ref-pasche2023sibils), [2023c](#ref-pasche2023towards))"),
          "works of the same authors share the label")
    check(cite("a [@10_1093_nar_gkaa328; @caucheteur2026sibils].").startswith(
        "a ([Caucheteur et\u00a0al.,\u00a02026](#ref-caucheteur2026sibils); [Gobeill et\u00a0al.,\u00a02020](#ref-10_1093_nar_gkaa328))."),
          "[@a; @b] gives one parenthesis")
    out = cite("a [@10_1093_nar_gkaa328].")
    check('\n## References\n\n<div class="biblio" markdown>\n\n- <span id="ref-10_1093_nar_gkaa328"></span>' in out,
          "References section for a work the page does not list")
    check("## References" not in cite("a [@10_1093_nar_gkaa328].", {"10_1093_nar_gkaa328"}),
          "no References section when the page lists the work")
    out = cite("a [@10_1093_nar_gkaa328] [@caucheteur2026sibils].", {"10_1093_nar_gkaa328"})
    check('\n## References\n\n<div class="biblio" markdown>\n\n- <span id="ref-caucheteur2026sibils"></span>' in out
          and 'id="ref-10_1093_nar_gkaa328"' not in out, "References lists only the works the page does not list")
    check(cite("a [@nosuchkey] b") == "a [@nosuchkey] b", "unknown key left as written")
    # A citation that is not understood stays as written, with a warning
    # (the strict build stops); a link whose text starts with "@" is not one.
    warnings = []
    handler = logging.Handler()
    handler.emit = lambda record: warnings.append(record.getMessage())
    log.addHandler(handler)
    try:
        for text in ("[@10_1093_nar_gkaa328, p. 5]", "[@ 10_1093_nar_gkaa328]", "[@10_1093_nar_gkaa328 ]",
                     "[-@ 10_1093_nar_gkaa328]", "[@10_1093_nar_gkaa328.]", "[see @10_1093_nar_gkaa328"):
            warnings.clear()
            out = cite(f"a {text} b")
            check(text in out and "## References" not in out
                  and (len(warnings) == 1 if text.startswith("[@") or text.startswith("[-@") else not warnings),
                  f"citation not understood: {text} ({warnings})")
        warnings.clear()
        out = cite("[@sibils](https://example.org/), [@nosuchkey], `[@x, p. 5]`")
        check(out.startswith("[@sibils](https://example.org/), [@nosuchkey], `[@x, p. 5]`")
              and len(warnings) == 1 and "unknown citation key nosuchkey" in warnings[0],
              f"links, unknown keys and code: no 'not understood' warning ({warnings})")
    finally:
        log.removeHandler(handler)
    # Keys with : . / + (BibTeX allows them).
    bib.entries["doe:2020/x.y+z"] = bib.entries["10_1093_nar_gkaa328"]
    try:
        check(cite("a [@doe:2020/x.y+z].").startswith("a ([Gobeill et\u00a0al.,\u00a02020](#ref-doe:2020/x.y+z))."),
              "key with : / . +")
    finally:
        del bib.entries["doe:2020/x.y+z"]
    code = ("!!! note\n\n    ```json\n    {\"x\": \"[@10_1093_nar_gkaa328]\"}\n    ```\n\n"
            "~~~\n[@10_1093_nar_gkaa328]\n~~~\n\nInline `[@10_1093_nar_gkaa328]` code.\n")
    check(cite(code) == code, "citations in fenced blocks (any indentation, ``` or ~~~) and code spans are left alone")
    double = replace_markers("<!-- sibils:cite 10_1093_nar_gkaa328 -->\n\n<!-- sibils:cite 10_1093_nar_gkaa328 -->\n",
                             extra, "test", bib)
    check(double.count('id="ref-10_1093_nar_gkaa328"') == 1, "a work printed twice gets one id")
    check(format_reference(bib.entries["pasche2023towards"]).startswith("Pasche E, Agosti D, Penev L, Groom Q,"
                                                                         " Flament A, Gobeill J, Ruch P (2023c)."),
          "year letter in the full reference")
    box = replace_markers("<!-- sibils:cite pasche2023towards -->", extra, "test", bib)
    check("Ruch P (2023). Towards" in box and "2023c" not in box, "no year letter in a How to cite box")

    # 9. Requests to cite: only on publications.md; a Citation row on each
    # service page, with the papers of its row of the table and of the box.
    sibils = "Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]"

    def service(row):
        return f'# S\n\n<div class="facts" markdown>\n\nAPI\n:   x\n\nCitation\n:   {row}\n\n</div>\n\nText.\n'

    good = {
        "publications.md": (
            '## How to cite\n\n!!! cite ""\n\n    If you use SIBiLS, please cite both papers:\n\n'
            "    <!-- sibils:cite 10_1093_nar_gkaa328 caucheteur2026sibils -->\n\n"
            "| Service or data | Publication |\n|---|---|\n"
            "| [Variomes](services/variomes/index.md) | <!-- sibils:cite-short pasche2022variomes --> |\n"
            "| [SynVar](services/synvar/index.md) | <!-- sibils:cite-short mottaz2022synvar -->, with the Variomes paper |\n"
            "| [QA](services/qa/index.md) | No dedicated publication. The pipeline is described in a report,"
            " <!-- sibils:cite-short flament2026qademonstrator --> |\n"
            "| [COVoc](data/vocabularies.md#covoc) vocabularies | <!-- sibils:cite-short caucheteur2023covoc --> |\n"),
        "services/variomes/index.md": service(f"Pasche et al. [-@pasche2022variomes], with the SIBiLS papers {sibils}"),
        "services/synvar/index.md": service(f"Mottaz et al. [-@mottaz2022synvar], with the Variomes paper Pasche et al."
                                            f" [-@pasche2022variomes] and the SIBiLS papers {sibils}"),
        "services/qa/index.md": service(f"The SIBiLS papers {sibils}") + "Described in [@flament2026qademonstrator].\n",
        "about/index.md": ("To cite SIBiLS, see [How to cite](../publications.md#how-to-cite). Please write to us."
                           " We cite the report [@flament2026qademonstrator]. Please read the citation rules.\n\n"
                           "```markdown\n!!! cite \"\"\n"
                           "    Please cite:\n\n    <!-- sibils:cite pasche2022variomes -->\n```\n"),
    }
    services = ["services/variomes/index.md", "services/synvar/index.md", "services/qa/index.md"]
    found = check_cite_requests(good, services)
    check(found == [], f"requests to cite where the site makes them: {found}")
    for change, expected in (
            ({"about/index.md": '!!! cite ""\n    <!-- sibils:cite pasche2022variomes -->\n'}, "has a cite box"),
            ({"about/index.md": "??? cite \"BibTeX\"\n    x\n"}, "has a cite box"),
            ({"about/index.md": "If you use it,\nplease also cite the SIBiLS papers.\n"}, "asks to cite"),
            ({"about/index.md": "If you use it, please consider citing the SIBiLS papers.\n"}, "asks to cite"),
            ({"about/index.md": "Please check that your paper cites both papers.\n"}, "asks to cite"),
            ({"about/index.md": "Please make sure that\nthe SIBiLS papers are cited.\n"}, "asks to cite"),
            ({"services/qa/index.md": "# S\n\nNo facts box.\n"}, "has no Citation row"),
            ({"services/qa/index.md": service("The SIBiLS paper Gobeill et al. [-@10_1093_nar_gkaa328]")},
             "the Citation row of services/qa/index.md cites 10_1093_nar_gkaa328;"),
            ({"services/synvar/index.md": service(f"Mottaz et al. [-@mottaz2022synvar], with the SIBiLS papers {sibils}")},
             "pasche2022variomes"),
            ({"services/triage/index.md": service(f"The SIBiLS papers {sibils}")}, "has no row in the table")):
        pages = dict(good, **change)
        found = check_cite_requests(pages, services + [k for k in change if k.startswith("services/")
                                                       and k not in services])
        check(len(found) == 1 and expected in found[0], f"requests to cite, {expected!r}: {found}")

    tables = None
    try:
        import markdown as markdown_lib

        # "|" in a title is escaped; with the tables extension the escape
        # gives "|" in a list item and in a table cell.
        sample = "a | b"
        cell = markdown_lib.markdown(f"| x |\n|---|\n| {_md_inline(sample)} |", extensions=["tables"])
        item = markdown_lib.markdown(f"- {_md_inline(sample)}", extensions=["tables"])
        check("<td>a | b</td>" in cell and "<li>a | b</li>" in item, "escaped | in a table cell and a list")

        page_html = markdown_lib.markdown(vocab_md, extensions=["tables", "attr_list", "md_in_html", "toc"])
        tables = page_html.count("<table>")
        n_groups = sum(len(c["groups"]) for c in extra["terminology_groups"])
        check(tables == n_groups + 1, f"{tables} tables in the HTML, expected {n_groups + 1}")
        counts_html = markdown_lib.markdown(counts_md, extensions=["tables"])
        check(counts_html.count("<tr>") == len(extra["collections"]) + 1, "counts table rows in the HTML")
    except ImportError:
        print("(markdown package not available: HTML check skipped)")

    # Summary.
    print(f"count:         release {extra['release']}, {extra['source']}, {extra['date']}")
    for c in extra["collections"]:
        parts = ", ".join(f"{p['label']} {p['count_display']}" for p in c["partitions"])
        print(f"  {c['table_label']:<20} {c['all_display']:>12} (home page: {c['approx_display']})  {parts}")
    print(
        f"terminologies: release {extra['terminologies_release']}, {extra['terminologies_source']}, "
        f"{extra['terminologies_date']}, {len(extra['terminologies'])} vocabularies"
    )
    for cat in extra["terminology_groups"]:
        sizes = ", ".join(f"{g['title'] or '(no subcategory)'} {len(g['entries'])}" for g in cat["groups"])
        print(f"  {cat['title']:<32} {sizes}")
    print(f"rendered:      vocabularies {len(vocab_md):,} characters" + (f", {tables} tables" if tables else ""))
    print(f"corrections:   {len(corrections['applied'])} applied"
          + (f", no longer matching: {', '.join(corrections['stale'])}" if corrections["stale"] else ""))
    print(f"fallback:      {message}")
    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print("  - " + failure)
        return 1
    print("OK")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true", help="rewrite data/*.json from the API")
    group.add_argument("--selftest", action="store_true", help="check the snapshots and the rendering")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    return refresh() if args.refresh else selftest()


if __name__ == "__main__":
    sys.exit(main())
