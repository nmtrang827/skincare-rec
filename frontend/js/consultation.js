// consultation.js
// Controls the multi-step consultation flow.
// Pattern: one source-of-truth object (state), 
// one function to render from that state (goToStep).

// ── State ────────────────────────────────────────────────────
// Everything the consultation knows is stored here.
// We'll add more fields as we build each step.
import { quiz } from "./quiz.js";
const state = {
  currentStep: 1,
  path: null,
  totalSteps: 4,
  quizIndex: 0,
  quizAnswers: {},
  priceMin: 0,
  priceMax: 230,

  concernScores: {
    Acne_Severity: 0,
    Dryness_Severity: 0,
    Sensitivity_Severity: 0,
    Pigmentation_Severity: 0,
    Aging_Severity: 0
  }
};

// ── DOM references ───────────────────────────────────────────
// Grab these once at the top — cheaper than querying every time.
const allSteps    = document.querySelectorAll('.consult-step');
const progressFill = document.getElementById('progressFill');
const stepCounter  = document.getElementById('stepCounter');
const progressBar  = document.querySelector('.progress-bar-track');

const quizCounter = document.getElementById("quizCounter");
const quizQuestion = document.getElementById("quizQuestion");
const quizAnswers = document.getElementById("quizAnswers");

const acneSlider = document.getElementById("acneSlider");
const drynessSlider = document.getElementById("drynessSlider");
const sensitivitySlider = document.getElementById("sensitivitySlider");
const pigmentationSlider = document.getElementById("pigmentationSlider");
const agingSlider = document.getElementById("agingSlider");

const acneValue = document.getElementById("acneValue");
const drynessValue = document.getElementById("drynessValue");
const sensitivityValue = document.getElementById("sensitivityValue");
const pigmentationValue = document.getElementById("pigmentationValue");
const agingValue = document.getElementById("agingValue");

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

function renderQuizQuestion() {
    const q = quiz[state.quizIndex];
    quizCounter.textContent = `Question ${state.quizIndex + 1} of ${quiz.length}`;
    quizQuestion.textContent = q.question;
    quizAnswers.innerHTML = "";
    q.answers.forEach(answer => {
        const button = document.createElement("button");
        button.className = "quiz-answer";
        button.textContent = answer.text;
        button.onclick = () => {
            state.quizAnswers[q.id] = answer.value;
            if (state.quizIndex < quiz.length - 1) {
                state.quizIndex++;
                renderQuizQuestion();
            } else {
                calculateQuizScores();
                fillConcernSliders();
                goToStep(3);
            }
        };
        quizAnswers.appendChild(button);
    });
}

function calculateQuizScores() {
    const totals = {};
    const weights = {};
    quiz.forEach(question => {
        const answer = state.quizAnswers[question.id];
        if (answer === undefined) return;
        if (!totals[question.category]) {
            totals[question.category] = 0;
            weights[question.category] = 0;
        }
        totals[question.category] += answer * question.weight;
        weights[question.category] += question.weight;
    });

    // Convert weighted totals into final 0–10 scores
    Object.keys(totals).forEach(category => {
        state.concernScores[category] = Number((totals[category] / weights[category]).toFixed(1));
    });

    console.log("Quiz answers:");
    console.log(state.quizAnswers);

    console.log("Calculated concern scores:");
    console.log(state.concernScores);
}

function fillConcernSliders() {
    acneSlider.value = state.concernScores.Acne_Severity;
    drynessSlider.value = state.concernScores.Dryness_Severity;
    sensitivitySlider.value = state.concernScores.Sensitivity_Severity;
    pigmentationSlider.value = state.concernScores.Pigmentation_Severity;
    agingSlider.value = state.concernScores.Aging_Severity;

    acneValue.textContent = acneSlider.value;
    drynessValue.textContent = drynessSlider.value;
    sensitivityValue.textContent = sensitivitySlider.value;
    pigmentationValue.textContent = pigmentationSlider.value;
    agingValue.textContent = agingSlider.value;
}

// ── Step 1: path selection ───────────────────────────────────
document.getElementById("chooseQuiz").addEventListener("click", () => {
    state.path = "quiz";
    state.quizIndex = 0;
    goToStep(2);
    renderQuizQuestion();
});

document.getElementById('chooseManual').addEventListener('click', () => {
  state.path = 'manual';
  // Manual path skips the quiz — goes straight to concerns (step 3)
  goToStep(3);
});

// ── Step 2: quiz navigation ──────────────────────────────────
document.getElementById('backFromQuiz').addEventListener('click', () => {
  if (state.quizIndex > 0) {
    state.quizIndex--;
    renderQuizQuestion();
  } else {
    goToStep(1);
  }
});

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


acneSlider.addEventListener("input", () => {
    acneValue.textContent = acneSlider.value;
    state.concernScores.Acne_Severity = Number(acneSlider.value);
});

drynessSlider.addEventListener("input", () => {
    drynessValue.textContent = drynessSlider.value;
    state.concernScores.Dryness_Severity = Number(drynessSlider.value);
});

sensitivitySlider.addEventListener("input", () => {
    sensitivityValue.textContent = sensitivitySlider.value;
    state.concernScores.Sensitivity_Severity = Number(sensitivitySlider.value);
});

pigmentationSlider.addEventListener("input", () => {
    pigmentationValue.textContent = pigmentationSlider.value;
    state.concernScores.Pigmentation_Severity = Number(pigmentationSlider.value);
});

agingSlider.addEventListener("input", () => {
    agingValue.textContent = agingSlider.value;
    state.concernScores.Aging_Severity = Number(agingSlider.value);
});

// ── Price range ───────────────────────────────────────────────
const budgetSlider = document.getElementById("budgetSlider");
const budgetValue = document.getElementById("budgetValue");

budgetSlider.addEventListener("input", () => {

    budgetValue.textContent = `£${budgetSlider.value}`;

    state.priceMin = 0;
    state.priceMax = Number(budgetSlider.value);

});

// ── Fetch & navigate ──────────────────────────────────────────
const resultsLoading = document.getElementById('resultsLoading');

async function fetchAndNavigate() {
  resultsLoading.hidden = false;
  document.getElementById('backFromScan').disabled = true;

  const payload = {
    ...state.concernScores,
    Price_Min: state.priceMin,
    Price_Max: state.priceMax,
  };

  try {
    const res = await fetch('http://127.0.0.1:5000/recommend_tfidf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const products = await res.json();
    sessionStorage.setItem('skincare_results', JSON.stringify(products));
    sessionStorage.setItem('skincare_profile', JSON.stringify(payload));
    window.location.href = 'results.html';

  } catch (err) {
    resultsLoading.hidden = true;
    document.getElementById('backFromScan').disabled = false;
    const el = document.createElement('p');
    el.className = 'fetch-error';
    el.textContent = "Couldn't reach the server. Make sure the backend is running.";
    resultsLoading.before(el);
    console.error(err);
  }
}

// ── Step 4 listeners ──────────────────────────────────────────
document.getElementById('skipAI').addEventListener('click', fetchAndNavigate);
document.getElementById('chooseAI').addEventListener('click', fetchAndNavigate); // AI wired later

// ── Init ─────────────────────────────────────────────────────
goToStep(1);