/*
 * SIBiLS documentation theme: search dialog.
 *
 * Reads search/search_index.json, written at build time by the MkDocs
 * "search" plugin (one entry per page and per section), and searches it in
 * the browser: every word of the query must appear in the title or the text
 * of an entry; title matches rank first. Results link to the section anchor.
 * The JSON in #__search-pages (partials/search.html) gives each page's H1,
 * used as the page title instead of its nav label, and its sections, shown
 * under each result; the H1 section entry, a copy of the page, is dropped.
 *
 * Opens with the sub-bar button or the "/" key; Escape closes; Up/Down move
 * between results; Enter opens the first result from the input.
 */
(function () {
  'use strict';

  var dialog = document.getElementById('__search-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') {
    // No <dialog> support: hide the search buttons rather than offer a dead control.
    Array.prototype.forEach.call(document.querySelectorAll('[data-search-open]'), function (b) {
      b.hidden = true;
    });
    return;
  }

  var pages = {};
  try {
    pages = JSON.parse(document.getElementById('__search-pages').textContent) || {};
  } catch (e) { /* no map: nav labels and no context lines */ }

  var input = document.getElementById('__search-input');
  var list = document.getElementById('__search-results');
  var status = document.getElementById('__search-status');
  var baseUrl = document.documentElement.getAttribute('data-base-url') || '.';
  var MAX_RESULTS = 25;
  var MAX_PER_PAGE = 4;

  var docs = null;
  var loading = null;
  var opener = null;
  var timer = null;

  function joinUrl(base, path) {
    if (base.slice(-1) === '/') base = base.slice(0, -1);
    return base + '/' + path;
  }

  function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function loadIndex() {
    if (loading) return loading;
    loading = fetch(joinUrl(baseUrl, 'search/search_index.json'), { credentials: 'same-origin' })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (data) {
        var pageTitles = {};
        data.docs.forEach(function (d) {
          if (d.location.indexOf('#') === -1) {
            var info = pages[d.location];
            pageTitles[d.location] = (info && info.t) || d.title || '';
          }
        });
        var list = [];
        data.docs.forEach(function (d) {
          var page = d.location.split('#')[0];
          var info = pages[page] || null;
          var isPage = d.location.indexOf('#') === -1;
          // The H1 section repeats the page entry (whose text covers it).
          if (!isPage && info && info.h && d.location === page + info.h) return;
          var pageTitle = pageTitles[page] || '';
          var title = isPage ? pageTitle : (d.title || '');
          // Drop the permalink signs (¶) the index keeps from the headings,
          // and the H1 at the start of a page's text (it is the title).
          var text = (d.text || '').replace(/\s*\u00b6/g, '');
          if (isPage && pageTitle && text.indexOf(pageTitle) === 0) text = text.slice(pageTitle.length);
          // Context line: the sections above the page, then the page itself
          // for a section result ("API › BiodiversityPMC › Fetch").
          var trail = info && info.p ? [info.p] : [];
          if (!isPage && pageTitle && pageTitle !== title) trail.push(pageTitle);
          list.push({
            location: d.location,
            page: page,
            isPage: isPage,
            title: title || pageTitle,
            where: trail.join(' \u203a '),
            text: text,
            titleLower: (title || pageTitle).toLowerCase(),
            textLower: text.toLowerCase()
          });
        });
        docs = list;
        return docs;
      });
    loading.catch(function () { loading = null; });
    return loading;
  }

  var WORD = /[\p{L}\p{N}]+/gu;
  function terms(query) {
    var words = query.toLowerCase().match(WORD) || [];
    var seen = {};
    return words.filter(function (w) {
      if (w.length < 2 || seen[w]) return false;
      seen[w] = true;
      return true;
    });
  }

  function isWordStart(text, index) {
    return index === 0 || !/[\p{L}\p{N}]/u.test(text.charAt(index - 1));
  }

  function count(text, term, max) {
    var n = 0, i = text.indexOf(term);
    while (i !== -1 && n < max) { n++; i = text.indexOf(term, i + term.length); }
    return n;
  }

  function score(doc, words, phrase) {
    var total = 0;
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      var inTitle = doc.titleLower.indexOf(w);
      var inText = doc.textLower.indexOf(w);
      if (inTitle === -1 && inText === -1) return 0;
      if (inTitle !== -1) total += isWordStart(doc.titleLower, inTitle) ? 10 : 4;
      if (inText !== -1) total += 1 + Math.min(count(doc.textLower, w, 8), 8) * 0.4;
    }
    if (phrase.length > 2 && doc.titleLower === phrase) total += 15;
    else if (phrase.length > 2 && doc.titleLower.indexOf(phrase) !== -1) total += 6;
    if (words.length > 1 && doc.textLower.indexOf(phrase) !== -1) total += 4;
    if (doc.isPage) total += 1;
    return total;
  }

  // Escapes `text` and wraps the query words in <mark>.
  function highlight(text, words) {
    if (!words.length) return escapeHtml(text);
    var pattern = new RegExp('(' + words.map(function (w) {
      return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }).join('|') + ')', 'giu');
    var out = '', last = 0, match;
    while ((match = pattern.exec(text)) !== null) {
      out += escapeHtml(text.slice(last, match.index)) + '<mark>' + escapeHtml(match[0]) + '</mark>';
      last = match.index + match[0].length;
      if (match[0].length === 0) pattern.lastIndex++;
    }
    return out + escapeHtml(text.slice(last));
  }

  function snippet(doc, words) {
    var text = doc.text.replace(/\s+/g, ' ').trim();
    if (!text) return '';
    var lower = text.toLowerCase();
    var first = -1;
    words.forEach(function (w) {
      var i = lower.indexOf(w);
      if (i !== -1 && (first === -1 || i < first)) first = i;
    });
    var start = Math.max(0, (first === -1 ? 0 : first) - 60);
    if (start > 0) {
      var space = text.indexOf(' ', start);
      if (space !== -1 && space < start + 20) start = space + 1;
    }
    var end = Math.min(text.length, start + 180);
    if (end < text.length) {
      var cut = text.lastIndexOf(' ', end);
      if (cut > start + 120) end = cut;
    }
    return (start > 0 ? '… ' : '') + highlight(text.slice(start, end), words) + (end < text.length ? ' …' : '');
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function render(query) {
    var words = terms(query);
    list.innerHTML = '';
    if (!query.trim()) { setStatus(''); return; }
    if (!words.length) {
      setStatus(query.trim().length < 2 ? 'Type at least two characters.' :
        'Search for words of at least two letters or digits.');
      return;
    }
    if (!docs) return;

    var phrase = words.join(' ');
    var scored = [];
    docs.forEach(function (doc) {
      var s = score(doc, words, phrase);
      if (s > 0) scored.push({ doc: doc, score: s });
    });
    scored.sort(function (a, b) { return b.score - a.score; });

    var perPage = {};
    var shown = [];
    for (var i = 0; i < scored.length && shown.length < MAX_RESULTS; i++) {
      var doc = scored[i].doc;
      perPage[doc.page] = (perPage[doc.page] || 0) + 1;
      if (perPage[doc.page] <= MAX_PER_PAGE) shown.push(doc);
    }

    if (!shown.length) {
      setStatus('No results for “' + query.trim() + '”.');
      return;
    }
    setStatus(scored.length === 1 ? '1 result' :
      (scored.length > shown.length ? 'Top ' + shown.length + ' of ' + scored.length + ' results' : shown.length + ' results'));

    var html = shown.map(function (doc) {
      var where = doc.where ? '<span class="r-page">' + escapeHtml(doc.where) + '</span>' : '';
      var text = snippet(doc, words);
      return '<li><a href="' + escapeHtml(joinUrl(baseUrl, doc.location)) + '">' +
        '<span class="r-title">' + highlight(doc.title, words) + '</span>' + where +
        (text ? '<span class="r-snippet">' + text + '</span>' : '') +
        '</a></li>';
    }).join('');
    list.innerHTML = html;
  }

  function run() {
    var query = input.value;
    if (docs) { render(query); return; }
    if (query.trim()) setStatus('Loading the search index…');
    loadIndex().then(function () { render(input.value); }, function () {
      setStatus('Search is unavailable: the search index could not be loaded.');
    });
  }

  function open(initial) {
    if (dialog.open) { input.focus(); return; }
    opener = document.activeElement;
    if (typeof initial === 'string') input.value = initial;
    dialog.showModal();
    input.focus();
    input.select();
    run();
  }

  function close() {
    if (dialog.open) dialog.close();
  }

  dialog.addEventListener('close', function () {
    window.clearTimeout(timer);
    if (opener && typeof opener.focus === 'function' && document.contains(opener)) opener.focus();
  });

  // Escape always closes (some browsers would only clear the search field).
  dialog.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.preventDefault();
      close();
    }
  });

  input.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(run, 80);
  });

  function resultLinks() {
    return Array.prototype.slice.call(list.querySelectorAll('a'));
  }

  input.addEventListener('keydown', function (event) {
    var links = resultLinks();
    if (event.key === 'ArrowDown' && links.length) {
      event.preventDefault();
      links[0].focus();
    } else if (event.key === 'Enter') {
      event.preventDefault();
      window.clearTimeout(timer);
      if (docs) render(input.value);
      links = resultLinks();
      if (links.length) {
        close();
        window.location.href = links[0].href;
      }
    }
  });

  list.addEventListener('keydown', function (event) {
    var links = resultLinks();
    var index = links.indexOf(document.activeElement);
    if (index === -1) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (index < links.length - 1) links[index + 1].focus();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (index > 0) links[index - 1].focus(); else input.focus();
    } else if (event.key === 'Home') {
      event.preventDefault();
      links[0].focus();
    } else if (event.key === 'End') {
      event.preventDefault();
      links[links.length - 1].focus();
    }
  });

  // Same-page anchors do not reload the page: close the dialog ourselves.
  list.addEventListener('click', function (event) {
    if (event.target.closest('a')) close();
  });

  Array.prototype.forEach.call(document.querySelectorAll('[data-search-open]'), function (button) {
    button.addEventListener('click', function () { open(); });
  });

  // "/" opens the search, unless the visitor is typing somewhere.
  document.addEventListener('keydown', function (event) {
    if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey || event.defaultPrevented) return;
    var target = event.target;
    var tag = target && target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (target && target.isContentEditable)) return;
    if (document.querySelector('dialog[open]')) return;
    event.preventDefault();
    open();
  });

  // Prefetch the index when the visitor shows an intent to search.
  function prefetch() { loadIndex().catch(function () { /* reported when searching */ }); }
  Array.prototype.forEach.call(document.querySelectorAll('[data-search-open]'), function (button) {
    button.addEventListener('pointerenter', prefetch, { once: true });
    button.addEventListener('focus', prefetch, { once: true });
  });

  // ?q=term opens the search with that query (links from elsewhere).
  var match = /[?&]q=([^&]*)/.exec(window.location.search);
  if (match) {
    try { open(decodeURIComponent(match[1].replace(/\+/g, ' '))); } catch (e) { /* bad encoding */ }
  }
})();
