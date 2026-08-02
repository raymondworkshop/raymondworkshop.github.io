---
name: memex
description: >-
  Build and extend the myblog memex wiki — wikilinks, backlinks, hubs, tags,
  and related-page panels. Use when editing memex posts, adding cross-links,
  or changing blog.py memex behavior.
---

# Memex skill

Personal wiki woven through this static blog. Links create backlinks at build
time. Entry: `_posts/memex.md` → `/memex.html`.

## Mental model

- **Manifesto** — `_posts/memex.md` → `/memex.html`
- **Hubs** — `_posts/memex/*.md` with `section:` → `/memex/{area}`
- **Pages** — `_posts/{section}/…`
- **Backlinks** — build-time; “Linked from (N)” on each page

```bash
python3 blog.py --fast         # incremental (default)
python3 blog.py --memex        # full site + wiki
python3 blog.py --memex-only   # wiki/backlinks only
# make run | run-memex | memex-build
```

## CLI (`memex.py`)

```bash
python3 memex.py stats|missing|orphans|top -n 15|search <q>
python3 memex.py resolve|page|backlinks|outgoing "<title>"
# make memex CMD="stats"
```

## Linking

```markdown
[[Philosophy]]
[[Hamlet]]                       # unique substring OK
[[Learning|how I learn things]]  # display text
#insight #learning               # hashtag-only line → linked tags
[About Beauty](/philosophy/…)   # internal URL → upgraded to wikilink
```

```yaml
tags: [learning, notes]
related: [About Beauty, Self]    # also: seealso
aliases: [成為自由人, a-free-man] # also: aka
```

Unresolved `[[…]]` → dashed `wikilink-missing`. Fix title or add alias.

### Backlink sources

`[[wikilink]]` · internal `[text](url)` · hashtag-only lines ·
`tags`/`categories`/`topics` · section dir → hub · `related`/`seealso`.
Deduped per source→target.

### Title resolution

Registered keys: slug, lowercase title, file stem (± date), derived aliases
(`Notes on 'Hamlet'` → `Hamlet`), leading `!` stripped, `aliases`/`aka`.

1. **Exact** — normalized + OpenCC CJK variants
2. **Fuzzy** — scored (exact > prefix/word > substring; shorter / more
   backlinks tie-break). Needs ≥15 pt margin; ≤2 chars need exact/prefix;
   else `difflib` typo hint (0.88)
3. Debug: `memex.py resolve` / `missing`

**Unlinked mentions** (prose names a page without `[[…]]`) appear in UI /
`memex.py mentions` but do **not** create backlinks.

## Wiki UI

`templates/memex.html`: Links to · Linked from · Mentioned but not linked ·
Related in {Area} · See also · (hubs) Referenced across memex · All pages.
Manifesto: search, hubs. Index: `/memex/index.html`.

## New area

1. Hub `_posts/memex/my-area.md` with `section: my-area` matching `_posts/my-area/`
2. Seed with `[[links]]` / “Start here”
3. `python3 blog.py`; link hub from `_posts/memex.md`

## Enriching the graph

Prefer `[[wikilinks]]` · hub maps (5–15 anchors) · consistent `tags` ·
`related:` for strong ties · `aliases:` for short names · keep hashtag
lines · check `wikilink-missing` after rebuild.

## Key files

| Path | Role |
|------|------|
| `blog.py` / `blog_build/fast.py` | entry · incremental build |
| `blog_build/memex/{resolve,links,graph,queries}.py` | resolver · links · graph · panels |
| `blog_build/{posts,writer}.py` | parse · HTML/search |
| `memex.py` · `test_memex_resolve.py` | CLI · tests |
| `templates/memex{,_manifesto,_index}.html` | wiki UI |
| `_posts/memex.md` · `_posts/memex/*.md` | manifesto · hubs |

## Excluded

`MEMEX_EXCLUDED_SECTIONS` in `blog_build/config.py` — skip wiki preprocess,
templates, graph, search, A–Z (plain HTML still built). Current: `diary`,
`learning`, `new-apple-notes`, `origin-apple-notes`, `invest`, `self`.

## Agent checklist

1. Read target posts + `_posts/memex/` hubs
2. Add `[[wikilinks]]` / `tags` / `related` / `aliases` (not bare mentions)
3. Update hub “Start here” / “Related areas” when adding key pages
4. Rebuild and spot-check backlinks
5. Prefer unique short aliases over ambiguous fuzzy targets
