/*
 * SIBiLS home page: current collection counts from the SIBiLS API.
 *
 * partials/counts.html (the only page that loads this file) is built with a
 * round lower bound of each count, in grey (dd.is-approx) and preceded by a
 * visually hidden "at least ". This script reads the API once and writes each
 * exact number in place, in the normal text colour. Each value is replaced
 * only if its own count is valid: an integer not below data-min (half the
 * round number, written by the build). If the API is slower than
 * TIMEOUT_MS, fails, or returns anything unexpected, the approximate values
 * stay: no message, no retry, nothing announced to screen readers.
 */
(function () {
  'use strict';

  // The API answers in about 0.1 s; 3 s leaves room for a new TLS connection
  // on a slow mobile network. Later, a number changing under the reader's eyes
  // is more distracting than useful, and the approximate value is true anyway.
  var TIMEOUT_MS = 3000;

  var box = document.querySelector('[data-count-url]');
  if (!box || !window.fetch || !window.AbortController || !window.Intl) return;
  var cells = box.querySelectorAll('dd[data-count]');
  if (!cells.length) return;

  // Same format as the build (Python "{:,}"): 41,438,260.
  var format = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format;

  // A count is an integer, at least data-min: a 0 or a partial count while
  // the API is being updated would contradict the "at least" just shown.
  // JSON "-0" is read as 0 (Intl writes "-0").
  function count(entry, cell) {
    var n = entry && entry.all;
    var min = Math.max(0, Number(cell.getAttribute('data-min')) || 0);
    return Number.isSafeInteger(n) && n >= min ? n + 0 : null;
  }

  var controller = new AbortController();
  var timer = window.setTimeout(function () { controller.abort(); }, TIMEOUT_MS);

  // A simple CORS request (GET, no custom header: no preflight), without
  // cookies; the API sees the site's origin as Referer, never the page path.
  window.fetch(box.getAttribute('data-count-url'), {
    mode: 'cors',
    credentials: 'omit',
    referrerPolicy: 'strict-origin',
    signal: controller.signal
  }).then(function (response) {
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return response.json();
  }).then(function (data) {
    // An answer completed after the timeout is ignored (abort() also
    // rejects a body still being read).
    if (controller.signal.aborted) return;
    window.clearTimeout(timer);
    if (!data || data.success !== true || !data.count || typeof data.count !== 'object') return;
    Array.prototype.forEach.call(cells, function (cell) {
      var n = count(data.count[cell.getAttribute('data-count')], cell);
      if (n === null) return;
      cell.textContent = format(n);  // also removes the hidden "at least "
      cell.classList.remove('is-approx');
    });
  }).catch(function () {
    // Network error, CORS refusal, HTTP error, invalid JSON or timeout: the
    // approximate values stay.
    window.clearTimeout(timer);
  });
})();
