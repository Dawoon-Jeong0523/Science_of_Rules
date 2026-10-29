#!/usr/bin/env python3
"""Export the public pages and their assets into one portable HTML review file."""
from base64 import b64encode
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import mimetypes
import re
from build import NAV
from validate import main as validate

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
ROUTES = {f'{slug}.html': ('home' if slug == 'index' else slug) for slug, _ in NAV}


class EmbedAssets(HTMLParser):
    """Rewrite generated public markup; never read outside the static bundle."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.ids = set()
        self.fragments = []
        self.asset_cache = {}

    def asset_uri(self, source):
        parts = urlsplit(source)
        if parts.scheme or parts.netloc or parts.query or parts.fragment:
            raise ValueError(f'Expected a local static asset: {source}')
        path = (DIST/unquote(parts.path)).resolve()
        if not path.is_relative_to(DIST.resolve()) or not path.is_file():
            raise ValueError(f'Invalid public asset: {source}')
        if path not in self.asset_cache:
            mime = {'.webp':'image/webp', '.svg':'image/svg+xml', '.jpg':'image/jpeg',
                    '.jpeg':'image/jpeg', '.png':'image/png'}.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]
            if not mime or not mime.startswith('image/'):
                raise ValueError(f'Expected an image: {source}')
            self.asset_cache[path] = f'data:{mime};base64,'+b64encode(path.read_bytes()).decode('ascii')
        return self.asset_cache[path]

    def tag(self, tag, attributes, closing=False):
        a = dict(attributes)
        if 'id' in a:
            if a['id'] in self.ids:
                raise ValueError(f'Duplicate ID across views: {a["id"]}')
            self.ids.add(a['id'])
        if tag in ('iframe', 'object', 'embed') or 'srcset' in a:
            raise ValueError(f'Unsupported embedded resource: {tag}')
        if 'src' in a:
            if tag != 'img':
                raise ValueError(f'Unexpected external resource: {tag}')
            a['src'] = self.asset_uri(a['src'])
        if tag == 'link':
            if a.get('rel') != 'icon':
                raise ValueError('Stylesheets must be inlined before export')
            a['href'] = self.asset_uri(a['href'])
        elif 'href' in a:
            parts = urlsplit(a['href'])
            if parts.scheme in ('https', 'http', 'mailto'):
                if tag == 'a' and parts.scheme != 'mailto':
                    a.update(target='_blank', rel='noopener noreferrer')
            elif parts.scheme or parts.netloc or parts.query:
                raise ValueError(f'Unsupported link: {a["href"]}')
            elif parts.path:
                if parts.path.startswith('assets/'):
                    a['href'] = self.asset_uri(a['href'])
                elif parts.path in ROUTES:
                    a['href'] = '#'+(parts.fragment or 'view-'+ROUTES[parts.path])
                else:
                    raise ValueError(f'Unexpected file link: {a["href"]}')
            if a['href'].startswith('#'):
                self.fragments.append(unquote(a['href'][1:]))
        attrs = ''.join(' '+key if value is None else f' {key}="{escape(value, quote=True)}"' for key,value in a.items())
        self.output.append(f'<{tag}{attrs}{" /" if closing else ""}>')

    def handle_starttag(self, tag, attrs): self.tag(tag, attrs)
    def handle_startendtag(self, tag, attrs): self.tag(tag, attrs, True)
    def handle_endtag(self, tag): self.output.append(f'</{tag}>')
    def handle_data(self, data): self.output.append(data)
    def handle_entityref(self, name): self.output.append('&'+name+';')
    def handle_charref(self, name): self.output.append('&#'+name+';')
    def handle_decl(self, decl): self.output.append('<!'+decl+'>')
    def handle_comment(self, data): self.output.append('<!--'+data+'-->')


def export_dashboard():
    main_pattern = re.compile(r'<main id="main">(.*?)</main>', re.S)
    sections = []
    for slug, label in NAV:
        raw = (DIST/f'{slug}.html').read_text(encoding='utf-8')
        matches = main_pattern.findall(raw)
        if len(matches) != 1:
            raise ValueError(f'Expected one main element in {slug}')
        route = ROUTES[slug+'.html']
        sections.append(f'<section id="view-{route}" data-view="{route}" data-label="{label}" aria-label="{label}">{matches[0]}</section>')
    shell = (DIST/'index.html').read_text(encoding='utf-8')
    shell = main_pattern.sub(lambda _: '<main id="main">'+''.join(sections)+'</main>', shell, count=1)
    css = (DIST/'assets/site.css').read_text(encoding='utf-8')
    if re.search(r'@import|url\s*\(', css, re.I):
        raise ValueError('CSS has resources that need embedding')
    shell = shell.replace('<link rel="stylesheet" href="assets/site.css">', '<style>'+css+'</style>')
    shell = shell.replace('<script src="assets/site.js" defer></script>', '')
    shell = re.sub(r'<title>.*?</title>', '<title>Science of Rules — Local review</title>', shell, count=1)
    shell = shell.replace('<span>Research · People · Shared knowledge</span>', '<span>Local review copy · Profile and source links open online</span>')
    shell = shell.replace('</head>', '<noscript><style>[data-view]{display:block!important}.main-nav{display:flex!important}</style></noscript></head>')

    parser = EmbedAssets()
    parser.feed(shell)
    missing = set(parser.fragments)-parser.ids
    if missing:
        raise ValueError(f'Missing internal anchors: {sorted(missing)}')
    html = ''.join(parser.output)
    scripts = [(DIST/'assets/site.js').read_text(encoding='utf-8'), (ROOT/'assets/dashboard.js').read_text(encoding='utf-8')]
    if any('</script' in js.lower() for js in scripts):
        raise ValueError('Unexpected script closing tag in source')
    # Inline defer does not defer execution: initialize only after the full DOM.
    inline = '\n'.join('<script>\n'+js+'\n</script>' for js in scripts)
    html = html.replace('</body>',inline+'\n</body>')
    if re.search(r'/project/|/home/|source_document|\.docx|local_path',html):
        raise ValueError('Unexpected internal reference in review artifact')
    destination = ROOT/'review/science-of-rules-dashboard.html'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(html, encoding='utf-8')
    print(f'Created {destination} ({destination.stat().st_size:,} bytes; {len(sections)} views; {len(parser.asset_cache)} embedded image assets)')
    return destination


if __name__ == '__main__':
    validate()
    export_dashboard()
