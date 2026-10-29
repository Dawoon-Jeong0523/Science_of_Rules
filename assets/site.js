/* Progressive enhancements; all content is available without JavaScript. */
const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
if (menu && nav) {
  document.documentElement.classList.add('has-js');
  const closeMenu = () => { menu.setAttribute('aria-expanded', 'false'); nav.classList.remove('is-open'); };
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); }
  });
  nav.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
}

const model = document.querySelector('[data-evolution]');
if (model) {
  const descriptions = {
    replication: 'Ideas travel: institutions copy language and refer to existing rules.',
    variation: 'Rules change: amendments and reinterpretations introduce new forms.',
    selection: 'Some persist: application, citation, and repeal reshape the population.'
  };
  model.querySelectorAll('[data-stage-button]').forEach(button => {
    button.addEventListener('click', () => {
      model.dataset.stage = button.dataset.stageButton;
      model.querySelectorAll('[data-stage-button]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      model.querySelector('[data-stage-description]').textContent = descriptions[button.dataset.stageButton];
    });
  });
}

const catalog = document.querySelector('[data-catalog]');
if (catalog) {
  const search = catalog.querySelector('input[type="search"]');
  const buttons = [...catalog.querySelectorAll('[data-filter]')];
  const entries = [...catalog.querySelectorAll('[data-dataset]')];
  let active = 'all';
  const update = () => {
    const term = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    entries.forEach(entry => {
      const match = (active === 'all' || entry.dataset.formats.split(' ').includes(active)) && entry.textContent.toLocaleLowerCase().includes(term);
      entry.hidden = !match;
      if (match) visible += 1;
    });
    catalog.querySelector('[data-result-count]').textContent = `${visible} collection${visible === 1 ? '' : 's'}`;
    catalog.querySelector('[data-no-results]').hidden = visible !== 0;
  };
  search.addEventListener('input', update);
  buttons.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.filter;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    update();
  }));
  catalog.querySelector('[data-reset]').addEventListener('click', () => {
    search.value = ''; active = 'all';
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.filter === 'all')));
    update(); search.focus();
  });
}

// Prepare email locally; no form data is transmitted or persisted by this site.
const proposalForm = document.querySelector('[data-proposal-form]');
if (proposalForm) {
  const workspace = proposalForm.closest('.proposal-workspace');
  const draft = workspace.querySelector('[data-proposal-draft]');
  const preview = workspace.querySelector('#proposal-preview');
  const status = workspace.querySelector('[data-proposal-status]');
  const help = workspace.querySelector('[data-draft-help]');
  const openEmail = workspace.querySelector('[data-open-proposal-email]');
  const recipient = proposalForm.dataset.recipient;
  let draftText = '';

  proposalForm.addEventListener('input', event => {
    if (typeof event.target.setCustomValidity === 'function') event.target.setCustomValidity('');
    if (draftText) {
      draftText = '';
      preview.value = '';
      draft.hidden = true;
      openEmail.href = `mailto:${recipient}`;
      status.textContent = 'Your outline has changed. Prepare a new email draft when you are ready.';
    }
  });
  proposalForm.addEventListener('submit', event => {
    event.preventDefault();
    proposalForm.querySelectorAll('[required]').forEach(field => {
      field.setCustomValidity(field.value.trim() ? '' : 'Please fill out this field.');
    });
    if (!proposalForm.reportValidity()) return;
    const values = Object.fromEntries([...new FormData(proposalForm)].map(([key, value]) => [key, value.trim()]));
    const subject = `[Science of Rules] ${values.title}`;
    const body = [
      'Hello Science of Rules team,', '', values.summary, '',
      `Name: ${values.name}`, `Reply email: ${values.email}`,
      ...(values.affiliation ? [`Affiliation: ${values.affiliation}`] : [])
    ].join('\r\n');
    const subjectLink = `mailto:${recipient}?subject=${encodeURIComponent(subject)}`;
    const fullLink = `${subjectLink}&body=${encodeURIComponent(body)}`;
    const longDraft = fullLink.length > 1800;
    openEmail.href = longDraft ? subjectLink : fullLink;
    draftText = `To: ${recipient}\r\nSubject: ${subject}\r\n\r\n${body}`;
    preview.value = draftText;
    help.textContent = longDraft
      ? 'This draft is long. Copy it or download the full text below, then paste it into your email or attach the file. Open email app fills in the recipient and subject only.'
      : 'Open your email app to review and send this draft. If your app does not open or omits any text, copy the full draft below or download it and email it to the proposal contact.';
    status.textContent = 'Your email draft is ready. No email has been sent.';
    draft.hidden = false;
    draft.querySelector('h3').focus();
  });
  workspace.querySelector('[data-copy-proposal]').addEventListener('click', async () => {
    if (!draftText) return;
    let copied = false;
    try {
      await navigator.clipboard.writeText(draftText);
      copied = true;
    } catch {
      preview.focus();
      preview.select();
      try { copied = document.execCommand('copy'); } catch { /* Manual copy remains available. */ }
    }
    status.textContent = copied
      ? 'Draft copied. Paste it into your email app, review it, and send it when ready.'
      : 'Select the draft text and copy it manually, or use Download .txt.';
  });
  workspace.querySelector('[data-download-proposal]').addEventListener('click', () => {
    if (!draftText) return;
    const url = URL.createObjectURL(new Blob([draftText], { type: 'text/plain;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'science-of-rules-proposal.txt';
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    status.textContent = 'Draft file prepared. Attach it to an email to the proposal contact when ready.';
  });
  proposalForm.hidden = false;
}
