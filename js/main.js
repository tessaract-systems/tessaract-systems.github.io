/* Tessaract Systems — site behaviour
   -------------------------------------------------------------------------
   Every block guards its own elements so a missing node on one page can
   never stop the blocks below it from running.
   ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var CONTACT_EMAIL = 'info.tessaractsystems@gmail.com';

  /* ---------------------------------------------------------------------
     1. Scroll-driven layer stack
     --------------------------------------------------------------------- */
  (function () {
    var stack = document.querySelector('.stack');
    if (!stack) return;

    var shells = Array.prototype.slice.call(stack.querySelectorAll('.layer-shell'));
    var steps = Array.prototype.slice.call(document.querySelectorAll('[data-step]'));
    if (!steps.length) return;

    var stacked = window.matchMedia('(max-width: 860px)');
    var current = 0;

    var setState = function (state, highlight) {
      stack.setAttribute('data-state', String(state));
      shells.forEach(function (shell) {
        var n = Number(shell.getAttribute('data-layer'));
        shell.classList.toggle('is-ghost', state > 0 && n > state);
        shell.classList.toggle('is-active', highlight && n === state);
      });
    };

    var applyLayout = function () {
      if (stacked.matches) setState(4, false);
      else setState(current, true);
    };

    if (!('IntersectionObserver' in window)) {
      // No observer: show the finished stack rather than the folded one.
      current = 4;
      applyLayout();
      return;
    }

    var visible = new Map();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.set(entry.target, entry);
        else visible.delete(entry.target);
      });

      // Pick the intersecting step whose box centre sits nearest the viewport
      // centre. Entry order is not guaranteed, so never trust the last entry.
      var mid = window.innerHeight / 2;
      var best = null;
      var bestDistance = Infinity;

      visible.forEach(function (entry) {
        var box = entry.target.getBoundingClientRect();
        var distance = Math.abs(box.top + box.height / 2 - mid);
        if (distance < bestDistance) {
          bestDistance = distance;
          best = entry.target;
        }
      });

      if (best) current = Number(best.getAttribute('data-step'));
      if (!stacked.matches) setState(current, true);
    }, { rootMargin: '-45% 0px -45% 0px' });

    steps.forEach(function (el) { observer.observe(el); });

    if (typeof stacked.addEventListener === 'function') stacked.addEventListener('change', applyLayout);
    else if (typeof stacked.addListener === 'function') stacked.addListener(applyLayout);

    applyLayout();
  }());

  /* ---------------------------------------------------------------------
     2. Header shadow on scroll
     --------------------------------------------------------------------- */
  (function () {
    var header = document.querySelector('.site-header');
    if (!header) return;

    var ticking = false;
    var update = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
      ticking = false;
    };

    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    update();
  }());

  /* ---------------------------------------------------------------------
     3. Mobile navigation
     --------------------------------------------------------------------- */
  (function () {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.getElementById('site-nav');
    if (!toggle || !nav) return;

    var setNav = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    };

    toggle.addEventListener('click', function () {
      setNav(toggle.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setNav(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setNav(false);
        toggle.focus();
      }
    });

    document.addEventListener('click', function (e) {
      if (!nav.classList.contains('is-open')) return;
      if (nav.contains(e.target) || toggle.contains(e.target)) return;
      setNav(false);
    });
  }());

  /* ---------------------------------------------------------------------
     4. Booking button
     Give the link a data-booking="https://cal.com/..." value and it becomes
     a real scheduling link. Without one it simply focuses the form.
     --------------------------------------------------------------------- */
  (function () {
    var link = document.getElementById('book-link');
    if (!link) return;

    var url = (link.getAttribute('data-booking') || '').trim();

    if (url) {
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener';
      return;
    }

    link.addEventListener('click', function (e) {
      var name = document.getElementById('f-name');
      if (!name) return;
      e.preventDefault();
      name.scrollIntoView({ block: 'center', behavior: 'smooth' });
      name.focus({ preventScroll: true });
    });
  }());

  /* ---------------------------------------------------------------------
     5. Contact form
     Posts to the configured endpoint. If no key has been set yet it falls
     back to opening the visitor's mail client, so a lead is never silently
     dropped.
     --------------------------------------------------------------------- */
  (function () {
    var form = document.getElementById('contact-form');
    var status = document.getElementById('form-status');
    if (!form || !status) return;

    var button = form.querySelector('button[type="submit"]');
    var keyField = form.querySelector('[name="access_key"]');
    var key = keyField ? keyField.value.trim() : '';
    var endpointReady = key && key.indexOf('YOUR-') !== 0;

    var setStatus = function (text, ok) {
      status.textContent = text;
      status.classList.toggle('is-ok', !!ok);
    };

    var composeBody = function (data) {
      var lines = [data.get('message') || '', ''];
      if (data.get('stage')) lines.push('Where they are: ' + data.get('stage'));
      lines.push('— ' + (data.get('name') || ''));
      if (data.get('company')) lines.push(data.get('company'));
      lines.push(data.get('email') || '');
      return lines.join('\n');
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var fields = ['name', 'email', 'message'].map(function (n) { return form.elements[n]; });
      var invalid = fields.filter(function (f) { return f && !f.checkValidity(); });

      fields.forEach(function (f) {
        if (f) f.setAttribute('aria-invalid', String(invalid.indexOf(f) > -1));
      });

      if (invalid.length) {
        setStatus(
          invalid[0].name === 'email' && invalid[0].value
            ? 'Enter a valid work email, for example name@company.com.'
            : 'Fill in your name, email and message so we can reply.',
          false
        );
        invalid[0].focus();
        return;
      }

      var data = new FormData(form);

      // Silently accept and drop anything that filled the honeypot.
      if (data.get('botcheck')) {
        setStatus('Thanks, your message has been sent.', true);
        form.reset();
        return;
      }

      if (!endpointReady) {
        var subject = 'Discovery call: ' + (data.get('company') || data.get('name'));
        window.location.href = 'mailto:' + CONTACT_EMAIL +
          '?subject=' + encodeURIComponent(subject) +
          '&body=' + encodeURIComponent(composeBody(data));
        setStatus('Your email app should open with the message ready to send.', true);
        return;
      }

      if (button) {
        button.disabled = true;
        button.textContent = 'Sending…';
      }
      setStatus('Sending your message…', true);

      fetch(form.action, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: data
      })
        .then(function (res) { return res.json().catch(function () { return {}; }); })
        .then(function (result) {
          if (result && result.success) {
            form.reset();
            setStatus('Thanks. Your message is with us and we\'ll reply within one business day.', true);
          } else {
            throw new Error('rejected');
          }
        })
        .catch(function () {
          setStatus('That didn\'t send. Please email ' + CONTACT_EMAIL + ' and we\'ll pick it up straight away.', false);
        })
        .then(function () {
          if (button) {
            button.disabled = false;
            button.textContent = 'Send message';
          }
        });
    });
  }());

  /* ---------------------------------------------------------------------
     6. Portfolio carousel
     Native scroll-snap does the moving; this only drives the buttons, the
     counter and the progress bar, and reads its card count from the DOM.
     With JS off the track is still a scrollable, swipeable list.
     --------------------------------------------------------------------- */
  (function () {
    var track = document.getElementById('work-track');
    if (!track) return;

    var allCards = Array.prototype.slice.call(track.children);
    if (!allCards.length) return;

    // Only the cards the active filter leaves on screen.
    var cards = allCards;

    var prev = document.querySelector('[data-carousel-prev]');
    var next = document.querySelector('[data-carousel-next]');
    var current = document.querySelector('[data-carousel-current]');
    var total = document.querySelector('[data-carousel-total]');
    var bar = document.querySelector('.carousel-progress-bar');

    var pad = function (n) { return n < 10 ? '0' + n : String(n); };

    var relabel = function () {
      if (total) total.textContent = pad(cards.length);
      cards.forEach(function (card, i) {
        card.setAttribute('role', 'group');
        card.setAttribute('aria-roledescription', 'slide');
        card.setAttribute('aria-label', (i + 1) + ' of ' + cards.length);
      });
    };
    relabel();

    var step = function () {
      if (cards.length < 2) return cards[0].offsetWidth;
      return cards[1].offsetLeft - cards[0].offsetLeft;
    };

    var maxScroll = function () {
      return Math.max(0, track.scrollWidth - track.clientWidth);
    };

    // How many whole cards fit in view; used so the buttons page sensibly on
    // wide screens instead of nudging one card at a time.
    var perView = function () {
      var s = step();
      return s > 0 ? Math.max(1, Math.floor((track.clientWidth + 1) / s)) : 1;
    };

    var indexFromScroll = function () {
      var s = step();
      if (s <= 0) return 0;
      return Math.min(cards.length - 1, Math.round(track.scrollLeft / s));
    };

    var render = function () {
      var max = maxScroll();
      var i = indexFromScroll();
      // Sub-pixel card widths leave a few px of slack at either end.
      var atStart = track.scrollLeft <= 4;
      var atEnd = track.scrollLeft >= max - 4;

      if (current) current.textContent = pad(i + 1);
      if (prev) prev.disabled = atStart;
      if (next) next.disabled = atEnd;

      // Fade only the edge that still has cards beyond it. The width itself
      // stays in CSS (--fade-size) so it can shrink on narrow screens.
      track.style.setProperty('--fade-l', atStart ? '0px' : 'var(--fade-size)');
      track.style.setProperty('--fade-r', atEnd ? '0px' : 'var(--fade-size)');

      if (bar) {
        var visible = Math.min(1, track.clientWidth / track.scrollWidth);
        var progress = max > 0 ? track.scrollLeft / max : 0;
        bar.style.width = (visible * 100) + '%';
        // Travels across exactly the space its own width leaves free.
        bar.style.transform = 'translateX(' + (progress * (100 / visible - 100)) + '%)';
      }
    };

    var move = function (direction) {
      track.scrollBy({ left: direction * step() * perView(), behavior: 'smooth' });
    };

    if (prev) prev.addEventListener('click', function () { move(-1); });
    if (next) next.addEventListener('click', function () { move(1); });

    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); move(-1); }
      else if (e.key === 'Home') { e.preventDefault(); track.scrollTo({ left: 0, behavior: 'smooth' }); }
      else if (e.key === 'End') { e.preventDefault(); track.scrollTo({ left: maxScroll(), behavior: 'smooth' }); }
    });

    // Keep a card fully in view when it is reached by tabbing into its links.
    track.addEventListener('focusin', function (e) {
      var card = e.target.closest('.work-card');
      if (!card) return;
      var s = step();
      if (s > 0) track.scrollTo({ left: cards.indexOf(card) * s, behavior: 'smooth' });
    });

    var ticking = false;
    track.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { render(); ticking = false; });
    }, { passive: true });

    if ('ResizeObserver' in window) new ResizeObserver(render).observe(track);
    else window.addEventListener('resize', render);

    // Capability filter. Hidden cards leave the flow entirely, so the counter,
    // the buttons and the progress bar all stay honest about what is showing.
    var filters = Array.prototype.slice.call(document.querySelectorAll('.work-filter'));
    var empty = document.querySelector('.work-empty');

    if (filters.length) {
      filters.forEach(function (button) {
        button.addEventListener('click', function () {
          var group = button.getAttribute('data-filter');

          filters.forEach(function (other) {
            var on = other === button;
            other.classList.toggle('is-on', on);
            other.setAttribute('aria-pressed', String(on));
          });

          allCards.forEach(function (card) {
            var show = group === 'all' || card.getAttribute('data-group') === group;
            card.hidden = !show;
          });

          cards = allCards.filter(function (card) { return !card.hidden; });
          relabel();

          if (empty) empty.hidden = cards.length > 0;

          // Mandatory snapping re-snaps to whatever card now sits nearest the
          // old offset, which drags the track back. Turn snapping off, force
          // the new layout, reset, then put snapping back.
          track.style.scrollSnapType = 'none';
          void track.offsetWidth;
          track.scrollLeft = 0;

          window.requestAnimationFrame(function () {
            track.style.scrollSnapType = '';
            render();
          });
        });
      });
    }

    render();
  }());

  /* ---------------------------------------------------------------------
     7. Price currency
     Every price element carries data-usd, data-eur, data-gbp and data-aed.
     The visitor's choice is remembered; a first visit guesses from the
     time zone and otherwise stays on USD, which is also the no-JS text.
     --------------------------------------------------------------------- */
  (function () {
    var prices = Array.prototype.slice.call(document.querySelectorAll('[data-usd]'));
    if (!prices.length) return;

    var CODES = ['usd', 'eur', 'gbp', 'aed'];
    var KEY = 'ts-currency';
    var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-currency]'));
    var formatters = {};

    var guess = function () {
      try {
        var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
        if (tz === 'Europe/London') return 'gbp';
        if (tz.indexOf('Europe/') === 0) return 'eur';
        if (tz === 'Asia/Dubai') return 'aed';
      } catch (e) { /* fall through */ }
      return 'usd';
    };

    var format = function (code, value) {
      if (!formatters[code]) {
        formatters[code] = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: code.toUpperCase(),
          maximumFractionDigits: 0
        });
      }
      return formatters[code].format(value);
    };

    var apply = function (code) {
      prices.forEach(function (el) {
        var value = Number(el.getAttribute('data-' + code));
        if (!isNaN(value) && value > 0) el.textContent = format(code, value);
      });
      buttons.forEach(function (button) {
        button.setAttribute('aria-pressed', String(button.getAttribute('data-currency') === code));
      });
    };

    var saved = null;
    try { saved = window.localStorage.getItem(KEY); } catch (e) { /* storage blocked */ }
    apply(CODES.indexOf(saved) > -1 ? saved : guess());

    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        var code = button.getAttribute('data-currency');
        if (CODES.indexOf(code) < 0) return;
        apply(code);
        try { window.localStorage.setItem(KEY, code); } catch (e) { /* storage blocked */ }
      });
    });
  }());

  /* ---------------------------------------------------------------------
     8. Footer year
     --------------------------------------------------------------------- */
  (function () {
    var year = document.getElementById('year');
    if (year) year.textContent = new Date().getFullYear();
  }());
}());
