#
import json
import pathlib
import re
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
}

# render markdown into HTML
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)


# TODO: Only support "*.md" now
# types = ["*.md", "*.markdown"]

_markdown = markdown.Markdown(
    extensions=[
        "tables",
        "footnotes",
        "attr_list",
        markdown.extensions.fenced_code.FencedCodeExtension(lang_prefix="language-"),
    ]
)

# TODO check more pathlib
def list_subdirs(root: str) -> Iterator[pathlib.Path]:
    """get all subdirs"""
    subdirs = [
        pathlib.Path(subdir.stem)  # bugs, get the last subdir
        for subdir in pathlib.Path(root).iterdir()
        if subdir.is_dir()
    ]
    subdirs.append(pathlib.Path("."))
    return iter(subdirs)


def get_sources(path: pathlib.Path) -> Iterator[pathlib.Path]:
    return pathlib.Path(SRCS).joinpath(path).glob("*.md")


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


def render_markdown(markdown_text: str) -> str:
    # TODO render-code
    _markdown.reset()
    content = _markdown.convert(markdown_text)
    content = highlighting.highlight(content)

    return content


# TODO - get relative static link from title
def get_static_link(title: str) -> str:
    # like Farewell, Google -> farewell-google
    s = "-"
    link = s.join(re.findall(r"[\w]+", title)).lower()

    return link


def write_post(post: frontmatter.Post, content: str):
    # print(str(post["path"]) + "/" + (post["title"]))
    # TODO: mkdir all tag subdirs
    """
    tags = []
    if post.get("tags"):
        tags = post["tags"]
    if post.get("categories"):
        tags = post["categories"]

    if tags:
        post["stem"] = (
            get_static_link(post["title"]) + "-" + post["date"].strftime("%Y-%m-%d")
        )
        # post["tags"] = get_static_link(post["tags"])

        for tag in tags:
            path = pathlib.Path(
                "./docs/{}/{}/index.html".format(
                    str(tag).lower(),
                    post["stem"],
                )
            )
            path.parent.mkdir(parents=True, exist_ok=True)
    """
    if post.get("tags") or post.get("categories"):
        post["stem"] = (
            get_static_link(post["title"]) + "-" + post["date"].strftime("%Y-%m-%d")
        )
        # post["tags"] = get_static_link(post["tags"])

        path = pathlib.Path(
            "./docs/{}/{}/index.html".format(
                str(post["path"]).lower(),
                post["stem"],
            )
        )
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        path = pathlib.Path("./docs/{}.html".format(post["title"].lower()))

    template = jinja_env.get_template("post.html")
    rendered = template.render(post=post, content=content)
    path.write_text(rendered)


def write_pygments_style_sheet():
    css = highlighting.get_style_css(style.themeStyle)
    pathlib.Path("./docs/static/pygments.css").write_text(css)
    

def write_posts(path: pathlib.Path) -> Sequence[frontmatter.Post]:
    posts = []
    sources = get_sources(path)

    for source in sources:
        print("src: ", str(source))
        post = parse_source(source)
        """
        # take tags as a dir
        if post.get("tags"):
            post["tags"] = get_static_link(post["tags"])
        """

        content = render_markdown(post.content)
        post["path"] = path
        write_post(post, content)
        # post["stem"] = get_static_link(post["title"])
        posts.append(post)

    return posts


def write_index(posts: Sequence[frontmatter.Post], path: pathlib.Path):
    # Home index
    posts = sorted(posts, key=lambda post: post["date"], reverse=True)
    if path == pathlib.Path("."):
        write_paginated_home(posts)
        return

    path = pathlib.Path("./docs/{}/index.html".format(str(path)))
    template = jinja_env.get_template("index.html")
    rendered = template.render(posts=posts)
    path.write_text(rendered)


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
            "previous_url": "/index.html" if page == 2 else f"/page/{page - 1}/index.html" if page > 2 else None,
            "next_url": f"/page/{page + 1}/index.html" if page < total_pages else None,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = template.render(posts=posts[start:end], pagination=pagination)
        output_path.write_text(rendered)


def write_docs(root: str):
    subdirs = list_subdirs(root)
    for subdir in subdirs:
        # remove the old subdir
        # write index in each sub
        posts = write_posts(subdir)
        write_index(posts, subdir)


def section_label(path: pathlib.Path) -> str:
    name = str(path).strip("./")
    return name.lstrip("_").title() if name else "Blog"


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_topics(post: frontmatter.Post) -> list[str]:
    topics: list[str] = []
    for field in ("categories", "tags"):
        if post.get(field):
            for topic in post[field]:
                value = str(topic).strip().lower()
                if value and value != "home":
                    topics.append(value)
    return list(dict.fromkeys(topics))


def get_post_url(post: frontmatter.Post, path: pathlib.Path) -> str:
    if post.get("tags") or post.get("categories"):
        if post.get("date"):
            stem = (
                get_static_link(post["title"])
                + "-"
                + post["date"].strftime("%Y-%m-%d")
            )
        else:
            stem = get_static_link(post["title"])
        section = str(path).lower()
        if section == ".":
            return f"/./{stem}"
        return f"/{section}/{stem}"
    return f"/{post['title'].lower()}.html"


def get_excerpt(post: frontmatter.Post) -> str:
    if post.get("abstract"):
        return strip_markdown(str(post["abstract"]))[:200]
    return strip_markdown(post.content)[:200]


def collect_search_posts() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    post_id = 0

    for subdir in list_subdirs(SRCS):
        for source in get_sources(subdir):
            post = parse_source(source)
            post["path"] = subdir
            plain_body = strip_markdown(post.content)
            topics = get_topics(post)
            post_id += 1
            entries.append(
                {
                    "id": str(post_id),
                    "title": post["title"],
                    "date": post["date"].strftime("%Y-%m-%d")
                    if post.get("date")
                    else "",
                    "url": get_post_url(post, subdir),
                    "section": section_label(subdir),
                    "topics": topics,
                    "excerpt": get_excerpt(post),
                    "body": plain_body,
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


# the dir to put the src files
SRCS = "./_posts/"


def main():
    # doc = pathlib.Path("_posts/hello.md")
    # replace tag functions with dir
    srcs = SRCS  # by default
    target = "./docs/"
    try:
        # TODO - CHECH THE ISSUE ON code highlighting
        # cannot update font-size in pygments
        #write_pygments_style_sheet() 
        write_docs(srcs)
        search_posts = collect_search_posts()
        write_search_index(search_posts)
        write_search_page()
        print(f"search: indexed {len(search_posts)} posts")
    except OSError as e:
        print("Erros: %s - %s." % (e.filename, e.strerror))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    main()
