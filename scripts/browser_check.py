#!/usr/bin/env python3
"""Optional browser QA. Requires Playwright; no runtime site dependencies.

Proposal checks inspect generated mailto links without opening them or sending email.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import parse_qs, quote, urlsplit
import json
import shutil
from playwright.sync_api import sync_playwright
from build import NAV

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/'review'
REVIEW.mkdir(exist_ok=True)
RECIPIENT = json.loads((ROOT/'content/project.json').read_text())['proposals']['email']
PAGES = [slug for slug, _ in NAV]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def no_overflow(page, label):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow: {label}'
    assert page.locator('[data-proposal-form]').evaluate('''form =>
      [form, ...form.querySelectorAll('input, textarea, button')].every(element => {
        const rect = element.getBoundingClientRect();
        return !rect.width || (rect.left >= 0 && rect.right <= innerWidth + 1);
      })'''), f'Form field outside viewport: {label}'


def fill_proposal(page, values):
    for key, value in values.items():
        page.locator(f'[data-proposal-form] [name="{key}"]').fill(value)


def expected_draft(values):
    subject = '[Science of Rules] '+values['title']
    body = '\r\n'.join([
        'Hello Science of Rules team,', '', values['summary'], '',
        'Name: '+values['name'], 'Reply email: '+values['email'],
        *(['Affiliation: '+values['affiliation']] if values['affiliation'] else [])
    ])
    return subject, body, f'To: {RECIPIENT}\r\nSubject: {subject}\r\n\r\n{body}'


def assert_download(page, expected, mode):
    with page.expect_download() as pending:
        page.locator('[data-download-proposal]').click()
    download = pending.value
    assert download.failure() is None, mode
    assert download.suggested_filename == 'science-of-rules-proposal.txt'
    # read_bytes preserves CRLF, so this verifies the actual file, not its preview.
    assert Path(download.path()).read_bytes().decode('utf-8') == expected, mode


def assert_nojs_proposal(browser, url, mode, offline=False):
    context = browser.new_context(java_script_enabled=False, offline=offline,
                                  viewport={'width':320,'height':780})
    page = context.new_page()
    requests = []
    page.on('request', lambda r:requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    page.goto(url, wait_until='networkidle')
    assert page.locator('[data-proposal-form]').is_hidden(), mode
    assert page.locator('[data-proposal-draft]').is_hidden(), mode
    assert page.locator('.proposal-nojs').is_visible(), mode
    direct = page.locator('.proposal-nojs a').get_attribute('href')
    assert urlsplit(direct).scheme == 'mailto'
    assert urlsplit(direct).path == RECIPIENT
    assert parse_qs(urlsplit(direct).query)['subject'] == ['Research proposal — Science of Rules']
    assert page.get_by_role('navigation',name='Main navigation').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), mode
    if offline:
        assert not requests, requests
    context.close()
    report['checks'].append(f'{mode}: no-JS hidden form, visible direct email and navigation')


def assert_proposal(page, url, mode):
    page.goto(url, wait_until='networkidle')
    form = page.locator('[data-proposal-form]')
    assert form.is_visible(), mode
    assert page.locator('[data-proposal-draft]').is_hidden()
    assert form.locator('[required]').count() == 4
    assert not form.evaluate('form => form.checkValidity()')
    form.get_by_role('button',name='Prepare email').click()
    assert page.locator('[data-proposal-draft]').is_hidden()
    short = {'name':'Alex 윤', 'email':'alex+rules@example.org',
             'affiliation':'Research & Society', 'title':'Rules & café — 협업',
             'summary':'A short research idea & evidence.\n두 번째 줄: rules evolve.'}
    fill_proposal(page, {**short, 'email':'not-an-email'})
    assert page.locator('#proposal-email').evaluate('field => field.validity.typeMismatch')
    form.get_by_role('button',name='Prepare email').click()
    assert page.locator('[data-proposal-draft]').is_hidden()
    fill_proposal(page, {**short, 'name':'   '})
    form.get_by_role('button',name='Prepare email').click()
    assert page.locator('#proposal-name').evaluate('field => field.validity.customError')
    assert page.locator('[data-proposal-draft]').is_hidden()
    fill_proposal(page, short)
    form.get_by_role('button',name='Prepare email').click()
    assert page.locator('[data-proposal-draft]').is_visible()
    subject, body, full_text = expected_draft(short)
    mailto = page.locator('[data-open-proposal-email]').get_attribute('href')
    expected_link = f'mailto:{RECIPIENT}?subject='+quote(subject,safe="~!*'()")+'&body='+quote(body,safe="~!*'()")
    assert mailto == expected_link, (mode, mailto, expected_link)
    parts = urlsplit(mailto)
    assert parts.path == RECIPIENT
    assert parse_qs(parts.query) == {'subject':[subject], 'body':[body]}
    assert page.locator('#proposal-preview').input_value() == full_text.replace('\r\n','\n')
    assert_download(page, full_text, mode+' short download')
    page.locator('#proposal-title').fill('Edited outline')
    assert page.locator('[data-proposal-draft]').is_hidden()
    assert page.locator('#proposal-preview').input_value() == ''
    assert page.locator('[data-open-proposal-email]').get_attribute('href') == f'mailto:{RECIPIENT}'
    assert 'changed' in page.locator('[data-proposal-status]').inner_text()

    suffix = '\n규칙 & café END'
    long_values = {**short, 'title':'Long proposal', 'summary':'A'*(4000-len(suffix))+suffix}
    assert len(long_values['summary']) == 4000
    fill_proposal(page, long_values)
    form.get_by_role('button',name='Prepare email').click()
    subject, body, full_text = expected_draft(long_values)
    mailto = page.locator('[data-open-proposal-email]').get_attribute('href')
    assert mailto == f'mailto:{RECIPIENT}?subject='+quote(subject,safe="~!*'()")
    assert parse_qs(urlsplit(mailto).query) == {'subject':[subject]}
    assert page.locator('#proposal-preview').input_value() == full_text.replace('\r\n','\n')
    assert 'recipient and subject only' in page.locator('[data-draft-help]').inner_text()
    assert_download(page, full_text, mode+' long download')

    # Deterministic Clipboard API success records the exact complete long draft.
    page.evaluate('''() => {
      window.__qaCopied = null;
      Object.defineProperty(navigator, 'clipboard', {configurable:true,
        value:{writeText:async text => {window.__qaCopied=text;}}});
    }''')
    page.locator('[data-copy-proposal]').click()
    page.wait_for_function("document.querySelector('[data-proposal-status]').textContent.startsWith('Draft copied.')")
    assert page.evaluate('window.__qaCopied') == full_text
    # Denied Clipboard API must select all preview text and try the copy fallback.
    page.evaluate('''() => {
      navigator.clipboard.writeText = async () => {throw new Error('QA denied clipboard');};
      window.__qaFallbackCalls = 0;
      window.__qaOriginalExecCommand = document.execCommand;
      document.execCommand = command => {
        if(command==='copy'){window.__qaFallbackCalls++;return true;}
        return false;
      };
    }''')
    page.locator('[data-copy-proposal]').click()
    page.wait_for_function('window.__qaFallbackCalls === 1')
    assert page.locator('[data-proposal-status]').inner_text().startswith('Draft copied.')
    assert page.locator('#proposal-preview').evaluate('field => field.selectionStart===0 && field.selectionEnd===field.value.length')
    page.evaluate("() => {document.execCommand = () => {window.__qaFallbackCalls++;return false;};}")
    page.locator('[data-copy-proposal]').click()
    page.wait_for_function("document.querySelector('[data-proposal-status]').textContent.includes('copy it manually')")
    assert page.evaluate('window.__qaFallbackCalls') == 2
    assert page.locator('#proposal-preview').evaluate('field => field.selectionStart===0 && field.selectionEnd===field.value.length')
    page.evaluate('() => {document.execCommand = window.__qaOriginalExecCommand;}')

    page.set_viewport_size({'width':320,'height':780})
    menu = page.get_by_role('button',name='Menu')
    if menu.get_attribute('aria-expanded') == 'true': menu.click()
    menu.click()
    assert menu.get_attribute('aria-expanded') == 'true'
    assert page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Project',exact=True).is_visible()
    no_overflow(page,mode+' 320px open menu and long draft')
    page.keyboard.press('Escape')
    assert menu.get_attribute('aria-expanded') == 'false'
    no_overflow(page,mode+' 320px closed menu and long draft')
    report['checks'].append(f'{mode}: required/email/whitespace validation; exact Unicode, ampersand and newline mailto; edit invalidation; 4,000-character subject-only mailto; actual short/long downloads; clipboard success and both fallback paths; 320px menu/form')


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler,directory=str(ROOT/'dist')))
thread = Thread(target=server.serve_forever,daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}/'
report = {'pages':[], 'checks':[], 'errors':[]}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,args=['--no-sandbox'])
        report['browser'] = browser.version
        context = browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
        page = context.new_page()
        page.on('pageerror', lambda error:report['errors'].append(str(error)))
        page.on('requestfailed', lambda request:report['errors'].append(request.url))
        for width,height in [(1440,1000),(390,844),(320,780),(768,1024)]:
            page.set_viewport_size({'width':width,'height':height})
            for name in PAGES:
                response=page.goto(base+name+'.html',wait_until='networkidle')
                assert response.status==200
                assert page.locator('h1').count()==1
                assert page.locator('html').get_attribute('lang')=='en'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow: {name} @ {width}'
                page.evaluate("Promise.all([...document.images].map(img => { img.loading='eager'; return img.decode(); }))")
                assert page.evaluate('[...document.images].every(i=>i.complete && i.naturalWidth>0)'), name
                report['pages'].append({'name':name,'width':width,'status':response.status,'overflow':False})
                if width==1440 and name in ['index','people','data','project']:
                    page.screenshot(path=str(REVIEW/f'{name}-desktop.png'),full_page=True)
                    if name=='index': page.screenshot(path=str(REVIEW/'home-desktop.png'))
                if width==390 and name=='index':
                    page.screenshot(path=str(REVIEW/'home-mobile.png'),full_page=True)
                    page.screenshot(path=str(REVIEW/'home-mobile-top.png'))
                if width==320 and name=='project':
                    page.screenshot(path=str(REVIEW/'project-mobile.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.goto(base,wait_until='networkidle')
        menu=page.get_by_role('button',name='Menu')
        assert menu.get_attribute('aria-expanded')=='false'
        menu.click()
        assert menu.get_attribute('aria-expanded')=='true'
        page.keyboard.press('Escape')
        assert menu.get_attribute('aria-expanded')=='false'
        menu.click()
        page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='People',exact=True).click()
        assert page.url.endswith('people.html')
        assert page.locator('.person-card').count()==5
        assert page.locator('.assistant-card').count()==4
        assert page.locator('.pi-card, .person-card, .assistant-card').count()==8
        report['checks'].append('Mobile navigation, Escape, 8-person team roster')
        page.goto(base+'outputs.html',wait_until='networkidle')
        assert page.locator('.publication-entry').count()==7
        report['checks'].append('Seven related publications preserved')
        page.goto(base,wait_until='networkidle')
        page.locator('[data-stage-button="variation"]').click()
        assert 'amendments' in page.locator('[data-stage-description]').inner_text()
        assert page.locator('[data-stage-button="variation"]').get_attribute('aria-pressed')=='true'
        page.locator('[data-stage-button="selection"]').click()
        assert 'repeal' in page.locator('[data-stage-description]').inner_text()
        report['checks'].append('Evolution illustration controls')
        page.goto(base+'data.html',wait_until='networkidle')
        for category,count in [('web',2),('ocr',2),('reference',3),('planned',2),('all',7)]:
            page.locator(f'[data-filter="{category}"]').click()
            assert page.locator('[data-dataset]:visible').count()==count,category
        page.get_by_role('searchbox').fill('Regulations')
        assert page.locator('[data-dataset]:visible').count()==1
        page.locator('#cfr summary').click()
        assert page.locator('#cfr details').get_attribute('open') is not None
        page.get_by_role('searchbox').fill('unmatched-example-123')
        assert page.locator('[data-no-results]').is_visible()
        page.locator('[data-reset]').click()
        assert page.locator('[data-dataset]:visible').count()==7
        report['checks'].append('All catalog filters, combined search, details, empty state and reset')
        page.goto((ROOT/'dist/index.html').as_uri(),wait_until='networkidle')
        assert page.locator('h1').inner_text()=='How do\nrules evolve?'
        menu=page.get_by_role('button',name='Menu')
        menu.click()
        page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Data',exact=True).click()
        page.locator('[data-filter="ocr"]').click()
        assert page.locator('[data-dataset]:visible').count()==2
        report['checks'].append('Offline file:// navigation and filtering')
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        plain=nojs.new_page()
        plain.goto(base+'data.html',wait_until='networkidle')
        assert plain.get_by_role('navigation').is_visible()
        assert plain.locator('[data-dataset]:visible').count()==7
        nojs.close()
        report['checks'].append('Content and navigation available without JavaScript')
        assert_proposal(page,base+'project.html','Regular site')
        assert_nojs_proposal(browser,base+'project.html','Regular site')
        with TemporaryDirectory(prefix='science-of-rules-standalone-') as temporary:
            isolated=Path(temporary)/'science-of-rules-dashboard.html'
            shutil.copy2(REVIEW/'science-of-rules-dashboard.html',isolated)
            assert len(list(Path(temporary).iterdir()))==1
            offline=browser.new_context(offline=True,viewport={'width':1440,'height':1000})
            standalone=offline.new_page()
            external=[]
            standalone.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:','https:')) else None)
            standalone.on('pageerror',lambda error:report['errors'].append(str(error)))
            assert_proposal(standalone,isolated.as_uri()+'#view-project','Standalone offline HTML')
            assert standalone.locator('[data-view="project"]').is_visible()
            assert standalone.locator('[data-view]:visible').count()==1
            standalone.goto(isolated.as_uri()+'#propose',wait_until='networkidle')
            assert standalone.locator('[data-view="project"]').is_visible()
            assert standalone.locator('#propose').is_visible()
            standalone.goto(isolated.as_uri()+'#view-people',wait_until='networkidle')
            assert standalone.locator('[data-view="people"]').is_visible()
            assert standalone.locator('.pi-card, .person-card, .assistant-card').count()==8
            standalone.goto(isolated.as_uri()+'#view-outputs',wait_until='networkidle')
            assert standalone.locator('[data-view="outputs"]').is_visible()
            assert standalone.locator('.publication-entry').count()==7
            assert not external,external
            report['standalone_external_requests']=external
            report['checks'].append('Isolated single HTML: offline #view-project/#propose routes, 8 people, 7 publications, zero external requests')
            assert_nojs_proposal(browser,isolated.as_uri()+'#propose','Standalone offline HTML',offline=True)
            offline.close()
        assert not report['errors'],report['errors']
        browser.close()
        report['status']='passed'
except Exception as error:
    report['status']='failed'
    report['failure']=f'{type(error).__name__}: {error}'
    raise
finally:
    server.shutdown()
    server.server_close()
    (REVIEW/'browser-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
