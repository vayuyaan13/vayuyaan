#!/usr/bin/env python3
"""Dependency-free checks for the Vayuyaan GitHub Pages site.

Validates sitemap coverage, canonical metadata, basic document structure,
JSON-LD syntax, and local links/assets before a change is merged.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
import sys
import xml.etree.ElementTree as ET

SITE = "https://vayuyaan13.github.io/vayuyaan/"
ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.description: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.h1_count = 0
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images_missing_alt = 0
        self.jsonld_parts: list[str] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_current: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in a:
            self.images_missing_alt += 1
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "meta":
            if a.get("name", "").lower() == "description" and a.get("content"):
                self.description.append(a["content"].strip())
            if a.get("name", "").lower() == "robots" and a.get("content"):
                self.robots.append(a["content"].lower())
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            if a.get("href"):
                self.canonicals.append(a["href"].strip())
        for key in ("href", "src", "poster"):
            value = a.get(key)
            if value:
                self.links.append(value.strip())
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_current = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld_parts.append("".join(self._jsonld_current).strip())
            self._in_jsonld = False
            self._jsonld_current = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_current.append(data)


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE
    if rel.endswith("/index.html"):
        return SITE + rel[:-len("index.html")]
    return SITE + rel


def local_target(page: Path, raw_url: str) -> tuple[Path | None, str]:
    absolute = urljoin(page_url(page), raw_url)
    parts = urlsplit(absolute)
    if parts.scheme not in ("http", "https") or parts.netloc != "vayuyaan13.github.io":
        return None, parts.fragment
    prefix = "/vayuyaan/"
    if not parts.path.startswith(prefix):
        return None, parts.fragment
    relative = unquote(parts.path[len(prefix):])
    target = (ROOT / relative) if relative else (ROOT / "index.html")
    if target.is_dir():
        target = target / "index.html"
    elif not target.exists() and not target.suffix:
        target = target / "index.html"
    return target, parts.fragment


def main() -> int:
    errors: list[str] = []
    html_files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    sitemap_path = ROOT / "sitemap.xml"

    if not sitemap_path.is_file():
        print("ERROR: sitemap.xml is missing")
        return 1

    try:
        sitemap = ET.parse(sitemap_path).getroot()
    except ET.ParseError as exc:
        print(f"ERROR: sitemap.xml is invalid: {exc}")
        return 1

    locs = [
        (node.text or "").strip()
        for node in sitemap.iter()
        if node.tag.endswith("loc")
    ]
    if len(locs) != len(set(locs)):
        errors.append("sitemap.xml contains duplicate URL entries")

    sitemap_paths: set[Path] = set()
    for loc in locs:
        parts = urlsplit(loc)
        if loc.startswith(SITE):
            rel = unquote(parts.path[len(urlsplit(SITE).path):])
            target = ROOT / rel / "index.html" if rel and not rel.endswith(".html") else ROOT / (rel or "index.html")
            if not target.is_file():
                errors.append(f"sitemap URL has no matching file: {loc}")
            else:
                sitemap_paths.add(target)
        else:
            errors.append(f"sitemap URL is outside the GitHub Pages property: {loc}")

    parsed_pages: dict[Path, PageParser] = {}
    for path in html_files:
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: HTML could not be read: {exc}")
            continue
        parsed_pages[path] = parser

        robots = " ".join(parser.robots)
        indexable = "noindex" not in robots
        rel = path.relative_to(ROOT).as_posix()
        if indexable:
            if len(parser.title_parts) == 0 or not "".join(parser.title_parts).strip():
                errors.append(f"{rel}: missing page title")
            if len(parser.description) != 1:
                errors.append(f"{rel}: expected exactly one meta description, found {len(parser.description)}")
            if len(parser.canonicals) != 1:
                errors.append(f"{rel}: expected exactly one canonical, found {len(parser.canonicals)}")
            elif parser.canonicals[0] != page_url(path):
                errors.append(f"{rel}: canonical is not self-referencing ({parser.canonicals[0]})")
            if parser.h1_count != 1:
                errors.append(f"{rel}: expected exactly one H1, found {parser.h1_count}")
            if parser.images_missing_alt:
                errors.append(f"{rel}: {parser.images_missing_alt} image(s) are missing an alt attribute")
            if path not in sitemap_paths:
                errors.append(f"{rel}: indexable page is missing from sitemap")

        if indexable:
            for block in parser.jsonld_parts:
                if not block:
                    errors.append(f"{rel}: empty JSON-LD script block")
                    continue
                try:
                    json.loads(block)
                except json.JSONDecodeError as exc:
                    errors.append(f"{rel}: invalid JSON-LD ({exc})")

    for path in sitemap_paths:
        parser = parsed_pages.get(path)
        if parser and "noindex" in " ".join(parser.robots):
            errors.append(f"{path.relative_to(ROOT)}: noindex page must not be in sitemap")

    seen_titles: dict[str, str] = {}
    seen_descriptions: dict[str, str] = {}
    for path, parser in parsed_pages.items():
        if "noindex" in " ".join(parser.robots):
            continue
        rel = path.relative_to(ROOT).as_posix()
        title = "".join(parser.title_parts).strip()
        description = parser.description[0].strip() if parser.description else ""
        if title in seen_titles:
            errors.append(f"{rel}: duplicate title also used by {seen_titles[title]}")
        else:
            seen_titles[title] = rel
        if description and description in seen_descriptions:
            errors.append(f"{rel}: duplicate meta description also used by {seen_descriptions[description]}")
        elif description:
            seen_descriptions[description] = rel

    for page, parser in parsed_pages.items():
        rel = page.relative_to(ROOT).as_posix()
        for raw in parser.links:
            if raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            target, fragment = local_target(page, raw)
            if target is None:
                continue
            try:
                target.resolve().relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: local URL escapes repository: {raw}")
                continue
            if not target.is_file():
                errors.append(f"{rel}: broken local link or asset: {raw}")
                continue
            if fragment and target.suffix.lower() in (".html", ".htm"):
                target_parser = parsed_pages.get(target)
                if target_parser and fragment not in target_parser.ids:
                    errors.append(f"{rel}: missing anchor #{fragment} in {target.relative_to(ROOT)}")

    if errors:
        print(f"Site checks failed with {len(errors)} issue(s):")
        for error in errors:
            print(f" - {error}")
        return 1

    indexable_count = sum(
        "noindex" not in " ".join(parser.robots)
        for parser in parsed_pages.values()
    )
    print(
        f"Site checks passed: {len(parsed_pages)} HTML files, "
        f"{indexable_count} indexable pages, {len(sitemap_paths)} sitemap URLs. "
        "Metadata, canonicals, JSON-LD and local links are consistent."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
