// consultation.js
// Controls the multi-step consultation flow.
// Pattern: one source-of-truth object (state), 
// one function to render from that state (goToStep).

// ── State ────────────────────────────────────────────────────
// Everything the consultation knows is stored here.
// We'll add more fields as we build each step.
const state = {
  currentStep: 1,
  path: null,       // 'quiz' or 'manual' — set when user picks on step 1
  totalSteps: 4,
};

// ── DOM references ───────────────────────────────────────────
// Grab these once at the top — cheaper than querying every time.
const allSteps    = document.querySelectorAll('.consult-step');
const progressFill = document.getElementById('progressFill');
const stepCounter  = document.getElementById('stepCounter');
const progressBar  = document.querySelector('.progress-bar-track');

// ── Core: go to a step ───────────────────────────────────────
// This is the engine of the whole page.
// NEVER show/hide steps manually elsewhere — always call goToStep().
function goToStep(n) {
  // 1. Hide all steps
  allSteps.forEach(s => s.hidden = true);

  // 2. Show only the target step
  const target = document.querySelector(`.consult-step[data-step="${n}"]`);
  if (!target) return;
  target.hidden = false;

  // 3. Update state
  state.currentStep = n;

  // 4. Update progress bar
  const pct = (n / state.totalSteps) * 100;
  progressFill.style.width = pct + '%';

  // 5. Update ARIA on progress bar (accessibility)
  progressBar.setAttribute('aria-valuenow', n);

  // 6. Update step counter text
  stepCounter.textContent = `Step ${n} of ${state.totalSteps}`;

  // 7. Scroll to top smoothly (matters on mobile)
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Step 1: path selection ───────────────────────────────────
document.getElementById('chooseQuiz').addEventListener('click', () => {
  state.path = 'quiz';
  goToStep(2);
});

document.getElementById('chooseManual').addEventListener('click', () => {
  state.path = 'manual';
  // Manual path skips the quiz — goes straight to concerns (step 3)
  goToStep(3);
});

// ── Step 2: quiz navigation ──────────────────────────────────
document.getElementById('backFromQuiz').addEventListener('click', () => goToStep(1));
document.getElementById('nextFromQuiz').addEventListener('click', () => goToStep(3));

// ── Step 3: concerns navigation ─────────────────────────────
document.getElementById('backFromConcerns').addEventListener('click', () => {
  // Where we go back to depends on which path the user took
  goToStep(state.path === 'quiz' ? 2 : 1);
});
document.getElementById('nextFromConcerns').addEventListener('click', () => goToStep(4));

// ── Step 4: AI scan navigation ───────────────────────────────
document.getElementById('backFromScan').addEventListener('click', () => goToStep(3));
document.getElementById('nextFromScan').addEventListener('click', () => {
  // Placeholder: will navigate to results.html once that page exists
  window.location.href = 'results.html';
});

// ── Init ─────────────────────────────────────────────────────
goToStep(1);