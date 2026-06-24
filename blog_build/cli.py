from typing import Sequence

from blog_build.config import SRCS
from blog_build.fast import run_fast_build, touch_memex_build_stamp
from blog_build.memex import state
from blog_build.memex.graph import build_memex_context
from blog_build.writer import (
    collect_search_posts,
    rewrite_memex_pages,
    write_docs,
    write_memex_index,
    write_search_index,
    write_search_page,
)


def main(argv: Sequence[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build myblog static site.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Incremental build with wiki links, backlinks, and search (default).",
    )
    parser.add_argument(
        "--memex",
        action="store_true",
        help="Full rebuild: all HTML + wiki links + backlinks + search.",
    )
    parser.add_argument(
        "--memex-only",
        action="store_true",
        help="Rebuild memex/wiki pages and indexes only; skip other HTML.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.fast or (not args.memex and not args.memex_only):
            run_fast_build()
            return

        if args.memex or args.memex_only:
            print("memex: building link graph...")
            state.set_ctx(build_memex_context())

        if args.memex_only:
            count = rewrite_memex_pages(SRCS)
            write_memex_index()
            search_posts = collect_search_posts()
            write_search_index(search_posts)
            write_search_page()
            touch_memex_build_stamp()
            stats = state.get_ctx().get("stats", {})
            print(
                f"memex-only: refreshed {count} pages, "
                f"{stats.get('pages', 0)} pages, {stats.get('hubs', 0)} hubs"
            )
            print(f"search: indexed {len(search_posts)} posts")
            return

        write_docs(SRCS, memex_enabled=True)
        write_memex_index()
        search_posts = collect_search_posts()
        write_search_index(search_posts)
        write_search_page()
        touch_memex_build_stamp()
        stats = state.get_ctx().get("stats", {})
        print(f"memex: {stats.get('pages', 0)} pages, {stats.get('hubs', 0)} hubs")
        print(f"search: indexed {len(search_posts)} posts")
    except OSError as e:
        print("Erros: %s - %s." % (e.filename, e.strerror))
