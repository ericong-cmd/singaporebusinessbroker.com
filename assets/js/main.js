/* Singapore Business Broker — site runtime. No dependencies. */
(function () {
  'use strict';

  var WA_NUMBER = '6589518821';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.body.classList.add('loaded');

  /* ---------- Sticky header condense ---------- */
  var header = document.querySelector('.site-header');
  var sentinel = document.getElementById('top-sentinel');
  if (header && sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      header.classList.toggle('condensed', !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.querySelector('.menu-btn');
  var mobileNav = document.querySelector('.mobile-nav');
  if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  /* ---------- Scroll reveals ---------- */
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in-view');
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in-view'); });
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.faq-q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var open = item.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      var panel = item.querySelector('.faq-a');
      if (panel) panel.hidden = !open;
    });
  });

  /* ---------- Sticky mobile action bar (appears past the hero) ---------- */
  var bar = document.querySelector('.action-bar');
  if (bar) {
    document.body.classList.add('has-bar');
    var heroEl = document.querySelector('.hero, .page-hero');
    if (heroEl && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        bar.classList.toggle('up', !entries[0].isIntersecting);
      }, { threshold: 0 }).observe(heroEl);
    } else {
      bar.classList.add('up');
    }
  }

  /* ---------- Sale-readiness scorecard ---------- */
  var form = document.getElementById('readiness');
  if (!form) return;

  /* Each question carries a weight; option values are 0..1 of that weight.
     Total weight = 100. Gap copy fires when the answer scores below `flag`. */
  var QUESTIONS = [
    { name: 'accounts',  w: 14, flag: 0.6, gap: 'Get at least three years of clean, comparable financial statements together — buyers price uncertainty as risk, and unaudited or restated accounts are the single most common reason a price gets cut at due diligence.' },
    { name: 'ebitda',    w: 12, flag: 0.6, gap: 'Normalise your earnings: separate genuine business profit from owner salary, personal expenses and one-offs. Until adjusted EBITDA is defensible on paper, any valuation is guesswork.' },
    { name: 'owner',     w: 14, flag: 0.6, gap: 'Reduce owner dependence. If key customer relationships, pricing decisions or technical knowledge sit only with you, buyers discount the price or push more of it into an earn-out.' },
    { name: 'customers', w: 10, flag: 0.6, gap: 'Customer concentration is a valuation issue. Where one client is a large share of revenue, buyers want contracts, history and a plan for what happens if that client leaves.' },
    { name: 'contracts', w: 9,  flag: 0.6, gap: 'Put the paperwork in order: customer and supplier contracts, the tenancy, licences, and any agreement with a change-of-control clause. Missing documents stall due diligence and cost momentum.' },
    { name: 'statutory', w: 9,  flag: 0.6, gap: 'Bring statutory records current — ACRA filings, registers of members and controllers, board resolutions, and properly stamped past share transfers. These are checked early and are slow to fix late.' },
    { name: 'team',      w: 10, flag: 0.6, gap: 'A second line of management materially raises value. Buyers pay more for a business that keeps running after the founder steps back.' },
    { name: 'growth',    w: 8,  flag: 0.6, gap: 'Be ready to evidence the trend. Whether revenue is rising or flat, a buyer wants a documented explanation and a credible forward view, not a verbal one.' },
    { name: 'reason',    w: 8,  flag: 0.6, gap: 'Be clear about why you are selling and what you want afterwards. Buyers test this question, and an uncertain answer reads as a seller who may withdraw.' },
    { name: 'timeline',  w: 6,  flag: 0.6, gap: 'A structured sale runs six to eight months. If your timeline is shorter than that, expect a narrower buyer pool and a lower price.' }
  ];

  var BANDS = [
    { min: 80, label: 'Sale-ready', summary: 'Your business looks ready to go to market. At this level the priority is running a competitive process — reaching several capable buyers at once rather than negotiating with the first one who calls.' },
    { min: 60, label: 'Nearly ready', summary: 'The foundations are there. A focused two to three months of preparation on the gaps below would likely change both the price you achieve and the certainty of getting to completion.' },
    { min: 40, label: 'Preparation needed', summary: 'Going to market now would probably cost you money. The gaps below are all fixable, usually within six to twelve months, and fixing them before buyers see the business is far cheaper than fixing them during due diligence.' },
    { min: 0,  label: 'Early stage', summary: 'A sale is premature today, and that is useful to know now rather than after a failed process. Treat the gaps below as a twelve to twenty-four month value-building plan.' }
  ];

  var result = document.getElementById('score-out');
  var errEl = document.getElementById('score-error');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var score = 0, answered = 0, gaps = [];
    QUESTIONS.forEach(function (q) {
      var picked = form.querySelector('input[name="' + q.name + '"]:checked');
      if (!picked) return;
      answered++;
      var v = parseFloat(picked.value);
      score += v * q.w;
      if (v < q.flag) gaps.push(q.gap);
    });

    if (answered < QUESTIONS.length) {
      if (errEl) {
        errEl.textContent = 'Please answer all ' + QUESTIONS.length + ' questions — ' +
          (QUESTIONS.length - answered) + ' still to go.';
        errEl.hidden = false;
      }
      var firstMissing = QUESTIONS.filter(function (q) {
        return !form.querySelector('input[name="' + q.name + '"]:checked');
      })[0];
      if (firstMissing) {
        var el = form.querySelector('input[name="' + firstMissing.name + '"]');
        if (el) el.closest('.q-block').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
      }
      return;
    }
    if (errEl) errEl.hidden = true;

    var pct = Math.round(score);
    var band = BANDS.filter(function (b) { return pct >= b.min; })[0];

    document.getElementById('score-num').innerHTML = pct + '<small>&#8202;/&#8202;100</small>';
    document.getElementById('score-band').textContent = band.label;
    document.getElementById('score-summary').textContent = band.summary;

    var list = document.getElementById('score-gaps');
    var heading = document.getElementById('score-gaps-h');
    list.innerHTML = '';
    if (gaps.length) {
      heading.hidden = false;
      gaps.slice(0, 5).forEach(function (text) {
        var li = document.createElement('li');
        li.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
          'stroke-width="2.2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg><span></span>';
        li.querySelector('span').textContent = text;
        list.appendChild(li);
      });
    } else {
      heading.hidden = true;
    }

    result.classList.add('show');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        result.classList.add('visible');
        var fill = document.getElementById('score-meter');
        if (fill) fill.style.width = pct + '%';
      });
    });

    var msg = 'Hi, I completed the sale-readiness scorecard on singaporebusinessbroker.com.\n' +
      'Score: ' + pct + '/100 (' + band.label + ')\n' +
      'I’d like a confidential conversation about what it would take to get my business sale-ready.';
    var waLink = document.getElementById('score-wa');
    if (waLink) waLink.href = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(msg);

    var mailLink = document.getElementById('score-mail');
    if (mailLink) {
      mailLink.href = 'mailto:eric.ong@thefundingassembly.com' +
        '?subject=' + encodeURIComponent('Sale-readiness scorecard result') +
        '&body=' + encodeURIComponent(msg);
    }

    result.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
  });

  form.addEventListener('reset', function () {
    result.classList.remove('show', 'visible');
    if (errEl) errEl.hidden = true;
    var fill = document.getElementById('score-meter');
    if (fill) fill.style.width = '0';
  });
})();
