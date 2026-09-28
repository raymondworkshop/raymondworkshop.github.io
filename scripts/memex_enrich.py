#!/usr/bin/env python3
"""Densify the memex graph across curated posts.

Wraps distinctive title mentions as [[wikilinks]] and adds related: edges to
other curated pages. Skips single-word apple-note stubs as link targets.

Usage:
  .venv/bin/python scripts/memex_enrich.py                 # dry-run
  .venv/bin/python scripts/memex_enrich.py --write
  .venv/bin/python scripts/memex_enrich.py --section learning --write
  .venv/bin/python scripts/memex_enrich.py --write --follow-symlinks
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import frontmatter

from blog_build.config import CJK_RE, NOTES_ON_TITLE, NOTES_ON_TITLE_PLAIN
from blog_build.posts import (
    collect_memex_sources,
    collect_post_aliases,
    get_topics,
    is_memex_hub_dir,
    is_memex_manifesto,
    memex_section_key,
)

# High-signal sections for graph densification (not dump folders).
CURATED_SECTIONS = {
    "",  # root posts
    "learning",
    "philosophy",
    "softskills",
    "self",
    "business",
    "notes",
    "new-notes",  # aliased onto notes; still curated book notes
    "research",
    "tech",
    "language",
    "course",
    "invest",
    "diary",
    "wiki",
    "blog",
}

NOISY_SECTIONS = {
    "origin-apple-notes",
    "new-apple-notes",
    "twitter",
}

# Never auto-link these common English tokens even if a page exists.
STOP_LABELS = {
    "notes",
    "self",
    "todo",
    "home",
    "post",
    "blog",
    "memex",
    "important",
    "everything",
    "experience",
    "expression",
    "creative",
    "business",
    "learning",
    "management",
    "leadership",
    "communication",
    "conversation",
    "relationship",
    "relationships",
    "negotiation",
    "emotions",
    "emotion",
    "health",
    "family",
    "families",
    "lifestyle",
    "reputation",
    "investment",
    "language",
    "listening",
    "softskills",
    "thinking",
    "writing",
    "reading",
    "work",
    "love",
    "life",
    "summary",
    "update",
    "weekly",
    "daily",
    "review",
}

CODE_FENCE_RE = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]+`")
EXISTING_WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]+\)")


@dataclass
class Page:
    path: pathlib.Path
    post: frontmatter.Post
    section: str
    title: str
    labels: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


@dataclass
class Change:
    path: pathlib.Path
    wikilinks: list[str] = field(default_factory=list)
    related_added: list[str] = field(default_factory=list)
    updated: str = ""


def clean_title(title: str) -> str:
    return title.strip().lstrip("!").strip()


def is_under_root(path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def label_variants(title: str, aliases: list[str]) -> list[str]:
    out: list[str] = []
    for raw in [title, clean_title(title), *aliases]:
        text = str(raw).strip()
        if not text:
            continue
        out.append(text)
        stripped = text.lstrip("!").strip()
        if stripped and stripped != text:
            out.append(stripped)
        notes = NOTES_ON_TITLE.match(stripped) or NOTES_ON_TITLE_PLAIN.match(stripped)
        if notes:
            inner = notes.group(1).strip().strip("'\"")
            if inner:
                out.append(inner)
    seen: set[str] = set()
    uniq: list[str] = []
    for label in sorted(out, key=len, reverse=True):
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(label)
    return uniq


def is_distinctive_label(label: str) -> bool:
    """Reject single common words / dates that pollute auto-linking."""
    if not label:
        return False
    key = label.lower().strip()
    if key in STOP_LABELS:
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", key):
        return False
    if CJK_RE.search(label):
        compact = re.sub(r"\s+", "", label)
        return len(compact) >= 4
    # Prefer multi-word titles, or long distinctive single tokens
    if " " in label or "-" in label or "'" in label or "’" in label:
        return len(label) >= 8
    return len(label) >= 18


def is_curated_target(page: Page) -> bool:
    if page.section in NOISY_SECTIONS:
        return False
    if page.section not in CURATED_SECTIONS and page.section:
        # unknown section: allow if title is distinctive
        return is_distinctive_label(clean_title(page.title))
    return is_distinctive_label(clean_title(page.title)) or " " in clean_title(page.title)


def mask_spans(text: str) -> tuple[str, list[str]]:
    vault: list[str] = []

    def stash(match: re.Match[str]) -> str:
        vault.append(match.group(0))
        return f"\0PROT{len(vault) - 1}\0"

    masked = CODE_FENCE_RE.sub(stash, text)
    masked = INLINE_CODE_RE.sub(stash, masked)
    masked = EXISTING_WIKILINK_RE.sub(stash, masked)
    masked = MD_LINK_RE.sub(stash, masked)
    return masked, vault


def unmask_spans(text: str, vault: list[str]) -> str:
    return re.sub(r"\0PROT(\d+)\0", lambda m: vault[int(m.group(1))], text)


def wrap_mentions(
    body: str,
    candidates: list[tuple[str, str]],
    *,
    self_title: str,
    max_links: int,
) -> tuple[str, list[str]]:
    masked, vault = mask_spans(body)
    linked: list[str] = []
    self_keys = {self_title.lower(), clean_title(self_title).lower()}

    for label, canonical in candidates:
        if len(linked) >= max_links:
            break
        if canonical.lower() in self_keys or clean_title(canonical).lower() in self_keys:
            continue
        if canonical in linked:
            continue

        if CJK_RE.search(label):
            regex = re.compile(re.escape(label))
        else:
            regex = re.compile(rf"(?<!\w){re.escape(label)}(?!\w)", re.IGNORECASE)

        match = regex.search(masked)
        if not match:
            continue

        display = match.group(0)
        if display == canonical or display.lower() == canonical.lower():
            replacement = f"[[{canonical}]]"
        else:
            replacement = f"[[{canonical}|{display}]]"

        masked = masked[: match.start()] + replacement + masked[match.end() :]
        linked.append(canonical)

    return unmask_spans(masked, vault), linked


def parse_related(post: frontmatter.Post) -> list[str]:
    values: list[str] = []
    for field_name in ("related", "seealso"):
        raw = post.get(field_name)
        if not raw:
            continue
        if isinstance(raw, str):
            values.append(raw.strip())
        else:
            values.extend(str(v).strip() for v in raw if str(v).strip())
    return list(dict.fromkeys(values))


def suggest_related(
    page: Page,
    by_section: dict[str, list[Page]],
    curated_pages: list[Page],
    newly_linked: list[str],
    *,
    max_related: int,
) -> list[str]:
    existing = {clean_title(t).lower() for t in parse_related(page.post)}
    existing.add(page.title.lower())
    existing.add(clean_title(page.title).lower())
    picks: list[str] = []

    def add(title: str) -> None:
        key = clean_title(title).lower()
        if key in existing:
            return
        if not is_distinctive_label(clean_title(title)) and " " not in clean_title(title):
            return
        existing.add(key)
        picks.append(title)

    for title in newly_linked:
        add(title)
        if len(picks) >= max_related:
            return picks

    my_topics = set(page.topics)
    # Prefer same-section curated peers, then other curated pages with shared tags
    candidates: list[tuple[int, str]] = []
    section_peers = [
        p for p in by_section.get(page.section, []) if is_curated_target(p)
    ]
    for peer in section_peers:
        if peer.path == page.path:
            continue
        score = 10 + len(my_topics & set(peer.topics)) * 3
        candidates.append((score, peer.title))

    if len(candidates) < max_related and my_topics:
        for peer in curated_pages:
            if peer.path == page.path or peer.section == page.section:
                continue
            overlap = len(my_topics & set(peer.topics))
            if overlap <= 0:
                continue
            candidates.append((overlap * 3, peer.title))

    candidates.sort(key=lambda item: (-item[0], item[1].lower()))
    for _score, title in candidates:
        add(title)
        if len(picks) >= max_related:
            break
    return picks


def patch_related_frontmatter(raw: str, related: list[str]) -> str:
    if not related or not raw.startswith("---"):
        return raw
    end = raw.find("\n---", 3)
    if end < 0:
        return raw
    fm = raw[3:end]
    body = raw[end + 4 :]
    if not fm.endswith("\n"):
        fm += "\n"

    fm = re.sub(
        r"^(related|seealso):\s*\[[^\]]*\]\s*\n",
        "",
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r"^(related|seealso):\s*\n(?:[ \t]*-[ \t].*\n)*",
        "",
        fm,
        flags=re.MULTILINE,
    )

    def yaml_item(title: str) -> str:
        if any(ch in title for ch in ":!#'\"[]{},"):
            escaped = title.replace('"', '\\"')
            return f'"{escaped}"'
        return title

    line = "related: [" + ", ".join(yaml_item(t) for t in related) + "]\n"
    if re.search(r"^title:\s*", fm, re.MULTILINE):
        fm = re.sub(r"^(title:\s*.*\n)", rf"\1{line}", fm, count=1, flags=re.MULTILINE)
    else:
        fm = line + fm
    if not fm.endswith("\n"):
        fm += "\n"
    return f"---{fm}---{body}"


def load_pages() -> list[Page]:
    pages: list[Page] = []
    for post, subdir, source in collect_memex_sources():
        if is_memex_manifesto(post, subdir) or is_memex_hub_dir(subdir):
            continue
        title = str(post.get("title") or "").strip()
        if not title:
            continue
        path = pathlib.Path(source)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        else:
            path = path.resolve()
        pages.append(
            Page(
                path=path,
                post=post,
                section=memex_section_key(subdir),
                title=title,
                labels=label_variants(title, collect_post_aliases(post)),
                topics=get_topics(post),
            )
        )
    return pages


def build_candidates(pages: list[Page]) -> list[tuple[str, str]]:
    label_owners: dict[str, set[str]] = defaultdict(set)
    label_display: dict[str, str] = {}
    title_for: dict[str, str] = {}
    for page in pages:
        if not is_curated_target(page):
            continue
        for label in page.labels:
            if not is_distinctive_label(label):
                continue
            key = label.lower()
            label_owners[key].add(page.title)
            label_display[key] = label
            title_for[key] = page.title

    candidates: list[tuple[str, str]] = []
    for key, owners in label_owners.items():
        if len(owners) != 1:
            continue
        candidates.append((label_display[key], title_for[key]))
    candidates.sort(key=lambda item: len(item[0]), reverse=True)
    return candidates


def enrich_page(
    page: Page,
    candidates: list[tuple[str, str]],
    by_section: dict[str, list[Page]],
    curated_pages: list[Page],
    *,
    max_links: int,
    max_related: int,
    link_body: bool,
    add_related: bool,
) -> Change | None:
    raw = page.path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return None
    end = raw.find("\n---", 3)
    if end < 0:
        return None

    fm_block = raw[: end + 4]
    file_body = raw[end + 4 :]
    body = page.post.content or ""
    # Normalize comparison against frontmatter's content
    body_from_file = file_body[1:] if file_body.startswith("\n") else file_body

    change = Change(path=page.path)
    new_body = body_from_file
    linked: list[str] = []

    if link_body and body_from_file.strip():
        new_body, linked = wrap_mentions(
            body_from_file,
            candidates,
            self_title=page.title,
            max_links=max_links,
        )
        change.wikilinks = linked

    final_related = parse_related(page.post)
    if add_related:
        suggested = suggest_related(
            page,
            by_section,
            curated_pages,
            linked,
            max_related=max_related,
        )
        existing_keys = {clean_title(t).lower() for t in final_related}
        related_new = [
            t for t in suggested if clean_title(t).lower() not in existing_keys
        ]
        change.related_added = related_new
        final_related = final_related + related_new

    if not change.wikilinks and not change.related_added:
        return None

    prefix = "\n" if file_body.startswith("\n") else ""
    updated = fm_block + prefix + new_body
    if raw.endswith("\n") and not updated.endswith("\n"):
        updated += "\n"

    if change.related_added:
        updated = patch_related_frontmatter(
            updated, final_related[: max(max_related, len(parse_related(page.post)))]
        )

    change.updated = updated
    return change


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--section", action="append", default=[])
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="allow writing files outside the myblog repo (e.g. symlinked notes)",
    )
    parser.add_argument("--max-links", type=int, default=6)
    parser.add_argument("--max-related", type=int, default=5)
    parser.add_argument("--no-body", action="store_true")
    parser.add_argument("--no-related", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    all_pages = load_pages()
    curated_pages = [p for p in all_pages if is_curated_target(p)]
    targets = curated_pages
    if args.section:
        want = set(args.section)
        targets = [p for p in curated_pages if p.section in want]

    candidates = build_candidates(all_pages)
    by_section: dict[str, list[Page]] = defaultdict(list)
    for p in all_pages:
        by_section[p.section].append(p)

    changes: list[Change] = []
    skipped_external = 0
    for page in targets:
        if not args.follow_symlinks and not is_under_root(page.path):
            skipped_external += 1
            continue
        change = enrich_page(
            page,
            candidates,
            by_section,
            curated_pages,
            max_links=args.max_links,
            max_related=args.max_related,
            link_body=not args.no_body,
            add_related=not args.no_related,
        )
        if not change:
            continue
        changes.append(change)
        if args.limit and len(changes) >= args.limit:
            break

    link_total = sum(len(c.wikilinks) for c in changes)
    related_total = sum(len(c.related_added) for c in changes)
    print(
        f"targets: {len(targets)} | change: {len(changes)} | "
        f"wikilinks+: {link_total} | related+: {related_total} | "
        f"skip-external: {skipped_external} | "
        f"mode: {'WRITE' if args.write else 'DRY-RUN'}"
    )

    show = changes if args.verbose else changes[:40]
    for change in show:
        try:
            rel = change.path.relative_to(ROOT)
        except ValueError:
            rel = change.path
        bits = []
        if change.wikilinks:
            bits.append("[[" + ", ".join(change.wikilinks[:5]) + "]]")
        if change.related_added:
            bits.append("related+ " + ", ".join(change.related_added[:5]))
        print(f"  {rel}: {'; '.join(bits)}")
    if not args.verbose and len(changes) > 40:
        print(f"  … and {len(changes) - 40} more (use -v)")

    if args.write:
        for change in changes:
            change.path.write_text(change.updated, encoding="utf-8")
        print(f"wrote {len(changes)} files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
