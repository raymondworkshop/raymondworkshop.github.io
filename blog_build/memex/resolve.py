import difflib
import pathlib
import re
from typing import Sequence

import frontmatter

from blog_build.config import (
    CJK_RE,
    FUZZY_MIN_SCORE,
    FUZZY_SCORE_GAP,
    QUOTE_CHARS,
    SHORT_QUERY_MAX_LEN,
)
from blog_build.memex import state
from blog_build.posts import (
    collect_post_aliases,
    get_hub_url,
    get_post_stem,
    get_post_url,
    get_static_link,
    is_memex_hub_dir,
    is_memex_manifesto,
)
from blog_build.search import expand_for_search


def register_wikilink_target(
    registry: dict[str, dict[str, str]],
    title: str,
    url: str,
    *,
    stem: str | None = None,
    aliases: Sequence[str] | None = None,
) -> None:
    entry = {"url": url, "title": title}
    registry[get_static_link(title)] = entry
    registry[title.lower().strip()] = entry
    if stem:
        registry[stem.lower().strip()] = entry
    for alias in aliases or ():
        alias = alias.strip()
        if alias:
            registry[alias.lower()] = entry
            registry[get_static_link(alias)] = entry


def normalize_wikilink_key(text: str) -> str:
    text = text.strip().lstrip("!").strip()
    text = text.strip(QUOTE_CHARS)
    text = re.sub(r"\s+", " ", text).lower()
    return text


def wikilink_key_variants(text: str) -> list[str]:
    base = normalize_wikilink_key(text)
    if not base:
        return []
    variants = [base]
    if CJK_RE.search(base):
        for line in expand_for_search(base).split("\n"):
            line = line.strip().lower()
            if line and line not in variants:
                variants.append(line)
    return variants


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


def build_fuzzy_lookup(
    sources: Sequence[tuple[frontmatter.Post, pathlib.Path, pathlib.Path]],
) -> list[tuple[str, dict[str, str]]]:
    from blog_build.config import DATED_STEM_SUFFIX

    seen: set[tuple[str, str]] = set()
    lookup: list[tuple[str, dict[str, str]]] = []

    for post, subdir, _source in sources:
        if is_memex_manifesto(post, subdir):
            entry = {"url": "/memex.html", "title": post["title"]}
            labels = [str(post["title"])]
        elif is_memex_hub_dir(subdir):
            entry = {"url": get_hub_url(post), "title": post["title"]}
            labels = [str(post["title"])]
            if post.get("section"):
                labels.append(str(post["section"]))
        else:
            entry = {"url": get_post_url(post, subdir), "title": post["title"]}
            labels = [str(post["title"]), *collect_post_aliases(post)]
            stem = get_post_stem(post, subdir)
            labels.append(stem)
            dated_match = DATED_STEM_SUFFIX.match(stem)
            if dated_match:
                labels.append(dated_match.group(1))

        for label in labels:
            label = str(label).strip()
            if not label:
                continue
            dedupe_key = (normalize_wikilink_key(label), entry["url"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            lookup.append((label, entry))
    return lookup


def build_title_lookup(
    registry: dict[str, dict[str, str]],
) -> list[tuple[str, dict[str, str]]]:
    seen_urls: set[str] = set()
    lookup: list[tuple[str, dict[str, str]]] = []
    for entry in registry.values():
        url = entry["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        lookup.append((entry["title"], entry))
    return lookup


def _has_word_boundary_match(query: str, label: str) -> bool:
    query_norm = normalize_wikilink_key(query)
    label_norm = normalize_wikilink_key(label)
    if not query_norm or not label_norm:
        return False
    if CJK_RE.search(query_norm) or CJK_RE.search(label_norm):
        return any(variant in label_norm for variant in wikilink_key_variants(query))
    pattern = r"(?<!\w)" + re.escape(query_norm) + r"(?!\w)"
    return bool(re.search(pattern, label_norm))


def score_fuzzy_match(
    query: str,
    label: str,
    *,
    backlink_count: int = 0,
) -> int:
    query_norm = normalize_wikilink_key(query)
    label_norm = normalize_wikilink_key(label)
    if not query_norm or not label_norm:
        return 0

    query_variants = wikilink_key_variants(query)
    label_variants = wikilink_key_variants(label)
    if any(q == l for q in query_variants for l in label_variants):
        score = 100
    elif len(query_norm) <= SHORT_QUERY_MAX_LEN:
        if any(l.startswith(q) for q in query_variants for l in label_variants):
            score = 80
        else:
            return 0
    elif any(l.startswith(q) for q in query_variants for l in label_variants):
        ratio = len(query_norm) / max(len(label_norm), 1)
        score = 80 + int(ratio * 10)
    elif _has_word_boundary_match(query, label):
        score = 70
    elif any(q in l for q in query_variants for l in label_variants):
        ratio = len(query_norm) / max(len(label_norm), 1)
        score = 50 + int(ratio * 20)
    else:
        return 0

    score += max(0, 10 - min(len(label_norm), 10))
    score += min(backlink_count, 20)
    return score


def resolve_wikilink_candidates(
    target: str,
    registry: dict[str, dict[str, str]],
    *,
    fuzzy_lookup: list[tuple[str, dict[str, str]]] | None = None,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
    backlink_counts: dict[str, int] | None = None,
    min_score: int = FUZZY_MIN_SCORE,
    return_all: bool = False,
) -> list[tuple[dict[str, str], int, str]]:
    lookup = fuzzy_lookup if fuzzy_lookup is not None else title_lookup
    backlink_counts = backlink_counts or {}

    for variant in wikilink_key_variants(target):
        if variant in registry:
            entry = registry[variant]
            return [(entry, 100, variant)]
        slug = get_static_link(variant)
        if slug and slug in registry:
            entry = registry[slug]
            return [(entry, 100, slug)]

    key = target.strip()
    for candidate in (key, key.lstrip("!").strip()):
        if candidate.lower() in registry:
            entry = registry[candidate.lower()]
            return [(entry, 100, candidate)]
        slug = get_static_link(candidate)
        if slug in registry:
            entry = registry[slug]
            return [(entry, 100, slug)]

    if not lookup:
        return []

    best_by_url: dict[str, tuple[dict[str, str], int, str]] = {}
    for label, entry in lookup:
        url = normalize_memex_url(entry["url"])
        score = score_fuzzy_match(
            target,
            label,
            backlink_count=backlink_counts.get(url, 0),
        )
        if score < min_score:
            continue
        current = best_by_url.get(url)
        if current is None or score > current[1]:
            best_by_url[url] = (entry, score, label)

    ranked = sorted(
        best_by_url.values(),
        key=lambda item: (-item[1], item[0]["title"].lower()),
    )
    if not ranked:
        normalized_labels = {
            normalize_wikilink_key(label): (label, entry)
            for label, entry in lookup
            if normalize_wikilink_key(label)
        }
        query_norm = normalize_wikilink_key(target)
        if query_norm:
            close = difflib.get_close_matches(
                query_norm,
                list(normalized_labels.keys()),
                n=3,
                cutoff=0.88,
            )
            typo_hits = [normalized_labels[key] for key in close]
            if len(typo_hits) == 1:
                label, entry = typo_hits[0]
                return [(entry, 45, label)]
        return []

    if return_all:
        return ranked

    top_entry, top_score, top_label = ranked[0]
    if len(ranked) == 1:
        return [(top_entry, top_score, top_label)]

    runner_up_score = ranked[1][1]
    if top_score - runner_up_score >= FUZZY_SCORE_GAP:
        return [(top_entry, top_score, top_label)]
    return ranked


def resolve_wikilink(
    target: str,
    registry: dict[str, dict[str, str]],
    *,
    fuzzy_lookup: list[tuple[str, dict[str, str]]] | None = None,
    title_lookup: list[tuple[str, dict[str, str]]] | None = None,
    backlink_counts: dict[str, int] | None = None,
) -> dict[str, str] | None:
    ctx = state.get_ctx()
    if backlink_counts is None and ctx.get("backlink_counts"):
        backlink_counts = ctx["backlink_counts"]
    candidates = resolve_wikilink_candidates(
        target,
        registry,
        fuzzy_lookup=fuzzy_lookup,
        title_lookup=title_lookup,
        backlink_counts=backlink_counts,
    )
    if not candidates:
        return None
    top_entry, top_score, _label = candidates[0]
    if len(candidates) == 1:
        return top_entry
    if top_score - candidates[1][1] >= FUZZY_SCORE_GAP:
        return top_entry
    return None
