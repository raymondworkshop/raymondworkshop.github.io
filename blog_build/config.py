import pathlib
import re

SRCS = "./_posts/"
POSTS_PER_PAGE = 20

MEMEX_EXCLUDED_SECTIONS: set[str] = set()
MEMEX_HUB_DIR = pathlib.Path("memex")

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
HASHTAG_TAG_LINE = re.compile(r"^(?:#[^\s#]\S*\s*)+$", re.MULTILINE)
HASHTAG_TOKEN = re.compile(r"#[^\s#]\S*")

EXCLUDED_INDEX_TITLES = {
    "Slides",
    "About",
    "links",
    "invest",
    "docs",
    "ideas",
    "Projects",
    "Talks",
    "Bookshelf",
    "Coaching",
    "business",
    "Memex",
}

MEMEX_BUILD_STAMP = pathlib.Path("./docs/static/.memex-build-stamp")

CJK_RE = re.compile(r"[\u3040-\u9fff\uff00-\uffef]")

NOTES_ON_TITLE = re.compile(
    r"^notes on ['\"](.+?)['\"]?\s*$", re.IGNORECASE
)
NOTES_ON_TITLE_PLAIN = re.compile(r"^notes on (.+)$", re.IGNORECASE)
DATED_STEM_SUFFIX = re.compile(r"^(.+)-\d{4}-\d{2}-\d{2}$")

QUOTE_CHARS = "'\"'\"“”‘’"
FUZZY_MIN_SCORE = 50
FUZZY_SCORE_GAP = 15
SHORT_QUERY_MAX_LEN = 2
