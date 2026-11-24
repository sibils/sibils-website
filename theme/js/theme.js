/*
 * SIBiLS documentation theme: progressive enhancements (no framework).
 * Everything here is optional: without JavaScript the pages stay readable
 * and the navigation stays usable (see the .no-js rules in sibils.css).
 *
 *  - light/dark toggle (the initial theme is applied by the inline script
 *    in <head>, before the first paint)
 *  - wordmark in the white bar once the red header has left the screen
 *  - menu drawer (below 1024px): sections, section pages
 *  - copy buttons on code blocks; hanging indent of wrapped JSON lines;
 *    long JSON outputs shortened to 18 lines with a "Show all" button
 *  - horizontal scrolling wrapper around tables; keyboard access to
 *    anything that scrolls sideways (tables, code blocks); parameter tables
 *    stacked on phones
 *  - line breaks in inline code, example URLs and the web addresses of
 *    references (after "/", not after a hyphen)
 *  - content tabs: the chosen label (curl, Python...) is selected in every
 *    tab set and remembered across pages
 *  - title of the embedded Swagger UI frames
 *  - "On this page" highlight of the current section
 *  - click-to-load videos: the YouTube player is created on click
 *  - printing: details opened, link and video addresses
 */
(function () {
  'use strict';

  var doc = document.documentElement;
  var STORE_KEY = 'sibils-theme';

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function announce(message) {
    var live = document.getElementById('__live-status');
    if (!live) return;
    live.textContent = '';
    window.setTimeout(function () { live.textContent = message; }, 50);
  }

  /* Theme toggle ------------------------------------------------------- */

  var toggles = $$('[data-theme-toggle]');

  function storedTheme() {
    try { return window.localStorage.getItem(STORE_KEY); } catch (e) { return null; }
  }

  function syncToggles() {
    var dark = doc.getAttribute('data-theme') === 'dark';
    toggles.forEach(function (button) {
      button.setAttribute('aria-pressed', dark ? 'true' : 'false');
      button.title = dark ? 'Switch to light theme' : 'Switch to dark theme';
    });
  }

  function setTheme(theme, remember) {
    doc.setAttribute('data-theme', theme);
    if (remember) {
      try { window.localStorage.setItem(STORE_KEY, theme); } catch (e) { /* private mode */ }
    }
    syncToggles();
  }

  toggles.forEach(function (button) {
    button.addEventListener('click', function () {
      setTheme(doc.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    });
  });
  syncToggles();

  // Follow the system while the visitor has not chosen.
  if (window.matchMedia) {
    var systemDark = window.matchMedia('(prefers-color-scheme: dark)');
    var onSystemChange = function (event) {
      var saved = storedTheme();
      if (saved !== 'light' && saved !== 'dark') setTheme(event.matches ? 'dark' : 'light', false);
    };
    if (systemDark.addEventListener) systemDark.addEventListener('change', onSystemChange);
    else if (systemDark.addListener) systemDark.addListener(onSystemChange);
  }

  // Keep several open tabs in sync.
  window.addEventListener('storage', function (event) {
    if (event.key === STORE_KEY && (event.newValue === 'light' || event.newValue === 'dark')) {
      setTheme(event.newValue, false);
    }
  });

  /* Wordmark in the white bar once the red band has left the screen ------ */

  // The white bar is sticky; the red band above it scrolls away. While the
  // band (with its wordmark) is on screen, the bar's title is the text
  // "SIBiLS Documentation"; once the band has gone, .is-stuck shows the
  // wordmark's letters on a red chip instead (CSS), at once. The root's top
  // edge is moved down 1px, so that a band at 0px of the screen counts as
  // gone. A page opened lower down (at an anchor, or by Back) gets the chip
  // from the observer's first report. The observer reports only after a
  // frame is painted, so a jump to the top (Home key, a link to the top)
  // showed both logos for a frame; scroll events run before the paint, so
  // the scroll listener sets the same state in time.
  var band = document.querySelector('.site-header');
  var bar = document.querySelector('.subbar');
  if (band && bar && 'IntersectionObserver' in window) {
    var setStuck = function () {
      bar.classList.toggle('is-stuck', band.getBoundingClientRect().bottom < 1);
    };
    new IntersectionObserver(setStuck, { rootMargin: '-1px 0px 0px 0px' }).observe(band);
    window.addEventListener('scroll', setStuck, { passive: true });
  }

  /* Height of the sticky white bar: --bar-h --------------------------------- */

  // Anchors, focused elements (scroll-padding-top), the sidebar and "On this
  // page" (--sticky-top) stay below the sticky white bar. The CSS assumes its
  // usual 53px (--subbar-h, also the value without JavaScript); the bar is
  // taller when it wraps, with a larger default font size for instance (two
  // rows, 116px, at 150% and 1024px). --bar-h is its measured height. An
  // inline script right after the bar (partials/subbar.html) sets it first,
  // before the browser scrolls to the anchor of the address (the target is
  // further down the page). A ResizeObserver keeps it up to date;
  // onBarResize lists what else depends on it.
  var barHeight = 53;
  var onBarResize = [];
  if (bar) {
    var measureBar = function () {
      var h = Math.ceil(bar.getBoundingClientRect().height);
      if (!h || h === barHeight && doc.style.getPropertyValue('--bar-h')) return;
      barHeight = h;
      doc.style.setProperty('--bar-h', h + 'px');
      onBarResize.forEach(function (callback) { callback(); });
    };
    measureBar();
    if ('ResizeObserver' in window) new ResizeObserver(measureBar).observe(bar);
  }

  // A page opened at an anchor: the page above it still changes after the
  // browser has scrolled to it (web font, this script), and Firefox does not
  // always follow it: it can end up under the bar, or above the screen near
  // the end of a page. Scroll to it once more when the page has loaded, if
  // it is not where it should be. Not if the page has been scrolled in the
  // meantime: a wheel, touch, key or mouse press, or any scroll that takes
  // the anchor further from its place on screen while it stays at the same
  // place in the page (a screen reader, find in page); a change of the page
  // above it moves it in the page too, and the page end can push it down.
  // Not on Back or Reload either, where the browser restores the earlier
  // position.
  var anchor = null;
  try {
    anchor = window.location.hash &&
      document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
  } catch (e) { /* malformed %-escape in the address */ }
  var navEntry = window.performance && performance.getEntriesByType &&
    performance.getEntriesByType('navigation')[0];
  if (anchor && (!navEntry || navEntry.type === 'navigate') && document.readyState !== 'complete') {
    var scrolledAway = false;
    var place = function () { return parseFloat(getComputedStyle(doc).scrollPaddingTop) || 0; };
    var atEnd = function () { return window.scrollY >= doc.scrollHeight - window.innerHeight - 1; };
    var seen = null;
    var noteAnchor = function () {
      var top = anchor.getBoundingClientRect().top;
      seen = { top: top, inPage: top + window.scrollY };
    };
    var onAnchorScroll = function () {
      var top = anchor.getBoundingClientRect().top;
      var samePlaceInPage = Math.abs(top + window.scrollY - seen.inPage) < 1;
      var further = Math.abs(top - place()) > Math.abs(seen.top - place()) + 1;
      var pushedByPageEnd = top > seen.top && atEnd();
      if (samePlaceInPage && further && !pushedByPageEnd) scrolledAway = true;
      noteAnchor();
    };
    var onInput = function () { scrolledAway = true; };
    noteAnchor();
    window.addEventListener('scroll', onAnchorScroll, { passive: true });
    var pageResize = 'ResizeObserver' in window ? new ResizeObserver(noteAnchor) : null;
    if (pageResize) pageResize.observe(document.body);
    ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (type) {
      window.addEventListener(type, onInput, { once: true, passive: true });
    });
    window.addEventListener('load', function () {
      window.requestAnimationFrame(function () {
        window.removeEventListener('scroll', onAnchorScroll);
        if (pageResize) pageResize.disconnect();
        var top = anchor.getBoundingClientRect().top;
        if (!scrolledAway && (top < place() - 2 || top > place() + 2 && !atEnd())) anchor.scrollIntoView();
      });
    }, { once: true });
  }

  /* Dialogs: menu drawer (search.js handles the search dialog) ----------- */

  // Close any of our dialogs with its close buttons or a click on the backdrop.
  $$('dialog').forEach(function (dialog) {
    $$('[data-dialog-close]', dialog).forEach(function (button) {
      button.addEventListener('click', function () { dialog.close(); });
    });
    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) dialog.close();
    });
  });

  var drawer = document.getElementById('__drawer');
  var menuButtons = $$('[data-drawer-open]');
  // A heading link of the current page (.snav__toc) closes the drawer, then
  // goes to the heading. Going there before the drawer has closed (and given
  // the focus back to the menu button) leaves the heading far down the screen.
  if (drawer) {
    drawer.addEventListener('click', function (event) {
      var link = event.target.closest && event.target.closest('.snav__toc a');
      if (!link || !drawer.open) return;
      event.preventDefault();
      drawer.addEventListener('close', function () {
        window.setTimeout(function () {
          var target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
          if (window.location.hash === link.hash && target) target.scrollIntoView();
          else window.location.hash = link.hash;
        }, 0);
      }, { once: true });
      drawer.close();
    });
  }

  // The menu opens at its top (the sections) when the current page fits
  // below; else it scrolls as little as needed to show the current page and,
  // while the current page stays on screen, the page's headings listed under
  // it.
  var scrollDrawer = function () {
    drawer.scrollTop = 0;
    var current = drawer.querySelector('[aria-current="page"]');
    if (!current) return;
    var bottom = drawer.getBoundingClientRect().bottom;
    var head = drawer.querySelector('.drawer__head');
    var top = head ? head.getBoundingClientRect().bottom : drawer.getBoundingClientRect().top;
    var next = current.nextElementSibling;
    var last = next && next.classList.contains('snav__toc') ? next : current;
    var link = current.getBoundingClientRect();
    var needLink = link.bottom - bottom;
    var needHeadings = last.getBoundingClientRect().bottom + 8 - bottom;
    var keepLink = link.top - 8 - top;
    drawer.scrollTop = Math.max(0, needLink, Math.min(needHeadings, keepLink));
  };

  if (drawer && typeof drawer.showModal === 'function') {
    menuButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        drawer.showModal();
        button.setAttribute('aria-expanded', 'true');
        scrollDrawer();
      });
    });
    drawer.addEventListener('close', function () {
      menuButtons.forEach(function (button) {
        button.setAttribute('aria-expanded', 'false');
      });
      // The button is in the sticky bar, always on screen: focusing it must
      // not scroll the page (Chromium scrolls to show a focused element that
      // lies in the scroll-padding-top area).
      if (menuButtons[0] && menuButtons[0].offsetParent !== null) menuButtons[0].focus({ preventScroll: true });
    });
    // Leaving the page with the menu open (by one of its links): close it,
    // so that Back, which can restore the page as it was (back/forward
    // cache), shows the page and not the open menu.
    window.addEventListener('pagehide', function () { if (drawer.open) drawer.close(); });
    // The drawer is for small screens only.
    if (window.matchMedia) {
      var wide = window.matchMedia('(min-width: 1024px)');
      var onWide = function (event) { if (event.matches && drawer.open) drawer.close(); };
      if (wide.addEventListener) wide.addEventListener('change', onWide);
      else if (wide.addListener) wide.addListener(onWide);
    }
  } else {
    // No <dialog> support: keep the main navigation visible instead.
    doc.classList.add('no-dialog');
    menuButtons.forEach(function (button) { button.hidden = true; });
  }

  /* Copy buttons on code blocks ------------------------------------------ */

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.top = '-1000px';
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(area);
      if (ok) resolve(); else reject(new Error('copy failed'));
    });
  }

  var copyBlocks = [];
  $$('.content .highlight').forEach(function (block) {
    var code = block.querySelector('pre code') || block.querySelector('pre');
    if (!code) return;
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-btn';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    var timer = null;
    button.addEventListener('click', function () {
      var clone = code.cloneNode(true);
      $$('.linenos, .linenodiv', clone).forEach(function (n) { n.parentNode.removeChild(n); });
      var text = clone.textContent.replace(/\n$/, '');
      copyText(text).then(function () {
        button.textContent = 'Copied';
        button.classList.add('is-copied');
        announce('Code copied to clipboard');
      }, function () {
        button.textContent = 'Press Ctrl+C';
        announce('Copy failed: select the code and press Ctrl+C');
      }).then(function () {
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
          button.textContent = 'Copy';
          button.classList.remove('is-copied');
        }, 2000);
      });
    });
    block.appendChild(button);

    var lines = code.textContent.replace(/\n$/, '').split('\n');
    copyBlocks.push({ block: block, pre: block.querySelector('pre'), button: button, lines: lines });
    if (lines.length === 1) block.classList.add('is-oneline');

    // Wrapped JSON and BibTeX (and shell commands on phones) continue right
    // of their first line: --ind is the line's indentation (line spans, see CSS).
    if (block.classList.contains('language-json') || block.classList.contains('language-bash') ||
        block.classList.contains('language-bibtex')) {
      $$('code > span[id^="__span"]', block).forEach(function (line) {
        line.style.setProperty('--ind', /^ */.exec(line.textContent)[0].length);
      });
    }

    // Long JSON outputs: the first 18 lines, and a button to show all of
    // them. Copy still copies the whole block.
    var n = lines.length;
    if (block.classList.contains('language-json') && n > 24) {
      block.classList.add('is-clamped');
      var more = document.createElement('button');
      more.type = 'button';
      more.className = 'expand-btn';
      more.setAttribute('aria-expanded', 'false');
      more.textContent = 'Show all ' + n + ' lines';
      more.addEventListener('click', function () {
        var open = !block.classList.toggle('is-clamped');
        more.setAttribute('aria-expanded', String(open));
        more.textContent = open ? 'Show fewer lines' : 'Show all ' + n + ' lines';
        if (!open) more.scrollIntoView({ block: 'nearest' });
      });
      block.appendChild(more);
    }
  });

  /* Tables: scroll horizontally inside a wrapper ------------------------- */

  // Text of the nearest heading before `el` in the content (permalink sign
  // removed), or ''.
  function headingBefore(el) {
    for (var node = el; node && !(node.classList && node.classList.contains('content')); node = node.parentElement) {
      for (var sib = node.previousElementSibling; sib; sib = sib.previousElementSibling) {
        if (/^H[1-6]$/.test(sib.tagName)) {
          var clone = sib.cloneNode(true);
          $$('.headerlink', clone).forEach(function (n) { n.parentNode.removeChild(n); });
          return clone.textContent.replace(/\s+/g, ' ').trim();
        }
      }
    }
    return '';
  }

  var wraps = [];
  var wrapNames = {};
  $$('.content table').forEach(function (table) {
    if (table.closest('.highlighttable') || table.classList.contains('highlighttable')) return;
    var wrap = table.parentElement;
    if (!wrap || !wrap.classList.contains('table-wrap')) {
      wrap = document.createElement('div');
      wrap.className = 'table-wrap';
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    }
    // Name, used when the table scrolls: its caption, else the heading above
    // it; a number tells apart several tables under one heading.
    var caption = table.querySelector('caption');
    var base = (caption && caption.textContent.trim()) || headingBefore(wrap) || 'Table';
    wrapNames[base] = (wrapNames[base] || 0) + 1;
    wrap.setAttribute('data-name', base + (wrapNames[base] > 1 ? ' (table ' + wrapNames[base] + ')' : ' (table)'));
    wraps.push(wrap);

    // Phones: a column of running text keeps a readable width (CSS .is-prose)
    // in tables of three columns or more.
    var head = table.tHead && table.tHead.rows[0];
    var body = table.tBodies[0];

    // Parameter and field tables (first header "Parameter" or "Field", and a
    // "Description" column) are stacked on phones (CSS table.is-params): each
    // cell gets its header as a label. ARIA roles keep the table semantics,
    // which Safari drops when the display of table elements changes.
    if (head && body && !table.closest('.vocab-table')) {
      var names = Array.prototype.map.call(head.cells, function (cell) { return cell.textContent.trim(); });
      if (/^(Parameter|Field)$/.test(names[0]) && names.indexOf('Description') > 0) {
        table.classList.add('is-params');
        table.setAttribute('role', 'table');
        [table.tHead].concat(Array.prototype.slice.call(table.tBodies)).forEach(function (group) {
          group.setAttribute('role', 'rowgroup');
        });
        Array.prototype.forEach.call(table.rows, function (row) {
          row.setAttribute('role', 'row');
          Array.prototype.forEach.call(row.cells, function (cell, i) {
            cell.setAttribute('role', cell.tagName === 'TH' ? 'columnheader' : 'cell');
            if (cell.tagName === 'TD') cell.setAttribute('data-label', names[i] || '');
          });
        });
      }
    }
    if (!head || !body || head.cells.length < 3) return;
    for (var c = 0; c < head.cells.length; c++) {
      var total = 0, n = 0;
      for (var r = 0; r < body.rows.length; r++) {
        var cell = body.rows[r].cells[c];
        if (cell) { total += cell.textContent.trim().length; n++; }
      }
      if (n && total / n >= 40) head.cells[c].classList.add('is-prose');
    }
  });

  // Anything that scrolls sideways gets keyboard focus, so it can be scrolled
  // without a mouse; a table also gets a name.
  var pres = $$('.content pre');
  function updateScrollers() {
    wraps.forEach(function (wrap) {
      if (wrap.scrollWidth > wrap.clientWidth + 1) {
        wrap.tabIndex = 0;
        wrap.setAttribute('role', 'region');
        wrap.setAttribute('aria-label', wrap.getAttribute('data-name') + ', scrolls horizontally');
      } else {
        wrap.removeAttribute('tabindex');
        wrap.removeAttribute('role');
        wrap.removeAttribute('aria-label');
      }
    });
    pres.forEach(function (pre) {
      if (pre.scrollWidth > pre.clientWidth + 1) pre.tabIndex = 0;
      else pre.removeAttribute('tabindex');
    });
    updateCopyClash();
  }
  // Touch screens show the copy button all the time: blocks whose first
  // lines would run under it get a band above the code (.has-copy-clash).
  // Characters are counted at 0.6em, a little wider than most monospace
  // fonts, so the check errs on the side of adding the band.
  var touch = window.matchMedia ? window.matchMedia('(hover: none)') : null;
  function updateCopyClash() {
    copyBlocks.forEach(function (c) {
      c.block.classList.remove('has-copy-clash');
      if (!touch || !touch.matches || !c.pre || !c.pre.offsetWidth) return;
      var cs = getComputedStyle(c.pre);
      var lh = parseFloat(cs.lineHeight), padT = parseFloat(cs.paddingTop), padL = parseFloat(cs.paddingLeft);
      var cw = parseFloat(cs.fontSize) * 0.6;
      var rows = Math.max(1, Math.ceil((c.button.offsetTop + c.button.offsetHeight - padT) / lh));
      var free = c.button.offsetLeft - padL - 8;
      if (c.lines.slice(0, rows).some(function (l) { return l.replace(/\s+$/, '').length * cw > free; })) {
        c.block.classList.add('has-copy-clash');
      }
    });
  }
  var resizeQueued = false;
  var queueUpdate = function () {
    if (resizeQueued) return;
    resizeQueued = true;
    window.requestAnimationFrame(function () { resizeQueued = false; updateScrollers(); });
  };
  if (wraps.length || pres.length) {
    updateScrollers();
    window.addEventListener('resize', queueUpdate);
    // Blocks in a tab or a closed <details> have no width until shown.
    document.addEventListener('change', function (event) {
      if (event.target.matches && event.target.matches('.tabbed-set > input')) queueUpdate();
    });
    document.addEventListener('toggle', queueUpdate, true);
  }

  /* Line breaks in inline code and example URLs ------------------------- */

  // Line-break opportunities after "/", "?" and "&" (and "_" in table cells),
  // never right after "https://".
  function breakAfterSeparators(el, cell) {
    var text = el.textContent;
    var re = cell ? /(\/+|[?&_])/ : /(\/+|[?&])/;
    if (!re.test(text)) return;
    var parts = text.split(re);
    el.textContent = '';
    parts.forEach(function (part, i) {
      if (!part) return;
      el.appendChild(document.createTextNode(part));
      if (i % 2 && !(part.charAt(0) === '/' && /:$/.test(parts[i - 1] || ''))) {
        el.appendChild(document.createElement('wbr'));
      }
    });
  }
  // Short chips ("POST /batch", "Content-Type") never break; nor do cell
  // values shorter than 48 characters, such as base URLs (the table scrolls
  // instead).
  $$('.content code').forEach(function (code) {
    if (code.closest('pre') || code.children.length) return;
    var len = code.textContent.length;
    var cell = !!code.closest('th, td');
    if (len <= 24 || (cell && len < 48)) code.classList.add('is-nowrap');
    else breakAfterSeparators(code, cell);
  });
  // A paragraph that is only a URL link (an example request) reads as code.
  $$('.content p > a[href^="http"]').forEach(function (a) {
    if (a.children.length || !/^https?:\/\//.test(a.textContent.trim())) return;
    if (a.parentElement.textContent.trim() !== a.textContent.trim()) return;
    a.classList.add('is-url');
    breakAfterSeparators(a, false);
  });

  /* Content tabs: one choice for every tab set, remembered ---------------- */

  // Choosing "Python" in one set selects "Python" in every set that has that
  // label, on this page and on the next ones (localStorage). The set that was
  // clicked stays where it is on screen while the others change height.
  var TAB_KEY = 'sibils-tab';
  function tabLabel(input) {
    var label = input.parentNode.querySelector('.tabbed-labels > label[for="' + input.id + '"]');
    return label ? label.textContent.trim() : '';
  }
  function selectTab(text, except) {
    $$('.content .tabbed-set').forEach(function (set) {
      if (set === except) return;
      $$('.tabbed-labels > label', set).some(function (label) {
        if (label.textContent.trim() !== text) return false;
        var input = document.getElementById(label.htmlFor);
        if (input && !input.checked) input.checked = true;
        return true;
      });
    });
  }
  if ($$('.content .tabbed-set').length) {
    var savedTab = null;
    try { savedTab = window.localStorage.getItem(TAB_KEY); } catch (e) { /* private mode */ }
    if (savedTab) { selectTab(savedTab, null); queueUpdate(); }
    document.addEventListener('change', function (event) {
      var input = event.target;
      if (!input.matches || !input.matches('.content .tabbed-set > input')) return;
      var set = input.parentNode;
      var text = tabLabel(input);
      if (!text) return;
      var before = set.getBoundingClientRect().top;
      selectTab(text, set);
      window.scrollBy(0, set.getBoundingClientRect().top - before);
      try { window.localStorage.setItem(TAB_KEY, text); } catch (e) { /* private mode */ }
      queueUpdate();
    });
  }

  /* Embedded Swagger UI (mkdocs-swagger-ui-tag): name the frames ---------- */

  $$('iframe.swagger-ui-iframe:not([title])').forEach(function (frame) {
    frame.title = 'Interactive API reference (Swagger UI)';
  });

  /* "On this page": highlight the section being read --------------------- */

  var tocLinks = $$('.toc a[href^="#"]');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var entries = [];
    tocLinks.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute('href').slice(1));
      var heading = document.getElementById(id);
      if (heading) entries.push({ heading: heading, link: link });
    });

    var activeLink = null;
    var setActive = function (link) {
      if (link === activeLink) return;
      if (activeLink) {
        activeLink.classList.remove('is-active');
        activeLink.removeAttribute('aria-current');
      }
      activeLink = link;
      if (link) {
        link.classList.add('is-active');
        link.setAttribute('aria-current', 'true');
        // Keep the active entry in view when the TOC is taller than its box.
        var box = link.closest('.toc');
        if (box && box.scrollHeight > box.clientHeight) {
          var t = link.getBoundingClientRect().top - box.getBoundingClientRect().top;
          if (t < 0 || t + link.offsetHeight > box.clientHeight) box.scrollTop += t - box.clientHeight / 3;
        }
      }
    };

    // The current section is the last heading above a line just under the
    // sticky sub-bar; the observer tells us when headings cross that line.
    // Both follow the bar's height (--bar-h above).
    var offset = barHeight + 24;
    var update = function () {
      var current = null;
      for (var i = 0; i < entries.length; i++) {
        // A heading hidden by a filter (js/vocab-filter.js) has no box: skip it.
        if (!entries[i].heading.getClientRects().length) continue;
        if (entries[i].heading.getBoundingClientRect().top - offset <= 1) current = entries[i];
        else break;
      }
      // At the very bottom of the page, the last section is the current one.
      if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 2 && entries.length) {
        current = entries[entries.length - 1];
      }
      setActive(current ? current.link : null);
    };

    var observer = null;
    var observeHeadings = function () {
      offset = barHeight + 24;
      if (observer) observer.disconnect();
      observer = new IntersectionObserver(update, {
        rootMargin: '-' + offset + 'px 0px -40% 0px',
        threshold: [0, 1]
      });
      entries.forEach(function (entry) { observer.observe(entry.heading); });
    };
    observeHeadings();
    onBarResize.push(function () { observeHeadings(); update(); });
    window.addEventListener('hashchange', function () { window.requestAnimationFrame(update); });
    window.addEventListener('scrollend', update);
    update();
  }

  /* Click-to-load videos --------------------------------------------------- */

  // <div class="video" data-embed="PLAYER URL" data-title="..."><a href="VIDEO PAGE">...</a></div>
  // shows a local play button; the player iframe is created only when the
  // reader clicks, so the page contacts the video host only then. Without
  // JavaScript the link opens the video page.
  $$('.content .video[data-embed] > a').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var box = link.parentNode;
      var frame = document.createElement('iframe');
      e.preventDefault();
      frame.src = box.getAttribute('data-embed');
      frame.title = box.getAttribute('data-title') || link.textContent.trim();
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.allowFullscreen = true;
      box.replaceChild(frame, link);
      frame.focus();
    });
  });

  /* Printing ---------------------------------------------------------------- */

  // The print style adds the address after external links: not after links
  // whose text already is the address.
  var bare = function (url) {
    return url.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/\/$/, '');
  };
  $$('.content a[href^="http"]').forEach(function (a) {
    if (bare(a.textContent) === bare(a.getAttribute('href'))) a.classList.add('is-bare');
  });
  // Videos print as their address.
  $$('.content .video').forEach(function (box) {
    var media = box.querySelector('source[src], video[src], iframe[src], a[href]');
    if (media) box.setAttribute('data-src', media.src || media.href || media.getAttribute('src'));
  });

  // Collapsed blocks are opened for printing.
  var closedForPrint = [];
  window.addEventListener('beforeprint', function () {
    closedForPrint = $$('.content details:not([open])');
    closedForPrint.forEach(function (d) { d.open = true; });
  });
  window.addEventListener('afterprint', function () {
    closedForPrint.forEach(function (d) { d.open = false; });
    closedForPrint = [];
  });

  /* Web addresses in references ------------------------------------------ */

  // A web address shown in a reference (a bare link, marked .is-bare above)
  // breaks after a "/" (<wbr>), not after a hyphen, where the break would
  // read as a hyphenated word ("news- | releases"): each hyphen is kept with
  // the next character (span.url-nobr). Done here rather than in the hook:
  // tags in the link text would put spaces into the address in the search
  // index.
  $$('.content .biblio a.is-bare, .content .admonition.cite a.is-bare').forEach(function (a) {
    var parts = a.textContent.match(/-+[^-\/]|\/|[^-\/]+|-+/g) || [];
    a.textContent = '';
    parts.forEach(function (part) {
      var node;
      if (/^-+[^-\/]$/.test(part)) {
        node = document.createElement('span');
        node.className = 'url-nobr';
        node.textContent = part;
      } else {
        node = document.createTextNode(part);
      }
      a.appendChild(node);
      if (part === '/') a.appendChild(document.createElement('wbr'));
    });
  });
})();
