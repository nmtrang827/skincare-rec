# SkinRx

Personalised skincare recommendation web app with AI-powered acne detection.

**Live demo:** https://skincare-rec.vercel.app

---

## Features

- **Guided consultation** — multi-step quiz that builds a skin profile
- **Hybrid recommender** — TF-IDF + rule-based scoring across 1,100+ products
- **AI acne scan** — YOLOv8 model trained on ACNE04 dataset, detects lesions and maps count to severity score
- **Results dashboard** — skin profile, recommended ingredients, matched products, budget filter
- **Shareable results** — save consultation to PostgreSQL, get a permanent link
- **PDF export** — print-optimised stylesheet, no external library

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | HTML, CSS, JavaScript (ES Modules) |
| Backend | Python, Flask, REST API |
| Recommender | scikit-learn, TF-IDF, cosine similarity |
| AI model | YOLOv8 (Ultralytics), trained on ACNE04 |
| Database | PostgreSQL (Supabase) |
| Deployment | Docker, Vercel, Render |

---

## Architecture
frontend/ Static site → Vercel
├── index.html Landing page
├── consultation.html Multi-step quiz
├── results.html Dashboard
├── css/
└── js/

backend/ Flask API → Render (Docker)
├── server.py Routes: /recommend_tfidf, /analyze, /save_results, /results/:id
├── recommender_tfidf.py Hybrid scoring engine
├── skin_analyzer.py YOLOv8 inference
└── model/best.pt Trained weights (ACNE04)

data/
└── products.json 1,100+ scraped LookFantastic products
---

## Run locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Frontend**
```bash
cd frontend
npx live-server --port=5173
```

> AI scan requires `backend/model/best.pt` (not included in repo).

---

## How the recommender works

1. User completes quiz → concern scores (0–10) per category
2. Scores map to target ingredients via `CONCERN_TO_INGREDIENTS`
3. TF-IDF vectorises product ingredient lists
4. Hybrid score = `α × rule_score + (1-α) × tfidf_score`
5. Top 12 products returned, filtered by budget

---

## How the AI scan works

1. User uploads a selfie
2. YOLOv8 runs inference (`conf=0.15`, `imgsz=640`)
3. Lesion count → severity score: `min(10, (count/30) × 9 + 1)`
4. Score feeds into `Acne_Severity` field of the recommender

> AI scan runs locally only. The deployed version uses quiz/manual scores.