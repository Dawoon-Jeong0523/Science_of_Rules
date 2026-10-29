#!/usr/bin/env python3
"""Loopback-only preview. Never serve the surrounding research directory."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

root = Path(__file__).resolve().parents[1] / 'dist'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8765)
args = parser.parse_args()
if not (root/'index.html').is_file():
    parser.error('Run python scripts/build.py first.')
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
    print(f'Local preview: http://127.0.0.1:{args.port}', flush=True)
    print('Serving only dist/. Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
