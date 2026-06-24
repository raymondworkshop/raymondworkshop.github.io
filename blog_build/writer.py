import json
import pathlib
from typing import Any, Sequence

import frontmatter
import jinja2

import highlighting
import style
from blog_build.config import EXCLUDED_INDEX_TITLES, POSTS_PER_PAGE, SRCS
from blog_build.memex import state
from blog_build.memex.links import preprocess_memex_links
from blog_build.memex.queries import (
    get_backlinks_for_post,
    get_hub_summaries,
    get_outgoing_links,
    get_related_pages,
    get_section_hub_for_path,
    get_section_pages_for_post,
    get_section_referenced_for_post,
    get_see_also_pages,
    get_sibling_hubs,
    get_top_referenced_pages,
    get_unlinked_mentions_for_post,
)
from blog_build.memex.resolve import normalize_memex_url
from blog_build.posts import (
    collect_memex_sources,
    get_excerpt,
    get_hub_url,
    get_post_output_path,
    get_post_stem,
    get_post_url,
    get_sources,
    get_static_link,
    get_topics,
    is_memex_hub_dir,
    is_memex_manifesto,
    is_memex_post_path,
    is_section_dir,
    list_subdirs,
    memex_section_key,
    parse_source,
    render_markdown,
    section_label,
    should_preprocess_wikilinks,
    strip_markdown,
)
from blog_build.search import expand_for_search

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)


def render_memex_page(
    post: frontmatter.Post, subdir: pathlib.Path, source: pathlib.Path
) -> None:
    post["path"] = subdir
    body = post.content or ""
    if should_preprocess_wikilinks(post, subdir):
        body = preprocess_memex_links(body)
    content = render_markdown(body)
    write_post(post, content, subdir)


def write_post(post: frontmatter.Post, content: str, path: pathlib.Path):
    output = get_post_output_path(post, path)
    if output.parent != pathlib.Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)
    if is_memex_hub_dir(path):
        post["stem"] = get_static_link(post["title"])
    elif post.get("tags") or post.get("categories") or is_section_dir(path):
        post["stem"] = get_post_stem(post, path)

    ctx = state.get_ctx()
    backlinks = get_backlinks_for_post(post, path)
    section_pages = get_section_pages_for_post(post)
    is_hub = is_memex_hub_dir(path) and bool(post.get("section"))

    if is_memex_manifesto(post, path):
        template = jinja_env.get_template("memex_manifesto.html")
        rendered = template.render(
            post=post,
            content=content,
            stats=ctx.get("stats", {}),
            outgoing_links=get_outgoing_links(post),
            hub_summaries=get_hub_summaries(),
            top_referenced=get_top_referenced_pages(),
            backlinks=backlinks,
        )
    elif is_memex_post_path(path):
        template = jinja_env.get_template("memex.html")
        rendered = template.render(
            post=post,
            content=content,
            backlinks=backlinks,
            section_pages=section_pages,
            is_hub=is_hub,
            section_hub=get_section_hub_for_path(path, post),
            outgoing_links=get_outgoing_links(post),
            related_pages=get_related_pages(post, path),
            see_also_pages=get_see_also_pages(post, path),
            section_referenced=get_section_referenced_for_post(post),
            sibling_hubs=get_sibling_hubs(post) if is_hub else [],
            unlinked_mentions=get_unlinked_mentions_for_post(post, path),
        )
    else:
        template = jinja_env.get_template("post.html")
        rendered = template.render(post=post, content=content)

    output.write_text(rendered)


def write_pygments_style_sheet():
    css = highlighting.get_style_css(style.themeStyle)
    pathlib.Path("./docs/static/pygments.css").write_text(css)


def write_posts(
    path: pathlib.Path, *, memex_enabled: bool = False
) -> Sequence[frontmatter.Post]:
    posts = []
    sources = get_sources(path)

    for source in sources:
        print("src: ", str(source))
        post = parse_source(source)
        post["path"] = path

        body = post.content or ""
        if memex_enabled and should_preprocess_wikilinks(post, path):
            body = preprocess_memex_links(body)
        content = render_markdown(body)

        write_post(post, content, path)
        posts.append(post)

    return posts


def rewrite_memex_pages(
    root: str, *, only: set[pathlib.Path] | None = None
) -> int:
    count = 0
    for subdir in list_subdirs(root):
        from blog_build.posts import is_memex_excluded_path

        if is_memex_excluded_path(subdir):
            continue
        for source in get_sources(subdir):
            source_key = source.resolve()
            if only is not None and source_key not in only:
                continue
            post = parse_source(source)
            print("src: ", str(source))
            render_memex_page(post, subdir, source)
            count += 1
    return count


def write_indexes_for_sections(sections: set[pathlib.Path]) -> None:
    for subdir in sections:
        posts = []
        for source in get_sources(subdir):
            post = parse_source(source)
            post["path"] = subdir
            posts.append(post)
        write_index(posts, subdir)


def write_index(posts: Sequence[frontmatter.Post], path: pathlib.Path):
    posts = sorted(posts, key=lambda post: post.get("date") or "", reverse=True)
    if path == pathlib.Path("."):
        write_paginated_home(posts)
        return
    if is_memex_hub_dir(path):
        return

    output = pathlib.Path("./docs/{}/index.html".format(str(path)))
    template = jinja_env.get_template("index.html")
    rendered = template.render(posts=posts)
    output.write_text(rendered)


def should_show_on_home(post: frontmatter.Post) -> bool:
    return post["title"] not in EXCLUDED_INDEX_TITLES


def write_paginated_home(posts: Sequence[frontmatter.Post]):
    posts = [post for post in posts if should_show_on_home(post)]
    template = jinja_env.get_template("index.html")
    total_pages = max(1, (len(posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE)

    for page in range(1, total_pages + 1):
        start = (page - 1) * POSTS_PER_PAGE
        end = start + POSTS_PER_PAGE
        output_path = pathlib.Path("./docs/index.html")
        if page > 1:
            output_path = pathlib.Path(f"./docs/page/{page}/index.html")

        pagination = {
            "page": page,
            "total_pages": total_pages,
            "previous_url": "/index.html"
            if page == 2
            else f"/page/{page - 1}/index.html"
            if page > 2
            else None,
            "next_url": f"/page/{page + 1}/index.html" if page < total_pages else None,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = template.render(posts=posts[start:end], pagination=pagination)
        output_path.write_text(rendered)


def write_memex_index() -> None:
    entries: list[dict[str, Any]] = []
    backlinks = state.get_ctx().get("backlinks", {})

    for post, subdir, _source in collect_memex_sources():
        if is_memex_manifesto(post, subdir):
            continue
        if is_memex_hub_dir(subdir):
            url = get_hub_url(post)
            entries.append(
                {
                    "title": post["title"],
                    "url": url,
                    "section": "Hub",
                    "kind": "hub",
                    "backlink_count": len(
                        backlinks.get(normalize_memex_url(url), [])
                    ),
                }
            )
            continue
        url = get_post_url(post, subdir)
        entries.append(
            {
                "title": post["title"],
                "url": url,
                "section": section_label(subdir),
                "kind": "page",
                "backlink_count": len(
                    backlinks.get(normalize_memex_url(url), [])
                ),
            }
        )

    entries.sort(key=lambda item: (-item["backlink_count"], item["title"].lower()))
    output = pathlib.Path("./docs/memex/index.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    template = jinja_env.get_template("memex_index.html")
    rendered = template.render(entries=entries)
    output.write_text(rendered)


def write_docs(root: str, *, memex_enabled: bool = False):
    subdirs = list_subdirs(root)
    for subdir in subdirs:
        posts = write_posts(subdir, memex_enabled=memex_enabled)
        write_index(posts, subdir)


def collect_search_posts() -> list[dict[str, Any]]:
    from blog_build.memex.queries import get_outgoing_links

    entries: list[dict[str, Any]] = []
    ctx = state.get_ctx()
    section_hubs = ctx.get("section_hubs", {})
    backlinks = ctx.get("backlinks", {})

    for post_id, (post, subdir, _source) in enumerate(
        collect_memex_sources(), start=1
    ):
        if is_memex_manifesto(post, subdir):
            url = "/memex.html"
            section = "Memex"
            hub_url = ""
            hub_title = ""
        elif is_memex_hub_dir(subdir):
            url = get_hub_url(post)
            section = "Hub"
            hub_url = url
            hub_title = post["title"]
        else:
            url = get_post_url(post, subdir)
            section = section_label(subdir)
            hub = section_hubs.get(memex_section_key(subdir), {})
            hub_url = hub.get("url", "")
            hub_title = hub.get("title", "")

        plain_body = strip_markdown(post.content or "")
        title = post["title"]
        excerpt = get_excerpt(post)
        topics = get_topics(post)
        page_url = normalize_memex_url(url)

        entries.append(
            {
                "id": str(post_id),
                "title": title,
                "title_search": expand_for_search(title),
                "date": post["date"].strftime("%Y-%m-%d")
                if post.get("date")
                else "",
                "url": url,
                "section": section,
                "hub_url": hub_url,
                "hub_title": hub_title,
                "topics": topics,
                "topics_search": expand_for_search(" ".join(topics)),
                "excerpt": excerpt,
                "excerpt_search": expand_for_search(excerpt),
                "body": plain_body,
                "body_search": expand_for_search(plain_body),
                "backlink_count": len(backlinks.get(page_url, [])),
                "outgoing_count": len(get_outgoing_links(post)),
            }
        )

    return entries


def write_search_index(posts: Sequence[dict[str, Any]]) -> None:
    path = pathlib.Path("./docs/static/search-index.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(posts, ensure_ascii=False, indent=2))


def write_search_page() -> None:
    template = jinja_env.get_template("search.html")
    rendered = template.render()
    pathlib.Path("./docs/search.html").write_text(rendered)
