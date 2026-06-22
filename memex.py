#!/usr/bin/env python3
"""CLI for myblog memex wiki: inspect links, find gaps, run checks."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import blog


def load_context() -> dict[str, Any]:
    blog._memex_ctx = blog.build_memex_context()
    return blog._memex_ctx


def find_pages(query: str) -> list[tuple[Any, Any, Any]]:
    query_lower = query.strip().lower()
    query_slug = blog.get_static_link(query)
    matches: list[tuple[Any, Any, Any]] = []
    seen_urls: set[str] = set()

    for post, subdir, source in blog.collect_memex_sources():
        url = blog.normalize_memex_url(
            "/memex.html"
            if blog.is_memex_manifesto(post, subdir)
            else blog.get_hub_url(post)
            if blog.is_memex_hub_dir(subdir)
            else blog.get_post_url(post, subdir)
        )
        if url in seen_urls:
            continue

        title = str(post["title"]).lower()
        stem = str(post.get("_source_stem", "")).lower()
        source_name = source.name.lower()
        haystacks = {title, stem, source_name, url.lower(), blog.get_static_link(post["title"])}

        if (
            query_lower in title
            or query_lower == stem
            or query_slug in haystacks
            or query_lower in url.lower()
        ):
            matches.append((post, subdir, source))
            seen_urls.add(url)

    return matches


def pick_page(query: str) -> tuple[Any, Any, Any]:
    matches = find_pages(query)
    if not matches:
        print(f"No page matched: {query!r}", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"Multiple pages matched {query!r}:", file=sys.stderr)
        for post, subdir, _source in matches[:10]:
            print(
                f"  - {post['title']} ({blog.get_post_url(post, subdir)})",
                file=sys.stderr,
            )
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more", file=sys.stderr)
        sys.exit(1)
    return matches[0]


def page_url(post: Any, subdir: Any) -> str:
    if blog.is_memex_manifesto(post, subdir):
        return "/memex.html"
    if blog.is_memex_hub_dir(subdir):
        return blog.get_hub_url(post)
    return blog.get_post_url(post, subdir)


def cmd_stats(_args: argparse.Namespace) -> None:
    ctx = load_context()
    stats = ctx["stats"]
    backlinks = ctx["backlinks"]
    counts = [len(items) for items in backlinks.values()]
    zero_backlinks = sum(
        1
        for post, subdir, _source in blog.collect_memex_sources()
        if not blog.is_memex_manifesto(post, subdir)
        and not blog.is_memex_hub_dir(subdir)
        and not backlinks.get(blog.normalize_memex_url(page_url(post, subdir)), [])
    )

    print("Memex stats")
    print(f"  files       {stats['files']}")
    print(f"  pages       {stats['pages']}")
    print(f"  hubs        {stats['hubs']}")
    print(f"  wikilinks   {stats['wikilinks']}")
    print(f"  int. links  {stats['internal_links']}")
    print(f"  ext. links  {stats['external_links']}")
    print(f"  pages w/ 0 backlinks  {zero_backlinks}")
    if counts:
        print(f"  avg backlinks/page    {sum(counts) / len(counts):.1f}")
        print(f"  max backlinks         {max(counts)}")


def cmd_resolve(args: argparse.Namespace) -> None:
    ctx = load_context()
    entry = blog.resolve_wikilink(
        args.target,
        ctx["registry"],
        title_lookup=ctx["title_lookup"],
    )
    if not entry:
        print(f"Unresolved: {args.target!r}")
        sys.exit(1)
    print(f"{args.target!r} -> {entry['title']}")
    print(entry["url"])


def cmd_page(args: argparse.Namespace) -> None:
    load_context()
    post, subdir, source = pick_page(args.query)
    url = page_url(post, subdir)
    outgoing = blog.get_outgoing_links(post)
    backlinks = blog.get_backlinks_for_post(post, subdir)
    related = blog.get_related_pages(post, subdir)
    see_also = blog.get_see_also_pages(post, subdir)

    print(post["title"])
    print(f"  source   {source}")
    print(f"  section  {blog.memex_section_key(subdir)}")
    print(f"  url      {url}")
    topics = blog.get_topics(post)
    if topics:
        print(f"  topics   {', '.join(topics)}")
    aliases = blog.collect_post_aliases(post)
    if aliases:
        print(f"  aliases  {', '.join(aliases[:8])}")
        if len(aliases) > 8:
            print(f"           ... +{len(aliases) - 8} more")
    print(f"  outgoing {len(outgoing)}")
    for link in outgoing:
        print(f"    -> {link['title']}  {link['url']}")
    print(f"  backlinks {len(backlinks)}")
    for link in backlinks:
        print(f"    <- {link['title']}  {link['url']}")
    if related:
        print(f"  related  {len(related)}")
        for link in related:
            print(f"    ~  {link['title']}  {link['url']}")
    if see_also:
        print(f"  see also {len(see_also)}")
        for link in see_also:
            print(f"    ~  {link['title']}  {link['url']}")


def cmd_backlinks(args: argparse.Namespace) -> None:
    load_context()
    post, subdir, _source = pick_page(args.query)
    for link in blog.get_backlinks_for_post(post, subdir):
        print(f"{link['title']}\t{link['url']}")


def cmd_outgoing(args: argparse.Namespace) -> None:
    load_context()
    post, subdir, _source = pick_page(args.query)
    for link in blog.get_outgoing_links(post):
        print(f"{link['title']}\t{link['url']}")


def cmd_missing(_args: argparse.Namespace) -> None:
    ctx = load_context()
    registry = ctx["registry"]
    title_lookup = ctx["title_lookup"]
    missing: list[tuple[str, str, str]] = []

    for post, subdir, source in blog.collect_memex_sources():
        if not blog.should_preprocess_wikilinks(post, subdir):
            continue
        body = post.content or ""
        for match in blog.WIKILINK_PATTERN.finditer(body):
            target = match.group(1).strip()
            if not blog.resolve_wikilink(target, registry, title_lookup=title_lookup):
                missing.append((target, str(post["title"]), str(source)))

    if not missing:
        print("No unresolved wikilinks.")
        return

    print(f"Unresolved wikilinks ({len(missing)}):")
    for target, title, source in sorted(missing, key=lambda item: item[0].lower()):
        print(f"  [[{target}]]  in {title}  ({source})")


def cmd_orphans(args: argparse.Namespace) -> None:
    ctx = load_context()
    backlinks = ctx["backlinks"]
    orphans: list[tuple[str, str, str]] = []

    for post, subdir, source in blog.collect_memex_sources():
        if blog.is_memex_manifesto(post, subdir) or blog.is_memex_hub_dir(subdir):
            continue
        url = blog.normalize_memex_url(page_url(post, subdir))
        if not backlinks.get(url):
            orphans.append((post["title"], url, str(source)))

    orphans.sort(key=lambda item: item[0].lower())
    limit = args.limit
    if limit:
        orphans = orphans[:limit]

    print(f"Pages with no backlinks ({len(orphans)}{' shown' if args.limit else ''}):")
    for title, url, source in orphans:
        print(f"  {title}\t{url}\t({source})")


def cmd_top(args: argparse.Namespace) -> None:
    ctx = load_context()
    backlinks = ctx["backlinks"]
    rows: list[tuple[int, str, str]] = []
    seen_urls: set[str] = set()

    for post, subdir, _source in blog.collect_memex_sources():
        url = blog.normalize_memex_url(page_url(post, subdir))
        if url in seen_urls:
            continue
        seen_urls.add(url)
        count = len(backlinks.get(url, []))
        if count:
            rows.append((count, post["title"], page_url(post, subdir)))

    rows.sort(key=lambda item: (-item[0], item[1].lower()))
    for count, title, url in rows[: args.limit]:
        print(f"{count:4d}  {title}\t{url}")


def cmd_search(args: argparse.Namespace) -> None:
    matches = find_pages(args.query)
    if not matches:
        print(f"No pages matched: {args.query!r}")
        sys.exit(1)
    for post, subdir, source in matches[: args.limit]:
        print(f"{post['title']}\t{page_url(post, subdir)}\t({source.name})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and maintain the myblog memex wiki.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stats", help="show memex link statistics")

    resolve = subparsers.add_parser("resolve", help="test if a wikilink target resolves")
    resolve.add_argument("target", help="wikilink target, e.g. Philosophy or Hamlet")

    page = subparsers.add_parser("page", help="show one page and its link graph")
    page.add_argument("query", help="title, stem, or URL fragment")

    backlinks = subparsers.add_parser("backlinks", help="list pages linking to a page")
    backlinks.add_argument("query", help="title, stem, or URL fragment")

    outgoing = subparsers.add_parser("outgoing", help="list links from a page")
    outgoing.add_argument("query", help="title, stem, or URL fragment")

    subparsers.add_parser("missing", help="list unresolved [[wikilinks]] in posts")

    orphans = subparsers.add_parser("orphans", help="pages with zero backlinks")
    orphans.add_argument("-n", "--limit", type=int, default=30, help="max rows (default 30)")

    top = subparsers.add_parser("top", help="most-linked pages")
    top.add_argument("-n", "--limit", type=int, default=20, help="max rows (default 20)")

    search = subparsers.add_parser("search", help="find pages by title or stem")
    search.add_argument("query", help="search text")
    search.add_argument("-n", "--limit", type=int, default=20, help="max rows (default 20)")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    commands = {
        "stats": cmd_stats,
        "resolve": cmd_resolve,
        "page": cmd_page,
        "backlinks": cmd_backlinks,
        "outgoing": cmd_outgoing,
        "missing": cmd_missing,
        "orphans": cmd_orphans,
        "top": cmd_top,
        "search": cmd_search,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
