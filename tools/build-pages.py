#!/usr/bin/env python3
"""
Assemble the site's HTML pages from the shared partials.

The generated .html files are committed, so building is OPTIONAL — this exists
only so the header/footer live in one place instead of four.

    python3 tools/build-pages.py       # regenerate the four pages
    python3 tools/check-csp.py         # verify vercel.json's CSP hashes still match

Edit:
    tools/partials/head.html      <head>, masthead and nav (shared by every page)
    tools/partials/footer.html    footer and closing tags (shared by every page)
    tools/pages/<name>.body.html  the <main> content for one page

Placeholders used by head.html:
    %%TITLE%% %%DESC%% %%OGDESC%% %%PATH%% %%LDJSON%%
    %%C_HOME%% %%C_SOLUTIONS%% %%C_ABOUT%% %%C_CONTACT%%

Note: the inline JSON-LD block feeds the Content-Security-Policy hashes in
vercel.json. After changing any JSON-LD, run tools/check-csp.py and update the
hashes it prints.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SITE = "https://zzstudio.youngzyl.me"
EMAIL = "hello@zzstudio.youngzyl.me"

TAGLINE = "We help teams build AI that remembers, acts, and shows its work."


def org(**extra):
    base = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "zzstudio",
        "url": f"{SITE}/",
        "description": "AI solutions studio building hybrid context search vaults, "
                       "personal AI agents and skill management systems.",
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Taipei", "addressCountry": "TW"},
        "areaServed": "Worldwide",
        "knowsLanguage": ["en", "zh-Hant"],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Hybrid Context Search Vault"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Personal AI Agent"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Skill Management"}},
        ],
    }
    base.update(extra)
    return base


def page(kind, name, path):
    return {
        "@context": "https://schema.org",
        "@type": kind,
        "name": name,
        "url": f"{SITE}/{path}",
        "isPartOf": {"@type": "Organization", "name": "zzstudio", "url": f"{SITE}/"},
    }


PAGES = [
    (
        "index.html",
        {
            "title": "zzstudio — AI solutions studio in Taiwan",
            "desc": "zzstudio is a Taiwan-based AI solutions studio. We design, build and hand over "
                    "hybrid context vaults, personal AI agents and skill management systems for teams "
                    "that need AI to be trustworthy.",
            "ogdesc": TAGLINE,
            "path": "",
            "active": "C_HOME",
            "ldjson": org(),
        },
    ),
    (
        "solutions.html",
        {
            "title": "Solutions — zzstudio",
            "desc": "Hybrid context search vaults, personal AI agents, skill management and the "
                    "support model behind them.",
            "path": "solutions.html",
            "active": "C_SOLUTIONS",
            "ldjson": page("WebPage", "Solutions", "solutions.html"),
        },
    ),
    (
        "about.html",
        {
            "title": "Studio — zzstudio",
            "desc": "An applied AI studio in Taipei building context vaults, personal agents and "
                    "skill systems for teams that need AI to be accountable.",
            "path": "about.html",
            "active": "C_ABOUT",
            "ldjson": page("AboutPage", "Studio", "about.html"),
        },
    ),
    (
        "contact.html",
        {
            "title": "Contact — zzstudio",
            "desc": "Start a conversation with zzstudio about a hybrid retrieval vault, "
                    "a personal AI agent, or skill management.",
            "path": "contact.html",
            "active": "C_CONTACT",
            "ldjson": page("ContactPage", "Contact", "contact.html"),
        },
    ),
]

SLOTS = ("C_HOME", "C_SOLUTIONS", "C_ABOUT", "C_CONTACT")


def main() -> None:
    head = (TOOLS / "partials" / "head.html").read_text()
    footer = (TOOLS / "partials" / "footer.html").read_text()

    for name, meta in PAGES:
        doc = head
        values = {
            "TITLE": meta["title"],
            "DESC": meta["desc"],
            "OGDESC": meta.get("ogdesc", meta["desc"]),
            "PATH": meta["path"],
            "LDJSON": json.dumps(meta["ldjson"], indent=2, ensure_ascii=False),
        }
        for key, value in values.items():
            doc = doc.replace("%%" + key + "%%", value)
        for slot in SLOTS:
            doc = doc.replace("%%" + slot + "%%",
                              ' aria-current="page"' if slot == meta["active"] else "")

        leftovers = re.findall(r"%%[A-Z_]+%%", doc)
        if leftovers:
            raise SystemExit(f"{name}: unreplaced placeholders {sorted(set(leftovers))}")

        body = (TOOLS / "pages" / name.replace(".html", ".body.html")).read_text()
        out = doc.rstrip("\n") + "\n\n" + body.strip("\n") + "\n\n" + footer
        (ROOT / name).write_text(out)
        print(f"wrote {name} ({len(out):,} bytes)")


if __name__ == "__main__":
    main()
