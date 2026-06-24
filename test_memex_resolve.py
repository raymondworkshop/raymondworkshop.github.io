#!/usr/bin/env python3
"""Tests for memex wikilink resolution."""

from __future__ import annotations

import unittest

import blog


def make_registry(*pages: tuple[str, str, list[str] | None]) -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}
    for title, url, aliases in pages:
        blog.register_wikilink_target(registry, title, url, aliases=aliases or [])
    return registry


def make_lookup(
    *pages: tuple[str, str, list[str]],
) -> list[tuple[str, dict[str, str]]]:
    lookup: list[tuple[str, dict[str, str]]] = []
    for title, url, labels in pages:
        entry = {"title": title, "url": url}
        for label in labels:
            lookup.append((label, entry))
    return lookup


class MemexResolveTests(unittest.TestCase):
    def test_exact_title(self) -> None:
        registry = make_registry(("Philosophy", "/memex/philosophy", None))
        lookup = make_lookup(("Philosophy", "/memex/philosophy", ["Philosophy"]))
        entry = blog.resolve_wikilink("Philosophy", registry, fuzzy_lookup=lookup)
        self.assertEqual(entry["url"], "/memex/philosophy")

    def test_notes_on_derived_alias(self) -> None:
        post = blog.frontmatter.Post(content="")
        post["title"] = "Notes on 'Hamlet'"
        aliases = blog.collect_post_aliases(post)
        self.assertIn("Hamlet", aliases)
        registry = make_registry(("Notes on 'Hamlet'", "/blog/hamlet", aliases))
        lookup = make_lookup(("Notes on 'Hamlet'", "/blog/hamlet", ["Hamlet", "Notes on 'Hamlet'"]))
        entry = blog.resolve_wikilink("Hamlet", registry, fuzzy_lookup=lookup)
        self.assertEqual(entry["title"], "Notes on 'Hamlet'")

    def test_unique_substring(self) -> None:
        registry = make_registry(("Notes on 'Hamlet'", "/blog/hamlet", ["Hamlet"]))
        lookup = make_lookup(
            ("Notes on 'Hamlet'", "/blog/hamlet", ["Hamlet", "Notes on 'Hamlet'"])
        )
        entry = blog.resolve_wikilink("Hamlet", registry, fuzzy_lookup=lookup)
        self.assertIsNotNone(entry)

    def test_ambiguous_substring_returns_none(self) -> None:
        registry = make_registry(
            ("Learning one", "/learning/one", None),
            ("Learning two", "/learning/two", None),
        )
        lookup = make_lookup(
            ("Learning one", "/learning/one", ["Learning one"]),
            ("Learning two", "/learning/two", ["Learning two"]),
        )
        entry = blog.resolve_wikilink("learning", registry, fuzzy_lookup=lookup)
        self.assertIsNone(entry)

    def test_scored_disambiguation_prefers_hub(self) -> None:
        registry = make_registry(
            ("Philosophy", "/memex/philosophy", None),
            ("Notes on Philosophy", "/philosophy/notes", None),
        )
        lookup = make_lookup(
            ("Philosophy", "/memex/philosophy", ["Philosophy"]),
            (
                "Notes on Philosophy",
                "/philosophy/notes",
                ["Notes on Philosophy", "Philosophy"],
            ),
        )
        backlink_counts = {"/memex/philosophy": 25, "/philosophy/notes": 2}
        entry = blog.resolve_wikilink(
            "Philosophy",
            registry,
            fuzzy_lookup=lookup,
            backlink_counts=backlink_counts,
        )
        self.assertEqual(entry["url"], "/memex/philosophy")

    def test_normalize_quotes(self) -> None:
        registry = make_registry(("About Beauty", "/philosophy/beauty", None))
        lookup = make_lookup(("About Beauty", "/philosophy/beauty", ["About Beauty"]))
        entry = blog.resolve_wikilink("About Beauty", registry, fuzzy_lookup=lookup)
        self.assertIsNotNone(entry)

    def test_short_query_guard(self) -> None:
        registry = make_registry(
            ("On Writing", "/language/on-writing", None),
            ("On Reading", "/language/on-reading", None),
        )
        lookup = make_lookup(
            ("On Writing", "/language/on-writing", ["On Writing"]),
            ("On Reading", "/language/on-reading", ["On Reading"]),
        )
        entry = blog.resolve_wikilink("on", registry, fuzzy_lookup=lookup)
        self.assertIsNone(entry)

    def test_typo_near_miss(self) -> None:
        registry = make_registry(
            ("Notes on programing languages", "/tech/languages", None)
        )
        lookup = make_lookup(
            (
                "Notes on programing languages",
                "/tech/languages",
                ["Notes on programing languages", "programing languages"],
            )
        )
        entry = blog.resolve_wikilink(
            "programming languages",
            registry,
            fuzzy_lookup=lookup,
        )
        self.assertIsNotNone(entry)

    def test_candidates_on_ambiguity(self) -> None:
        registry = make_registry(
            ("Learning one", "/learning/one", None),
            ("Learning two", "/learning/two", None),
        )
        lookup = make_lookup(
            ("Learning one", "/learning/one", ["Learning one"]),
            ("Learning two", "/learning/two", ["Learning two"]),
        )
        candidates = blog.resolve_wikilink_candidates(
            "learning",
            registry,
            fuzzy_lookup=lookup,
        )
        self.assertGreaterEqual(len(candidates), 2)

    def test_normalize_wikilink_key(self) -> None:
        self.assertEqual(
            blog.normalize_wikilink_key("  !About Beauty  "),
            "about beauty",
        )


if __name__ == "__main__":
    unittest.main()
