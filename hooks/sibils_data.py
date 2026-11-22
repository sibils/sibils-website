#!/usr/bin/env python3
"""SIBiLS data for the website: collection counts and vocabularies.

MkDocs hook, registered under ``hooks:`` in mkdocs.yml. It uses the Python
standard library only.

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

and these markers are replaced in the Markdown of the pages:

    <!-- sibils:vocabularies -->       vocabulary tables, by category
    <!-- sibils:collection-counts -->  table of documents per collection
    <!-- sibils:release -->            SIBiLS release, for example 5.1.5.10
    <!-- sibils:date -->               build day, or the day the snapshot was saved,
                                       for example 22 November 2026 (the API gives
                                       no date: not the day the SIBiLS data changed)

On the page that contains ``sibils:vocabularies``, ``release`` and ``date``
describe the vocabulary data; on all other pages they describe the counts.
An unknown ``sibils:`` marker is reported as a warning (it is a typo in a page).

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
import html
import json
import logging
import os
import re
import socket
import sys
import tempfile
import urllib.error
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

MARKER_RE = re.compile(r"<!--\s*sibils:([A-Za-z0-9_-]+)\s*-->")


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


def replace_markers(markdown: str, extra: dict, src: str = "") -> str:
    vocab_page = re.search(r"<!--\s*sibils:vocabularies\s*-->", markdown) is not None
    release = extra["terminologies_release"] if vocab_page else extra["release"]
    date = extra["terminologies_date_display"] if vocab_page else extra["date_display"]

    def repl(match):
        name = match.group(1)
        if name == "vocabularies":
            return render_vocabularies(extra, markdown)
        if name == "collection-counts":
            return render_collection_counts(extra)
        if name == "release":
            return md_text(release)
        if name == "date":
            return date
        log.warning("sibils_data: unknown marker <!-- sibils:%s --> in %s", name, src or "a page")
        return match.group(0)

    return MARKER_RE.sub(repl, markdown)


# --------------------------------------------------------------------------
# MkDocs events


def on_config(config, **kwargs):
    try:
        datasets, message = load_datasets()
    except DataError as exc:
        from mkdocs.exceptions import PluginError

        raise PluginError(f"sibils_data: no API data and no usable snapshot: {exc}") from exc
    extra = build_extra(datasets)
    corrections = extra["terminology_corrections"]
    message += f"; {len(corrections['applied'])} vocabulary corrections applied"
    if corrections["stale"]:
        message += " (no longer matching the API, remove them: " + ", ".join(corrections["stale"]) + ")"
    log.info(message)
    config["extra"]["sibils"] = extra
    return config


def on_page_markdown(markdown, page, config, files, **kwargs):
    if "sibils:" not in markdown:
        return markdown
    return replace_markers(markdown, config["extra"]["sibils"], page.file.src_uri)


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

    tables = None
    try:
        import markdown as markdown_lib

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
