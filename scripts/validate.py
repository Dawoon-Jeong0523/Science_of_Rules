#!/usr/bin/env python3
"""Check the generated site's content boundary and all local navigation/assets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
from build import NAV

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1s = 0
        self.active = 0
        self.lang = None
        self.text = []

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1s += 1
        if a.get('aria-current') == 'page': self.active += 1
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'img':
            assert 'alt' in a, 'Missing image alternative text'
        for key in ('href', 'src'):
            if key in a: self.links.append(a[key])

    def handle_data(self, value):
        self.text.append(value)


def main():
    files = sorted(DIST.glob('*.html'))
    assert {p.stem for p in files} == {slug for slug, _ in NAV}
    pages = {}
    for path in files:
        raw = path.read_text()
        assert '{{' not in raw, f'Unrendered template in {path.name}'
        assert not re.search(r'/project/|/home/|source_document|\.docx|local_path|localhost', raw), f'Internal reference in {path.name}'
        parsed = Page()
        parsed.feed(raw)
        assert parsed.lang == 'en', path.name
        assert parsed.h1s == 1, path.name
        assert parsed.active == 1, path.name
        assert not re.search(r'[가-힣]', ''.join(parsed.text)), f'Non-English text in {path.name}'
        pages[path.resolve()] = parsed
    checked = 0
    for source, page in pages.items():
        for href in page.links:
            parsed = urlsplit(href)
            if parsed.scheme:
                assert parsed.scheme in ('https', 'http', 'mailto'), f'Invalid URL scheme: {href}'
                continue
            assert not parsed.netloc, f'Unexpected protocol-relative URL: {href}'
            assert not parsed.path.startswith('/'), f'Root-relative link breaks offline/subpath preview: {href}'
            target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
            assert target.is_relative_to(DIST.resolve()), f'Link leaves static bundle: {href}'
            assert target.is_file(), f'Missing file: {href} from {source.name}'
            if parsed.fragment:
                assert target in pages and unquote(parsed.fragment) in pages[target].ids, f'Missing anchor: {href}'
            checked += 1
    people = json.loads((ROOT/'content/people.json').read_text())
    assert len(people) == 8
    assert all(p['name'] for p in people)
    assert len({p['id'] for p in people}) == len(people)
    assert not list(DIST.rglob('*.json')), 'Source content should not be copied into the public bundle'
    for path in DIST.rglob('*'):
        if path.is_file():
            assert path.suffix in ('.html','.css','.js','.svg','.jpg','.png','.webp',''), f'Unexpected public file: {path}'
            assert path.stat().st_size < 2_000_000, f'Unexpected large public asset: {path}'
    print(f'PASS: {len(files)} English pages; {checked} local links/assets; 8 named team members; public-file boundary.')


if __name__ == '__main__':
    main()
