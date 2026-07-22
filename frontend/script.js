async function getRecommendations() {
    function cap(val) {
        val = Number(val);
        if (val < 0) return 0;
        if (val > 10) return 10;
        return val;
    }

    const user = {
        Budget_Level: document.getElementById("budget").value,
        Acne_Severity: cap(document.getElementById("acne").value),
        Dryness_Severity: cap(document.getElementById("dryness").value),
        Pigmentation_Severity: cap(document.getElementById("pigmentation").value),
        Aging_Severity: cap(document.getElementById("aging").value),
        Sensitivity_Severity: cap(document.getElementById("sensitivity").value)
    };

    // BUG FIX 1: Added all actual product types from the dataset (UK spelling + all categories).
    // These are only used as a last-resort fallback when a product has no image_url at all.
    const typeFallbackImages = {
        "Moisturiser":  "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=300&fit=crop",
        "Moisturizer":  "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=300&fit=crop",
        "Serum":        "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400&h=300&fit=crop",
        "Cleanser":     "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=300&fit=crop",
        "Toner":        "https://images.unsplash.com/photo-1601049541271-25cf5f3bfa72?w=400&h=300&fit=crop",
        "Mask":         "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=400&h=300&fit=crop",
        "Oil":          "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=300&fit=crop",
        "Bath Oil":     "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=300&fit=crop",
        "Mist":         "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400&h=300&fit=crop",
        "Balm":         "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&h=300&fit=crop",
        "Peel":         "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400&h=300&fit=crop",
        "Eye Care":     "https://images.unsplash.com/photo-1631390003047-4a858b4e4b5a?w=400&h=300&fit=crop",
        "Exfoliator":   "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=300&fit=crop",
        "Bath Salts":   "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=300&fit=crop",
        "Body Wash":    "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=300&fit=crop",
        "Sunscreen":    "https://images.unsplash.com/photo-1556228841-a3c527ebefe5?w=400&h=300&fit=crop",
        "Other":        "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop"
    };

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = '<div class="loading">Analyzing your skin profile...</div>';

    try {
        const response = await fetch("http://127.0.0.1:5000/recommend_tfidf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(user)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        resultsDiv.innerHTML = "";

        if (data.length === 0) {
            resultsDiv.innerHTML = '<div class="no-results">No products found matching your criteria. Please adjust your budget range or skin concern ratings.</div>';
            return;
        }

        data.forEach((product, index) => {
            // BUG FIX 2: Use the real image_url from the product data.
            // Falls back to type-based placeholder only if missing, then to "Other".
            const fallback = typeFallbackImages[product.type] || typeFallbackImages["Other"];
            const imageUrl = (product.image_url && !product.image_url.includes("unsplash"))
                ? product.image_url
                : fallback;

            // BUG FIX 3: Format price correctly — strip existing currency symbol,
            // then display with the symbol from the data (£) not a hardcoded $.
            const rawPrice = String(product.price);
            const currencySymbol = rawPrice.match(/^[^0-9]*/)[0] || "";
            const numericPrice = rawPrice.replace(/[^0-9.]/g, "");
            const displayPrice = currencySymbol
                ? `${currencySymbol}${numericPrice}`
                : `$${numericPrice}`;

            const delay = (index + 1) * 0.1;

            // BUG FIX 4: Use <img> with onerror instead of CSS background-image,
            // so broken image URLs gracefully fall back to the type placeholder.
            resultsDiv.innerHTML += `
            <div class="product-card" style="animation-delay: ${delay}s;">
                <div class="product-image">
                    <img
                        src="${imageUrl}"
                        alt="${product.name}"
                        onerror="this.onerror=null; this.src='${fallback}';"
                        style="width:100%; height:100%; object-fit:cover; display:block;"
                    />
                </div>
                <div class="product-info">
                    <h3>${product.name}</h3>
                    <p><strong>Type:</strong> ${product.type}</p>
                    <p class="price"><strong>Price:</strong> ${displayPrice}</p>
                    <p><strong>Active Ingredients:</strong> ${product.active_ingredients.join(", ")}</p>
                    <a href="${product.url}" target="_blank">View Product Details</a>
                </div>
            </div>
            `;
        });
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="error">
                <strong>Connection Error:</strong> ${error.message}<br><br>
                <small>Please ensure the backend server is running:<br>
                <code>cd backend && python server.py</code></small>
            </div>
        `;
        console.error("Error fetching recommendations:", error);
    }
}