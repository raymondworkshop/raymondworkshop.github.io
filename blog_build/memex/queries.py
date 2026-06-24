import pathlib
from collections import defaultdict
from typing import Any

import frontmatter

from blog_build.memex import state
from blog_build.memex.links import iter_resolved_links
from blog_build.memex.resolve import normalize_memex_url
from blog_build.posts import (
    collect_memex_sources,
    get_excerpt,
    get_hub_url,
    get_post_url,
    get_topics,
    is_memex_hub_dir,
    is_memex_manifesto,
    memex_section_key,
)


def get_backlinks_for_post(
    post: frontmatter.Post, path: pathlib.Path | None = None
) -> list[dict[str, str]]:
    path = path or post.get("path") or pathlib.Path(".")
    if is_memex_manifesto(post, path):
        url = "/memex.html"
    elif is_memex_hub_dir(path):
        url = get_hub_url(post)
    else:
        url = get_post_url(post, path)
    return state.get_ctx().get("backlinks", {}).get(normalize_memex_url(url), [])


def get_unlinked_mentions_for_post(
    post: frontmatter.Post, path: pathlib.Path | None = None
) -> list[dict[str, str]]:
    path = path or post.get("path") or pathlib.Path(".")
    if is_memex_manifesto(post, path) or is_memex_hub_dir(path):
        return []
    url = normalize_memex_url(get_post_url(post, path))
    return state.get_ctx().get("unlinked_mentions", {}).get(url, [])


def get_outgoing_links(post: frontmatter.Post) -> list[dict[str, str]]:
    ctx = state.get_ctx()
    registry = ctx.get("registry", {})
    url_registry = ctx.get("url_registry", {})
    section_hubs = ctx.get("section_hubs", {})
    title_lookup = ctx.get("fuzzy_lookup") or ctx.get("title_lookup", [])
    path = post.get("path") or pathlib.Path(".")
    source_url = normalize_memex_url(
        get_hub_url(post)
        if is_memex_hub_dir(path)
        else get_post_url(post, path)
        if not is_memex_manifesto(post, path)
        else "/memex.html"
    )
    links = [
        {"title": entry["title"], "url": entry["url"]}
        for entry in iter_resolved_links(
            post.content or "",
            registry,
            url_registry,
            post=post,
            path=path,
            section_hubs=section_hubs,
            title_lookup=title_lookup,
        )
        if normalize_memex_url(entry["url"]) != source_url
    ]
    return sorted(links, key=lambda item: item["title"].lower())


def get_section_hub_for_path(
    path: pathlib.Path, post: frontmatter.Post
) -> dict[str, str] | None:
    if is_memex_hub_dir(path):
        return None
    if post.get("title") == "About":
        return None
    section = memex_section_key(path)
    return state.get_ctx().get("section_hubs", {}).get(section)


def get_page_lookup() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for pages in state.get_ctx().get("section_posts", {}).values():
        for page in pages:
            lookup[normalize_memex_url(page["url"])] = page
    return lookup


def get_related_pages(
    post: frontmatter.Post, path: pathlib.Path, limit: int = 8
) -> list[dict[str, str]]:
    if is_memex_hub_dir(path):
        return []
    my_url = normalize_memex_url(get_post_url(post, path))
    neighbor_urls: set[str] = set()
    for link in get_outgoing_links(post):
        neighbor_urls.add(normalize_memex_url(link["url"]))
    for link in get_backlinks_for_post(post, path):
        neighbor_urls.add(normalize_memex_url(link["url"]))
    neighbor_urls.discard(my_url)

    section = memex_section_key(path)
    section_pages = state.get_ctx().get("section_posts", {}).get(section, [])
    related = [
        page
        for page in section_pages
        if normalize_memex_url(page["url"]) in neighbor_urls
    ]
    if len(related) >= limit:
        return related[:limit]

    seen_urls = {normalize_memex_url(page["url"]) for page in related}
    seen_urls.add(my_url)
    my_topics = set(get_topics(post))
    page_lookup = get_page_lookup()
    if my_topics:
        topic_scores: dict[str, int] = defaultdict(int)
        topic_pages = state.get_ctx().get("topic_pages", {})
        for topic in my_topics:
            for page in topic_pages.get(topic, []):
                page_url = normalize_memex_url(page["url"])
                if page_url not in seen_urls:
                    topic_scores[page_url] += 1
        for page_url, _score in sorted(
            topic_scores.items(), key=lambda item: (-item[1], item[0])
        ):
            page = page_lookup.get(page_url)
            if page:
                related.append(page)
                seen_urls.add(page_url)
            if len(related) >= limit:
                break

    return related[:limit]


def get_see_also_pages(
    post: frontmatter.Post, path: pathlib.Path, limit: int = 6
) -> list[dict[str, str]]:
    if is_memex_hub_dir(path):
        return []
    my_url = normalize_memex_url(get_post_url(post, path))
    related_urls = {
        normalize_memex_url(page["url"]) for page in get_related_pages(post, path)
    }
    my_topics = set(get_topics(post))
    if not my_topics:
        return []

    topic_pages = state.get_ctx().get("topic_pages", {})
    topic_scores: dict[str, int] = defaultdict(int)
    page_lookup: dict[str, dict[str, str]] = {}
    for topic in my_topics:
        for page in topic_pages.get(topic, []):
            page_url = normalize_memex_url(page["url"])
            page_lookup[page_url] = page
            if page_url in related_urls or page_url == my_url:
                continue
            topic_scores[page_url] += 1

    see_also: list[dict[str, str]] = []
    for page_url, score in sorted(
        topic_scores.items(), key=lambda item: (-item[1], item[0])
    ):
        if score < 1:
            continue
        page = page_lookup.get(page_url)
        if page:
            see_also.append(page)
        if len(see_also) >= limit:
            break
    return see_also


def get_section_pages_for_post(post: frontmatter.Post) -> list[dict[str, str]]:
    section = post.get("section")
    if not section:
        return []
    return state.get_ctx().get("section_posts", {}).get(str(section), [])


def get_section_referenced_for_post(post: frontmatter.Post) -> list[dict[str, Any]]:
    section = post.get("section")
    if not section:
        return []
    return state.get_ctx().get("section_referenced", {}).get(str(section), [])


def get_sibling_hubs(post: frontmatter.Post) -> list[dict[str, str]]:
    current_url = get_hub_url(post)
    return [hub for hub in state.get_ctx().get("hubs", []) if hub["url"] != current_url]


def get_hub_summaries() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for post, subdir, _source in collect_memex_sources():
        if not is_memex_hub_dir(subdir):
            continue
        summaries.append(
            {
                "title": post["title"],
                "url": get_hub_url(post),
                "excerpt": get_excerpt(post),
                "section": str(post.get("section", "")),
            }
        )
    return sorted(summaries, key=lambda item: item["title"].lower())


def get_top_referenced_pages(limit: int = 12) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for section_pages in state.get_ctx().get("section_referenced", {}).values():
        pages.extend(section_pages)
    pages.sort(key=lambda item: (-item["backlink_count"], item["title"].lower()))
    return pages[:limit]
