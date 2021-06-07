#
import cmarkgfm
import frontmatter
import pathlib
from typing import Iterator
from typing import Sequence
import jinja2

# TODO check more pathlib


def list_dirs(rootdir):
    """get all subdirs"""
    subpaths = []
    for path in pathlib.Path(rootdir).iterdir():
        if path.is_dir():
            list_dirs(path)


def get_sources(dir: str) -> Iterator[pathlib.Path]:
    return pathlib.Path(dir).glob("_posts/*.md")


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


def render_markdown(markdown_text: str) -> str:
    content = cmarkgfm.markdown_to_html_with_extensions(
        markdown_text, extensions=["table", "autolink", "strikethrough"]
    )

    return content


# render markdown into HTML
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)

# TODO - get relative static link from title
import re


def get_static_link(title: str) -> str:
    s = "-"
    # Farewell, Google -> farewell-google
    link = s.join(re.findall(r"[\w]+", title)).lower()
    return link


def write_post(post: frontmatter.Post, content: str):
    if post.get("tags"):
        post["stem"] = get_static_link(post["title"])
        # post["tags"] = get_static_link(post["tags"])

        path = pathlib.Path(
            "./docs/{}/{}/index.html".format(post["tags"], post["stem"])
        )
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        path = pathlib.Path("./docs/{}.html".format(post["title"].lower()))

    template = jinja_env.get_template("post.html")
    rendered = template.render(post=post, content=content)
    path.write_text(rendered)


def write_posts(dir: str) -> Sequence[frontmatter.Post]:
    posts = []
    sources = get_sources()

    for source in sources:
        post = parse_source(source)
        """
        # take tags as a dir
        if post.get("tags"):
            post["tags"] = get_static_link(post["tags"])
        """

        content = render_markdown(post.content)
        write_post(post, content)
        post["stem"] = get_static_link(post["title"])
        posts.append(post)

    return posts


def get_all_posts():
    dirs = list_dirs()
    return


def write_tag_index(posts: Sequence[frontmatter.Post], tag: str):
    # some tag index
    posts = sorted(posts, key=lambda post: post["date"], reverse=True)
    if tag == "home":
        path = pathlib.Path("./docs/index.html")
        template = jinja_env.get_template("index.html")
    else:
        path = pathlib.Path("./docs/{}/index.html".format(tag))
        template = jinja_env.get_template("tag.html")

    rendered = template.render(posts=posts)
    path.write_text(rendered)


def write_index(posts: Sequence[frontmatter.Post]):
    # Home index
    posts = sorted(posts, key=lambda post: post["date"], reverse=True)
    path = pathlib.Path("./docs/index.html")
    template = jinja_env.get_template("index.html")
    rendered = template.render(posts=posts)
    path.write_text(rendered)


def main():
    # doc = pathlib.Path("_posts/hello.md")
    # generate index at each subdir
    root = "."  # by default
    posts = write_posts(root)
    write_index(posts)
    # write_post(post, content)
    # return


if __name__ == "__main__":
    main()
