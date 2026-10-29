# Maintenance guide

## Update the content

Edit the relevant file in `content/`:

| File | Content |
|---|---|
| `project.json` | Project overview and collaboration contact |
| `research.json` | Research directions and hypotheses |
| `history.json` | Previous project and research history |
| `people.json` | Team names, affiliations, profiles, and portraits |
| `datasets.json` | Dataset descriptions, coverage, and provider links |
| `updates.json` | News; the first entry appears on the home page |
| `publications.json` | Related publications and source links |
| `outputs.json` | Project achievements |

Use English text, stable IDs, and confirmed ISO dates; use `null` for unknown dates. Keep related publications separate from project achievements. Dataset descriptions link to original providers; raw research datasets are stored separately.

## Build and check

From the repository root, using Python 3.9 or later:

```bash
python scripts/build.py
python scripts/validate.py
python scripts/serve.py --port 8765
```

The build writes seven pages to `dist/`. Preview them at `http://127.0.0.1:8765` on the same computer, or open `dist/index.html` directly. Edit source files rather than generated HTML.

Optional browser checks require Playwright and Chromium:

```bash
python scripts/browser_check.py
```

## Export a preview

After building, `python scripts/package_review.py` validates the existing build and writes both `review/science-of-rules-local-preview.zip` and `review/science-of-rules-dashboard.html`. The dashboard embeds its images, styles, and scripts for offline viewing. `python scripts/export_dashboard.py` refreshes only the standalone HTML.

## Assets and repository

Store portraits in `assets/portraits/` and update `ASSET_SOURCES.json` when replacing an image. Layout and behavior live in `templates/base.html`, `assets/site.css`, `assets/site.js`, and `assets/dashboard.js`.

Generated previews, local review notes, and local environment files are excluded by `.gitignore`. The repository contains the site sources; hosting and automatic deployment are not configured.
