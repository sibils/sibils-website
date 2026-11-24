/*
 * SIBiLS Vocabularies page: the "Annotation type" filter of the vocabulary
 * tables.
 *
 * hooks/sibils_data.py writes an empty div.vocab-filter above the tables and
 * the type of each vocabulary, exactly as the API returns it, in a data-type
 * attribute on the row's anchor: <span id="chebi" data-type="chemical">.
 * main.html loads this script only on the page that has that div. The script
 * fills the div with a select of the types, each with its number of
 * vocabularies, and a "Show all" button. Choosing a type hides
 * (.is-filtered-out) the rows of the other types, a table left empty with its
 * ### heading and its shared paragraph, a ## category left with no table, and
 * their entries in "On this page" and in the sidebar or menu drawer. It
 * relies on the order of the hook's blocks: ## category, optional ### group,
 * optional shared paragraph, div.vocab-table.
 *
 * The hiding applies on screen only (sibils.css): print shows every
 * vocabulary, and so does the page without JavaScript.
 *
 * The chosen type is kept in the address (?type=chemical) with replaceState:
 * a closed select changes on every arrow key, and Back should leave the page.
 * A link to a row or heading the filter hides clears the filter.
 */
(function () {
  'use strict';

  var place = document.querySelector('.content .vocab-filter');
  if (!place) return;
  // No filter: the div goes, with the height sibils.css keeps for it.
  function giveUp() { place.parentNode.removeChild(place); }
  if (!('URLSearchParams' in window)) return giveUp();
  var HIDE = 'is-filtered-out';

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  /* Data, read from the page ------------------------------------------------ */

  var rows = $$('.content .vocab-table [data-type]').map(function (el) {
    return { tr: el.closest('tr'), type: el.getAttribute('data-type') };
  }).filter(function (row) { return row.tr; });
  var counts = Object.create(null);
  rows.forEach(function (row) { counts[row.type] = (counts[row.type] || 0) + 1; });
  var total = rows.length;
  if (!total) return giveUp();
  // By lower case, code point order: "cell line", "cell type", "cell_lines".
  var types = Object.keys(counts).sort(function (a, b) {
    a = a.toLowerCase();
    b = b.toLowerCase();
    return a < b ? -1 : a > b ? 1 : 0;
  });

  // Each table with what comes before it up to the previous heading (shared
  // paragraph, ### heading), and each ## category with its tables.
  var groups = [];
  var categories = [];
  $$('.content .vocab-table').forEach(function (div) {
    var group = { parts: [div], h3: null, empty: false };
    group.rows = rows.filter(function (row) { return div.contains(row.tr); });
    var el = div.previousElementSibling;
    while (el && el.tagName !== 'H2' && el.tagName !== 'H3' && !el.classList.contains('vocab-table')) {
      group.parts.push(el);
      el = el.previousElementSibling;
    }
    if (el && el.tagName === 'H3') {
      group.parts.push(el);
      group.h3 = el;
    }
    while (el && el.tagName !== 'H2') el = el.previousElementSibling;
    if (!el) return;
    var cat = categories[categories.length - 1];
    if (!cat || cat.h2 !== el) categories.push(cat = { h2: el, groups: [] });
    cat.groups.push(group);
    groups.push(group);
  });

  // Entries of "On this page" and of the sidebar or drawer, by heading id.
  var tocItems = Object.create(null);
  $$('.toc a[href^="#"], .snav__toc a[href^="#"]').forEach(function (a) {
    var id;
    try { id = decodeURIComponent(a.getAttribute('href').slice(1)); } catch (e) { return; }
    if (id) (tocItems[id] = tocItems[id] || []).push(a.parentNode);
  });

  function hide(el, yes) {
    el.classList.toggle(HIDE, yes);
    (el.id && tocItems[el.id] || []).forEach(function (li) { li.classList.toggle(HIDE, yes); });
  }

  /* Controls ------------------------------------------------------------------ */

  place.setAttribute('role', 'search');
  place.setAttribute('aria-label', 'Vocabulary filter');
  var label = document.createElement('label');
  label.htmlFor = '__vocab-type';
  label.textContent = 'Annotation type';
  var select = document.createElement('select');
  select.id = '__vocab-type';
  select.add(new Option('All types', ''));
  types.forEach(function (type) { select.add(new Option(type + ' (' + counts[type] + ')', type)); });
  var reset = document.createElement('button');
  reset.type = 'button';
  reset.className = 'vocab-filter__reset';
  reset.hidden = true;
  reset.textContent = 'Show all ' + total + ' vocabularies';
  place.appendChild(label);
  place.appendChild(select);
  place.appendChild(reset);

  /* Filtering ------------------------------------------------------------------ */

  var current = '';

  // type: one of the data-type values, or '' for all types.
  function apply(type) {
    rows.forEach(function (row) { hide(row.tr, type !== '' && row.type !== type); });
    groups.forEach(function (group) {
      group.empty = !group.rows.some(function (row) { return !row.tr.classList.contains(HIDE); });
      group.parts.forEach(function (el) { hide(el, group.empty); });
    });
    categories.forEach(function (cat) {
      hide(cat.h2, cat.groups.every(function (group) { return group.empty; }));
    });
    // A ### heading right under its ## (the tables between them hidden) keeps
    // the spacing of "## + ###" (sibils.css).
    groups.forEach(function (group) {
      if (!group.h3 || group.empty) return;
      var prev = group.h3.previousElementSibling;
      while (prev && prev.classList.contains(HIDE)) prev = prev.previousElementSibling;
      group.h3.classList.toggle('is-first-group', !!prev && prev.tagName === 'H2');
    });
    select.value = type;
    reset.hidden = !type;
    current = type;
  }

  /* Address --------------------------------------------------------------------- */

  // The type named by ?type=: exactly, or else the one type that matches it
  // without regard to case and surrounding spaces (?type=Chemical); '' if none.
  function typeInAddress() {
    var type = new URLSearchParams(window.location.search).get('type');
    if (type === null || type in counts) return type || '';
    var key = type.trim().toLowerCase();
    var found = types.filter(function (t) { return t.toLowerCase() === key; });
    return found.length === 1 ? found[0] : '';
  }

  // The element named by the #fragment, if the filter hides it.
  function hiddenTarget() {
    var el = null;
    try {
      el = window.location.hash && document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    } catch (e) { /* malformed %-escape in the address */ }
    return el && el.closest('.' + HIDE) ? el : null;
  }

  // ?type= follows the select; other parameters stay; a #fragment the filter
  // hides is dropped.
  function save() {
    var params = new URLSearchParams(window.location.search);
    if (current) params.set('type', current);
    else params.delete('type');
    var query = params.toString();
    var url = window.location.pathname + (query ? '?' + query : '') + (hiddenTarget() ? '' : window.location.hash);
    try {
      window.history.replaceState(window.history.state, '', url);
    } catch (e) { /* Safari: more than 100 calls in 30 seconds */ }
  }

  /* Announcements --------------------------------------------------------------- */

  // Once, 500 ms after the last change (arrow keys on the closed select).
  var timer = null;
  function announceLater() {
    var live = document.getElementById('__live-status');
    if (!live) return;
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      live.textContent = '';
      timer = window.setTimeout(function () {
        var n = counts[current];
        live.textContent = current
          ? n + (n === 1 ? ' vocabulary' : ' vocabularies') + ' of type ' + current + ' shown.'
          : 'All ' + total + ' vocabularies shown.';
      }, 50);
    }, 500);
  }

  /* Events ----------------------------------------------------------------------- */

  apply(typeInAddress());
  if (hiddenTarget()) apply('');
  // A ?type= that shows everything (unknown, empty, or dropped because it
  // hides the #fragment) leaves the address; one in another case is written
  // as the type.
  var asked = new URLSearchParams(window.location.search).get('type');
  if (asked !== null && (!current || asked !== current)) save();

  select.addEventListener('change', function () {
    apply(select.value);
    save();
    announceLater();
  });

  reset.addEventListener('click', function () {
    apply('');
    save();
    announceLater();
    select.focus();  // the button disappears
  });

  window.addEventListener('hashchange', function () {
    var target = hiddenTarget();
    if (!target) return;
    apply('');
    save();
    target.scrollIntoView();
    announceLater();
  });

  // Back and Forward between addresses with another ?type=. A link to the
  // same page fires popstate, then hashchange, which handles it.
  window.addEventListener('popstate', function () {
    var type = typeInAddress();
    if (type === current) return;
    apply(type);
    var target = hiddenTarget();
    if (target) {
      apply('');
      save();
      target.scrollIntoView();
    }
    announceLater();
  });
})();
