#!/usr/bin/env python3
"""Addresses of sibils.org: redirect pages, published addresses, home buttons.

MkDocs hook, registered under ``hooks:`` in mkdocs.yml. sibils.org is a static
site: every deployment replaces the whole directory with the gh-pages branch,
and its server has no redirect rules for moved pages, so a page that moves
would answer 404 at its old address. For each entry of ``extra.redirects`` in
mkdocs.yml, this hook writes ``<old address>/index.html`` into the built site:
a page with no content of its own that sends the browser to the new page at
once.

    extra:
      redirects:
        api/biodiversitypmc/fetch/: developers/biodiversitypmc/fetch.md
        api/:
          page: developers/index.md
          fragments:
            sparql: developers/sparql/index.md
            fetch-api: developers/biodiversitypmc/fetch.md

Key: the old address, as published, in lower case, without the leading slash
and with the trailing one. Value: the Markdown file of the page that replaces
it; or ``page`` (that file) and ``fragments``, which sends old anchors with a
clear successor to another page or heading: ``old-id: file.md`` or
``old-id: file.md#new-id``. Anchors are matched without regard to case
(registries link https://sibils.org/api#Fetch-API).

The redirect page:

- calls ``location.replace()``, which leaves the old address out of the
  browser history. A ``#fragment`` listed under ``fragments`` goes to its
  successor; any other ``#fragment``, and the ``?query``, are passed on to the
  new page. Most anchors of the pages published before the redesign do not
  exist on the new pages: the browser then shows the new page from the top;
- has an instant ``<meta http-equiv="refresh">`` for browsers without
  JavaScript (it drops the ``?query`` and the ``#fragment``), which search
  engines read as a permanent redirect;
- names the new page in ``<link rel="canonical">`` (absolute URL, from
  ``site_url``) and in a plain link;
- loads no tracker: Matomo counts the visit once, on the new page.

The deployment (.github/workflows/publish.yml) does not run ``--strict``, so
every problem below stops the build (PluginError) instead of logging a warning
that nobody reads: a broken entry would otherwise publish a 404.

- a key that is not a lower-case path like ``api/synvar/`` (an address that
  differs only by case, such as /API/..., would share a folder with /api/ on
  macOS and Windows: handle it on the server);
- a value that is not a page of the site, or a ``fragments`` entry whose page
  or heading does not exist: when the new page moves again, update the value
  (never chain redirects); never remove an entry;
- two ``fragments`` keys that differ only by case;
- a key that is still the address of a page, or a file the build already
  wrote;
- a page whose address would start with /api/: no page of sibils.org is
  under /api/ (README.md, "Addresses");
- an address of data/published-urls.txt that has neither a page, nor a
  redirect page, nor a file of the site (a file that the theme writes, such
  as sitemap.xml, is looked for after the build): a listed address never
  disappears, so a page that moves needs an extra.redirects entry, and a line
  of the list is never removed;
- a button of the home page (front matter ``hero_actions``) whose ``url`` is
  a relative path that is not a page of the site (``developers/index.md``,
  optionally with ``#heading``, checked after the build): the theme macro
  that writes these links (resolve_url in theme/partials/macros.html) cannot
  check them.

A page whose address is not in data/published-urls.txt, or an
extra.redirects key that is not, is a warning (``--strict`` stops on it): add
the address of a new page to the list in the same commit, so that the list
stays complete. The list holds the production addresses: they are compared
with https://sibils.org/, not with ``site_url``, which ``mkdocs serve``
replaces with its own address (http://127.0.0.1:8000/).

``python hooks/redirects.py --selftest`` checks these rules against the
pages and the settings of the repository.
"""

from __future__ import annotations

import html
import json
import logging
import posixpath
import re
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.redirects")

REPO_DIR = Path(__file__).resolve().parent.parent
PUBLISHED_FILE = "data/published-urls.txt"  # relative to mkdocs.yml
PUBLISHED_ORIGIN = "https://sibils.org/"  # of every address of the list

PAGE_URLS: dict[str, str] = {}  # "developers/qa/index.md" -> "developers/qa/"
PAGE_DEST: dict[str, str] = {}  # "developers/qa/index.md" -> "developers/qa/index.html"
# "api/" -> ("developers/", {"fetch-api": ("developers/biodiversitypmc/fetch/", "")})
REDIRECTS: dict[str, tuple[str, dict[str, tuple[str, str]]]] = {}
# Headings to find in the built site: (where it is used, page src_uri, id).
ANCHORS: list[tuple[str, str, str]] = []
# Listed files that the theme writes during the build (static_templates, such
# as sitemap.xml), to find in the built site: (address, where it is listed).
THEME_FILES: list[tuple[str, str]] = []

MARKER = "<title>Page moved – SIBiLS</title>"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
""" + MARKER + """
<link rel="canonical" href="{canonical}">
<script>(function () {{
  var to = {target_js}, map = {map_js}, id = location.hash.slice(1), m;
  try {{ id = decodeURIComponent(id); }} catch (e) {{}}
  m = Object.prototype.hasOwnProperty.call(map, id.toLowerCase()) && map[id.toLowerCase()];
  location.replace(m ? m[0] + location.search + m[1] : to + location.search + location.hash);
}})();</script>
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
<p>This page has moved to <a href="{target}">{canonical}</a>.</p>
</body>
</html>
"""


def fail(message: str):
    raise PluginError(f"redirects: {message}")


def valid_key(old) -> bool:
    if not isinstance(old, str) or not old.endswith("/") or old.startswith("/") or old != old.lower():
        return False
    parts = old[:-1].split("/")
    return all(p and p not in (".", "..") and p == p.strip() for p in parts)


def page_target(where: str, value, anchor_allowed: bool) -> tuple[str, str]:
    """("developers/qa/index.md", "post-qa") for "developers/qa/index.md#post-qa"."""
    if not isinstance(value, str):
        fail(f"{where}: {value!r} is not the path of a Markdown file")
    src, _, anchor = value.partition("#")
    if anchor and not anchor_allowed:
        fail(f"{where}: {value}: name the page without #anchor (put old anchors under 'fragments')")
    if src not in PAGE_URLS:
        fail(f"{where} -> {src}: no such page (if it moved, point to its new file)")
    if anchor:
        ANCHORS.append((f"{where} -> {value}", src, anchor))
    return src, anchor


def parse_entry(old: str, value):
    """(page src_uri, {lower-case old id: (page src_uri, new id or "")})."""
    fragments = {}
    if isinstance(value, dict):
        unknown = sorted(set(value) - {"page", "fragments"})
        if unknown or "page" not in value:
            fail(f"{old}: write either a Markdown file, or 'page' (a Markdown file) and "
                 f"optionally 'fragments'{' (unknown: ' + ', '.join(map(str, unknown)) + ')' if unknown else ''}")
        fragments = value.get("fragments") or {}
        if not isinstance(fragments, dict):
            fail(f"{old}: 'fragments' maps old anchors to Markdown files, for example 'rest: developers/index.md'")
        value = value["page"]
    src, _ = page_target(old, value, anchor_allowed=False)
    mapped = {}
    for frag, target in fragments.items():
        if not isinstance(frag, str) or not frag or frag != frag.strip() or "#" in frag or " " in frag:
            fail(f"{old}: {frag!r}: write an old anchor without '#', for example 'fetch-api'")
        if frag.lower() in mapped:
            fail(f"{old}: the anchors {frag!r} and another one differ only by case (they are matched without case)")
        mapped[frag.lower()] = page_target(f"{old}#{frag}", target, anchor_allowed=True)
    return src, mapped


def on_files(files, config, **kwargs):
    PAGE_URLS.clear()
    PAGE_DEST.clear()
    REDIRECTS.clear()
    ANCHORS.clear()
    THEME_FILES.clear()
    for file in files.documentation_pages():
        url = "" if file.url in ("./", ".") else file.url
        PAGE_URLS[file.src_uri] = url
        PAGE_DEST[file.src_uri] = file.dest_uri
        if url.lower().startswith("api/"):
            fail(f"{file.src_uri} would be published under /api/, where sibils.org has no page; "
                 "put API guides under docs/developers/ (README.md, Addresses)")
    page_urls = {url.lower() for url in PAGE_URLS.values()}
    for old, value in ((config.get("extra") or {}).get("redirects") or {}).items():
        if not valid_key(old):
            fail(f"{old!r}: write the old address in lower case, without a leading slash, "
                 "with a trailing one (e.g. 'api/synvar/')")
        if old in page_urls:
            fail(f"{old} is the address of a page; remove this entry or move the page")
        src, fragments = parse_entry(old, value)
        REDIRECTS[old] = (PAGE_URLS[src], {frag: (PAGE_URLS[s], a) for frag, (s, a) in fragments.items()})
    check_published(files, config)
    return files


def read_published(path: Path) -> list[tuple[int, str]]:
    """(line number, URL) of each address of the list; # starts a comment."""
    if not path.is_file():
        fail(f"{PUBLISHED_FILE} not found: it lists the published addresses (README.md, Addresses)")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [(n, line.split("#", 1)[0].strip()) for n, line in enumerate(lines, 1)
            if line.split("#", 1)[0].strip()]


def check_published(files, config):
    """Every published address is still a page, a redirect page or a file;
    every page and every redirect is in the list."""
    pages = set(PAGE_URLS.values())
    other_files = {f.dest_uri for f in files if not f.is_documentation_page()}
    # The theme writes these after reading `files`, which does not have them.
    theme_files = set(getattr(config.get("theme"), "static_templates", None) or ())
    listed, missing = set(), []
    for n, url in read_published(Path(config["config_file_path"]).parent / PUBLISHED_FILE):
        where = f"{PUBLISHED_FILE}:{n}"
        if not url.startswith(PUBLISHED_ORIGIN) or "?" in url or " " in url:
            fail(f"{where}: {url!r}: write one address per line, starting with {PUBLISHED_ORIGIN}, without ?query")
        address = url[len(PUBLISHED_ORIGIN):]
        listed.add(address)
        if address in pages or address in REDIRECTS:
            continue
        if address and not address.endswith("/") and address in other_files:
            continue
        if address in theme_files:
            THEME_FILES.append((address, f"{url} ({where})"))
            continue
        missing.append(f"{url} ({where})")
    if missing:
        fail("published addresses with no page, no redirect page and no file: " + ", ".join(missing)
             + ". If a page moved, add its old address to extra.redirects in mkdocs.yml; "
             "never remove a line of the list (README.md, Addresses)")
    for src, url in sorted(PAGE_URLS.items()):
        if url not in listed:
            log.warning("redirects: %s is published at %s%s, which is not in %s: add it there",
                        src, PUBLISHED_ORIGIN, url, PUBLISHED_FILE)
    for old in sorted(set(REDIRECTS) - listed):
        log.warning("redirects: the old address %s%s (extra.redirects) is not in %s: add it there",
                    PUBLISHED_ORIGIN, old, PUBLISHED_FILE)


def on_page_markdown(markdown, page, config, files, **kwargs):
    """The buttons of the home page (front matter hero_actions) link pages that exist."""
    src = page.file.src_uri
    actions = (page.meta or {}).get("hero_actions") or []
    if not isinstance(actions, list):
        fail(f"{src}: hero_actions is a list of {{label, url}}")
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get("url"), str):
            fail(f"{src}: hero_actions: {action!r}: each button is {{label: ..., url: ...}}")
        url = action["url"]
        if url.startswith(("http://", "https://", "mailto:", "#", "/")):
            continue  # kept as written by resolve_url (theme/partials/macros.html)
        where = f"{src}: hero_actions {action.get('label')!r}"
        if not url.partition("#")[0].endswith(".md"):
            fail(f"{where}: {url!r}: write the path of the Markdown file of the page, "
                 "for example developers/index.md, so that the build can check it")
        page_target(where, url, anchor_allowed=True)
    return markdown


def relative(old: str, new_url: str) -> str:
    """Address of `new_url` (e.g. "developers/") from the page at `old` (e.g. "api/")."""
    target = posixpath.relpath(new_url or ".", old.rstrip("/") or ".")
    if target == ".":
        return "./"
    return target + ("/" if not new_url or new_url.endswith("/") else "")


def redirect_page(old: str, new_url: str, site_url: str | None, fragments: dict | None = None) -> str:
    """HTML of the page written at `old` (e.g. "api/") that sends to `new_url`
    (e.g. "developers/"), both relative to the site root. `fragments` maps an
    old anchor, in lower case, to (new url, new anchor or "")."""
    target = relative(old, new_url)
    canonical = (site_url or "/").rstrip("/") + "/" + new_url
    mapped = {frag: [relative(old, url), "#" + anchor if anchor else ""]
              for frag, (url, anchor) in sorted((fragments or {}).items())}
    return TEMPLATE.format(
        canonical=html.escape(canonical, quote=True),
        target=html.escape(target, quote=True),
        target_js=json.dumps(target).replace("<", "\\u003c"),
        map_js=json.dumps(mapped, separators=(",", ":")).replace("<", "\\u003c"),
    )


def has_id(text: str, anchor: str) -> bool:
    return re.search(r"""\sid=["']""" + re.escape(anchor) + """["']""", text) is not None


def on_post_build(config, **kwargs):
    site_dir = Path(config["site_dir"])
    for where, src, anchor in ANCHORS:
        built = site_dir / PAGE_DEST[src]
        if built.is_file() and not has_id(built.read_text(encoding="utf-8", errors="replace"), anchor):
            fail(f"{where}: {src} has no heading or element with id {anchor!r}")
    for address, where in THEME_FILES:
        if not (site_dir / address).is_file():
            fail(f"published address with no file: {where}: the theme did not write {address}; "
                 "never remove a line of the list (README.md, Addresses)")
    for old, (new_url, fragments) in sorted(REDIRECTS.items()):
        out = site_dir / old / "index.html"
        # A redirect page left by an earlier build ("mkdocs serve --dirty") is
        # rewritten; any other file there is a conflict.
        if out.exists() and MARKER not in out.read_text(encoding="utf-8", errors="replace"):
            fail(f"{old}: the build already wrote {out}; remove this entry or the file")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(redirect_page(old, new_url, config.get("site_url"), fragments), encoding="utf-8")
    if REDIRECTS:
        log.info("redirects: %d redirect pages written", len(REDIRECTS))


# --------------------------------------------------------------------------
# Command line


def load_site():
    """The settings and the files of the repository, as `mkdocs build` sees them."""
    from mkdocs.config import load_config
    from mkdocs.structure.files import get_files

    config = load_config(config_file=str(REPO_DIR / "mkdocs.yml"))
    files = get_files(config)
    files.add_files_from_theme(config.theme.get_env(), config)
    return config, files


def selftest() -> int:
    """Check the entries of mkdocs.yml, the published addresses, the home page
    buttons, the errors and the redirect pages."""
    import copy
    import tempfile
    from types import SimpleNamespace

    from mkdocs.structure.files import File, Files
    from mkdocs.utils.meta import get_data

    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    # Warnings are collected, not printed: some tests below expect them.
    warnings = []

    class Collect(logging.Handler):
        def emit(self, record):
            warnings.append(record.getMessage())

    log.addHandler(Collect(level=logging.WARNING))
    log.propagate = False

    config, files = load_site()
    redirects = config["extra"]["redirects"]
    config_file = config["config_file_path"]

    def with_redirects(changed, config_file_path=config_file):
        return {"extra": {"redirects": changed}, "site_url": config["site_url"],
                "config_file_path": config_file_path, "theme": config["theme"]}

    def expect_error(label, text, cfg=None, files_=None, post_build_site=None):
        try:
            on_files(files_ if files_ is not None else files, cfg if cfg is not None else config)
            if post_build_site is not None:
                on_post_build({"site_dir": post_build_site, "site_url": config["site_url"]})
            failures.append(f"{label}: no error")
        except PluginError as exc:
            check(text in str(exc), f"{label}: unexpected message {exc}")

    def without(src_uri):
        return Files([f for f in files if f.src_uri != src_uri])

    def plus_page(src_uri):
        return Files(list(files) + [File(src_uri, config["docs_dir"], config["site_dir"], True)])

    # 1. The entries of mkdocs.yml are valid; every old address gets a page;
    #    every published address is still served; every page is in the list.
    on_files(files, config)
    check(not warnings, "warnings: " + "; ".join(warnings))
    check(len(REDIRECTS) == len(redirects) and len(REDIRECTS) >= 20, f"{len(REDIRECTS)} redirects")
    check(REDIRECTS.get("api/biodiversitypmc/qa/", ("",))[0] == "developers/qa/", "api/biodiversitypmc/qa/ -> developers/qa/")
    api = REDIRECTS.get("api/", ("", {}))
    check(api[0] == "developers/", "api/ -> developers/")
    check(api[1].get("fetch-api") == ("developers/biodiversitypmc/fetch/", ""), "api/#Fetch-API -> fetch page")
    published = read_published(Path(config_file).parent / PUBLISHED_FILE)
    check(len(published) >= 64, f"{len(published)} published addresses")
    check(sorted(a for a, _ in THEME_FILES) == ["404.html", "sitemap.xml"], f"files of the theme: {THEME_FILES}")

    # "mkdocs serve" (./serve) sets site_url to its own address: the list,
    # which holds production addresses, is still valid.
    warnings.clear()
    try:
        on_files(files, dict(config, site_url="http://127.0.0.1:8000/"))
        check(not warnings, "mkdocs serve: warnings: " + "; ".join(warnings))
    except PluginError as exc:
        failures.append(f"mkdocs serve: {exc}")

    # 2. The redirect page.
    page = redirect_page("api/", api[0], config["site_url"], api[1])
    check('<link rel="canonical" href="https://sibils.org/developers/">' in page, "canonical of api/")
    check('content="0; url=../developers/"' in page, "meta refresh of api/")
    check('"fetch-api":["../developers/biodiversitypmc/fetch/",""]' in page, "fragment map of api/")
    check("matomo" not in page.lower(), "no tracker")
    check(relative("api/biodiversitypmc/qa/", "developers/qa/") == "../../../developers/qa/", "relative path")
    check(relative("api/", "") == "../", "relative path to the home page")
    check(redirect_page("a/", "b/", "https://x.org/", {"x": ("c/", "</script>")}).count("</script>") == 1,
          "a value cannot close the script")

    # 3. Broken entries stop the build.
    def changed(key, value=None, drop=None):
        out = copy.deepcopy(dict(redirects))
        if drop:
            out.pop(drop)
        if key is not None:
            out[key] = value
        return with_redirects(out)

    expect_error("target not a page", "no such page", changed("api/variomes/", "developers/variomes/gone.md"))
    expect_error("target with #anchor", "without #anchor", changed("api/variomes/", "developers/variomes/index.md#x"))
    expect_error("key of a page", "is the address of a page", changed("services/triage/", "services/triage/index.md"))
    expect_error("upper-case key", "lower case", changed("API/synvar/", "developers/synvar/index.md"))
    expect_error("leading slash", "lower case", changed("/api/synvar", "developers/synvar/index.md"))
    expect_error("no trailing slash", "lower case", changed("api/synvar", "developers/synvar/index.md"))
    expect_error("'..' in key", "lower case", changed("api/../x/", "developers/synvar/index.md"))
    expect_error("mapping without page", "write either", changed("api/", {"fragments": {"a": "index.md"}}))
    expect_error("unknown setting", "unknown: to", changed("api/", {"page": "developers/index.md", "to": "x"}))
    expect_error("fragment target not a page", "no such page",
                 changed("api/", {"page": "developers/index.md", "fragments": {"rest": "developers/gone.md"}}))
    expect_error("fragment with #", "without '#'",
                 changed("api/", {"page": "developers/index.md", "fragments": {"#rest": "developers/index.md"}}))
    expect_error("fragments differing by case", "differ only by case",
                 changed("api/", {"page": "developers/index.md",
                                  "fragments": {"Rest": "developers/index.md", "rest": "developers/index.md"}}))
    expect_error("page under /api/", "under /api/", files_=plus_page("api/foo/index.md"))

    # 4. A published address that disappears stops the build: an entry
    #    dropped, a page deleted or moved without an entry, a file deleted.
    expect_error("redirect entry dropped", "https://sibils.org/api/ (data/published-urls.txt:",
                 changed(None, drop="api/"))
    expect_error("legacy entry dropped", "https://sibils.org/biodiversitypmc/doc/sab/",
                 changed(None, drop="biodiversitypmc/doc/sab/"))
    expect_error("page deleted", "https://sibils.org/about/ (data/published-urls.txt:",
                 files_=without("about/index.md"))
    expect_error("page moved without an entry", "https://sibils.org/services/qa/",
                 files_=Files(list(without("services/qa/index.md"))
                              + [File("services/question-answering/index.md", config["docs_dir"],
                                      config["site_dir"], True)]))
    expect_error("file deleted", "https://sibils.org/api/sparql/sibils-ontology.ttl",
                 files_=without("api/sparql/sibils-ontology.ttl"))
    with tempfile.TemporaryDirectory() as tmp:
        fake_config = str(Path(tmp) / "mkdocs.yml")
        expect_error("no list", "not found", with_redirects(dict(redirects), fake_config))
        (Path(tmp) / "data").mkdir()
        lines = Path(config_file).parent.joinpath(PUBLISHED_FILE).read_text(encoding="utf-8")
        for label, bad in (("other host", "https://www.sibils.org/x/"), ("path only", "/about/sab/"),
                           ("query", "https://sibils.org/data/vocabularies/?type=drug")):
            (Path(tmp) / PUBLISHED_FILE).write_text(lines + bad + "\n", encoding="utf-8")
            expect_error(f"list line: {label}", "write one address per line",
                         with_redirects(dict(redirects), fake_config))

    # 5. A page, or a redirect, missing from the list is a warning.
    warnings.clear()
    on_files(plus_page("new-page.md"), config)
    check(any("new-page.md is published at https://sibils.org/new-page/" in w for w in warnings),
          "no warning for a page missing from the list")
    warnings.clear()
    on_files(files, changed("old/page/", "about/sab.md"))
    check(any("https://sibils.org/old/page/ (extra.redirects) is not in" in w for w in warnings),
          "no warning for a redirect missing from the list")

    # 6. The buttons of the home page.
    on_files(files, config)
    # docs/index.md may have no hero_actions (none at present): its buttons,
    # if any, are checked, then made-up ones.
    _, home_meta = get_data((Path(config["docs_dir"]) / "index.md").read_text(encoding="utf-8"))
    check(isinstance(home_meta.get("hero_actions") or [], list), "hero_actions of docs/index.md is a list")

    def home(actions):
        return SimpleNamespace(file=SimpleNamespace(src_uri="index.md"), meta={"hero_actions": actions})

    def expect_button_error(label, text, actions):
        try:
            on_page_markdown("", home(actions), config, files)
            failures.append(f"{label}: no error")
        except PluginError as exc:
            check(text in str(exc), f"{label}: unexpected message {exc}")

    try:
        on_page_markdown("", home(home_meta.get("hero_actions") or []), config, files)
        on_page_markdown("", home([{"label": "A", "url": "https://biodiversitypmc.sibils.org/"},
                                   {"label": "B", "url": "#how-to-cite"},
                                   {"label": "C", "url": "developers/index.md#responses"}]), config, files)
        check(bool(ANCHORS) and ANCHORS[-1][1:] == ("developers/index.md", "responses"),
              "anchor of a button checked after the build")
    except PluginError as exc:
        failures.append(f"valid buttons: {exc}")
    expect_button_error("button to a missing page", "no such page", [{"label": "APIs", "url": "developers/gone.md"}])
    expect_button_error("button to a page address", "path of the Markdown file", [{"label": "APIs", "url": "developers/"}])
    expect_button_error("button without url", "each button", [{"label": "APIs"}])
    expect_button_error("buttons not a list", "is a list", {"label": "APIs", "url": "developers/index.md"})

    # 7. After the build: a missing heading, and a file at an old address.
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "developers").mkdir()
        (site / "developers" / "index.html").write_text('<h2 id="responses">Responses</h2>', encoding="utf-8")
        (site / "sitemap.xml").write_text("<urlset/>", encoding="utf-8")
        (site / "404.html").write_text("<p>not found</p>", encoding="utf-8")
        expect_error("missing heading", "has no heading",
                     changed("api/", {"page": "developers/index.md",
                                      "fragments": {"rest": "developers/index.md#the-rest"}}),
                     post_build_site=site)
        on_files(files, changed("api/", {"page": "developers/index.md",
                                         "fragments": {"rest": "developers/index.md#responses"}}))
        on_post_build({"site_dir": site, "site_url": config["site_url"]})
        written = sorted(p.parent.relative_to(site).as_posix() + "/" for p in site.rglob("index.html")
                         if MARKER in p.read_text(encoding="utf-8"))
        check(written == sorted(REDIRECTS), "one redirect page per entry")
        on_post_build({"site_dir": site, "site_url": config["site_url"]})  # rewrites its own pages
        (site / "sitemap.xml").unlink()
        expect_error("sitemap.xml not written", "the theme did not write sitemap.xml", post_build_site=site)
        (site / "sitemap.xml").write_text("<urlset/>", encoding="utf-8")
        (site / "404.html").unlink()
        expect_error("404.html not written", "the theme did not write 404.html", post_build_site=site)
        (site / "404.html").write_text("<p>not found</p>", encoding="utf-8")
        (site / "api" / "variomes" / "index.html").write_text("<p>a page</p>", encoding="utf-8")
        expect_error("file at an old address", "already wrote", post_build_site=site)

    on_files(files, config)
    print(f"redirects:  {len(redirects)} entries in mkdocs.yml, "
          f"{sum(len(f) for _, f in REDIRECTS.values())} mapped anchors")
    print(f"published:  {len(published)} addresses in {PUBLISHED_FILE}, {len(PAGE_URLS)} pages")
    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print("  - " + failure)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] != ["--selftest"]:
        sys.exit("usage: python hooks/redirects.py --selftest")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    sys.exit(selftest())
