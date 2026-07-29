// ── Nav: add background when user scrolls down ──────────────
// Without this, the frosted nav can look odd at the very top
// against the hero gradient. On scroll, it solidifies slightly.
const nav = document.querySelector('.site-nav');

window.addEventListener('scroll', () => {
  if (window.scrollY > 20) {
    nav.style.background = 'rgba(250, 250, 250, 0.96)';
  } else {
    nav.style.background = 'rgba(250, 250, 250, 0.82)';
  }
}, { passive: true }); // passive: true = browser can optimise scroll performance

// ── Step cards: stagger their entrance on scroll ────────────
// IntersectionObserver watches when cards enter the viewport.
// We don't animate them on load — only when the user scrolls to them.
const stepCards = document.querySelectorAll('.step-card');

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      // Small stagger delay per card so they don't all pop at once
      setTimeout(() => {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }, i * 80);
      observer.unobserve(entry.target); // stop watching once animated
    }
  });
}, { threshold: 0.15 }); // trigger when 15% of card is visible

stepCards.forEach(card => {
  // Start cards invisible and slightly down
  card.style.opacity = '0';
  card.style.transform = 'translateY(16px)';
  card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(card);
});