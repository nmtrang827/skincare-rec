// ── Price range slider ──────────────────────────────────────────────────────
const priceMin = document.getElementById("priceMin");
const priceMax = document.getElementById("priceMax");
const rangeFill = document.getElementById("rangeFill");
const priceDisplay = document.getElementById("priceDisplay");

function updatePriceSlider() {
    const min = parseInt(priceMin.value);
    const max = parseInt(priceMax.value);
    const total = 230;

    // Prevent handles crossing
    if (min > max - 2) {
        priceMin.value = max - 2;
        return;
    }
    if (max < min + 2) {
        priceMax.value = min + 2;
        return;
    }

    const leftPct  = (min / total) * 100;
    const rightPct = (max / total) * 100;
    rangeFill.style.left  = leftPct + "%";
    rangeFill.style.width = (rightPct - leftPct) + "%";
    priceDisplay.textContent = `£${min} – £${max}`;
}

priceMin.addEventListener("input", updatePriceSlider);
priceMax.addEventListener("input", updatePriceSlider);
updatePriceSlider(); // init

// ── Severity sliders ────────────────────────────────────────────────────────
const severityIds = ["acne", "dryness", "pigmentation", "aging", "sensitivity"];

severityIds.forEach(id => {
    const slider = document.getElementById(id);
    const badge  = document.getElementById(id + "Val");
    slider.addEventListener("input", () => {
        badge.textContent = slider.value;
        // Tint badge darker as severity increases
        const v = parseInt(slider.value);
        const alpha = 0.06 + (v / 10) * 0.18;
        badge.style.background = `rgba(139,90,60,${alpha})`;
    });
});

// ── Fallback images per product type ────────────────────────────────────────
const typeFallbackImages = {
    "Moisturiser":  "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=400&fit=crop&q=80",
    "Moisturizer":  "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=400&fit=crop&q=80",
    "Serum":        "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=600&h=400&fit=crop&q=80",
    "Cleanser":     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=400&fit=crop&q=80",
    "Toner":        "https://images.unsplash.com/photo-1601049541271-25cf5f3bfa72?w=600&h=400&fit=crop&q=80",
    "Mask":         "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=400&fit=crop&q=80",
    "Oil":          "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=400&fit=crop&q=80",
    "Bath Oil":     "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=400&fit=crop&q=80",
    "Mist":         "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&h=400&fit=crop&q=80",
    "Balm":         "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=600&h=400&fit=crop&q=80",
    "Peel":         "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&h=400&fit=crop&q=80",
    "Eye Care":     "https://images.unsplash.com/photo-1631390003047-4a858b4e4b5a?w=600&h=400&fit=crop&q=80",
    "Exfoliator":   "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=600&h=400&fit=crop&q=80",
    "Bath Salts":   "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&h=400&fit=crop&q=80",
    "Body Wash":    "https://images.unsplash.com/photo-1631390003047-4a858b4e4b5a?w=600&h=400&fit=crop&q=80",
    "Sunscreen":    "https://images.unsplash.com/photo-1556228841-a3c527ebefe5?w=600&h=400&fit=crop&q=80",
    "Other":        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop&q=80",
};

// ── Main recommendation fetch ────────────────────────────────────────────────
async function getRecommendations() {
    const user = {
        Price_Min: parseInt(priceMin.value),
        Price_Max: parseInt(priceMax.value),
        Acne_Severity:          parseInt(document.getElementById("acne").value),
        Dryness_Severity:       parseInt(document.getElementById("dryness").value),
        Pigmentation_Severity:  parseInt(document.getElementById("pigmentation").value),
        Aging_Severity:         parseInt(document.getElementById("aging").value),
        Sensitivity_Severity:   parseInt(document.getElementById("sensitivity").value),
    };

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = '<div class="loading">Analysing your skin profile…</div>';

    try {
        const response = await fetch("http://127.0.0.1:5000/recommend_tfidf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(user),
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();
        resultsDiv.innerHTML = "";

        if (data.length === 0) {
            resultsDiv.innerHTML = '<div class="no-results">No products found in that price range for your skin profile. Try widening the budget or adjusting your concerns.</div>';
            return;
        }

        data.forEach((product, index) => {
            const fallback = typeFallbackImages[product.type] || typeFallbackImages["Other"];
            // Prefer real thcdn image; use type fallback if it's an Unsplash generic
            const imageUrl = (product.image_url && !product.image_url.includes("unsplash.com"))
                ? product.image_url
                : fallback;

            // Price: data is in £, display as-is
            const rawPrice = String(product.price).trim();
            const displayPrice = rawPrice.startsWith("£") ? rawPrice : `£${rawPrice.replace(/[^0-9.]/g, "")}`;

            const delay = index * 0.07;

            resultsDiv.innerHTML += `
            <div class="product-card" style="animation-delay:${delay}s;">
                <div class="product-image">
                    <img
                        src="${imageUrl}"
                        alt="${product.name}"
                        onerror="this.onerror=null; this.src='${fallback}';"
                    />
                </div>
                <div class="product-info">
                    <h3>${product.name}</h3>
                    <div class="product-meta">
                        <span class="product-type-tag">${product.type}</span>
                        <span class="product-price">${displayPrice}</span>
                    </div>
                    <p class="product-ingredients">
                        <strong>Key ingredients:</strong> ${product.active_ingredients.join(", ")}
                    </p>
                    <a class="product-link" href="${product.url}" target="_blank">View Product →</a>
                </div>
            </div>`;
        });

    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="error">
                <strong>Connection error:</strong> ${error.message}<br><br>
                <small>Make sure the backend is running:<br>
                <code>cd backend && python server.py</code></small>
            </div>`;
        console.error(error);
    }
}