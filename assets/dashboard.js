/* Navigation for the self-contained, offline review copy. */
(() => {
  const views = [...document.querySelectorAll('[data-view]')];
  const navigation = document.querySelector('.main-nav');
  const main = document.getElementById('main');
  let current = 'home';

  function showView(moveFocus = false) {
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)); }
    catch { fragment = ''; }
    let target = fragment ? document.getElementById(fragment) : null;
    let view = target?.closest('[data-view]');
    if (!view) {
      const route = fragment === 'main' ? current : 'home';
      view = views.find(item => item.dataset.view === route);
      target = fragment === 'main' ? main : view;
    }
    current = view.dataset.view;
    views.forEach(item => { item.hidden = item !== view; });
    document.body.dataset.page = current === 'home' ? 'index' : current;
    document.title = `${view.dataset.label} — Science of Rules · Local review`;
    navigation.querySelectorAll('a').forEach(item => {
      if (item.getAttribute('href') === `#view-${current}`) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
    });
    const menu = document.querySelector('.menu-toggle');
    menu.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('is-open');

    // A deep link must also reveal a collection hidden by an earlier filter.
    if (target.matches('[data-dataset]') && target.hidden) {
      target.closest('[data-catalog]').querySelector('[data-reset]').click();
    }
    if (moveFocus) {
      const focusTarget = target === view ? view.querySelector('h1') : target;
      requestAnimationFrame(() => {
        if (focusTarget) {
          focusTarget.setAttribute('tabindex', '-1');
          focusTarget.focus({preventScroll: true});
        }
        if (target === view || target === main) window.scrollTo({top: 0, behavior: 'instant'});
        else target.scrollIntoView({block: 'start', behavior: 'instant'});
      });
    }
  }

  window.addEventListener('hashchange', () => showView(true));
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (anchor.getAttribute('href') === location.hash) {
      event.preventDefault();
      showView(true);
    }
  });
  showView(Boolean(location.hash));
})();
