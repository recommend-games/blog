#!/usr/bin/env python3
"""
Append Internet Archive (Wayback) links next to external markdown links.

Preserves originals and adds:  [🗄️](https://web.archive.org/web/<encoded-url>)
which redirects to the latest snapshot (see IA redirect behaviour).

Skips: fenced code blocks, image links, web.archive.org, *.recommend.games.
Idempotent: does not add a second 🗄️ if already present after the link.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

# Hostnames we treat as stable / first-party (no archive companion).
SKIP_HOST_SUFFIXES = (".recommend.games",)
SKIP_HOSTS = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "boardgamegeek.com",
        "www.boardgamegeek.com",
        "recommend.games",
        "www.recommend.games",
        "github.com",
        "www.github.com",
        "gitlab.com",
        "www.gitlab.com",
        "de.wikipedia.org",
        "en.wikipedia.org",
    }
)

MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\((https?://[^)\s]+)\)")


def wayback_wrap(url: str) -> str:
    return "https://web.archive.org/web/" + quote(url, safe=":/=?#[]@!$&'()*+,;")


def should_skip(url: str) -> bool:
    if "web.archive.org" in url:
        return True
    host = (urlparse(url).hostname or "").lower()
    if host in SKIP_HOSTS:
        return True
    return any(host.endswith(sfx) for sfx in SKIP_HOST_SUFFIXES)


def already_has_archive_after(text: str, closing_paren_idx: int) -> bool:
    """Check text right after `)` of the markdown link."""
    rest = text[closing_paren_idx + 1 : closing_paren_idx + 48].lstrip()
    return rest.startswith("[🗄️](")


def process_outside_code(segment: str) -> tuple[str, int]:
    out = []
    last = 0
    replacements = 0
    for m in MD_LINK_RE.finditer(segment):
        url = m.group(2)
        start, end = m.span()
        out.append(segment[last:start])
        out.append(segment[start:end])
        if not should_skip(url) and not already_has_archive_after(segment, end - 1):
            out.append(f" [🗄️]({wayback_wrap(url)})")
            replacements += 1
        last = end
    out.append(segment[last:])
    return "".join(out), replacements


def split_code_fences(text: str) -> list[tuple[bool, str]]:
    """Returns list of (is_code, chunk) alternating."""
    fence_re = re.compile(r"^```[^\n]*\n.*?^```", re.MULTILINE | re.DOTALL)
    parts: list[tuple[bool, str]] = []
    pos = 0
    for m in fence_re.finditer(text):
        if m.start() > pos:
            parts.append((False, text[pos : m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    if pos < len(text):
        parts.append((False, text[pos:]))
    return parts


def process_file(path: Path) -> int:
    raw = path.read_text(encoding="utf-8")
    total_r = 0
    new_chunks = []
    for is_code, chunk in split_code_fences(raw):
        if is_code:
            new_chunks.append(chunk)
            continue
        chunk2, r = process_outside_code(chunk)
        total_r += r
        new_chunks.append(chunk2)
    new_raw = "".join(new_chunks)
    if new_raw != raw:
        path.write_text(new_raw, encoding="utf-8")
    return total_r


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    content = root / "content"
    if not content.is_dir():
        print("content/ not found", file=sys.stderr)
        sys.exit(1)
    grand = 0
    for md in sorted(content.rglob("*.md")):
        n = process_file(md)
        if n:
            print(f"{md.relative_to(root)}: +{n} archive link(s)")
            grand += n
    print(f"Done. {grand} archive link(s) added total.")


if __name__ == "__main__":
    main()
