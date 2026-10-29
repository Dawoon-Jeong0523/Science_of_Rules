#!/usr/bin/env python3
"""Check the generated site's content, local navigation, and portable assets."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
from build import ALIASES, NAV

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
FEATURED_PUBLICATIONS = {
    'us-legal-code-dataset', 'function-diversity-scaling', 'common-law-ages',
    'reddit-regulation', 'generative-function-growth',
}
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Element:
    def __init__(self, tag, attributes):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.text = []

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()

    def with_class(self, name):
        return [node for node in self.descendants()
                if name in node.attributes.get('class', '').split()]

    def readable_text(self):
        return ' '.join(''.join(self.text).split())


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1s = 0
        self.active = 0
        self.lang = None
        self.root = Element('document', {})
        self.stack = [self.root]
        self.text = self.root.text

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        node = Element(tag, attributes)
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)
        if tag == 'html':
            self.lang = attributes.get('lang')
        if tag == 'h1':
            self.h1s += 1
        if attributes.get('aria-current') == 'page':
            self.active += 1
        if 'id' in attributes:
            assert attributes['id'] not in self.ids, f'Duplicate ID: {attributes["id"]}'
            self.ids.add(attributes['id'])
        if tag == 'img':
            assert 'alt' in attributes, 'Missing image alternative text'
        for key in ('href', 'src'):
            if key in attributes:
                self.links.append(attributes[key])

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, value):
        for node in self.stack:
            node.text.append(value)


def read_content(name):
    return json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf-8'))


def check_research(page):
    publications = read_content('publications')
    assert len(publications) == 7, 'Retain all seven existing publications'
    assert 'publications' in page.ids, 'Research needs its stable publications anchor'
    cards = page.root.with_class('publication-entry')
    ids = [card.attributes.get('id') for card in cards]
    assert set(ids) == {paper['id'] for paper in publications} and len(ids) == len(publications)
    assert set(ids[:5]) == FEATURED_PUBLICATIONS, 'The five requested studies must appear first'
    for paper in publications:
        card = next(card for card in cards if card.attributes.get('id') == paper['id'])
        text = card.readable_text()
        assert paper['title'] in text and paper.get('summary') and paper['summary'] in text, paper['id']
        links = {node.attributes.get('href') for node in card.descendants() if node.tag == 'a'}
        assert paper['url'] in links, f'Missing publication link: {paper["id"]}'
        for link in paper.get('links', []):
            assert link['url'] in links, f'Missing publication version link: {paper["id"]}'
        figure = paper.get('figure')
        if figure:
            images = [node for node in card.descendants() if node.tag == 'img']
            assert any(node.attributes.get('src') == figure['src'] and
                       node.attributes.get('alt', '').strip() for node in images), paper['id']
            path = (ROOT/figure['src']).resolve()
            assert path.is_relative_to((ROOT/'assets/research').resolve()) and path.is_file(), paper['id']
            assert figure.get('source_url') and figure.get('caption'), f'Missing figure provenance: {paper["id"]}'
        else:
            placeholders = card.with_class('figure-todo')
            assert placeholders and any('TODO' in node.readable_text() for node in placeholders), paper['id']
    return len(publications)


def check_people(page):
    people = read_content('people')
    assert all(person['name'] for person in people)
    assert len({person['id'] for person in people}) == len(people)
    grids = page.root.with_class('researcher-grid')
    assert len(grids) == 1, 'Use one shared researcher roster'
    cards = grids[0].with_class('person-card')
    assert len(cards) == len(people)
    assert len(page.root.with_class('person-card')) == len(cards)
    assert {card.attributes.get('id') for card in cards} == {person['id'] for person in people}
    expected_portraits = {person['photo'] for person in people if person.get('photo')}
    for directory in (ROOT/'assets/portraits', DIST/'assets/portraits'):
        actual_portraits = {path.relative_to(directory).as_posix()
                            for path in directory.rglob('*') if path.is_file()}
        assert actual_portraits == expected_portraits, (
            f'Portrait files must match the current roster in {directory.relative_to(ROOT)}: '
            f'missing={sorted(expected_portraits-actual_portraits)}, '
            f'unused={sorted(actual_portraits-expected_portraits)}'
        )
    text = page.root.readable_text()
    for person in people:
        assert person['name'] in text, person['id']
        card = next(card for card in cards if card.attributes.get('id') == person['id'])
        image_sources = [node.attributes.get('src') for node in card.descendants() if node.tag == 'img']
        expected_images = ['assets/portraits/'+person['photo']] if person.get('photo') else []
        assert image_sources == expected_images, f'Portrait does not match the current roster: {person["id"]}'
    assert 'Vicky Chuqiao Yang' in text and re.search(r'Chris(?:topher(?: P\.)?)? Kempes', text)
    assert not re.search(r'Principal Investigator|Participating Researchers?|Research Assistants?', text, re.I)
    return len(people)


def check_news(page):
    lists = page.root.with_class('news-list')
    assert len(lists) == 1
    entries = lists[0].with_class('news-entry')
    assert entries, 'News cannot be empty'
    dated = []
    undated_seen = False
    for entry in entries:
        summaries = entry.with_class('news-summary')
        assert len(summaries) == 1 and summaries[0].readable_text(), 'News needs a concise summary'
        links = [node.attributes.get('href') for node in entry.descendants() if node.tag == 'a']
        assert any(link and link != '#' for link in links), 'News needs a source or detail link'
        times = [node for node in entry.descendants() if node.tag == 'time']
        if times:
            assert not undated_seen, 'Place undated items after the dated chronology'
            dated.append(date.fromisoformat(times[0].attributes['datetime']))
        else:
            undated_seen = True
            placeholders = entry.with_class('news-date-todo')
            assert placeholders and any('TODO' in node.readable_text() for node in placeholders), 'Unknown dates need an explicit TODO'
    assert dated == sorted(dated, reverse=True), 'News must be newest first'
    ids = {entry.attributes.get('id') for entry in entries}
    for publication in read_content('publications'):
        assert 'news-'+publication['id'] in ids, publication['id']
        if publication.get('revised'):
            assert 'news-'+publication['id']+'-revision' in ids, publication['id']
    return len(entries)


def main():
    expected_nav = [('index', 'Home'), ('project', 'Project'), ('research', 'Research'),
                    ('people', 'People'), ('news', 'News'), ('data', 'Data')]
    assert NAV == expected_nav, 'Navigation must expose the six current sections'
    assert ALIASES == {'updates': 'news', 'outputs': 'news'}
    files = sorted(DIST.glob('*.html'))
    assert {path.stem for path in files} == {slug for slug, _ in NAV} | set(ALIASES)
    pages = {}
    for path in files:
        raw = path.read_text(encoding='utf-8')
        assert '{{' not in raw, f'Unrendered template in {path.name}'
        assert not re.search(r'/project/|/home/|source_document|\.docx|local_path|localhost', raw), f'Internal reference in {path.name}'
        parsed = Page()
        parsed.feed(raw)
        assert parsed.lang == 'en' and parsed.h1s == 1 and parsed.active == 1, path.name
        text = parsed.root.readable_text()
        assert not re.search(r'[가-힣]', text), f'Non-English text in {path.name}'
        assert not re.search(r'six[\s-]month|6[\s-]month', text, re.I), f'Stale project duration in {path.name}'
        navigation = [node for node in parsed.root.descendants()
                      if node.tag == 'nav' and node.attributes.get('aria-label') == 'Main navigation']
        assert len(navigation) == 1, path.name
        nav_links = [node for node in navigation[0].descendants() if node.tag == 'a']
        assert [node.readable_text() for node in nav_links] == [label for _, label in NAV], path.name
        active = [node for node in nav_links if node.attributes.get('aria-current') == 'page']
        assert active[0].attributes['href'] == ALIASES.get(path.stem, path.stem)+'.html', path.name
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
            target = (source.parent/unquote(parsed.path)).resolve() if parsed.path else source
            assert target.is_relative_to(DIST.resolve()), f'Link leaves static bundle: {href}'
            assert target.is_file(), f'Missing file: {href} from {source.name}'
            if parsed.fragment:
                assert target in pages and unquote(parsed.fragment) in pages[target].ids, f'Missing anchor: {href}'
            checked += 1
    publications = check_research(pages[(DIST/'research.html').resolve()])
    people = check_people(pages[(DIST/'people.html').resolve()])
    news = check_news(pages[(DIST/'news.html').resolve()])
    for alias in ALIASES:
        assert check_news(pages[(DIST/f'{alias}.html').resolve()]) == news
    assert not list(DIST.rglob('*.json')), 'Source content should not be copied into the public bundle'
    for path in DIST.rglob('*'):
        if path.is_file():
            assert path.suffix in ('.html', '.css', '.js', '.svg', '.jpg', '.png', '.webp', ''), f'Unexpected public file: {path}'
            assert path.stat().st_size < 2_000_000, f'Unexpected large public asset: {path}'
    print(f'PASS: {len(NAV)} English pages + {len(ALIASES)} compatibility pages; '
          f'{checked} local links/assets; {people} researchers; {publications} publications; '
          f'{news} news entries; public-file boundary.')


if __name__ == '__main__':
    main()
