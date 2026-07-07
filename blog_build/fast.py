import pathlib
from typing import Any

from blog_build.config import MEMEX_BUILD_STAMP, SRCS
from blog_build.memex import state
from blog_build.memex.graph import build_memex_context
from blog_build.posts import (
    collect_excluded_sources,
    collect_memex_sources,
    list_subdirs,
    page_url_for_entry,
    source_is_stale,
)
from blog_build.writer import (
    collect_search_posts,
    rewrite_memex_pages,
    rewrite_plain_posts,
    write_indexes_for_sections,
    write_memex_index,
    write_search_index,
    write_search_page,
)


def needs_full_memex_rebuild() -> bool:
    if not pathlib.Path("./docs/static/search-index.json").exists():
        return True
    return not MEMEX_BUILD_STAMP.exists()


def touch_memex_build_stamp() -> None:
    MEMEX_BUILD_STAMP.parent.mkdir(parents=True, exist_ok=True)
    MEMEX_BUILD_STAMP.write_text("memex\n")


def collect_affected_urls(
    ctx: dict[str, Any], changed_urls: set[str]
) -> set[str]:
    backlinks = ctx.get("backlinks", {})
    affected = set(changed_urls)
    for url in changed_urls:
        for target_url, items in backlinks.items():
            if any(item["url"] == url for item in items):
                affected.add(target_url)
        for item in backlinks.get(url, []):
            affected.add(item["url"])
    return affected


def collect_pages_to_rewrite(ctx: dict[str, Any]) -> set[pathlib.Path]:
    changed_urls: set[str] = set()
    for post, subdir, source in collect_memex_sources():
        if source_is_stale(source, post, subdir):
            changed_urls.add(page_url_for_entry(post, subdir))

    if not changed_urls:
        return set()

    affected_urls = collect_affected_urls(ctx, changed_urls)
    to_rewrite: set[pathlib.Path] = set()
    for post, subdir, source in collect_memex_sources():
        if page_url_for_entry(post, subdir) in affected_urls:
            to_rewrite.add(source.resolve())
    return to_rewrite


def collect_stale_excluded_sources() -> list[pathlib.Path]:
    return [
        source.resolve()
        for post, subdir, source in collect_excluded_sources()
        if source_is_stale(source, post, subdir)
    ]


def run_fast_build() -> None:
    if needs_full_memex_rebuild():
        print("memex: no search index yet, running full wiki build...")
        print("memex: building link graph...")
        state.set_ctx(build_memex_context())
        count = rewrite_memex_pages(SRCS)
        plain_count = rewrite_plain_posts(SRCS)
        write_memex_index()
        search_posts = collect_search_posts()
        write_search_index(search_posts)
        write_search_page()
        touch_memex_build_stamp()
        write_indexes_for_sections(set(list_subdirs(SRCS)))
        stats = state.get_ctx().get("stats", {})
        print(
            f"fast: initial build refreshed {count} memex pages, "
            f"{plain_count} plain pages, "
            f"{stats.get('pages', 0)} pages, {stats.get('hubs', 0)} hubs"
        )
        print(f"search: indexed {len(search_posts)} posts")
        return

    stale_sources = [
        source.resolve()
        for post, subdir, source in collect_memex_sources()
        if source_is_stale(source, post, subdir)
    ]
    stale_excluded = collect_stale_excluded_sources()
    if not stale_sources and not stale_excluded:
        print("fast: up to date (wiki, backlinks, search unchanged)")
        return

    print("memex: building link graph...")
    state.set_ctx(build_memex_context())
    pages_to_rewrite = collect_pages_to_rewrite(state.get_ctx())
    count = rewrite_memex_pages(SRCS, only=pages_to_rewrite)
    plain_to_rewrite = set(stale_excluded)
    plain_count = (
        rewrite_plain_posts(SRCS, only=plain_to_rewrite)
        if plain_to_rewrite
        else 0
    )
    write_memex_index()
    search_posts = collect_search_posts()
    write_search_index(search_posts)
    write_search_page()
    touch_memex_build_stamp()

    affected_sections: set[pathlib.Path] = set()
    for post, subdir, source in collect_memex_sources():
        if source.resolve() in pages_to_rewrite:
            affected_sections.add(subdir)
    for post, subdir, source in collect_excluded_sources():
        if source.resolve() in plain_to_rewrite:
            affected_sections.add(subdir)
    if affected_sections:
        write_indexes_for_sections(affected_sections)

    stats = state.get_ctx().get("stats", {})
    print(
        f"fast: refreshed {count} memex pages, {plain_count} plain pages "
        f"({len(stale_sources)} memex edited, {len(stale_excluded)} plain edited, "
        f"{stats.get('pages', 0)} total pages)"
    )
    print(f"search: indexed {len(search_posts)} posts")
