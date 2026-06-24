"""Backward-compatible facade for blog_build."""

from __future__ import annotations

import frontmatter

from blog_build import cli
from blog_build.config import (
    EXCLUDED_INDEX_TITLES,
    FUZZY_MIN_SCORE,
    FUZZY_SCORE_GAP,
    HASHTAG_TAG_LINE,
    HASHTAG_TOKEN,
    MARKDOWN_LINK_PATTERN,
    MEMEX_EXCLUDED_SECTIONS,
    MEMEX_HUB_DIR,
    POSTS_PER_PAGE,
    SRCS,
    WIKILINK_PATTERN,
)
from blog_build.fast import (
    collect_affected_urls,
    collect_pages_to_rewrite,
    needs_full_memex_rebuild,
    run_fast_build,
    touch_memex_build_stamp,
)
from blog_build.memex import state
from blog_build.memex.graph import build_memex_context as _build_memex_context
from blog_build.memex.links import (
    iter_hashtag_links,
    iter_related_frontmatter,
    iter_resolved_links,
    iter_section_hub_link,
    iter_topic_links,
    preprocess_hashtag_tags,
    preprocess_internal_markdown_links,
    preprocess_memex_links,
    preprocess_wikilinks,
)
from blog_build.memex.queries import (
    get_backlinks_for_post,
    get_hub_summaries,
    get_outgoing_links,
    get_page_lookup,
    get_related_pages,
    get_section_hub_for_path,
    get_section_pages_for_post,
    get_section_referenced_for_post,
    get_see_also_pages,
    get_sibling_hubs,
    get_top_referenced_pages,
    get_unlinked_mentions_for_post,
)
from blog_build.memex.resolve import (
    build_fuzzy_lookup,
    build_title_lookup,
    build_url_registry,
    normalize_memex_url,
    normalize_wikilink_key,
    register_wikilink_target,
    resolve_wikilink,
    resolve_wikilink_candidates,
    score_fuzzy_match,
    wikilink_key_variants,
)
from blog_build.posts import (
    collect_memex_sources,
    collect_post_aliases,
    derive_post_title,
    get_excerpt,
    get_file_stem,
    get_hub_url,
    get_post_output_path,
    get_post_stem,
    get_post_url,
    get_sources,
    get_static_link,
    get_topics,
    is_memex_excluded_path,
    is_memex_hub_dir,
    is_memex_manifesto,
    is_memex_post_path,
    is_section_dir,
    list_subdirs,
    memex_section_key,
    normalize_post,
    page_url_for_entry,
    parse_source,
    render_markdown,
    section_label,
    should_preprocess_wikilinks,
    source_is_stale,
    strip_markdown,
)
from blog_build.search import expand_for_search
from blog_build.writer import (
    jinja_env,
    render_memex_page,
    rewrite_memex_pages,
    write_docs,
    write_index,
    write_indexes_for_sections,
    write_memex_index,
    write_paginated_home,
    write_post,
    write_posts,
    write_pygments_style_sheet,
    write_search_index,
    write_search_page,
    collect_search_posts,
    should_show_on_home,
)

# memex.py assigns blog._memex_ctx; keep in sync with state module
_memex_ctx = state._memex_ctx


def build_memex_context():
    ctx = _build_memex_context()
    state.set_ctx(ctx)
    global _memex_ctx
    _memex_ctx = ctx
    state._memex_ctx = ctx
    return ctx


main = cli.main

__all__ = [
    "SRCS",
    "POSTS_PER_PAGE",
    "MEMEX_EXCLUDED_SECTIONS",
    "MEMEX_HUB_DIR",
    "WIKILINK_PATTERN",
    "MARKDOWN_LINK_PATTERN",
    "HASHTAG_TAG_LINE",
    "HASHTAG_TOKEN",
    "EXCLUDED_INDEX_TITLES",
    "FUZZY_MIN_SCORE",
    "FUZZY_SCORE_GAP",
    "_memex_ctx",
    "frontmatter",
    "jinja_env",
    "main",
    "expand_for_search",
    "build_memex_context",
    "resolve_wikilink",
    "resolve_wikilink_candidates",
    "register_wikilink_target",
    "normalize_memex_url",
    "normalize_wikilink_key",
    "collect_memex_sources",
    "collect_post_aliases",
    "collect_search_posts",
    "run_fast_build",
]

if __name__ == "__main__":
    main()
