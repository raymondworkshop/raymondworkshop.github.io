import html
import pathlib
import re
from collections import defaultdict
from typing import Any, Iterator, Sequence

import frontmatter

from blog_build.config import (
    HASHTAG_TAG_LINE,
    HASHTAG_TOKEN,
    MARKDOWN_LINK_PATTERN,
    WIKILINK_PATTERN,
)
from blog_build.memex import state
from blog_build.memex.resolve import normalize_memex_url, resolve_wikilink
from blog_build.posts import (
    collect_memex_sources,
    get_excerpt,
    get_hub_url,
    get_post_url,
    get_topics,
    is_memex_hub_dir,
    is_memex_manifesto,
    memex_section_key,
    strip_markdown,
)
from blog_build.memex.resolve import (
    build_fuzzy_lookup,
    build_url_registry,
    normalize_wikilink_key,
    register_wikilink_target,
    wikilink_key_variants,
)
from blog_build.posts import collect_post_aliases, get_post_stem


def iter_hashtag_links(
    body: str,
    registry: dict[str, dict[str, str]],
    *,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or not HASHTAG_TAG_LINE.match(stripped):
            continue
        for match in HASHTAG_TOKEN.finditer(stripped):
            tag = match.group(0)[1:]
            entry = resolve_wikilink(tag, registry, title_lookup=title_lookup)
            if entry and entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry


def iter_topic_links(
    post: frontmatter.Post,
    registry: dict[str, dict[str, str]],
    section_hubs: dict[str, dict[str, str]],
    *,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for topic in get_topics(post):
        hub = section_hubs.get(topic)
        if hub and hub["url"] not in seen:
            seen.add(hub["url"])
            yield {"title": hub["title"], "url": hub["url"]}
        entry = resolve_wikilink(topic, registry, title_lookup=title_lookup)
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry


def iter_section_hub_link(
    path: pathlib.Path,
    section_hubs: dict[str, dict[str, str]],
) -> Iterator[dict[str, str]]:
    section = memex_section_key(path)
    if not section or section == "blog":
        return
    hub = section_hubs.get(section)
    if hub:
        yield {"title": hub["title"], "url": hub["url"]}


def iter_related_frontmatter(
    post: frontmatter.Post,
    registry: dict[str, dict[str, str]],
    *,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
) -> Iterator[dict[str, str]]:
    for field in ("related", "seealso"):
        if not post.get(field):
            continue
        values = post[field]
        if isinstance(values, str):
            values = [values]
        for value in values:
            entry = resolve_wikilink(
                str(value).strip(), registry, title_lookup=title_lookup
            )
            if entry:
                yield entry


def iter_resolved_links(
    body: str,
    registry: dict[str, dict[str, str]],
    url_registry: dict[str, dict[str, str]],
    *,
    post: frontmatter.Post | None = None,
    path: pathlib.Path | None = None,
    section_hubs: dict[str, dict[str, str]] | None = None,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for match in WIKILINK_PATTERN.finditer(body):
        entry = resolve_wikilink(
            match.group(1).strip(), registry, title_lookup=title_lookup
        )
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        url = normalize_memex_url(match.group(2))
        entry = url_registry.get(url) or resolve_wikilink(
            match.group(1).strip(), registry, title_lookup=title_lookup
        )
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    for entry in iter_hashtag_links(body, registry, title_lookup=title_lookup):
        if entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    if post and section_hubs is not None:
        for entry in iter_topic_links(
            post, registry, section_hubs, title_lookup=title_lookup
        ):
            if entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry
        for entry in iter_related_frontmatter(
            post, registry, title_lookup=title_lookup
        ):
            if entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry
    if path and section_hubs is not None:
        for entry in iter_section_hub_link(path, section_hubs):
            if entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry


def preprocess_hashtag_tags(text: str) -> str:
    ctx = state.get_ctx()
    registry = ctx.get("registry", {})
    title_lookup = ctx.get("fuzzy_lookup") or ctx.get("title_lookup", [])

    def repl_line(match: re.Match[str]) -> str:
        line = match.group(0)

        def repl_tag(tag_match: re.Match[str]) -> str:
            tag = tag_match.group(0)[1:]
            entry = resolve_wikilink(tag, registry, title_lookup=title_lookup)
            if entry:
                return f"[[{tag}|#{tag}]]"
            return tag_match.group(0)

        return HASHTAG_TOKEN.sub(repl_tag, line)

    return HASHTAG_TAG_LINE.sub(repl_line, text)


def preprocess_wikilinks(text: str) -> str:
    ctx = state.get_ctx()
    registry = ctx.get("registry", {})
    title_lookup = ctx.get("fuzzy_lookup") or ctx.get("title_lookup", [])

    def repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        display = match.group(2).strip() if match.group(2) else target
        entry = resolve_wikilink(target, registry, title_lookup=title_lookup)
        if entry:
            return (
                f'<a href="{html.escape(entry["url"])}" class="wikilink">'
                f"{html.escape(display)}</a>"
            )
        return f'<span class="wikilink-missing">{html.escape(display)}</span>'

    return WIKILINK_PATTERN.sub(repl, text)


def preprocess_internal_markdown_links(text: str) -> str:
    ctx = state.get_ctx()
    registry = ctx.get("registry", {})
    url_registry = ctx.get("url_registry", {})
    title_lookup = ctx.get("fuzzy_lookup") or ctx.get("title_lookup", [])

    def repl(match: re.Match[str]) -> str:
        display = match.group(1).strip()
        url = normalize_memex_url(match.group(2))
        entry = url_registry.get(url) or resolve_wikilink(
            display, registry, title_lookup=title_lookup
        )
        if entry:
            return (
                f'<a href="{html.escape(entry["url"])}" class="wikilink">'
                f"{html.escape(display)}</a>"
            )
        return match.group(0)

    return MARKDOWN_LINK_PATTERN.sub(repl, text)


def preprocess_memex_links(text: str) -> str:
    return preprocess_internal_markdown_links(
        preprocess_wikilinks(preprocess_hashtag_tags(text))
    )


def label_mentioned_in_body(label: str, body: str) -> bool:
    from blog_build.config import CJK_RE

    if len(normalize_wikilink_key(label)) < 4:
        return False
    body_lower = body.lower()
    body_compact = re.sub(r"\s+", "", body_lower)
    for variant in wikilink_key_variants(label):
        if CJK_RE.search(variant):
            if variant in body_compact or variant in normalize_wikilink_key(body):
                return True
            continue
        pattern = r"(?<!\w)" + re.escape(variant) + r"(?!\w)"
        if re.search(pattern, body_lower):
            return True
    return False


def build_unlinked_mentions(
    sources: Sequence[tuple[frontmatter.Post, pathlib.Path, pathlib.Path]],
    fuzzy_lookup: list[tuple[str, dict[str, str]]],
    outgoing_urls: dict[str, set[str]],
    plain_bodies: dict[str, str],
) -> dict[str, list[dict[str, str]]]:
    labels_by_url: dict[str, tuple[str, dict[str, str]]] = {}
    for label, entry in fuzzy_lookup:
        if len(normalize_wikilink_key(label)) < 4:
            continue
        target_url = normalize_memex_url(entry["url"])
        current = labels_by_url.get(target_url)
        if current is None or len(label) < len(current[0]):
            labels_by_url[target_url] = (label, entry)

    mention_index: list[tuple[str, dict[str, str], str, list[str]]] = []
    for target_url, (label, entry) in labels_by_url.items():
        variants = wikilink_key_variants(label)
        mention_index.append((target_url, entry, label, variants))
    mention_index.sort(key=lambda item: -len(item[2]))

    unlinked: dict[str, list[dict[str, str]]] = defaultdict(list)

    for post, subdir, _source in sources:
        if is_memex_manifesto(post, subdir) or is_memex_hub_dir(subdir):
            continue
        source_url = normalize_memex_url(get_post_url(post, subdir))
        body = plain_bodies.get(source_url, "")
        if not body:
            continue
        body_lower = body.lower()
        body_compact = re.sub(r"\s+", "", body_lower)
        body_norm = normalize_wikilink_key(body)
        linked_urls = outgoing_urls.get(source_url, set())
        seen_targets: set[str] = set()

        for target_url, entry, label, variants in mention_index:
            if target_url == source_url or target_url in linked_urls:
                continue
            if target_url in seen_targets:
                continue
            if not any(
                variant in body_compact or variant in body_norm or variant in body_lower
                for variant in variants
            ):
                continue
            if not label_mentioned_in_body(label, body):
                continue
            seen_targets.add(target_url)
            unlinked[source_url].append(
                {
                    "title": entry["title"],
                    "url": entry["url"],
                    "label": label,
                }
            )

    for url in unlinked:
        unlinked[url] = sorted(unlinked[url], key=lambda item: item["title"].lower())
    return dict(unlinked)


