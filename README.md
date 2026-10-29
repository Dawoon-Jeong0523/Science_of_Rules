# Science of Rules website

Source code and assets for reproducing the **Science of Rules** website, presenting the 2026 SNU Grand Quest project *Toward a Science of Rules: Can AI Change the Dynamics of Their Evolution?*

All page content, templates, styles, scripts, and portraits required to build the website are included in this repository. The build uses **Python 3.9+ and its standard library**; no additional packages or research datasets are required.

## Reproduce the website

```bash
git clone https://github.com/Dawoon-Jeong0523/Science_of_Rules.git
cd Science_of_Rules
python3 scripts/build.py
python3 scripts/validate.py
python3 scripts/serve.py --port 8765
```

Open <http://127.0.0.1:8765> on the computer running the server, or open `dist/index.html` directly.

The build creates seven pages in `dist/`: Home, Project, Research, People, Updates, Data, and Achievements. This directory is the complete static website and can be served by a static web server.

## Source files

| Path | Contents |
|---|---|
| `content/` | JSON content for the project, research, people, updates, publications, and data catalog |
| `assets/` | CSS, JavaScript, icons, and portraits |
| `templates/` | Shared page template |
| `scripts/` | Build, validation, preview, and export tools |
| `ASSET_SOURCES.json` | Image sources and provenance |
| `docs/MAINTENANCE.md` | Content editing and maintenance instructions |

Edit these source files, then rebuild and validate. Generated `dist/` and `review/` files are excluded from Git and recreated from the tracked sources.

## Create a portable copy

After building, run:

```bash
python3 scripts/package_review.py
```

This writes a ZIP of the website to `review/science-of-rules-local-preview.zip` and a standalone HTML copy with embedded assets to `review/science-of-rules-dashboard.html`.

Optional browser checks use `python3 scripts/browser_check.py` and additionally require Playwright and Chromium. The collaboration form prepares an email draft for the visitor to review and send. Hosting and automatic deployment are not configured.
