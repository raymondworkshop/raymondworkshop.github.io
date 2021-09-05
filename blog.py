#
import pathlib
import re
from typing import Iterator, Sequence

#import cmarkgfm
import frontmatter
import jinja2

import markdown
import markdown.extensions.fenced_code
import highlighting
import style

# render markdown into HTML
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
)


# TODO: Only support "*.md" now
# types = ["*.md", "*.markdown"]

_markdown = markdown.Markdown(
    extensions = [
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
    return subdirs


def get_sources(path: pathlib.Path) -> Iterator[pathlib.Path]:
    return pathlib.Path(SRCS).joinpath(path).glob("*.md")


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


def render_markdown(markdown_text: str) -> str:
    #TODO render-code
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
    #print(str(post["path"]) + "/" + (post["title"]))
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
    path = pathlib.Path("./docs/{}/index.html".format(str(path)))
    template = jinja_env.get_template("index.html")
    rendered = template.render(posts=posts)
    path.write_text(rendered)


def write_docs(root: str):
    subdirs = list_subdirs(root)
    for subdir in subdirs:
        # remove the old subdir
        # write index in each sub
        posts = write_posts(subdir)
        write_index(posts, subdir)

# the dir to put the src files
SRCS = "./_posts"

def main():
    # doc = pathlib.Path("_posts/hello.md")
    # replace tag functions with dir
    srcs = SRCS  # by default
    target = "./docs/"
    try:
        #TODO - CHECH THE ISSUE ON code highlighting  
        write_pygments_style_sheet()
        write_docs(srcs)
    except OSError as e:
        print("Erros: %s - %s." % (e.filename, e.strerror))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main()
