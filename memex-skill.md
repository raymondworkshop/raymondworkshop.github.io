---
name: memex
description: >-
  Build and extend the myblog memex wiki — wikilinks, backlinks, hubs, tags,
  and related-page panels. Use when editing memex posts, adding cross-links,
  or changing blog.py memex behavior.
---

# Memex skill

The memex is a personal wiki woven through this static blog. Pages link to each
other; every link creates a backlink on the target. Start at `_posts/memex.md`
(`/memex.html`) and follow links in any direction.

## Mental model

- **Manifesto** — `_posts/memex.md` → `/memex.html` (entry maze, search, hub list)
- **Hubs** — `_posts/memex/*.md` with `section:` → `/memex/{area}` (area maps)
- **Pages** — everything else under `_posts/{section}/` (notes, diary, blog, …)
- **Backlinks** — computed at build time; shown as “Linked from (N)” on each page

Rebuild after link changes:

```bash
python3 blog.py --memex-only   # wiki/backlinks only (~2 min)
python3 blog.py --memex        # full site + wiki
python3 blog.py                # fast HTML only (no wikilink resolve)

# Makefile shortcuts:
make run           # fast HTML
make run-memex     # full build
make memex-build   # wiki/backlinks only
```

## Memex CLI (`memex.py`)

Inspect links without rebuilding the site:

```bash
python3 memex.py stats
python3 memex.py resolve "Hamlet"
python3 memex.py page "About Beauty"
python3 memex.py backlinks Learning
python3 memex.py outgoing "Notes on Stoicism"
python3 memex.py missing          # unresolved [[wikilinks]]
python3 memex.py orphans          # pages with zero backlinks
python3 memex.py top -n 15        # most-linked pages
python3 memex.py search philosophy

# via Makefile:
make memex CMD="stats"
make memex CMD="missing"
make memex CMD='mentions "About Beauty"'
```

## Linking syntax

### Wikilinks (preferred)

```markdown
[[Philosophy]]
[[About Beauty]]
[[Hamlet]]                          # resolves if unique substring match
[[Notes on '成為自由人]]              # full or partial title
[[Learning|how I learn things]]     # custom display text
```

Unresolved targets render as dashed `wikilink-missing` spans — fix the title or
add an alias.

### Hashtag lines (Apple Notes style)

A line that is only hashtags becomes linked tags:

```markdown
#insight #learning
```

Hashtags resolve against page titles, stems, and hub names (e.g. `#learning`
→ Learning hub).

### Markdown internal links

```markdown
[About Beauty](/philosophy/about-beauty-2020-06-10)
```

Internal paths are upgraded to wikilinks when the URL matches a known page.

### Frontmatter links

```yaml
tags: [learning, notes]       # links to matching hubs / topics
related: [About Beauty, Self] # explicit wiki neighbors (outgoing + backlink)
aliases: [成為自由人, a-free-man] # extra wikilink targets for this page
```

Supported alias fields: `aliases`, `aka`.

## What creates backlinks automatically

| Source | Example |
|--------|---------|
| `[[wikilink]]` in body | `[[Philosophy]]` on any page |
| Internal `[text](url)` | hub cross-links in memex manifesto |
| Hashtag-only lines | `#insight` in origin-apple-notes |
| `tags` / `categories` / `topics` | `tags: [learning]` → Learning hub |
| Section directory | every `_posts/diary/*.md` → Diary hub |
| `related` / `seealso` frontmatter | explicit neighbor edges |

Backlinks are deduplicated per source→target pair.

## Title resolution rules

`blog.py` registers each page under:

- slugified title (`about-beauty`)
- lowercase full title
- file stem (and stem without date suffix)
- derived aliases (`Notes on 'Hamlet'` → `Hamlet`)
- leading `!` stripped (`!Improving your judgment skills`)
- frontmatter `aliases` / `aka`

**Exact match** tries normalized keys (lowercase, collapsed whitespace, stripped
quotes) plus OpenCC simplified/traditional variants for CJK text.

**Fuzzy match** searches titles, aliases, and stems with scored disambiguation:

| Signal | Effect |
|--------|--------|
| Normalized exact equality | highest score |
| Prefix match | strong |
| Whole-word match | strong |
| Substring match | moderate |
| Shorter label / more backlinks | tie-break |

A fuzzy hit resolves only when the top score beats the runner-up by a clear
margin (default 15 points). Targets ≤ 2 characters require exact or prefix
match only. If still unresolved, `difflib` typo matching may suggest one close
label (cutoff 0.88).

Debug resolution:

```bash
python3 memex.py resolve "Hamlet"      # shows candidates when ambiguous
python3 memex.py missing             # includes "did you mean" hints
```

**Unlinked mentions** — prose in a note that names another page title/alias but
has no `[[wikilink]]` yet. Shown in the “Mentioned but not linked” panel and via
`memex.py mentions`. These do **not** create backlinks until you add a wikilink.

## Wiki UI panels

Every memex page (`templates/memex.html`) can show:

| Panel | Meaning |
|-------|---------|
| **Links to** | outgoing wikilinks, tags, section hub, `related` |
| **Linked from (N)** | backlinks from other pages |
| **Mentioned but not linked** | other pages named in prose without `[[wikilink]]` |
| **Related in {Area}** | same-section pages you link to / that link to you |
| **See also** | other pages sharing `tags` / `categories` / `topics` |
| **Referenced across memex** | (hubs) pages in this area with inbound links |
| **All pages in {Area}** | (hubs) full section index |

Manifesto (`templates/memex_manifesto.html`) adds search, hub cards, and
“Most linked across memex”.

Full A–Z index with backlink counts: `/memex/index.html`.

## Adding a new area

1. Create hub `_posts/memex/my-area.md`:

```yaml
---
title: My Area
date: 2026-06-14
section: my-area
---
Intro text with [[links]] to seed pages.

### Start here
[[Some existing page]] · [[Another page]]
```

2. Add posts under `_posts/my-area/` (or link from other sections).
3. Run `python3 blog.py`.
4. Link the hub from `_posts/memex.md` under “Start anywhere” or body text.

`section:` in the hub frontmatter must match the `_posts/{section}/` directory
name for auto hub↔page links.

## Enriching the link graph

When editing or importing notes:

1. **Prefer wikilinks** over bare mentions — `[[Stoicism]]` not just “stoicism”.
2. **Use hub pages** as maps — list 5–15 anchor pages per area in `_posts/memex/*.md`.
3. **Tag consistently** — `tags: [learning, notes]` ties pages to hubs.
4. **Add `related:`** for strong pairwise ties the body does not spell out.
5. **Add `aliases:`** for short names (`成為自由人`, `hamlet`, `stoicism`).
6. **Hashtag exports** — keep Apple Notes tag lines; they become links on rebuild.
7. **Check missing links** — rebuild and look for `wikilink-missing` in HTML.

## Key files

| File | Role |
|------|------|
| `blog.py` | registry, resolve, backlinks, related/see-also, unlinked mentions |
| `memex.py` | CLI: resolve, missing, mentions, stats |
| `test_memex_resolve.py` | resolver unit tests |
| `templates/memex.html` | per-page wiki panels |
| `templates/memex_manifesto.html` | memex home |
| `templates/memex_index.html` | full index sorted by backlinks |
| `docs/static/search-index.json` | lunr search (`backlink_count` field) |
| `_posts/memex.md` | manifesto source |
| `_posts/memex/*.md` | area hubs |

## Excluded from memex

`MEMEX_EXCLUDED_SECTIONS` in `blog.py` (currently empty). Paths listed there
skip wikilink preprocessing and memex templates.

## Agent checklist

When asked to make memex “wiki” or “backlink”:

1. Read target posts and hub maps under `_posts/memex/`.
2. Add `[[wikilinks]]`, `tags`, `related`, or `aliases` — not just prose mentions.
3. Update hub “Start here” / “Related areas” lists when adding important pages.
4. Run `python3 blog.py` and spot-check backlinks on the built HTML.
5. Prefer unique short aliases over ambiguous fuzzy targets.
