/* ============================================================
   JMR LIFTING SOLUTIONS — Main animations & interactions
   ============================================================ */
(function () {
  'use strict';

  // Safety guard — if GSAP failed to load (offline, blocker), still run counters + non-GSAP code
  var hasGsap = typeof window.gsap !== 'undefined';
  var hasScrollTrigger = hasGsap && typeof window.ScrollTrigger !== 'undefined';
  if (hasScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  /* ---- Scroll progress bar ---- */
  const progressBar = document.getElementById('scrollProgress');
  if (progressBar) {
    function updateProgress() {
      const scrolled = window.scrollY;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? (scrolled / max) * 100 : 0;
      progressBar.style.width = pct + '%';
    }
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  /* ---- Intersection reveal for sections ---- */
  const revealElements = document.querySelectorAll(
    '.intro__title, .intro__body, .cap-card, .project, .process__step, .fleet-card, .big-stat, .contact__title, .contact__body, .contact__form, .contact__direct'
  );
  revealElements.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
  revealElements.forEach(el => io.observe(el));

  /* ---- Number counter animation (vanilla, IntersectionObserver) ----
     Works for both `.counter` (hero) and `.big-stat__num` (section 08).
     data-target: end value (integer)
     data-pad:    optional. Pad with leading zeros to N digits (e.g. "2" → 08)
     data-suffix: optional. Preserves suffix text like "hr", "+", "t"
     Fires ONCE per element when it enters the viewport. Duration: 2s. */
  (function initCounters() {
    const counters = document.querySelectorAll('.counter, .big-stat__num');
    if (!counters.length || !('IntersectionObserver' in window)) return;

    const DURATION = 2000; // ms
    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

    function animateCounter(el) {
      const target = parseInt(el.dataset.target || '0', 10);
      const pad = parseInt(el.dataset.pad || '0', 10);
      const suffix = el.dataset.suffix || '';
      const startTime = performance.now();

      function render(nowMs) {
        const elapsed = nowMs - startTime;
        const p = Math.min(elapsed / DURATION, 1);
        const value = Math.round(target * easeOutCubic(p));
        const numText = pad > 0 ? String(value).padStart(pad, '0') : value.toLocaleString();
        el.innerHTML = numText + (suffix ? '<span>' + suffix + '</span>' : '');
        if (p < 1) requestAnimationFrame(render);
      }
      requestAnimationFrame(render);
    }

    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target); // fire once
        }
      });
    }, { threshold: 0.3, rootMargin: '0px 0px -40px 0px' });

    counters.forEach(el => counterObserver.observe(el));
  })();

  /* ---- Hero parallax on scroll ---- */
  if (hasScrollTrigger && document.querySelector('.hero__img')) {
    gsap.to('.hero__img', {
      yPercent: 15,
      scale: 1.05,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: 'bottom top',
        scrub: 1
      }
    });
  }

  /* ---- Nav appearance on scroll ---- */
  const nav = document.querySelector('.nav');
  if (hasScrollTrigger && nav) {
    ScrollTrigger.create({
      start: 'top -100',
      end: 99999,
      onUpdate: (self) => {
        if (self.progress > 0) nav.style.background = 'rgba(10,10,11,0.95)';
        else nav.style.background = '';
      }
    });
  } else if (nav) {
    // Fallback — use scroll listener
    window.addEventListener('scroll', function(){
      nav.style.background = window.scrollY > 100 ? 'rgba(10,10,11,0.95)' : '';
    }, { passive: true });
  }

  /* ---- Operation section: pinned scroll animation ---- */
  const stage = document.getElementById('operationStage');
  const phaseName = document.getElementById('phaseName');
  const progressDegree = document.getElementById('progressDegree');
  const progressFill = document.getElementById('progressFill');

  if (hasScrollTrigger && stage && window.SceneEngine) {
    // Initialize the SVG scene
    window.SceneEngine.init();

    // Pin the stage and drive the animation with scroll
    ScrollTrigger.create({
      trigger: stage,
      start: 'top top',
      end: '+=1800',
      pin: true,
      pinSpacing: true,
      scrub: 0.6,
      onUpdate: (self) => {
        const p = self.progress;
        window.SceneEngine.update(p);

        // Update HUD
        let label = 'READY';
        if (p > 0.02 && p <= 0.15) label = 'PHASE 01 · HOOK DESCENT';
        else if (p > 0.15 && p <= 0.25) label = 'PHASE 02 · SLING TENSION';
        else if (p > 0.25 && p <= 0.90) label = 'PHASE 03 · UPENDING';
        else if (p > 0.90) label = 'PHASE 04 · VERTICAL SET';
        phaseName.textContent = label;

        // Rotation degrees (0 to 90 during phase 3)
        let deg = 0;
        if (p > 0.25 && p <= 0.90) {
          deg = ((p - 0.25) / (0.90 - 0.25)) * 90;
        } else if (p > 0.90) {
          deg = 90;
        }
        progressDegree.textContent = deg.toFixed(1) + '°';

        progressFill.style.width = (p * 100) + '%';
      }
    });
  }

  /* ---- Smooth scroll for anchor links ---- */
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href === '#' || href.length < 2) return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---- Mobile menu overlay ---- */
  const menuBtn = document.getElementById('menuBtn');
  const menuNav = document.querySelector('.nav');
  if (menuBtn && menuNav) {
    // Build overlay dynamically from existing nav links so all pages get it
    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu';
    overlay.setAttribute('aria-hidden', 'true');
    const linksList = menuNav.querySelector('.nav__links');
    const cta = menuNav.querySelector('.nav__cta');
    const linksHtml = linksList ? linksList.outerHTML.replace('nav__links', 'mobile-menu__links') : '';
    const ctaHtml = cta ? `<a href="${cta.getAttribute('href')}" class="mobile-menu__cta">${cta.textContent}</a>` : '';
    overlay.innerHTML = `
      <div class="mobile-menu__inner">
        <button class="mobile-menu__close" aria-label="Close menu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        ${linksHtml}
        ${ctaHtml}
        <div class="mobile-menu__contact">
          <a href="mailto:contact@jmrlifting.com">contact@jmrlifting.com</a>
          <a href="https://wa.me/918111002266" target="_blank" rel="noopener">WhatsApp us</a>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    const openMenu = () => {
      overlay.classList.add('is-open');
      overlay.setAttribute('aria-hidden', 'false');
      menuBtn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    };
    const closeMenu = () => {
      overlay.classList.remove('is-open');
      overlay.setAttribute('aria-hidden', 'true');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };
    menuBtn.addEventListener('click', openMenu);
    overlay.querySelector('.mobile-menu__close').addEventListener('click', closeMenu);
    overlay.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
  }

  /* ---- Cursor accent on cap-cards ---- */
  if (hasGsap) {
    document.querySelectorAll('.cap-card').forEach(card => {
      card.addEventListener('mouseenter', () => {
        gsap.to(card, { y: -6, duration: 0.4, ease: 'power2.out' });
      });
      card.addEventListener('mouseleave', () => {
        gsap.to(card, { y: 0, duration: 0.4, ease: 'power2.out' });
      });
    });
  }

})();
