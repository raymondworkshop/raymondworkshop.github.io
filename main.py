#
import cmarkgfm
import frontmatter
import pathlib
from typing import Iterator


def render_markdown(markdown_text: str) -> str:
    content = cmarkgfm.markdown_to_html_with_extensions(
        markdown_text, extensions=["table", "autolink", "strikethrough"]
    )

    return content


# check more pathlib
def get_sources() -> Iterator[pathlib.Path]:
    return pathlib.Path(".").glob("pages/*.md")


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


def main():
    doc = "pages/hello.md"
    print(render_markdown(doc))
    return


if __name__ == "__main__":
    main()
