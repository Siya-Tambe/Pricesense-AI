// ── Load dashboard ──────────────────────────────────────────────

async function loadDashboard() {
  const container = document.getElementById("watchlist");
  const countEl = document.getElementById("product-count");

  if (!container) return;

  container.innerHTML = `
    <div style="text-align:center;padding:40px 0;">
      <div class="spinner"></div>
      <p style="color:#888;font-size:13px;margin-top:12px;">Loading your products...</p>
    </div>`;

  try {
    const products = await getAllProducts();

    if (countEl) countEl.textContent = products.length;

    if (products.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="icon">🔍</div>
          <h3>No products tracked yet</h3>
          <p>Paste a product URL above to start tracking prices</p>
        </div>`;
      return;
    }

    container.innerHTML = products.map(renderProductRow).join("");

    container.querySelectorAll(".product-row").forEach((row) => {
      row.addEventListener("click", () => {
        const id = row.dataset.id;
        window.location.href = `product.html?id=${id}`;
      });
    });

  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="icon">⚠️</div>
        <h3>Could not load products</h3>
        <p style="font-size:13px;color:#aaa;">Make sure the backend server is running on port 8000</p>
      </div>`;
    console.error("Dashboard load error:", err);
  }
}


// ── Render a single product row ─────────────────────────────────

function renderProductRow(product) {
  const thumbHtml = product.thumbnail
    ? `<img src="${product.thumbnail}" class="product-thumb" alt="" onerror="this.outerHTML='<div class=\\'product-thumb\\'>${platformEmoji(product.platform)}</div>'">`
    : `<div class="product-thumb">${platformEmoji(product.platform)}</div>`;

  const verdictHtml = product.verdict
    ? `<span class="pill ${verdictPill(product.verdict)}">${verdictLabel(product.verdict)}</span>`
    : `<span class="pill pill-gray">Collecting data</span>`;

  const priceHtml = product.current_price
    ? `<div style="font-size:15px;font-weight:600;">${formatPrice(product.current_price)}</div>`
    : `<div style="font-size:13px;color:#aaa;">Fetching...</div>`;

  const statusDot = product.scrape_status === "success"
    ? `<span style="width:7px;height:7px;border-radius:50%;background:#3B6D11;display:inline-block;margin-right:4px;"></span>`
    : `<span style="width:7px;height:7px;border-radius:50%;background:#A32D2D;display:inline-block;margin-right:4px;"></span>`;

  const lastFetched = product.last_fetched
    ? `${statusDot}<span style="font-size:11px;color:#aaa;">${product.last_fetched}</span>`
    : "";

  const daysTracked = product.days_tracked > 0
    ? `<span style="font-size:11px;color:#aaa;margin-left:8px;">· ${product.days_tracked} data points</span>`
    : "";

  return `
    <div class="product-row" data-id="${product.id}">
      ${thumbHtml}
      <div style="flex:1;min-width:0;">
        <div class="product-name" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          ${escapeHtml(product.name || "Unknown product")}
        </div>
        <div class="product-meta" style="display:flex;align-items:center;gap:4px;flex-wrap:wrap;">
          <span class="pill ${platformColor(product.platform)}" style="font-size:10px;padding:1px 7px;">
            ${formatPlatform(product.platform)}
          </span>
          ${lastFetched}
          ${daysTracked}
        </div>
      </div>
      <div style="text-align:right;flex-shrink:0;">
        ${priceHtml}
        <div style="margin-top:4px;">${verdictHtml}</div>
      </div>
    </div>`;
}


// ── Handle URL form submission ──────────────────────────────────

async function handleTrackSubmit(event) {
  if (event) event.preventDefault();

  const input = document.getElementById("url-input");
  const btn = document.getElementById("track-btn");
  if (!input || !btn) return;

  const url = input.value.trim();
  if (!url) {
    showToast("Please paste a product URL first", "error");
    return;
  }

  if (!url.startsWith("http")) {
    showToast("Please enter a valid URL starting with http", "error");
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="width:14px;height:14px;border-width:2px;"></span> Fetching...`;

  try {
    const result = await trackProduct(url);
    input.value = "";
    showToast(
      result.message === "Product already being tracked"
        ? "Already tracking this product!"
        : `Added: ${result.product.name}`,
      "success"
    );
    await loadDashboard();
  } catch (err) {
    showToast(err.message || "Could not add product", "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "+ Track product";
  }
}


// ── Delete product ──────────────────────────────────────────────

async function handleDelete(productId) {
  if (!confirm("Stop tracking this product?")) return;
  try {
    await deleteProduct(productId);
    showToast("Product removed", "info");
    await loadDashboard();
  } catch (err) {
    showToast("Could not remove product", "error");
  }
}


// ── Platform emoji fallback ─────────────────────────────────────

function platformEmoji(platform) {
  const map = {
    amazon: "📦",
    flipkart: "🛒",
    myntra: "👗",
    croma: "💻",
    reliancedigital: "📱",
    meesho: "🛍️",
    tatacliq: "🏷️",
    snapdeal: "⚡",
  };
  return map[platform] || "🏷️";
}


// ── Escape HTML to prevent XSS ──────────────────────────────────

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}


// ── Init ────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();

  const form = document.getElementById("track-form");
  if (form) form.addEventListener("submit", handleTrackSubmit);

  const btn = document.getElementById("track-btn");
  if (btn) btn.addEventListener("click", handleTrackSubmit);
});