import re
from collections import defaultdict
from typing import Any

import frontmatter

from blog_build.config import (
    HASHTAG_TAG_LINE,
    HASHTAG_TOKEN,
    MARKDOWN_LINK_PATTERN,
    WIKILINK_PATTERN,
)
from blog_build.memex.links import build_unlinked_mentions, iter_resolved_links
from blog_build.memex.resolve import (
    build_fuzzy_lookup,
    build_url_registry,
    normalize_memex_url,
    register_wikilink_target,
    resolve_wikilink,
)
from blog_build.posts import (
    collect_memex_sources,
    collect_post_aliases,
    get_excerpt,
    get_hub_url,
    get_post_stem,
    get_post_url,
    get_topics,
    is_memex_hub_dir,
    is_memex_manifesto,
    memex_section_key,
    strip_markdown,
)

def build_memex_context() -> dict[str, Any]:
    registry: dict[str, dict[str, str]] = {}
    backlinks: dict[str, list[dict[str, str]]] = defaultdict(list)
    section_posts: dict[str, list[dict[str, str]]] = defaultdict(list)
    section_hubs: dict[str, dict[str, str]] = {}
    wikilink_count = 0
    internal_link_count = 0
    hashtag_link_count = 0
    external_link_count = 0
    line_count = 0
    page_count = 0
    hub_count = 0
    file_count = 0

    sources = collect_memex_sources()
    file_count = len(sources)

    for post, subdir, _source in sources:
        if is_memex_manifesto(post, subdir):
            register_wikilink_target(registry, post["title"], "/memex.html")
            continue
        if is_memex_hub_dir(subdir):
            hub_count += 1
            register_wikilink_target(registry, post["title"], get_hub_url(post))
            if post.get("section"):
                section_hubs[str(post["section"])] = {
                    "title": post["title"],
                    "url": get_hub_url(post),
                }
            continue

        page_count += 1
        url = get_post_url(post, subdir)
        stem = get_post_stem(post, subdir)
        aliases = collect_post_aliases(post)
        register_wikilink_target(
            registry, post["title"], url, stem=stem, aliases=aliases
        )
        if post.get("_source_stem"):
            register_wikilink_target(
                registry,
                str(post["_source_stem"]),
                url,
                stem=stem,
                aliases=aliases,
            )
        section_name = memex_section_key(subdir)
        section_posts[section_name].append(
            {
                "title": post["title"],
                "url": url,
                "excerpt": get_excerpt(post),
            }
        )

    url_registry = build_url_registry(registry)
    fuzzy_lookup = build_fuzzy_lookup(sources)
    topic_pages: dict[str, list[dict[str, str]]] = defaultdict(list)
    page_topics: dict[str, list[str]] = {}

    for post, subdir, _source in sources:
        if is_memex_manifesto(post, subdir) or is_memex_hub_dir(subdir):
            continue
        page_url = normalize_memex_url(get_post_url(post, subdir))
        topics = get_topics(post)
        page_topics[page_url] = topics
        page_entry = {
            "title": post["title"],
            "url": get_post_url(post, subdir),
            "section": memex_section_key(subdir),
        }
        for topic in topics:
            topic_pages[topic].append(page_entry)

    for topic in topic_pages:
        topic_pages[topic] = sorted(
            topic_pages[topic], key=lambda item: item["title"].lower()
        )

    for section_name in section_posts:
        section_posts[section_name] = sorted(
            section_posts[section_name], key=lambda item: item["title"].lower()
        )

    hubs: list[dict[str, str]] = []
    for post, subdir, _source in sources:
        if is_memex_hub_dir(subdir):
            hubs.append({"title": post["title"], "url": get_hub_url(post)})
    hubs.sort(key=lambda item: item["title"].lower())

    seen_backlinks: set[tuple[str, str]] = set()
    outgoing_urls: dict[str, set[str]] = defaultdict(set)
    plain_bodies: dict[str, str] = {}
    for post, subdir, _source in sources:
        body = post.content or ""
        line_count += body.count("\n") + (1 if body else 0)
        wikilink_count += len(WIKILINK_PATTERN.findall(body))
        file_hashtag_links = sum(
            1
            for line in body.splitlines()
            if HASHTAG_TAG_LINE.match(line.strip())
            for match in HASHTAG_TOKEN.finditer(line.strip())
            if resolve_wikilink(
                match.group(0)[1:], registry, fuzzy_lookup=fuzzy_lookup
            )
        )
        hashtag_link_count += file_hashtag_links
        internal_link_count += len(
            [
                match
                for match in MARKDOWN_LINK_PATTERN.finditer(body)
                if url_registry.get(normalize_memex_url(match.group(2)))
                or resolve_wikilink(
                    match.group(1).strip(), registry, fuzzy_lookup=fuzzy_lookup
                )
            ]
        ) + file_hashtag_links

        source_url = (
            "/memex.html"
            if is_memex_manifesto(post, subdir)
            else get_hub_url(post)
            if is_memex_hub_dir(subdir)
            else get_post_url(post, subdir)
        )
        source_url_norm = normalize_memex_url(source_url)
        if not is_memex_manifesto(post, subdir) and not is_memex_hub_dir(subdir):
            plain_bodies[source_url_norm] = strip_markdown(body)
        for entry in iter_resolved_links(
            body,
            registry,
            url_registry,
            post=post,
            path=subdir,
            section_hubs=section_hubs,
            title_lookup=fuzzy_lookup,
        ):
            target_url = normalize_memex_url(entry["url"])
            if target_url == source_url_norm:
                continue
            outgoing_urls[source_url_norm].add(target_url)
            key = (target_url, source_url_norm)
            if key in seen_backlinks:
                continue
            seen_backlinks.add(key)
            backlinks[target_url].append(
                {"title": post["title"], "url": source_url_norm}
            )

        external_link_count += len(re.findall(r"(?<!!)\[[^\]]+\]\([^)]+\)", body))

    for slug in backlinks:
        backlinks[slug] = sorted(
            backlinks[slug], key=lambda item: item["title"].lower()
        )

    section_referenced: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post, subdir, _source in sources:
        if is_memex_manifesto(post, subdir) or is_memex_hub_dir(subdir):
            continue
        section_name = memex_section_key(subdir)
        page_url = normalize_memex_url(get_post_url(post, subdir))
        page_backlinks = backlinks.get(page_url, [])
        if not page_backlinks:
            continue
        section_referenced[section_name].append(
            {
                "title": post["title"],
                "url": get_post_url(post, subdir),
                "excerpt": get_excerpt(post),
                "backlinks": page_backlinks,
                "backlink_count": len(page_backlinks),
            }
        )

    for section_name in section_referenced:
        section_referenced[section_name] = sorted(
            section_referenced[section_name],
            key=lambda item: (-item["backlink_count"], item["title"].lower()),
        )

    backlink_counts = {
        normalize_memex_url(url): len(items) for url, items in backlinks.items()
    }
    unlinked_mentions = build_unlinked_mentions(
        sources,
        fuzzy_lookup,
        outgoing_urls,
        plain_bodies,
    )

    stats = {
        "date": "2026-06-14",
        "files": file_count,
        "pages": page_count,
        "hubs": hub_count,
        "wikilinks": wikilink_count,
        "hashtag_links": hashtag_link_count,
        "internal_links": internal_link_count,
        "external_links": external_link_count,
        "lines": line_count,
    }

    return {
        "registry": registry,
        "url_registry": url_registry,
        "fuzzy_lookup": fuzzy_lookup,
        "title_lookup": fuzzy_lookup,
        "backlink_counts": backlink_counts,
        "unlinked_mentions": unlinked_mentions,
        "topic_pages": dict(topic_pages),
        "page_topics": page_topics,
        "backlinks": dict(backlinks),
        "section_posts": dict(section_posts),
        "section_referenced": dict(section_referenced),
        "section_hubs": section_hubs,
        "hubs": hubs,
        "stats": stats,
    }
