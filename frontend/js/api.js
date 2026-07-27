// api.js — single source of truth for backend communication
// Import this in any page that talks to Flask.

// ── Config ───────────────────────────────────────────────────
// Change this ONE line when you deploy. Nowhere else.
const API_BASE = 'http://127.0.0.1:5000';

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