import pathlib
import re
from typing import Iterator, Sequence

import frontmatter
import markdown
import markdown.extensions.fenced_code

import highlighting
from blog_build.config import (
    DATED_STEM_SUFFIX,
    MEMEX_EXCLUDED_SECTIONS,
    MEMEX_HUB_DIR,
    NOTES_ON_TITLE,
    NOTES_ON_TITLE_PLAIN,
    SRCS,
)

if not hasattr(frontmatter, "load"):
    raise RuntimeError(
        "Incompatible 'frontmatter' module detected. "
        "Install 'python-frontmatter' and remove the conflicting 'frontmatter' package."
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


def is_section_dir(path: pathlib.Path) -> bool:
    section = str(path).strip("./")
    return bool(section) and not is_memex_hub_dir(path)


def get_file_stem(post: frontmatter.Post) -> str:
    raw = post.get("_source_stem")
    if raw:
        slug = get_static_link(str(raw))
        return slug if slug else str(raw).lower()
    return get_static_link(post["title"])


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


def get_post_output_path(post: frontmatter.Post, path: pathlib.Path) -> pathlib.Path:
    if is_memex_hub_dir(path):
        stem = get_static_link(post["title"])
        return pathlib.Path(f"./docs/memex/{stem}/index.html")
    if post.get("tags") or post.get("categories") or is_section_dir(path):
        section = str(path).strip("./").lower()
        stem = get_post_stem(post, path)
        if section:
            return pathlib.Path(f"./docs/{section}/{stem}/index.html")
        return pathlib.Path(f"./docs/{stem}/index.html")
    return pathlib.Path("./docs/{}.html".format(post["title"].lower()))


def render_markdown(markdown_text: str) -> str:
    _markdown.reset()
    content = _markdown.convert(markdown_text)
    content = highlighting.highlight(content)
    return content


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


def get_excerpt(post: frontmatter.Post) -> str:
    if post.get("abstract"):
        return strip_markdown(str(post["abstract"]))[:200]
    return strip_markdown(post.content)[:200]


def get_topics(post: frontmatter.Post) -> list[str]:
    topics: list[str] = []
    for field in ("categories", "tags", "topics"):
        if post.get(field):
            for topic in post[field]:
                value = str(topic).strip().lower()
                if value and value != "home":
                    topics.append(value)
    return list(dict.fromkeys(topics))


def collect_post_aliases(post: frontmatter.Post) -> list[str]:
    aliases: list[str] = []
    title = str(post["title"]).strip()
    stripped_title = title.lstrip("!").strip()
    if stripped_title and stripped_title != title:
        aliases.append(stripped_title)

    notes_match = NOTES_ON_TITLE.match(title)
    if notes_match:
        aliases.append(notes_match.group(1).strip())
    else:
        plain_match = NOTES_ON_TITLE_PLAIN.match(title)
        if plain_match:
            aliases.append(plain_match.group(1).strip().strip("'\""))

    source_stem = post.get("_source_stem")
    if source_stem:
        stem = str(source_stem).strip()
        aliases.append(stem)
        dated_match = DATED_STEM_SUFFIX.match(stem)
        if dated_match:
            aliases.append(dated_match.group(1))

    for field in ("aliases", "aka"):
        if not post.get(field):
            continue
        values = post[field]
        if isinstance(values, str):
            values = [values]
        for value in values:
            alias = str(value).strip()
            if alias:
                aliases.append(alias)

    return list(dict.fromkeys(alias for alias in aliases if alias))


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


def source_is_stale(
    source: pathlib.Path, post: frontmatter.Post, path: pathlib.Path
) -> bool:
    output = get_post_output_path(post, path)
    if not output.exists():
        return True
    return source.stat().st_mtime > output.stat().st_mtime


def page_url_for_entry(post: frontmatter.Post, subdir: pathlib.Path) -> str:
    from blog_build.memex.resolve import normalize_memex_url

    if is_memex_manifesto(post, subdir):
        return normalize_memex_url("/memex.html")
    if is_memex_hub_dir(subdir):
        return normalize_memex_url(get_hub_url(post))
    return normalize_memex_url(get_post_url(post, subdir))
