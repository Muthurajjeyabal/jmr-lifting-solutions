/* ============================================================
   JMR LIFTING SOLUTIONS — Main animations & interactions
   ============================================================ */
(function () {
  'use strict';

  gsap.registerPlugin(ScrollTrigger);

  /* ---- Scroll progress bar ---- */
  const progressBar = document.getElementById('scrollProgress');
  function updateProgress() {
    const scrolled = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const pct = max > 0 ? (scrolled / max) * 100 : 0;
    progressBar.style.width = pct + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

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

  /* ---- Number counter animation ---- */
  document.querySelectorAll('.big-stat__num').forEach(el => {
    const target = parseInt(el.dataset.target || '0', 10);
    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      onEnter: () => {
        gsap.to({ v: 0 }, {
          v: target,
          duration: 2.2,
          ease: 'power2.out',
          onUpdate: function () {
            el.textContent = Math.round(this.targets()[0].v).toLocaleString();
          }
        });
      }
    });
  });

  /* ---- Hero parallax on scroll ---- */
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

  /* ---- Nav appearance on scroll ---- */
  const nav = document.querySelector('.nav');
  ScrollTrigger.create({
    start: 'top -100',
    end: 99999,
    onUpdate: (self) => {
      if (self.progress > 0) nav.style.background = 'rgba(10,10,11,0.95)';
      else nav.style.background = '';
    }
  });

  /* ---- Operation section: pinned scroll animation ---- */
  const stage = document.getElementById('operationStage');
  const phaseName = document.getElementById('phaseName');
  const progressDegree = document.getElementById('progressDegree');
  const progressFill = document.getElementById('progressFill');

  if (stage && window.SceneEngine) {
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

  /* ---- Mobile menu (basic) ---- */
  const menuBtn = document.getElementById('menuBtn');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      // simple toggle: scroll to capabilities as fallback
      document.querySelector('#capabilities')?.scrollIntoView({ behavior: 'smooth' });
    });
  }

  /* ---- Cursor accent on cap-cards ---- */
  document.querySelectorAll('.cap-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      gsap.to(card, { y: -6, duration: 0.4, ease: 'power2.out' });
    });
    card.addEventListener('mouseleave', () => {
      gsap.to(card, { y: 0, duration: 0.4, ease: 'power2.out' });
    });
  });

})();
