#!/usr/bin/env python3
"""Strip Apple Notes attachment placeholders and normalize front-matter spacing."""

import re
import sys
from pathlib import Path

OBJ = "\ufffc"
NOTE_RE = re.compile(r"^(---\nTitle:.*?\n---)\n(.*)\Z", re.DOTALL)


def clean_body(body: str) -> str:
    body = body.replace(OBJ, "")
    body = re.sub(r"^[ \t]+$", "", body, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip("\n")


def clean_export(text: str) -> str:
    parts = re.split(r"(?=^---\nTitle:)", text, flags=re.MULTILINE)
    blocks = []

    for part in parts:
        if not part:
            continue
        match = NOTE_RE.match(part)
        if not match:
            blocks.append(part)
            continue
        header, body = match.group(1), clean_body(match.group(2))
        blocks.append(f"{header}\n\n{body}\n\n")

    return "".join(blocks).rstrip("\n") + "\n"


def main() -> None:
    path = Path(sys.argv[1])
    path.write_text(clean_export(path.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
