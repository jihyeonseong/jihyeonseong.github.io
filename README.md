# jihyeonseong.github.io

Personal website of **Jihyeon Seong**, Ph.D. student in Artificial Intelligence at KAIST.

**→ [jihyeonseong.github.io](https://jihyeonseong.github.io)**

- [CV](https://jihyeonseong.github.io/cv/) · [Publications](https://jihyeonseong.github.io/publications/) · [Blog](https://jihyeonseong.github.io/blog/) — study notes and papers I read

## Where things live

| What | File |
| --- | --- |
| Site settings, socials, SEO | `_config.yml`, `_data/socials.yml` |
| About page | `_pages/about.md` |
| CV page | `_data/cv.yml` |
| CV PDF | `assets/pdf/cv.pdf` (built from a separate LaTeX source) |
| Publications | `_bibliography/papers.bib` |
| Repositories page | `_data/repositories.yml` |
| Blog posts | `_posts/YYYY-MM-DD-title.md` — template in `_drafts/` |
| EN/KO post toggle, per-language comments | `_includes/post_lang_toggle.liquid`, `_includes/giscus_by_lang.liquid` |

## Bilingual posts

A post can hold both English and Korean in one file. Wrap each language in
`<div class="lang-en" markdown="1">` / `<div class="lang-ko" markdown="1">`
(set `title_ko` for the Korean title). An EN/KO toggle appears next to the theme
toggle. Comments are split by language: EN shows the English thread, KO shows the
Korean thread and the English thread.

## Run locally

```bash
docker compose up
```

Then open <http://localhost:8080>. Edits rebuild automatically.

## Deploy

Pushing to `main` runs the `Deploy site` workflow, which builds the site and publishes it to the `gh-pages` branch. GitHub Pages serves `gh-pages`.

## Credits

Built with [al-folio](https://github.com/alshedivat/al-folio) (v1.2). The theme code is under the MIT License — see [`LICENSE`](LICENSE). Site content is © Jihyeon Seong.
