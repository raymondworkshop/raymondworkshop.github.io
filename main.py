#
import cmarkgfm
import frontmatter
import pathlib
from typing import Iterator
from typing import Sequence
import jinja2

# TODO check more pathlib
def get_sources() -> Iterator[pathlib.Path]:
    return pathlib.Path(".").glob("_posts/*.md", recursive=True)


def render_markdown(markdown_text: str) -> str:
    content = cmarkgfm.markdown_to_html_with_extensions(
        markdown_text, extensions=["table", "autolink", "strikethrough"]
    )

    return content


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


# render markdown into HTML
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)


def write_post(post: frontmatter.Post, content: str):
    path = pathlib.Path("./_site/{}.html".format(post["stem"]))

    return


def write_site(posts: Sequence[frontmatter.Post]):
    # sort
    # posts = sorted(posts, key=lambda post: post["date"], reverse=True)
    path = pathlib.Path("./templates/index.html")
    template = jinja_env.get_template("index.html")
    rendered = template.render(posts=posts)
    path.write_text(rendered)


def main():
    page = "pages/hello.md"
    write_site(page)
    return


if __name__ == "__main__":
    main()
