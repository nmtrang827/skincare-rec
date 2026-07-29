const IS_LOCAL = window.location.hostname === '127.0.0.1'
  || window.location.hostname === 'localhost';

export const API_BASE = IS_LOCAL
  ? 'http://127.0.0.1:5000'
  : 'https://skincare-rec.onrender.com';

// ── Fetch recommendations ────────────────────────────────────
// Takes a user profile object, returns a promise of product results.
// Throws on network error or non-200 response.
async function fetchRecommendations(userProfile) {
  const response = await fetch(`${API_BASE}/recommend_tfidf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userProfile),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  return response.json();
}

