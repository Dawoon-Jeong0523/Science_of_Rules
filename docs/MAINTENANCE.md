# Maintenance guide

## Update the content

Edit the relevant file in `content/`:

| File | Content |
|---|---|
| `project.json` | Ongoing project overview, Grand Quest and NSF context, and collaboration contact |
| `research.json` | Research directions and hypotheses |
| `research_sources.json` | Publication and figure provenance, versions, licenses, and asset checksums |
| `history.json` | Previous project and research history |
| `people.json` | One shared researcher roster: names, affiliations, profiles, and portraits |
| `people_sources.json` | Verified roster sources and verification dates |
| `datasets.json` | Dataset descriptions, coverage, and provider links |
| `updates.json` | Dated announcements and events for News, with source links |
| `publications.json` | Seven research publications: summaries, figures, source links, posting/revision dates, and featured order |
| `outputs.json` | Legacy output records retained in source; the former Achievements page now opens News |

Use English text and stable IDs. Describe the project as an ongoing collaboration; do not restore the former six-month framing. Keep researchers in one roster without separate investigator, participating-researcher, or assistant sections. Confirm identity and current affiliation against the recorded sources before changing a profile.

News combines `updates.json` with publication posting and revision dates, sorted newest first. Use confirmed `YYYY-MM-DD` dates; use `null` plus an explicit TODO note for unknown dates. An event's announcement date is not automatically its award or start date. Provide a concise summary and a source or detail link for each item. Unknown-date entries appear after dated news; do not invent dates to position them.

Research retains all seven publication IDs and the `research.html#publications` anchor. The five featured studies cover the US legal-code dataset, function-diversity scaling, common-law aging, Reddit, and generative function growth. Each publication needs a summary, article/preprint links, and either a local figure with attribution or an explicit `figure_todo`. Preserve journal and preprint links where both are available. Dataset descriptions link to original providers; raw research datasets are stored separately.

## Build and check

From the repository root, using Python 3.9 or later:

```bash
python scripts/build.py
python scripts/validate.py
python scripts/serve.py --port 8765
```

The build writes six main pages to `dist/`: Home, Project, Research, People, News, and Data. Two compatibility files, `outputs.html` and `updates.html`, also display News. Preview at `http://127.0.0.1:8765` on the same computer, or open `dist/index.html` directly. Edit source files rather than generated HTML.

Validation checks the six navigation labels, compatibility pages, local links, publication cards and figure placeholders, roster membership, News chronology, and the public-file boundary. The optional browser check covers desktop/mobile layouts, navigation, filters, proposal drafts, downloads, and offline viewing.

Optional browser checks require Playwright and Chromium:

```bash
python scripts/browser_check.py
```

## Export a preview

After building, `python scripts/package_review.py` validates the existing build and writes both `review/science-of-rules-local-preview.zip` and `review/science-of-rules-dashboard.html`. The dashboard embeds images, styles, and scripts for offline viewing and contains the six main sections. The `#publications` and `#propose` anchors open the appropriate section. `python scripts/export_dashboard.py` refreshes only the standalone HTML. Build and package before running browser checks.

## Assets and repository

Store portraits in `assets/portraits/` and original paper figures in `assets/research/`. A publication's `figure` object records `src`, `alt`, `label`, `source_url`, and `caption`; retain additional source-asset URL, credit, license, and version metadata when available. Update `ASSET_SOURCES.json` when adding or replacing images. Keep required images local so both the static folder and standalone export work offline.

Never substitute an invented chart for an unavailable paper figure. Use `figure: null` with a clear `figure_todo` until the original asset and its source can be confirmed. Layout and behavior live in `templates/base.html`, `assets/site.css`, `assets/site.js`, and `assets/dashboard.js`.

Generated previews, local review notes, and local environment files are excluded by `.gitignore`. The repository contains the site sources; hosting and automatic deployment are not configured.
