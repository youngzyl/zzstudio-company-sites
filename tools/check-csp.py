#!/usr/bin/env python3
"""
Verify that the Content-Security-Policy hashes in vercel.json match the inline
<script> blocks actually present in the built pages.

Why this exists: the CSP allows the inline JSON-LD structured data by SHA-256
hash. A hash is computed over the script's exact text content — including the
newlines between the tags. So editing a page's copy *or* its JSON-LD silently
invalidates the hash and the browser stops applying the structured data, with no
visible symptom. This check turns that silent failure into a loud one.

    python3 tools/check-csp.py          # verify, exit 1 on drift
    python3 tools/check-csp.py --write  # update vercel.json in place
"""
import base64
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERCEL = ROOT / "vercel.json"

SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.S)
SRC_RE = re.compile(r"\bsrc\s*=", re.I)


def hashes_for(path: pathlib.Path) -> list[str]:
    """CSP sha256 hashes for every *inline* <script> in a document.

    Scripts with a src attribute are covered by 'self', not by a hash, and a
    script with no content would otherwise contribute the hash of the empty
    string (47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=), which is noise.
    The hash covers the content exactly as the browser sees it, including the
    leading and trailing newlines between the tags.
    """
    out = []
    for attrs, content in SCRIPT_RE.findall(path.read_text()):
        if SRC_RE.search(attrs):
            continue
        digest = hashlib.sha256(content.encode("utf-8")).digest()
        out.append("'sha256-" + base64.b64encode(digest).decode("ascii") + "'")
    return out


def main() -> None:
    write = "--write" in sys.argv

    pages = sorted(ROOT.glob("*.html"))
    found: list[str] = []
    for page in pages:
        for h in hashes_for(page):
            if h not in found:
                found.append(h)

    config = json.loads(VERCEL.read_text())
    csp_headers = [
        h for entry in config.get("headers", [])
        for h in entry.get("headers", [])
        if h["key"] == "Content-Security-Policy"
    ]
    if not csp_headers:
        raise SystemExit("vercel.json: no Content-Security-Policy header found")

    csp = csp_headers[0]["value"]
    directive = next((d for d in csp.split(";") if d.strip().startswith("script-src")), None)
    if directive is None:
        raise SystemExit("vercel.json: CSP has no script-src directive")

    declared = sorted(set(re.findall(r"'sha256-[A-Za-z0-9+/=]+'", directive)))
    expected = sorted(set(found))

    print(f"pages scanned      : {', '.join(p.name for p in pages)}")
    print(f"inline scripts     : {len(expected)} unique")
    for h in expected:
        print("  ", h)

    if declared == expected:
        print("\n✓ vercel.json CSP hashes match the built pages")
        return

    only_declared = [h for h in declared if h not in expected]
    only_pages = [h for h in expected if h not in declared]
    print("\n✗ CSP hash drift")
    for h in only_declared:
        print("   in vercel.json but not in any page :", h)
    for h in only_pages:
        print("   in a page but missing from CSP    :", h)

    if write:
        new_directive = re.sub(
            r"script-src[^;]*",
            "script-src 'self' " + " ".join(expected),
            directive,
        ).rstrip()
        new_csp = csp.replace(directive.strip(), new_directive)
        VERCEL.write_text(VERCEL.read_text().replace(csp, new_csp))
        print("\n→ vercel.json updated")
        return

    print("\nRun with --write to update vercel.json.")
    sys.exit(1)


if __name__ == "__main__":
    main()
