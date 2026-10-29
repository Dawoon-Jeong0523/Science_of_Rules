#!/usr/bin/env python3
"""Render the curated English content into a portable static site (stdlib only)."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
NAV = [('index', 'Home'), ('project', 'Project'), ('research', 'Research'),
       ('people', 'People'), ('news', 'News'), ('data', 'Data')]
ALIASES = {'updates': 'news', 'outputs': 'news'}


def e(value):
    return escape(str(value if value is not None else ''), quote=True)


def read(name):
    return json.loads((ROOT / 'content' / f'{name}.json').read_text(encoding='utf-8'))


def link(url, label, cls='text-link', external=False):
    return f'<a class="{cls}" href="{e(url)}">{e(label)} <span aria-hidden="true">{"↗" if external else "→"}</span></a>'


def intro(label, title, description, extra=''):
    return f'<section class="page-intro"><div class="wrap"><p class="eyebrow accent-label">{e(label)}</p><h1>{e(title)}</h1>{extra}<p class="intro-text">{e(description)}</p></div></section>'


def evolution():
    return '''<figure class="evolution" data-evolution data-stage="replication">
      <div class="figure-heading"><span class="eyebrow">The life of a rule</span><span>AN EVOLUTIONARY LENS</span></div>
      <svg viewBox="0 0 420 295" role="img" aria-labelledby="evolution-title evolution-desc">
        <title id="evolution-title">A conceptual lineage of rules</title>
        <desc id="evolution-desc">Branches connect a rule to copies, variations, and surviving descendants. This is a conceptual illustration, not measured data.</desc>
        <circle class="ring" cx="210" cy="152" r="122"/><circle class="ring" cx="210" cy="152" r="86"/>
        <g class="column-label"><text x="26" y="28">ORIGIN</text><text x="125" y="28">COPY</text><text x="252" y="28">CHANGE</text><text x="357" y="28">PERSIST</text></g>
        <g class="branch"><path d="M43 151C82 151 89 84 139 84M43 151C82 151 89 151 139 151M43 151C82 151 89 218 139 218"/>
        <path d="M139 84C191 84 216 62 267 62M139 84C191 84 216 108 267 108M139 151C193 151 214 151 267 151M139 218C193 218 214 198 267 198M139 218C193 218 214 244 267 244"/>
        <path d="M267 62C315 62 333 83 380 83M267 108C315 108 333 83 380 83M267 151C315 151 333 150 380 150M267 198C315 198 333 218 380 218M267 244C315 244 333 218 380 218"/></g>
        <circle class="node-core" cx="43" cy="151" r="12"/>
        <g class="stage-focus focus-replication"><circle class="node" cx="139" cy="84" r="10"/><circle class="node" cx="139" cy="151" r="10"/><circle class="node" cx="139" cy="218" r="10"/><circle class="node-core" cx="139" cy="84" r="3"/><circle class="node-core" cx="139" cy="151" r="3"/><circle class="node-core" cx="139" cy="218" r="3"/></g>
        <g class="stage-focus focus-variation"><circle class="node" cx="267" cy="62" r="9"/><circle class="variant" cx="267" cy="108" r="9"/><circle class="node" cx="267" cy="151" r="9"/><circle class="variant" cx="267" cy="198" r="9"/><circle class="node" cx="267" cy="244" r="9"/></g>
        <g class="stage-focus focus-selection"><circle class="variant" cx="380" cy="83" r="12"/><circle class="node retired" cx="380" cy="150" r="11"/><path class="branch" d="m375 145 10 10m-10 0 10-10"/><circle class="node-core" cx="380" cy="218" r="12"/></g>
        <path d="M35 275H388m-5-4 5 4-5 4" fill="none" stroke="#adbaa2"/><text x="161" y="291" class="column-label">THROUGH TIME</text>
      </svg>
      <div class="stage-controls" role="group" aria-label="Explore the evolutionary processes">
        <button type="button" data-stage-button="replication" aria-pressed="true">01 Replication</button>
        <button type="button" data-stage-button="variation" aria-pressed="false">02 Variation</button>
        <button type="button" data-stage-button="selection" aria-pressed="false">03 Selection</button>
      </div>
      <p class="stage-description" data-stage-description aria-live="polite">Ideas travel: institutions copy language and refer to existing rules.</p>
      <figcaption class="figure-note">Conceptual illustration · not empirical data</figcaption>
    </figure>'''


def home(project, research, people, datasets, updates, history):
    directions = ''.join(f'<a class="direction-link" href="research.html#{e(d["id"])}"><span class="number">0{i}</span><div><h3>{e(d["name"])}</h3><p>{e(d["short"])}</p></div><span class="arrow" aria-hidden="true">↗</span></a>' for i, d in enumerate(research['directions'], 1))
    collections = ''.join(f'<a class="mini-dataset" href="data.html#{e(d["id"])}"><span class="dataset-type">{e(d["kind"])} · {e(d["region"])}</span><h3>{e(d["name"])}</h3><p>{e(d["description"])}</p><span class="small-link">Explore collection <span aria-hidden="true">↗</span></span></a>' for d in datasets[:2])
    portraits = ''.join(
        f'<img src="assets/portraits/{e(p["photo"])}" alt="{e(p["name"])}" width="58" height="58" loading="lazy">'
        if p['photo'] else f'<span class="avatar-initials" role="img" aria-label="TODO: portrait for {e(p["name"])}" title="{e(p["name"])}">TODO: portrait</span>'
        for p in people)
    latest = next((u for u in updates if u.get('date')), None)
    announcement = f'<div class="latest-line"><span class="eyebrow accent-label">Latest news<br><time datetime="{e(latest["date"])}">{e(latest["date"])}</time></span><h3><a href="news.html#{e(latest["id"])}">{e(latest["title"])}</a></h3><a href="news.html" aria-label="View all news">↗</a></div>' if latest else ''
    return f'''<section class="hero wrap"><div class="hero-copy"><p class="eyebrow accent-label">{e(project['program'])}</p><h1>How do<br>rules <em>evolve?</em></h1><p class="hero-question">And how do they shape<br>complex systems?</p><p class="hero-description">A growing home for research on rules, regulation, and institutional change—connecting NSF research and Grand Quest, from biological and social systems to the possibilities of AI.</p><div class="hero-actions">{link('research.html', 'Explore the research', 'button')}{link('people.html', 'Meet the team')}</div></div>{evolution()}</section>
    <div class="project-strip"><div class="wrap"><p class="program"><span class="status-dot" aria-hidden="true"></span><span class="eyebrow">A continuing inquiry into rules & regulation</span></p><p>Rules & institutions <span aria-hidden="true">&nbsp; / &nbsp;</span> Complexity <span aria-hidden="true">&nbsp; / &nbsp;</span> Artificial intelligence</p></div></div>
    <section class="section wrap research-overview"><div><p class="eyebrow accent-label">Our approach</p><h2>From individual rules<br>to evolving systems.</h2><p>We connect data, models, and theory to understand how regulation scales, how rules change, and how institutions learn.</p>{link('research.html#research-questions', 'Four connected questions')}{link('research.html#publications', 'Explore the papers')}</div><div>{directions}</div></section>
    <section class="question-band"><div class="wrap question-inner"><div><p class="eyebrow">The question behind the project</p><h2>{e(project['question'])}</h2></div><div><p>{e(project['question_text'])}</p>{link('research.html#hypotheses', 'Explore our hypotheses')}</div></div></section>
    <section class="section wrap history-teaser"><div><p class="eyebrow accent-label">Our research history</p><h2>{e(history['home_heading'])}</h2></div><div><p>{e(history['home_summary'])}</p>{link('research.html#previous-project', 'Previous project & shared origins')}</div></section>
    <section class="section wrap"><div class="section-heading"><div><p class="eyebrow accent-label">The empirical foundation</p><h2>Following rules through time.</h2></div>{link('data.html', 'Browse the data catalog')}</div><div class="mini-datasets">{collections}</div></section>
    <section class="section wrap team-teaser"><div class="teaser-inner"><div><p class="eyebrow accent-label">A collaborative inquiry</p><h2>Different perspectives. A shared question.</h2><p>Our team brings together researchers across institutions to examine the evolution of rules and the effects of AI.</p></div><div class="teaser-team"><div class="avatar-stack">{portraits}</div>{link('people.html', 'Meet our research team')}</div></div></section>
    <section class="wrap section" style="padding-top:0">{announcement}</section>'''


def project_page(project, research):
    proposals = project['proposals']
    email = proposals['email']
    mailto = 'mailto:'+email+'?subject='+quote('Research proposal — Science of Rules')
    directions = ''.join(f'<a class="project-direction" href="research.html#{e(d["id"])}"><span class="eyebrow accent-label">0{i} · {e(d["scope"])}</span><h3>{e(d["name"])}</h3><p>{e(d["short"])}</p><span class="project-direction-arrow" aria-hidden="true">↗</span></a>' for i,d in enumerate(research['directions'],1))
    return intro('The project', 'An inquiry that keeps growing.', 'A shared home for research and activities across Grand Quest and the NSF Understanding the Rules of Life collaboration.') + f'''<section class="section wrap"><article class="ongoing-project" id="shared-project"><div class="ongoing-project-header"><span class="eyebrow accent-label">{e(project['program'])}</span><span class="ongoing-badge"><span class="status-dot" aria-hidden="true"></span>{e(project['status'])}</span></div><h2>{e(project['title'])}</h2><p class="ongoing-description">{e(project['overview'])}</p><dl class="project-facts"><div><dt>Project lead</dt><dd>{e(project['principal_investigator'])}</dd></div><div><dt>Research scope</dt><dd>{e(project['scope'])}</dd></div></dl><div class="project-actions">{link('research.html','Explore the research','button')}{link('#propose','Propose a collaboration')}{link('research.html#previous-project','Our shared origins')}</div></article><div class="project-directions-heading"><h2 class="section-title">Questions that connect the work</h2><p>From the organization of complex systems to the evolution of rules and the effects of AI.</p></div><div class="project-directions">{directions}</div></section>
    <section class="proposal-section" id="propose"><div class="section wrap proposal-layout"><div class="proposal-intro"><p class="eyebrow accent-label">An invitation to collaborate</p><h2>{e(proposals['heading'])}</h2><p>{e(proposals['invitation'])}</p><p>{e(proposals['prompt'])}</p><div class="proposal-contact"><span class="eyebrow">Proposal contact</span><a href="{e(mailto)}">{e(email)}</a><p>You can email us directly, including any supporting documents.</p></div></div><div class="proposal-workspace"><form data-proposal-form data-recipient="{e(email)}" aria-label="Prepare a research proposal email" aria-describedby="proposal-guidance" hidden><h3>Start with a short outline.</h3><p class="form-guidance" id="proposal-guidance">Fields marked * are required. Prepare your draft here, then send it from your email app.</p><div class="proposal-fields"><div class="form-field"><label for="proposal-name">Your name *</label><input id="proposal-name" name="name" autocomplete="name" maxlength="100" required></div><div class="form-field"><label for="proposal-email">Your email *</label><input id="proposal-email" name="email" type="email" autocomplete="email" maxlength="254" required></div><div class="form-field full"><label for="proposal-affiliation">Affiliation <span>(optional)</span></label><input id="proposal-affiliation" name="affiliation" autocomplete="organization" maxlength="160"></div><div class="form-field full"><label for="proposal-title">Proposal title *</label><input id="proposal-title" name="title" maxlength="140" required></div><div class="form-field full"><label for="proposal-summary">Your idea *</label><textarea id="proposal-summary" name="summary" rows="7" maxlength="4000" aria-describedby="proposal-summary-help" required></textarea><p class="field-help" id="proposal-summary-help">Describe your research question, relevant data or methods, and the collaboration you have in mind. Up to 4,000 characters; you can attach longer documents in your email.</p></div></div><button class="button" type="submit">Prepare email <span aria-hidden="true">→</span></button><p class="form-footnote">Preparing a draft does not send an email. You review and send the message in your email app.</p></form><noscript><div class="proposal-nojs"><h3>Send us your idea.</h3><p>Email your name, affiliation, proposal title, and a brief outline to <a href="{e(mailto)}">{e(email)}</a>.</p></div></noscript><p class="proposal-status" data-proposal-status role="status" aria-live="polite"></p><section class="proposal-draft" data-proposal-draft aria-labelledby="proposal-draft-heading" hidden><h3 id="proposal-draft-heading" tabindex="-1">Your email draft</h3><label class="sr-only" for="proposal-preview">Full proposal email text</label><textarea id="proposal-preview" readonly rows="12" spellcheck="false"></textarea><p class="draft-help" data-draft-help></p><div class="draft-actions"><a class="button" data-open-proposal-email href="{e(mailto)}">Open email app <span aria-hidden="true">↗</span></a><button class="button secondary" data-copy-proposal type="button">Copy draft</button><button class="button secondary" data-download-proposal type="button">Download .txt</button></div></section></div></div></section>'''


def project_history(history):
    previous, current = history['previous'], history['current']
    return f'''<section class="section wrap project-history" id="previous-project"><div class="section-heading"><div><p class="eyebrow accent-label">Previous project & shared origins</p><h2>{e(history['heading'])}</h2></div></div><ol class="history-timeline"><li class="history-step"><div class="history-step-top"><span class="eyebrow">Previous project</span><span class="history-status">{e(previous['status'])}</span></div><p class="history-program">{e(previous['program'])}</p><h3>{e(previous['title'])}</h3><p class="history-meta">{e(previous['date_label'])} · Principal investigator: {e(previous['lead'])}</p><p>{e(previous['description'])}</p>{link(previous['source_url'],previous['source_label'],'person-profile',True)}</li><li class="history-step current"><div class="history-step-top"><span class="eyebrow">Grand Quest</span><span class="history-status">{e(current['status'])}</span></div><p class="history-program">{e(current['program'])}</p><h3>{e(current['title'])}</h3><p>{e(current['description'])}</p></li></ol><div class="history-bridge"><p>{e(history['connection'])}</p>{link('research.html#publications','Explore the research papers')}</div></section>'''


def research_page(project, research, history, publications):
    rows = ''
    for i, d in enumerate(research['directions'], 1):
        rows += f'''<article class="direction-detail" id="{e(d['id'])}"><span class="large-number">0{i}</span><div><div class="direction-top"><div><p class="eyebrow accent-label">{e(d['name'])}</p><h3>{e(d['question'])}</h3></div></div><div class="direction-copy"><p>{e(d['description'])}</p><div class="method-note"><span class="eyebrow">Approaches</span><p>{e(d['method'])}</p></div></div></div></article>'''
    hypotheses = ''.join(f'<article class="hypothesis"><span class="eyebrow accent-label">H0{i} · {e(h["name"])}</span><h3>{e(h["question"])}</h3><p>{e(h["text"])}</p></article>' for i, h in enumerate(research['hypotheses'], 1))
    return intro('Research', 'A science of evolving rules.', project['intro']) + publications_section(publications) + f'''<section class="section wrap" id="research-questions"><p class="eyebrow accent-label">Our shared questions</p><h2 class="section-title">From regulation to institutional learning.</h2><p class="section-lead">Questions that connect our work across complex systems and guide new collaborations.</p>{rows}</section><section class="section hypotheses" id="hypotheses"><div class="wrap"><p class="eyebrow accent-label">Questions to test</p><h2 class="section-title" style="margin-top:12px">Rule evolution & AI: working hypotheses</h2><p class="section-lead">Open hypotheses guiding ongoing research into institutional change.</p><div class="hypothesis-grid">{hypotheses}</div></div></section>''' + project_history(history)


def initials(name):
    return ''.join(part[0] for part in (name or 'Research Profile').split()[:2])


def portrait(person, pi=False):
    if person['photo']:
        return f'<img class="person-image" src="assets/portraits/{e(person["photo"])}" alt="{e(person["name"])}" width="400" height="432" loading="{"eager" if pi else "lazy"}">'
    return f'<div class="portrait-placeholder" role="img" aria-label="TODO: portrait for {e(person["name"])}"><span class="empty-portrait-label">TODO: portrait</span></div>'


def person_text(person, heading='h3'):
    profile = link(person['profile'], 'Researcher profile', 'person-profile', True) if person.get('profile') else '<p class="todo-note">TODO: profile link</p>'
    return f'<{heading}>{e(person["name"] or "Profile forthcoming")}</{heading}><p class="person-position">{e(person["position"])}</p><p class="person-affiliation">{e(person["affiliation"])}</p>' + (f'<p class="person-unit">{e(person["unit"])}</p>' if person['unit'] else '') + (f'<p class="person-unit">{e(person["profile_note"])}</p>' if person.get('profile_note') else '') + profile


def people_page(people):
    members = ''.join(f'<article class="person-card" id="{e(p["id"])}"><div class="portrait-wrap">{portrait(p)}</div>{person_text(p)}</article>' for p in people)
    return intro('People', 'A shared inquiry.', 'Researchers across Grand Quest and the NSF collaboration, connected by a common interest in rules, regulation, and complex systems.') + f'''<div class="wrap roster-intro"><span>{len(people)} collaborators</span><span>Connected questions, different perspectives</span></div><section class="wrap people-section" aria-label="Project collaborators"><div class="researcher-grid">{members}</div></section>'''


def data_page(datasets):
    entries = ''
    for d in datasets:
        tags = ''.join(f'<span class="tag">{e(t)}</span>' for t in d['formats'])
        sources = ''.join(link(s['url'], s['label'], '', True) for s in d['sources'])
        details = ''
        if d['coverage'] or d['quality'] or sources:
            details = '<details class="dataset-details"><summary>Coverage, quality & sources</summary>'
            if d['coverage']: details += f'<p><strong>Coverage.</strong> {e(d["coverage"])}</p>'
            if d['quality']: details += f'<p><strong>Quality.</strong> {e(d["quality"])}</p>'
            if sources: details += f'<div class="source-links">{sources}</div>'
            details += '</details>'
        entries += f'''<article class="dataset-entry" id="{e(d['id'])}" data-dataset data-formats="{e(' '.join(f.lower() for f in d['formats']))}"><div><span class="dataset-status {e(d['status_key'])}">{e(d['status'])}</span><h2>{e(d['name'])}</h2><p class="region">{e(d['region'])}</p><div>{tags}</div></div><div><p class="dataset-description">{e(d['description'])}</p>{details}</div></article>'''
    filters = ''.join(f'<button type="button" data-filter="{value}" aria-pressed="{"true" if value == "all" else "false"}">{label}</button>' for value, label in [('all','All'),('web','Web'),('ocr','OCR'),('reference','Reference'),('planned','Planned')])
    return intro('Data & materials', 'An observatory starts with evidence.', 'A catalog of research collections, reference materials, and planned sources for studying rules over time.') + f'''<section class="section catalog-section wrap" data-catalog><div class="catalog-tools"><div class="filter-group" role="group" aria-label="Filter collections by format">{filters}</div><div class="search-wrap"><label class="sr-only" for="dataset-search">Search collections</label><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="6.5" cy="6.5" r="4.5"/><path d="m10 10 4 4"/></svg><input id="dataset-search" type="search" placeholder="Search collections…" autocomplete="off"></div></div><div class="catalog-summary"><span data-result-count role="status" aria-live="polite">{len(datasets)} collections</span><span>Collection status, not research results</span></div><div>{entries}</div><div class="empty-search" data-no-results hidden><h2>No matching collections.</h2><p>Try another term or remove the selected filter.</p><button class="button secondary" type="button" data-reset>Clear search & filters</button></div><aside class="catalog-note"><span class="eyebrow accent-label">About access and quality</span><p>This catalog describes materials held or planned by the project. Research copies are not distributed through this site. Where available, links lead to original providers. Collection assembly does not establish completeness, OCR accuracy, or readiness for every analysis.</p></aside></section>'''


def news_items(updates, publications):
    """Use the publication record as the single source of publication news."""
    items = [dict(item) for item in updates]
    for p in publications:
        published = p['status'] == 'published'
        items.append({
            'id': 'news-'+p['id'], 'date': p.get('first_posted'),
            'category': 'Publication' if published else 'Preprint',
            'title': f"{p['title']} — {'published in '+p['venue'] if published else 'preprint posted'}.",
            'link': p.get('url'), 'link_label': 'Paper' if published else 'Preprint',
            'research_link': 'research.html#'+p['id'],
        })
        if p.get('revised'):
            items.append({
                'id': 'news-'+p['id']+'-revision', 'date': p['revised'],
                'category': 'Preprint update', 'title': p['title']+' — revised preprint posted.',
                'link': p.get('url'), 'link_label': 'Preprint',
                'research_link': 'research.html#'+p['id'],
            })
    return sorted(items, key=lambda item: item.get('date') or '', reverse=True)


def news_page(items):
    entries = ''
    for item in items:
        date = f'<time datetime="{e(item["date"])}">{e(item["date"])}</time>' if item.get('date') else '<span class="news-date-todo">TODO: date</span>'
        if item.get('date_end'):
            date += f'<span aria-hidden="true"> – </span><time datetime="{e(item["date_end"])}">{e(item["date_end"])}</time>'
        source = link(item['link'],item.get('link_label') or 'Details','news-link',True) if item.get('link') else '<span class="todo-note">TODO: source link</span>'
        research = link(item['research_link'],'Research','news-link') if item.get('research_link') else ''
        entries += f'<li class="news-entry" id="{e(item["id"])}"><div class="news-date">{date}</div><p class="news-summary"><span class="news-category">{e(item["category"])}</span>{e(item["title"])} <span class="news-links">{source}{research}</span></p></li>'
    return intro('News', 'News & milestones.', 'Workshops, awards, publications, and updates from our shared research. Explore Research for the ideas and findings behind the papers.') + f'<section class="section wrap"><ul class="news-list">{entries}</ul></section>'


def publications_section(publications):
    entries = ''
    priority = ['us-legal-code-dataset', 'function-diversity-scaling', 'common-law-ages', 'reddit-regulation', 'generative-function-growth']
    ordered = sorted(publications, key=lambda p: priority.index(p['id']) if p['id'] in priority else len(priority))
    for p in ordered:
        status = 'Journal article' if p['status'] == 'published' else 'Preprint'
        fig = p.get('figure')
        if fig and fig.get('src'):
            caption = link(fig['source_url'],fig.get('label') or 'Figure source','figure-source',True) if fig.get('source_url') else '<span class="todo-note">TODO: figure source</span>'
            credit = e(fig.get('credit') or '')
            if fig.get('license_url'):
                credit += ' · '+link(fig['license_url'],fig.get('license') or 'License','figure-source',True)
            visual = f'<figure class="research-figure"><a href="{e(fig["src"])}" download="{e(Path(fig["src"]).name)}" aria-label="Download figure for {e(p["title"])}"><img src="{e(fig["src"])}" alt="{e(fig["alt"])}" loading="lazy"></a><figcaption>{caption}<span>{e(fig.get("caption") or "")}</span><span class="figure-credit">{credit}</span></figcaption></figure>'
        else:
            visual = f'<figure class="research-figure"><div class="figure-todo"><span class="eyebrow">Main figure</span><p>{e(p.get("figure_todo") or "TODO: verify and add the main figure.")}</p></div></figure>'
        links = ''.join(link(item['url'],item['label'],'person-profile',True) for item in p['links'] if item.get('url')) or '<span class="todo-note">TODO: paper link</span>'
        heading = f'<a href="{e(p["url"])}">{e(p["title"])}</a>' if p.get('url') else e(p.get('title') or 'TODO: paper title')
        authors = '; '.join(p['authors'])
        entries += f'''<article class="publication-entry" id="{e(p['id'])}">{visual}<div class="publication-body"><div class="publication-meta"><span class="publication-status {e(p['status'])}">{e(status)}</span><span>{e(p['year'])} · {e(p['citation'])}</span></div><h3>{heading}</h3><p class="publication-summary">{e(p.get('summary') or 'TODO: verify the research summary.')}</p><p class="publication-authors">{e(authors)}</p><div class="publication-links">{links}</div></div></article>'''
    return f'''<section class="section wrap research-papers" id="publications"><div class="publication-intro"><div><p class="eyebrow accent-label">Research in focus</p><h2 class="section-title">Papers & preprints.</h2><p>Evidence and ideas across our shared research questions.</p></div><span class="eyebrow">{len(publications)} selected works</span></div><div class="publication-list">{entries}</div></section>'''


def main():
    project, research, people, datasets, updates = [read(n) for n in ['project','research','people','datasets','updates']]
    history, publications = read('history'), read('publications')
    updates = news_items(updates, publications)
    if len({p['id'] for p in people}) != len(people):
        raise ValueError('People IDs must be unique')
    for person in people:
        if not person['name']:
            raise ValueError(f'Missing English name: {person["id"]}')
        photo = person['photo']
        if photo and (Path(photo).name != photo or not (ROOT/'assets/portraits'/photo).is_file()):
            raise ValueError(f'Invalid portrait: {photo}')
    pages = {
        'index': ('Science of Rules — Rules, regulation & complex systems', home(project,research,people,datasets,updates,history)),
        'project': ('Project — Science of Rules', project_page(project,research)),
        'research': ('Research — Science of Rules', research_page(project,research,history,publications)),
        'people': ('People — Science of Rules', people_page(people)),
        'news': ('News — Science of Rules', news_page(updates)),
        'data': ('Data — Science of Rules', data_page(datasets))
    }
    for alias, target in ALIASES.items():
        pages[alias] = pages[target]
    if DIST.is_symlink():
        raise ValueError('Refusing to build into a symlink')
    DIST.mkdir(exist_ok=True)
    if (DIST/'assets').is_symlink():
        raise ValueError('Refusing to replace symlinked assets')
    if (DIST/'assets').exists():
        shutil.rmtree(DIST/'assets')
    shutil.copytree(ROOT/'assets',DIST/'assets')
    template = (ROOT/'templates/base.html').read_text(encoding='utf-8')
    for page,(title,body) in pages.items():
        navigation = ''.join(f'<a href="{slug}.html"'+(' aria-current="page"' if slug==ALIASES.get(page, page) else '')+f'>{label}</a>' for slug,label in NAV)
        rendered = template
        for key,value in {'title':e(title),'description':e(project['tagline']),'page':page,'navigation':navigation,'content':body}.items():
            rendered = rendered.replace('{{'+key+'}}',value)
        (DIST/f'{page}.html').write_text(rendered, encoding='utf-8')
    (DIST/'.nojekyll').write_text('', encoding='utf-8')
    print(f'Built {len(pages)} English pages into {DIST}')


if __name__ == '__main__':
    main()
