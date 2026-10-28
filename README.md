# Science of Rules

Research website for **Toward a Science of Rules: Can AI Change the Dynamics of Their Evolution?**, a 2026 SNU Grand Quest project.

Seven pages present the project, research agenda, team, updates, data catalog, and achievements. JSON content is rendered into a static HTML/CSS/JavaScript website.

## Run locally

Requires **Python 3.9+**. Building and basic validation use only the Python standard library.

```bash
python scripts/build.py
python scripts/validate.py
python scripts/serve.py --port 8765
```

Open <http://127.0.0.1:8765>, or open `dist/index.html` directly.

## Structure

| Path | Contents |
|---|---|
| `content/` | Project, research, people, updates, publications, and dataset descriptions |
| `assets/` | CSS, JavaScript, icons, and portraits |
| `templates/` | Shared page template |
| `scripts/` | Build, validation, preview, and export tools |
| `ASSET_SOURCES.json` | Image sources and provenance |
| `docs/MAINTENANCE.md` | Detailed maintenance guide |

Edit `content/*.json`, then rebuild and validate. Generated `dist/` and `review/` files are excluded from Git; research datasets are maintained separately.

## Share a preview

After building, run `python scripts/package_review.py` to create a standalone HTML dashboard and a ZIP of the website in `review/`.

Optional browser checks: `python scripts/browser_check.py` (requires Playwright and Chromium).

The collaboration form prepares an email draft for the visitor to review and send. Hosting and automatic deployment are not configured.
