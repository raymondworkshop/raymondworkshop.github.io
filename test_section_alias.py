import pathlib
from datetime import date

import frontmatter

from blog_build.posts import (
    canonical_section,
    derive_post_date,
    get_alias_output_path,
    get_post_output_path,
    get_post_url,
    is_aliased_section,
    memex_section_key,
    section_label,
    source_dirs_for_section,
)


def test_canonical_section_aliases_new_notes():
    assert canonical_section(pathlib.Path("new-notes")) == pathlib.Path("notes")
    assert canonical_section(pathlib.Path("notes")) == pathlib.Path("notes")
    assert canonical_section(pathlib.Path("wiki")) == pathlib.Path("wiki")
    assert is_aliased_section(pathlib.Path("new-notes"))
    assert not is_aliased_section(pathlib.Path("notes"))


def test_memex_section_key_and_label():
    assert memex_section_key(pathlib.Path("new-notes")) == "notes"
    assert section_label(pathlib.Path("new-notes")) == "Notes"


def test_source_dirs_include_alias():
    dirs = source_dirs_for_section(pathlib.Path("notes"))
    assert pathlib.Path("notes") in dirs
    assert pathlib.Path("new-notes") in dirs


def test_urls_and_redirect_path():
    post = frontmatter.Post("body", title="Difficult Conversations")
    post["_source_stem"] = "2026-07-30-difficult-conversations"
    path = pathlib.Path("new-notes")
    assert get_post_url(post, path) == "/notes/2026-07-30-difficult-conversations"
    assert get_post_output_path(post, path) == pathlib.Path(
        "./docs/notes/2026-07-30-difficult-conversations/index.html"
    )
    assert get_alias_output_path(post, path) == pathlib.Path(
        "./docs/new-notes/2026-07-30-difficult-conversations/index.html"
    )
    assert get_alias_output_path(post, pathlib.Path("notes")) is None


def test_derive_post_date_from_exported_and_filename():
    post = frontmatter.Post("body", exported="2026-07-30")
    assert derive_post_date(post, pathlib.Path("book.md")) == date(2026, 7, 30)

    post2 = frontmatter.Post("body")
    assert derive_post_date(
        post2, pathlib.Path("2026-08-05-the-psychology-of-money.md")
    ) == date(2026, 8, 5)

    post3 = frontmatter.Post("body", date="2022-06-17", exported="2026-07-30")
    assert derive_post_date(post3, pathlib.Path("x.md")) == date(2022, 6, 17)
