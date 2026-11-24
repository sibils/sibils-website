#!/usr/bin/env python3
"""Unlisted pages: built and reachable at their address, but not advertised.

MkDocs hook, registered under ``hooks:`` in mkdocs.yml. A page matched by
``not_in_nav`` in mkdocs.yml is built like any other page, but:

- it is not in the nav, so no menu, tab, sidebar or pager lists it;
- no page of the nav may link to it: such a link is a warning, so the strict
  build stops (unlisted pages may link to each other and to any page);
- it is left out of the site search (search/search_index.json) and of
  sitemap.xml (theme/sitemap.xml), and has ``<meta name="robots"
  content="noindex">`` (theme/partials/head.html);
- while it is rendered, it is attached to the top-level nav section of the
  nearest listed page above its address (developers/otf/ goes under the
  "API" section of developers/), so the page has that section's tab,
  sidebar, breadcrumb and layout (the wide API column).

Used for the guides of the APIs the team keeps internal: the annotation and
vocabularies API (/developers/otf/) and the query parser (/developers/query/).
Their address is still in data/published-urls.txt: whoever has the address
keeps it (hooks/redirects.py).

    ./venv/bin/python hooks/unlisted.py --selftest
"""

from __future__ import annotations

import json
import logging
import posixpath
import re
import sys
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.unlisted")

# Unlisted documentation pages, by src_uri (set in on_files).
UNLISTED: set[str] = set()

# [text](target.md), [text](target.md#anchor), [text](target.md "title");
# also reference definitions "[id]: target.md".
MD_LINK_RE = re.compile(r"\]\(\s*<?([^)\s>#]+\.md)(?:#[^)\s>]*)?>?(?:\s+\"[^\"]*\")?\s*\)|^\s*\[[^\]]+\]:\s*<?([^\s>#]+\.md)",
                        re.M)
FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,}).*?^\1\2[ \t]*$", re.M | re.S)


def linked_pages(markdown: str, src_uri: str) -> list[str]:
    """src_uri of the Markdown files that a page links to, outside fenced code."""
    text = FENCE_RE.sub("", markdown)
    base = posixpath.dirname(src_uri)
    found = []
    for match in MD_LINK_RE.finditer(text):
        target = match.group(1) or match.group(2)
        if "://" in target or target.startswith("/"):
            continue
        found.append(posixpath.normpath(posixpath.join(base, target)))
    return found


def section_for(url: str, listed: list) -> object | None:
    """Top-level nav section of the listed page whose address is the longest
    prefix of ``url`` (the home page, address "", does not count)."""
    best = None
    for page in listed:
        if page.url and url.startswith(page.url) and (best is None or len(page.url) > len(best.url)):
            best = page
    if best is None:
        return None
    item = best
    while item.parent is not None:
        item = item.parent
    return item if item is not best else None


def on_files(files, config, **kwargs):
    UNLISTED.clear()
    UNLISTED.update(f.src_uri for f in files.documentation_pages() if f.inclusion.is_not_in_nav())
    return files


def on_page_markdown(markdown, page, config, files, **kwargs):
    if page.file.src_uri in UNLISTED:
        return markdown
    for target in linked_pages(markdown, page.file.src_uri):
        if target in UNLISTED:
            log.warning("unlisted: %s links to %s, which is unlisted (not_in_nav in mkdocs.yml): "
                        "remove the link, or put the page in the nav", page.file.src_uri, target)
    return markdown


def on_page_context(context, page, config, nav, **kwargs):
    if page.file.src_uri in UNLISTED and page.parent is None:
        section = section_for(page.url, nav.pages)
        if section is not None:
            # MkDocs sets page.active = False after rendering; with this
            # parent, that also clears the section.
            page.parent = section
            section.active = True
    return context


def on_post_build(config, **kwargs):
    if not UNLISTED:
        return
    path = Path(config["site_dir"]) / "search" / "search_index.json"
    if not path.exists():
        return
    urls = set()
    for src_uri in UNLISTED:
        stem = src_uri[:-len(".md")]
        if stem == "index" or stem.endswith("/index"):
            stem = stem[:-len("index")]
        else:
            stem += "/"
        urls.add(stem)
    index = json.loads(path.read_text(encoding="utf-8"))
    before = len(index["docs"])
    index["docs"] = [d for d in index["docs"] if d["location"].split("#", 1)[0] not in urls]
    path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    log.info("unlisted: %d pages built but not listed; %d search entries removed",
             len(UNLISTED), before - len(index["docs"]))


# --------------------------------------------------------------------------
# Selftest


def selftest() -> int:
    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    md = ("See [OTF](../otf/index.md#annotate), [ref](reference.md \"Ref\") and [web](https://x.org/a.md).\n"
          "```\n[code](../otf/index.md)\n```\n"
          "[id]: ../query/index.md\n")
    check(linked_pages(md, "developers/biodiversitypmc/search.md")
          == ["developers/otf/index.md", "developers/biodiversitypmc/reference.md", "developers/query/index.md"],
          f"linked_pages: {linked_pages(md, 'developers/biodiversitypmc/search.md')}")

    class Item:
        def __init__(self, url, parent=None):
            self.url, self.parent = url, parent

    api = Item(None)
    listed = [Item(""), Item("developers/", api), Item("developers/biodiversitypmc/", Item(None, api)),
              Item("about/")]
    check(section_for("developers/otf/", listed) is api, "section of developers/otf/")
    check(section_for("developers/biodiversitypmc/x/", listed) is api, "section through a subsection")
    check(section_for("other/", listed) is None, "no section: only the home page is a prefix")
    check(section_for("about/x/", listed) is None, "no section: the prefix page is top-level")

    for message in failures:
        print("FAIL:", message)
    print("OK" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
