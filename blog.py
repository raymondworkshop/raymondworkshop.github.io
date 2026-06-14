#
import html
import json
import pathlib
import re
from collections import defaultdict
from typing import Any, Iterator, Sequence

# import cmarkgfm
import frontmatter
import jinja2

import markdown
import markdown.extensions.fenced_code
import highlighting
import style

if not hasattr(frontmatter, "load"):
    raise RuntimeError(
        "Incompatible 'frontmatter' module detected. "
        "Install 'python-frontmatter' and remove the conflicting 'frontmatter' package."
    )

POSTS_PER_PAGE = 20
CJK_RE = re.compile(r"[\u3040-\u9fff\uff00-\uffef]")
MEMEX_EXCLUDED_SECTIONS: set[str] = set()
MEMEX_HUB_DIR = pathlib.Path("memex")
WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
HASHTAG_TAG_LINE = re.compile(r"^(?:#[^\s#]\S*\s*)+$", re.MULTILINE)
HASHTAG_TOKEN = re.compile(r"#[^\s#]\S*")

EXCLUDED_INDEX_TITLES = {
    "Slides",
    "About",
    "links",
    "invest",
    "docs",
    "ideas",
    "Projects",
    "Talks",
    "Bookshelf",
    "Coaching",
    "business",
    "Memex",
}

_memex_ctx: dict[str, Any] = {}

# render markdown into HTML
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)


_markdown = markdown.Markdown(
    extensions=[
        "tables",
        "footnotes",
        "attr_list",
        markdown.extensions.fenced_code.FencedCodeExtension(lang_prefix="language-"),
    ]
)


def list_subdirs(root: str) -> Iterator[pathlib.Path]:
    """get all subdirs"""
    subdirs = [
        pathlib.Path(subdir.stem)
        for subdir in pathlib.Path(root).iterdir()
        if subdir.is_dir()
    ]
    subdirs.append(pathlib.Path("."))
    return iter(subdirs)


def get_sources(path: pathlib.Path) -> Iterator[pathlib.Path]:
    return pathlib.Path(SRCS).joinpath(path).glob("*.md")


def derive_post_title(post: frontmatter.Post, source: pathlib.Path) -> str:
    if post.get("title"):
        return str(post["title"]).strip()
    for line in (post.content or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source.stem


def normalize_post(post: frontmatter.Post, source: pathlib.Path) -> frontmatter.Post:
    post["title"] = derive_post_title(post, source)
    post["_source_stem"] = source.stem
    return post


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return normalize_post(post, source)


def is_section_dir(path: pathlib.Path) -> bool:
    section = str(path).strip("./")
    return bool(section) and not is_memex_hub_dir(path)


def get_file_stem(post: frontmatter.Post) -> str:
    raw = post.get("_source_stem")
    if raw:
        slug = get_static_link(str(raw))
        return slug if slug else str(raw).lower()
    return get_static_link(post["title"])


def render_markdown(markdown_text: str) -> str:
    _markdown.reset()
    content = _markdown.convert(markdown_text)
    content = highlighting.highlight(content)
    return content


def get_static_link(title: str) -> str:
    s = "-"
    link = s.join(re.findall(r"[\w]+", title)).lower()
    return link


def is_memex_excluded_path(path: pathlib.Path) -> bool:
    section = str(path).strip("./")
    return section in MEMEX_EXCLUDED_SECTIONS


def is_memex_post_path(path: pathlib.Path) -> bool:
    return not is_memex_excluded_path(path)


def memex_section_key(path: pathlib.Path) -> str:
    section = str(path).strip("./")
    return section if section else "blog"


def is_memex_hub_dir(path: pathlib.Path) -> bool:
    return str(path).strip("./") == str(MEMEX_HUB_DIR)


def is_memex_manifesto(post: frontmatter.Post, path: pathlib.Path) -> bool:
    return path == pathlib.Path(".") and post.get("title") == "Memex"


def should_preprocess_wikilinks(post: frontmatter.Post, path: pathlib.Path) -> bool:
    return is_memex_manifesto(post, path) or is_memex_post_path(path)


def register_wikilink_target(
    registry: dict[str, dict[str, str]],
    title: str,
    url: str,
    *,
    stem: str | None = None,
) -> None:
    entry = {"url": url, "title": title}
    registry[get_static_link(title)] = entry
    registry[title.lower().strip()] = entry
    if stem:
        registry[stem.lower().strip()] = entry


def resolve_wikilink(
    target: str, registry: dict[str, dict[str, str]]
) -> dict[str, str] | None:
    key = target.strip()
    if key.lower() in registry:
        return registry[key.lower()]
    slug = get_static_link(key)
    if slug in registry:
        return registry[slug]
    return None


def normalize_memex_url(url: str) -> str:
    url = url.strip().split("#", 1)[0].split("?", 1)[0]
    if url.endswith("/index.html"):
        url = url[: -len("/index.html")] or "/"
    if url.endswith("/") and len(url) > 1:
        url = url.rstrip("/")
    return url


def build_url_registry(registry: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    url_registry: dict[str, dict[str, str]] = {}
    for entry in registry.values():
        url_registry[normalize_memex_url(entry["url"])] = entry
    return url_registry


def get_topics(post: frontmatter.Post) -> list[str]:
    topics: list[str] = []
    for field in ("categories", "tags", "topics"):
        if post.get(field):
            for topic in post[field]:
                value = str(topic).strip().lower()
                if value and value != "home":
                    topics.append(value)
    return list(dict.fromkeys(topics))


def iter_hashtag_links(
    body: str, registry: dict[str, dict[str, str]]
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or not HASHTAG_TAG_LINE.match(stripped):
            continue
        for match in HASHTAG_TOKEN.finditer(stripped):
            tag = match.group(0)[1:]
            entry = resolve_wikilink(tag, registry)
            if entry and entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry


def iter_topic_links(
    post: frontmatter.Post,
    registry: dict[str, dict[str, str]],
    section_hubs: dict[str, dict[str, str]],
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for topic in get_topics(post):
        hub = section_hubs.get(topic)
        if hub and hub["url"] not in seen:
            seen.add(hub["url"])
            yield {"title": hub["title"], "url": hub["url"]}
        entry = resolve_wikilink(topic, registry)
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry


def iter_resolved_links(
    body: str,
    registry: dict[str, dict[str, str]],
    url_registry: dict[str, dict[str, str]],
    *,
    post: frontmatter.Post | None = None,
    section_hubs: dict[str, dict[str, str]] | None = None,
) -> Iterator[dict[str, str]]:
    seen: set[str] = set()
    for match in WIKILINK_PATTERN.finditer(body):
        entry = resolve_wikilink(match.group(1).strip(), registry)
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        url = normalize_memex_url(match.group(2))
        entry = url_registry.get(url) or resolve_wikilink(match.group(1).strip(), registry)
        if entry and entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    for entry in iter_hashtag_links(body, registry):
        if entry["url"] not in seen:
            seen.add(entry["url"])
            yield entry
    if post and section_hubs is not None:
        for entry in iter_topic_links(post, registry, section_hubs):
            if entry["url"] not in seen:
                seen.add(entry["url"])
                yield entry


def preprocess_hashtag_tags(text: str) -> str:
    registry = _memex_ctx.get("registry", {})

    def repl_line(match: re.Match[str]) -> str:
        line = match.group(0)

        def repl_tag(tag_match: re.Match[str]) -> str:
            tag = tag_match.group(0)[1:]
            entry = resolve_wikilink(tag, registry)
            if entry:
                return f"[[{tag}|#{tag}]]"
            return tag_match.group(0)

        return HASHTAG_TOKEN.sub(repl_tag, line)

    return HASHTAG_TAG_LINE.sub(repl_line, text)


def preprocess_wikilinks(text: str) -> str:
    registry = _memex_ctx.get("registry", {})

    def repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        display = match.group(2).strip() if match.group(2) else target
        entry = resolve_wikilink(target, registry)
        if entry:
            return (
                f'<a href="{html.escape(entry["url"])}" class="wikilink">'
                f"{html.escape(display)}</a>"
            )
        return f'<span class="wikilink-missing">{html.escape(display)}</span>'

    return WIKILINK_PATTERN.sub(repl, text)


def preprocess_internal_markdown_links(text: str) -> str:
    registry = _memex_ctx.get("registry", {})
    url_registry = _memex_ctx.get("url_registry", {})

    def repl(match: re.Match[str]) -> str:
        display = match.group(1).strip()
        url = normalize_memex_url(match.group(2))
        entry = url_registry.get(url) or resolve_wikilink(display, registry)
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


def get_post_stem(post: frontmatter.Post, path: pathlib.Path) -> str:
    if is_memex_hub_dir(path):
        return get_static_link(post["title"])
    if post.get("tags") or post.get("categories"):
        if post.get("date"):
            return (
                get_static_link(post["title"])
                + "-"
                + post["date"].strftime("%Y-%m-%d")
            )
        return get_static_link(post["title"])
    if is_section_dir(path):
        return get_file_stem(post)
    return get_static_link(post["title"])


def get_hub_url(post: frontmatter.Post) -> str:
    return f"/memex/{get_static_link(post['title'])}"


def collect_memex_sources() -> list[tuple[frontmatter.Post, pathlib.Path, pathlib.Path]]:
    collected: list[tuple[frontmatter.Post, pathlib.Path, pathlib.Path]] = []

    for subdir in list_subdirs(SRCS):
        if is_memex_excluded_path(subdir):
            continue
        for source in get_sources(subdir):
            post = parse_source(source)
            post["path"] = subdir
            collected.append((post, subdir, source))
    return collected


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
        register_wikilink_target(registry, post["title"], url, stem=stem)
        if post.get("_source_stem"):
            register_wikilink_target(
                registry, str(post["_source_stem"]), url, stem=stem
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
    for post, subdir, _source in sources:
        body = post.content or ""
        line_count += body.count("\n") + (1 if body else 0)
        wikilink_count += len(WIKILINK_PATTERN.findall(body))
        file_hashtag_links = sum(
            1
            for line in body.splitlines()
            if HASHTAG_TAG_LINE.match(line.strip())
            for match in HASHTAG_TOKEN.finditer(line.strip())
            if resolve_wikilink(match.group(0)[1:], registry)
        )
        hashtag_link_count += file_hashtag_links
        internal_link_count += len(
            [
                match
                for match in MARKDOWN_LINK_PATTERN.finditer(body)
                if url_registry.get(normalize_memex_url(match.group(2)))
                or resolve_wikilink(match.group(1).strip(), registry)
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
        for entry in iter_resolved_links(
            body,
            registry,
            url_registry,
            post=post,
            section_hubs=section_hubs,
        ):
            target_url = normalize_memex_url(entry["url"])
            if target_url == source_url_norm:
                continue
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
        "backlinks": dict(backlinks),
        "section_posts": dict(section_posts),
        "section_referenced": dict(section_referenced),
        "section_hubs": section_hubs,
        "hubs": hubs,
        "stats": stats,
    }


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
    return _memex_ctx.get("backlinks", {}).get(normalize_memex_url(url), [])


def get_outgoing_links(post: frontmatter.Post) -> list[dict[str, str]]:
    registry = _memex_ctx.get("registry", {})
    url_registry = _memex_ctx.get("url_registry", {})
    section_hubs = _memex_ctx.get("section_hubs", {})
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
            section_hubs=section_hubs,
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
    return _memex_ctx.get("section_hubs", {}).get(section)


def get_related_pages(
    post: frontmatter.Post, path: pathlib.Path, limit: int = 8
) -> list[dict[str, str]]:
    if is_memex_hub_dir(path):
        return []
    section = memex_section_key(path)
    my_url = get_post_url(post, path)
    neighbor_urls: set[str] = set()
    for link in get_outgoing_links(post):
        neighbor_urls.add(link["url"])
    for link in get_backlinks_for_post(post, path):
        neighbor_urls.add(link["url"])
    neighbor_urls.discard(my_url)
    section_pages = _memex_ctx.get("section_posts", {}).get(section, [])
    related = [page for page in section_pages if page["url"] in neighbor_urls]
    return related[:limit]


def get_section_pages_for_post(
    post: frontmatter.Post,
) -> list[dict[str, str]]:
    section = post.get("section")
    if not section:
        return []
    return _memex_ctx.get("section_posts", {}).get(str(section), [])


def get_section_referenced_for_post(
    post: frontmatter.Post,
) -> list[dict[str, Any]]:
    section = post.get("section")
    if not section:
        return []
    return _memex_ctx.get("section_referenced", {}).get(str(section), [])


def get_sibling_hubs(post: frontmatter.Post) -> list[dict[str, str]]:
    current_url = get_hub_url(post)
    return [
        hub
        for hub in _memex_ctx.get("hubs", [])
        if hub["url"] != current_url
    ]


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
    for section_pages in _memex_ctx.get("section_referenced", {}).values():
        pages.extend(section_pages)
    pages.sort(key=lambda item: (-item["backlink_count"], item["title"].lower()))
    return pages[:limit]


def write_post(post: frontmatter.Post, content: str, path: pathlib.Path):
    if is_memex_hub_dir(path):
        stem = get_static_link(post["title"])
        post["stem"] = stem
        output = pathlib.Path(f"./docs/memex/{stem}/index.html")
        output.parent.mkdir(parents=True, exist_ok=True)
    elif post.get("tags") or post.get("categories") or is_section_dir(path):
        post["stem"] = get_post_stem(post, path)
        section = str(path).strip("./").lower()
        if section:
            output = pathlib.Path(f"./docs/{section}/{post['stem']}/index.html")
        else:
            output = pathlib.Path(f"./docs/{post['stem']}/index.html")
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        output = pathlib.Path("./docs/{}.html".format(post["title"].lower()))

    backlinks = get_backlinks_for_post(post, path)
    section_pages = get_section_pages_for_post(post)
    is_hub = is_memex_hub_dir(path) and bool(post.get("section"))

    if is_memex_manifesto(post, path):
        template = jinja_env.get_template("memex_manifesto.html")
        rendered = template.render(
            post=post,
            content=content,
            stats=_memex_ctx.get("stats", {}),
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
            section_referenced=get_section_referenced_for_post(post),
            sibling_hubs=get_sibling_hubs(post) if is_hub else [],
        )
    else:
        template = jinja_env.get_template("post.html")
        rendered = template.render(post=post, content=content)

    output.write_text(rendered)


def write_pygments_style_sheet():
    css = highlighting.get_style_css(style.themeStyle)
    pathlib.Path("./docs/static/pygments.css").write_text(css)


def write_posts(path: pathlib.Path) -> Sequence[frontmatter.Post]:
    posts = []
    sources = get_sources(path)

    for source in sources:
        print("src: ", str(source))
        post = parse_source(source)
        post["path"] = path

        body = post.content or ""
        if should_preprocess_wikilinks(post, path):
            body = preprocess_memex_links(body)
        content = render_markdown(body)

        write_post(post, content, path)
        posts.append(post)

    return posts


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
    entries: list[dict[str, str]] = []

    for post, subdir, _source in collect_memex_sources():
        if is_memex_manifesto(post, subdir):
            continue
        if is_memex_hub_dir(subdir):
            entries.append(
                {
                    "title": post["title"],
                    "url": get_hub_url(post),
                    "section": "Hub",
                    "kind": "hub",
                }
            )
            continue
        entries.append(
            {
                "title": post["title"],
                "url": get_post_url(post, subdir),
                "section": section_label(subdir),
                "kind": "page",
            }
        )

    entries.sort(key=lambda item: item["title"].lower())
    output = pathlib.Path("./docs/memex/index.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    template = jinja_env.get_template("memex_index.html")
    rendered = template.render(entries=entries)
    output.write_text(rendered)


def write_docs(root: str):
    subdirs = list_subdirs(root)
    for subdir in subdirs:
        posts = write_posts(subdir)
        write_index(posts, subdir)


def section_label(path: pathlib.Path) -> str:
    name = str(path).strip("./")
    if not name:
        return "Blog"
    return name.replace("-", " ").replace("_", " ").title()


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_post_url(post: frontmatter.Post, path: pathlib.Path) -> str:
    if is_memex_hub_dir(path):
        return get_hub_url(post)
    if post.get("tags") or post.get("categories") or is_section_dir(path):
        stem = get_post_stem(post, path)
        section = str(path).strip("./").lower()
        if section:
            return f"/{section}/{stem}"
        return f"/{stem}"
    return f"/{post['title'].lower()}.html"


def get_excerpt(post: frontmatter.Post) -> str:
    if post.get("abstract"):
        return strip_markdown(str(post["abstract"]))[:200]
    return strip_markdown(post.content)[:200]


_opencc_s2t = None
_opencc_t2s = None


def expand_for_search(text: str) -> str:
    if not text or not CJK_RE.search(text):
        return text
    global _opencc_s2t, _opencc_t2s
    if _opencc_s2t is None:
        from opencc import OpenCC

        _opencc_s2t = OpenCC("s2t")
        _opencc_t2s = OpenCC("t2s")
    variants = [text, _opencc_s2t.convert(text), _opencc_t2s.convert(text)]
    return "\n".join(dict.fromkeys(variants))


def collect_search_posts() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    section_hubs = _memex_ctx.get("section_hubs", {})
    backlinks = _memex_ctx.get("backlinks", {})

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


SRCS = "./_posts/"


def main():
    global _memex_ctx
    try:
        _memex_ctx = build_memex_context()
        write_docs(SRCS)
        write_memex_index()
        search_posts = collect_search_posts()
        write_search_index(search_posts)
        write_search_page()
        print(f"memex: { _memex_ctx['stats']['pages']} pages, {_memex_ctx['stats']['hubs']} hubs")
        print(f"search: indexed {len(search_posts)} posts")
    except OSError as e:
        print("Erros: %s - %s." % (e.filename, e.strerror))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    main()
