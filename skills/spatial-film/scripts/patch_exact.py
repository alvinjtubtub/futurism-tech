"""Exact find/replace across files, safe on CRLF files. Every search string must match exactly once.

Use when several files need scripted exact-string edits (the Edit tool is still first choice for a
few). A plain Python replace silently fails on CRLF files, because the search strings in a script
are LF (BOVault 2026-09-25: preload.cjs was CRLF, the patch asserted and the batch stopped halfway).
This normalises to LF, replaces, then restores the file's own line endings.

    import sys; sys.path.insert(0, "<skill>/scripts")
    from patch_exact import patch
    patch("compositions/s02-workflows.html", [("old text", "new text")])

Write the calling script with the Write tool (never a heredoc: search strings often hold backslashes).

Re-runnable: a pair whose `old` is gone but whose (non-empty) `new` is already there counts as applied
and is skipped, so after one file's pair fails you fix that pair and rerun the WHOLE script (files
patched earlier in the run are not re-patched). Each file is all-or-nothing. On a miss it says when the
text would match with indentation ignored - copy the indentation from a Read of the file, never guess
it (PortfolioV2 2026-10-02: a 6-space guess where the file had 4).
"""


def _flat(s):
    return "\n".join(line.strip() for line in s.split("\n"))


def patch(path, pairs):
    with open(path, encoding="utf8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    for old, new in pairs:
        count = text.count(old)
        if count == 0 and new and new in text:
            print(f"{path}: already applied, skipped: {old[:60]!r}")
            continue
        if count != 1:
            hint = " (matches if indentation is ignored: copy it from the file)" if count == 0 and _flat(old) in _flat(text) else ""
            raise SystemExit(f"{path}: expected 1 match, found {count}{hint}: {old[:80]!r}")
        text = text.replace(old, new)
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf8", newline="") as f:
        f.write(text)


def cut(path, start, end):
    """Remove a block: from the start of `start` up to (not including) `end`. Both markers must match
    exactly once, `end` after `start`. Deletes a function or section without pasting its whole body as
    a search string (an agent once hand-wrapped this)."""
    with open(path, encoding="utf8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    for marker in (start, end):
        count = text.count(marker)
        if count != 1:
            raise SystemExit(f"{path}: expected 1 match, found {count}: {marker[:80]!r}")
    a, b = text.index(start), text.index(end)
    if b <= a:
        raise SystemExit(f"{path}: end marker comes before the start marker")
    text = text[:a] + text[b:]
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf8", newline="") as f:
        f.write(text)
