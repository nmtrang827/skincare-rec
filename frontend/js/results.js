import { API_BASE } from './api.js';
import { CONCERN_TO_INGREDIENTS } from './ingredientMap.js';

// ── Constants ─────────────────────────────────────────────────
const FALLBACK_IMAGES = {
  "Moisturiser": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=400&fit=crop&q=80",
  "Moisturizer": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=400&fit=crop&q=80",
  "Serum": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=600&h=400&fit=crop&q=80",
  "Cleanser": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=400&fit=crop&q=80",
  "Toner": "https://images.unsplash.com/photo-1601049541271-25cf5f3bfa72?w=600&h=400&fit=crop&q=80",
  "Mask": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=400&fit=crop&q=80",
  "Oil": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=400&fit=crop&q=80",
  "Sunscreen": "https://images.unsplash.com/photo-1556228841-a3c527ebefe5?w=600&h=400&fit=crop&q=80",
  "Other": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop&q=80",
};

const CONCERN_LABELS = {
  Acne_Severity: "Acne",
  Dryness_Severity: "Dryness",
  Sensitivity_Severity: "Sensitivity",
  Pigmentation_Severity: "Pigmentation",
  Aging_Severity: "Aging",
};

// ── Read sessionStorage ───────────────────────────────────────
const params = new URLSearchParams(window.location.search);
const sharedId = params.get('id');

let products, profile;

if (sharedId) {
  // Load from database via shared link
  try {
    const res = await fetch(`${API_BASE}/results/${sharedId}`);
    if (!res.ok) throw new Error('Not found');
    const data = await res.json();
    products = data.products;
    profile = data.profile;
  } catch (err) {
    document.body.innerHTML = `
      <div style="text-align:center; padding: 80px 20px; color: #6B7A8D;">
        <p style="font-size: 1.1rem; margin-bottom: 16px;">Results not found or expired.</p>
        <a href="consultation.html" style="color: #C084A0;">Start a new consultation →</a>
      </div>`;
    throw err;
  }
} else {
  // Load from sessionStorage (normal flow)
  const raw = {
    results: sessionStorage.getItem('skincare_results'),
    profile: sessionStorage.getItem('skincare_profile'),
  };
  if (!raw.results || !raw.profile) {
    window.location.href = 'consultation.html';
  }
  products = JSON.parse(raw.results);
  profile = JSON.parse(raw.profile);
}

// ── Derive recommended ingredients from profile ───────────────
// For each concern where severity > 2, collect its ingredient list.
// Deduplicate with a Set so no ingredient appears twice.
function getRecommendedIngredients(profile) {
  const seen = new Set();
  const result = [];

  Object.entries(CONCERN_TO_INGREDIENTS).forEach(([concern, ingredients]) => {
    const severity = profile[concern] ?? 0;
    if (severity > 2) {
      ingredients.forEach(ing => {
        if (!seen.has(ing)) {
          seen.add(ing);
          result.push(ing);
        }
      });
    }
  });

  // If all concerns are very low, show a basic hydration set
  return result.length > 0
    ? result
    : ["hyaluronic acid", "ceramide", "glycerin", "panthenol"];
}

// ── Render: concern bars ──────────────────────────────────────
// Each bar uses the --pct CSS variable trick from results.css.
// We skip Price_Min and Price_Max — those aren't skin concerns.
function renderConcernBars(profile) {
  const container = document.getElementById('concernBars');

  const html = Object.entries(CONCERN_LABELS).map(([key, label]) => {
    const value = profile[key] ?? 0;
    const pct = (value / 10) * 100;

    return `
      <div class="concern-bar-item">
        <div class="concern-bar-header">
          <span class="concern-bar-label">${label}</span>
          <span class="concern-bar-value">${value}/10</span>
        </div>
        <div class="concern-bar-track">
          <div class="concern-bar-fill" style="--pct: ${pct}%"></div>
        </div>
      </div>`;
  }).join('');

  container.innerHTML = html;
}

// ── Render: ingredient chips ──────────────────────────────────
function renderIngredientChips(profile) {
  const container = document.getElementById('ingredientChips');
  const ingredients = getRecommendedIngredients(profile);

  container.innerHTML = ingredients
    .map(ing => `<span class="chip">${ing}</span>`)
    .join('');
}

// ── Render: product cards ─────────────────────────────────────
function renderProducts(products) {
  const grid = document.getElementById('productsGrid');
  const count = document.getElementById('productsCount');

  count.textContent = `${products.length} products`;

  if (products.length === 0) {
    grid.innerHTML = `
      <div class="state-empty">
        <p>No products matched your profile and budget.</p>
        <a href="consultation.html" class="btn-primary">Try again</a>
      </div>`;
    return;
  }

  grid.innerHTML = products.map((product, index) => {
    const fallback = FALLBACK_IMAGES[product.type] || FALLBACK_IMAGES["Other"];
    const rawImage = product.image_url || "";
    const imageUrl = (rawImage && !rawImage.includes("unsplash.com"))
      ? `${API_BASE}/proxy-image?url=${encodeURIComponent(rawImage)}`
      : fallback;

    const rawPrice = String(product.price).trim();
    const displayPrice = rawPrice.startsWith("£") ? rawPrice : `£${rawPrice.replace(/[^0-9.]/g, "")}`;

    const delay = index * 0.05;
    const ingredients = product.active_ingredients?.join(", ") || "—";

    return `
      <div class="product-card" style="animation-delay: ${delay}s;">
        <div class="product-img">
          <img
            src="${imageUrl}"
            alt="${product.name}"
            onerror="this.onerror=null; this.src='${fallback}';"
          />
        </div>
        <div class="product-body">
          <h2 class="product-name">${product.name}</h2>
          <div class="product-meta">
            <span class="product-type">${product.type}</span>
            <span class="product-price">${displayPrice}</span>
          </div>
          <p class="product-ingredients">
            <strong>Key ingredients:</strong> ${ingredients}
          </p>
          <a class="product-link" href="${product.url}" target="_blank">
            View product →
          </a>
        </div>
      </div>`;
  }).join('');
}

// ── Budget slider ─────────────────────────────────────────────
// Lets the user adjust budget and re-fetch without retaking quiz.
const budgetSlider = document.getElementById('budgetSliderResults');
const budgetDisplay = document.getElementById('budgetDisplay');
const refreshBtn = document.getElementById('refreshResults');

// Initialise slider to the value used in the consultation
budgetSlider.value = profile.Price_Max ?? 50;
budgetDisplay.textContent = `£${budgetSlider.value}`;

budgetSlider.addEventListener('input', () => {
  budgetDisplay.textContent = `£${budgetSlider.value}`;
});

refreshBtn.addEventListener('click', async () => {
  refreshBtn.disabled = true;
  refreshBtn.textContent = 'Refreshing…';

  const updatedProfile = {
    ...profile,
    Price_Min: 0,
    Price_Max: Number(budgetSlider.value),
  };

  try {
    const res = await fetch(`${API_BASE}/recommend_tfidf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedProfile),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const newProducts = await res.json();

    // Update sessionStorage so a page refresh keeps the new results
    sessionStorage.setItem('skincare_results', JSON.stringify(newProducts));
    sessionStorage.setItem('skincare_profile', JSON.stringify(updatedProfile));

    renderProducts(newProducts);

  } catch (err) {
    console.error(err);
    alert("Couldn't reach the server. Make sure the backend is running.");
  } finally {
    refreshBtn.disabled = false;
    refreshBtn.textContent = 'Refresh products →';
  }
});

// ── Save results + get shareable link ────────────────────────
const saveBtn = document.getElementById('saveResults');
const saveFeedback = document.getElementById('saveFeedback');

saveBtn.addEventListener('click', async () => {
  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving…';

  try {
    const res = await fetch(`${API_BASE}/save_results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, products }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const data = await res.json();
    const link = `${window.location.origin}/results.html?id=${data.id}`;

    // Copy link to clipboard
    await navigator.clipboard.writeText(link);

    saveFeedback.hidden = false;
    saveFeedback.textContent = `Link copied to clipboard`;
    saveBtn.textContent = 'Link copied ✓';

  } catch (err) {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save & get link';
    saveFeedback.hidden = false;
    saveFeedback.style.color = '#E53E3E';
    saveFeedback.textContent = 'Could not save. Try again.';
    console.error(err);
  }
});

// ── PDF download ──────────────────────────────────────────────
document.getElementById('downloadPdf').addEventListener('click', () => {
  window.print();
});

// ── Init ──────────────────────────────────────────────────────
// Run all three render functions once, in order.
renderConcernBars(profile);
renderIngredientChips(profile);
renderProducts(products);