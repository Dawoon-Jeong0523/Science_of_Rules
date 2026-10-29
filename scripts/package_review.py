#!/usr/bin/env python3
"""Package only the validated static site for offline colleague review."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from validate import main as validate
from export_dashboard import export_dashboard

root=Path(__file__).resolve().parents[1]
validate()
(root/'review').mkdir(exist_ok=True)
destination=root/'review/science-of-rules-local-preview.zip'
with ZipFile(destination,'w',ZIP_DEFLATED) as archive:
    for path in sorted((root/'dist').rglob('*')):
        if path.is_file():
            archive.write(path,path.relative_to(root/'dist'))
print(f'Created {destination} ({destination.stat().st_size:,} bytes)')
export_dashboard()
