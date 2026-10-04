# zzstudio — company website

Static marketing site for **zzstudio**, an applied AI solutions studio in Taipei,
Taiwan. Describes three offerings — hybrid context search vaults, personal AI
agents, and skill management — plus the studio's support model.

**Live:** https://zzstudio.youngzyl.me

No build step. No dependencies. No CDN. No framework. Just HTML, CSS and a small
progressive-enhancement script, so it deploys unchanged to GitHub Pages or Vercel.

---

## Files

| Path | What it is |
| --- | --- |
| `index.html` | Home — hero, three offerings, capabilities, process, Taiwan, CTA |
| `solutions.html` | Deep detail on the three offerings + four engagement shapes |
| `about.html` | Studio story, six principles, Taiwan, careers/partnership |
| `contact.html` | Direct lines, enquiry form, FAQ |
| `404.html` | Not-found page, self-styled so it survives being served from a deep URL |
| `styles.css` | The entire design system (tokens → components → motion) |
| `main.js` | Theme toggle, mobile nav, scroll reveals, form → `mailto:` |
| `og.png` | 1200×630 social preview card (source: `tools/og.svg`) |
| `vercel.json` | Clean URLs, cache policy, security headers incl. a hashed CSP |
| `CNAME` | Custom domain for GitHub Pages |
| `.nojekyll` | Tells GitHub Pages to serve the files as-is |
| `robots.txt`, `sitemap.xml` | Crawling and indexing |
| `.vercelignore` | Keeps build templates off public URLs on Vercel |
| `tools/` | Optional page generator, CSP checker, and the Actions workflow variant |

The four pages share a header and footer. Those live in exactly one place, in
`tools/partials/`, and the checked-in `.html` files are generated from them.

---

## Local preview

Any static server works:

```bash
python3 -m http.server 8000     # → http://localhost:8000
```

Opening `index.html` straight from the filesystem also works.

---

## Deploy

### GitHub Pages

The site is published straight from the `main` branch — no build step, so no CI
is required.

1. Push to `main`.
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   then choose branch `main` and folder `/ (root)`.
3. The site is live at `https://youngzyl.github.io/zzstudio-company-sites/`
   within a minute or so.

`.nojekyll` is present, so GitHub serves the files as-is instead of running them
through Jekyll. `CNAME` already contains `zzstudio.youngzyl.me`, so the custom
domain is picked up from the repository.

With that file present, GitHub Pages serves the site at the custom domain once
DNS points at it:

| Type | Name | Value |
| --- | --- | --- |
| `A` | `zzstudio` | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| `CNAME` | `www.zzstudio` | `youngzyl.github.io` |

(or an `AAAA`/`CNAME` equivalent — see GitHub's “Managing a custom domain”).
Then tick **Enforce HTTPS**.

> To use the default `youngzyl.github.io/zzstudio-company-sites` URL instead of
the custom domain, delete `CNAME` and replace `https://zzstudio.youngzyl.me`
> with that URL in `tools/build-pages.py`, `robots.txt` and `sitemap.xml`, then
> re-run the generator.

#### Optional: deploy via GitHub Actions

Branch deployment publishes everything in the repository, including `tools/` and
this README. `tools/deploy-pages.workflow.yml` is a ready-to-use workflow that
stages only the runtime files, so build templates never reach a public URL.

Adding a workflow file requires the `workflow` OAuth scope, so it is kept out of
the way until you opt in:

```bash
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
git mv tools/deploy-pages.workflow.yml .github/workflows/deploy-pages.yml
git commit -m "deploy via GitHub Actions" && git push
```

Then set **Settings → Pages → Source: GitHub Actions**. (Don't do both: the two
modes conflict.)

### Vercel

```bash
npx vercel --prod        # or import the repo at vercel.com/new
```

No framework preset, no build command, output directory is the repository root.
Vercel picks up `vercel.json` (clean URLs, caching, security headers), so
`/solutions.html` is also reachable as `/solutions`. Add the custom domain under
**Project → Settings → Domains**.

---

## Editing content

Change the shared chrome once, then regenerate:

```bash
python3 tools/build-pages.py
```

| Edit this | To change |
| --- | --- |
| `tools/partials/head.html` | `<head>`, meta tags, masthead, primary nav |
| `tools/partials/footer.html` | Footer columns and fine print |
| `tools/pages/<name>.body.html` | The `<main>` content of one page |

Page titles, descriptions, canonical URLs and JSON-LD live in the `PAGES` table
at the top of `tools/build-pages.py`.

Editing the generated `.html` files directly also works — just remember the
header/footer appear in all four.

### Regenerating the social card

```bash
inkscape tools/og.svg --export-type=png --export-filename=og.png \
  --export-width=1200 --export-height=630
```

---

## Design system

Warm editorial, in the spirit of Anthropic's site and the
[linuxdo-ai-feed](https://youngzyl.github.io/linuxdo-ai-feed/) layout: ivory
paper, one clay accent, hairline rules instead of heavy cards, serif display
type over a sans body, and no external font requests.

Tokens live at the top of `styles.css`:

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--paper` | `#faf9f5` | `#141312` | Page background |
| `--paper-2` | `#f2f0e9` | `#1b1918` | Panels, figures |
| `--ink` | `#191817` | `#ece7de` | Body text |
| `--muted` | `#6d675e` | `#9b938a` | Secondary text |
| `--rule` | `#e2ded3` | `#302d28` | Hairlines |
| `--clay` | `#b8532f` | `#e2a07a` | Single accent |

Type is a system stack — Iowan Old Style / Palatino / Songti SC for display,
the platform UI font for body, and `ui-monospace` for labels and citations.
Spacing uses one scale (`--s1`…`--s9`, 4px → 104px) for every margin, gap and
padding.

Dark mode follows `prefers-color-scheme` and can be overridden by the header
toggle, which persists to `localStorage`.

---

## Before going live

- **Email.** `hello@zzstudio.youngzyl.me` is used in the footer, contact page,
  404 page, the enquiry form and the JSON-LD. Create the mailbox or replace it:

  ```bash
  grep -rl 'hello@zzstudio.youngzyl.me' --include='*.html' --include='*.js' . \
    | xargs sed -i 's|hello@zzstudio.youngzyl.me|you@example.com|g'
  ```

  Also update `EMAIL` in `tools/build-pages.py`.

- **GitHub link.** The footer points at `https://github.com/`; set the real org.

- **JSON-LD → CSP.** If you edit any page's structured data, the CSP hashes in
  `vercel.json` go stale (silently — only the browser's structured-data
  extraction stops working). Re-check and fix with:

  ```bash
  python3 tools/check-csp.py          # verify
  python3 tools/check-csp.py --write  # update vercel.json
  ```

  GitHub Pages ignores `vercel.json` entirely and sends no CSP, so this only
  affects the Vercel deployment.

---

## What was verified

Checked with headless Chromium against the built site:

- **Layout** — hero is two columns ≥980px, sticky header pins at scroll, no
  horizontal overflow at 1440px or 390px, diagram text renders ≥11px.
- **Contrast (WCAG AA/AAA)** — light: ink 16.8:1, muted 5.3:1, clay 4.6:1.
  Dark: ink 15.1:1, muted 6.1:1, clay 8.4:1.
- **Accessibility** — one `<h1>` per page, skip link, visible focus rings,
  every link has text or an `aria-label`, `aria-expanded` on the nav toggle,
  no standalone tap target under 32px, 44px primary buttons, keyboard-closable
  mobile menu, `prefers-reduced-motion` honoured.
- **Behaviour** — theme toggle flips and persists, scroll reveals resolve to
  visible, mobile menu opens/closes and closes on navigation, active nav item is
  correct per page, the enquiry form builds a well-formed `mailto:` carrying
  name/email/topic/brief and exposes it as a clickable fallback.
- **Integrity** — all four pages parse without unclosed tags, no duplicate IDs,
  no broken internal links or asset references, no console or network errors,
  CSP hashes match the inline scripts, OG image text fits inside 1200×630 with
  no overlaps.
