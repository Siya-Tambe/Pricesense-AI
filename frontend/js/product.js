let currentProduct = null;

// ── Get product ID from URL ─────────────────────────────────────

function getProductId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}


// ── Load full product detail ────────────────────────────────────

async function loadProduct() {
  const id = getProductId();
  if (!id) {
    window.location.href = "dashboard.html";
    return;
  }

  try {
    const product = await getProduct(id);
    currentProduct = product;
    renderProductHeader(product);
    renderStatCards(product);
    renderVerdictCard(product);
    renderPriceChart(product);
    renderAlertPanel(product);
    renderDataStatus(product);
  } catch (err) {
    document.getElementById("page-content").innerHTML = `
      <div class="empty-state">
        <div class="icon">⚠️</div>
        <h3>Could not load product</h3>
        <p style="font-size:13px;color:#aaa;">${err.message}</p>
        <a href="dashboard.html" class="btn-primary" style="display:inline-block;margin-top:16px;text-decoration:none;">
          Back to dashboard
        </a>
      </div>`;
  }
}


// ── Product header ──────────────────────────────────────────────

function renderProductHeader(product) {
  const el = document.getElementById("product-header");
  if (!el) return;

  const thumbHtml = product.thumbnail
    ? `<img src="${product.thumbnail}" style="width:52px;height:52px;border-radius:10px;object-fit:cover;border:1px solid rgba(0,0,0,0.08);" onerror="this.style.display='none'">`
    : `<div style="width:52px;height:52px;border-radius:10px;background:#f8f9fb;border:1px solid rgba(0,0,0,0.08);display:flex;align-items:center;justify-content:center;font-size:24px;">${platformEmoji(product.platform)}</div>`;

  el.innerHTML = `
    <div style="display:flex;align-items:flex-start;gap:14px;">
      ${thumbHtml}
      <div style="flex:1;min-width:0;">
        <h1 style="font-size:18px;font-weight:600;line-height:1.4;margin-bottom:6px;">
          ${escapeHtml(product.name || "Unknown product")}
        </h1>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span class="pill ${platformColor(product.platform)}">${formatPlatform(product.platform)}</span>
          <span class="pill ${scrapeStatusPill(product.scrape_status)}">${scrapeStatusText(product.scrape_status)}</span>
          ${product.last_fetched ? `<span style="font-size:12px;color:#aaa;">Updated ${product.last_fetched}</span>` : ""}
          <a href="${product.url}" target="_blank" style="font-size:12px;color:#185FA5;text-decoration:none;">
            View on ${formatPlatform(product.platform)} ↗
          </a>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-shrink:0;">
        <button class="btn-secondary" onclick="handleRefresh()">Refresh</button>
        <button class="btn-danger" onclick="handleDelete()">Remove</button>
      </div>
    </div>`;
}


// ── Stat cards ──────────────────────────────────────────────────

function renderStatCards(product) {
  const el = document.getElementById("stat-cards");
  if (!el) return;

  const stats = product.stats || {};
  const pred = product.prediction || {};

  const changeColor = pred.stats?.price_change_pct < 0 ? "#3B6D11" : pred.stats?.price_change_pct > 0 ? "#A32D2D" : "#888";
  const changeSign = pred.stats?.price_change_pct > 0 ? "+" : "";
  const changePct = pred.stats?.price_change_pct != null
    ? `<div class="sub" style="color:${changeColor};">${changeSign}${pred.stats.price_change_pct}% forecast</div>`
    : `<div class="sub">Not enough data</div>`;

  el.innerHTML = `
    <div class="stat-card">
      <div class="label">Current price</div>
      <div class="value">${formatPrice(product.current_price)}</div>
      <div class="sub">${product.days_tracked} data points</div>
    </div>
    <div class="stat-card">
      <div class="label">All-time low</div>
      <div class="value" style="color:#3B6D11;">${formatPrice(stats.all_time_low)}</div>
      <div class="sub">Lowest recorded</div>
    </div>
    <div class="stat-card">
      <div class="label">7-day forecast</div>
      <div class="value">${formatPrice(pred.forecast_day7)}</div>
      ${changePct}
    </div>
    <div class="stat-card">
      <div class="label">Volatility</div>
      <div class="value" style="font-size:18px;">${volatilityLabel(pred.stats?.volatility)}</div>
      <div class="sub">${pred.stats?.volatility != null ? pred.stats.volatility + "% swings" : "—"}</div>
    </div>`;
}


// ── Verdict card ────────────────────────────────────────────────

function renderVerdictCard(product) {
  const el = document.getElementById("verdict-card");
  if (!el) return;

  const pred = product.prediction || {};
  const daysTracked = product.days_tracked || 0;

  if (daysTracked < 2) {
    el.innerHTML = `
      <div class="collecting-banner" style="flex-direction:column;align-items:flex-start;gap:8px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:18px;">📊</span>
          <strong>Still collecting data</strong>
        </div>
        <p style="font-size:13px;line-height:1.6;">
          PriceSense needs at least 2 data points to start analysing price trends.
          Check back soon — prices are fetched automatically every 8 hours.
        </p>
        <div style="width:100%;background:#B5D4F4;border-radius:4px;height:4px;margin-top:4px;">
          <div style="width:${Math.min((daysTracked/7)*100, 100)}%;background:#185FA5;height:4px;border-radius:4px;transition:width 0.5s;"></div>
        </div>
        <span style="font-size:11px;color:#185FA5;">${daysTracked} of 7 recommended data points collected</span>
      </div>`;
    return;
  }

  if (!pred.verdict) {
    el.innerHTML = `
      <div class="collecting-banner">
        <span style="font-size:18px;">⏳</span>
        <span>Analysing price trends... check back shortly.</span>
      </div>`;
    return;
  }

  const verdict = pred.verdict;
  el.innerHTML = `
    <div class="verdict-card ${verdict}">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
        <div class="verdict-icon ${verdict}">${verdictEmoji(verdict)}</div>
        <div>
          <div class="verdict-title">${verdictLabel(verdict)}</div>
          <div class="verdict-sub">
            ${pred.forecast_day7 ? `Forecast: ${formatPrice(pred.forecast_day7)} in 7 days` : ""}
          </div>
        </div>
      </div>
      <div style="display:flex;gap:6px;margin-bottom:4px;flex-wrap:wrap;">
        <span class="pill ${confidencePill(pred.confidence)}">${(pred.confidence || "").charAt(0).toUpperCase() + (pred.confidence || "").slice(1)} confidence</span>
        ${pred.stats?.days_tracked ? `<span class="pill pill-gray">${pred.stats.days_tracked} data points</span>` : ""}
      </div>
      ${pred.reasoning ? `<div class="ai-box">💡 ${escapeHtml(pred.reasoning)}</div>` : ""}
    </div>`;
}


// ── Price chart ─────────────────────────────────────────────────

function renderPriceChart(product) {
  const el = document.getElementById("chart-container");
  if (!el) return;

  if (!product.price_history || product.price_history.length < 2) {
    el.innerHTML = `
      <div style="text-align:center;padding:48px 0;color:#aaa;font-size:14px;">
        Not enough price data yet — check back after a few fetches
      </div>`;
    return;
  }

  el.innerHTML = `<canvas id="price-chart" style="height:220px;"></canvas>`;

  const pred = product.prediction || {};
  renderChart(
    "price-chart",
    product.price_history,
    pred.forecast_day3,
    pred.forecast_day7
  );
}


// ── Alert panel ─────────────────────────────────────────────────

function renderAlertPanel(product) {
  const el = document.getElementById("alert-panel");
  if (!el) return;

  const hasAlert = product.alert_enabled && product.alert_price;

  el.innerHTML = `
    <div style="margin-bottom:12px;">
      <div class="alert-row">
        <div class="alert-dot" style="background:${hasAlert ? "#3B6D11" : "#aaa"};"></div>
        <span style="flex:1;font-weight:500;">
          ${hasAlert ? `Alert set at ${formatPrice(product.alert_price)}` : "No alert set"}
        </span>
        ${hasAlert ? `<span class="pill pill-green">Active</span>` : `<span class="pill pill-gray">Off</span>`}
      </div>
    </div>

    <div style="font-size:13px;color:#888;margin-bottom:10px;">
      Notify me when price drops below:
    </div>

    <div style="display:flex;gap:8px;align-items:center;">
      <div style="position:relative;flex:1;">
        <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#888;font-size:14px;">₹</span>
        <input
          type="number"
          id="alert-input"
          placeholder="${product.current_price ? Math.round(product.current_price * 0.9) : "Enter price"}"
          value="${product.alert_price || ""}"
          style="width:100%;padding:9px 12px 9px 28px;border:1.5px solid rgba(0,0,0,0.1);border-radius:8px;font-size:14px;font-family:'Inter',sans-serif;outline:none;"
          onfocus="this.style.borderColor='#185FA5'"
          onblur="this.style.borderColor='rgba(0,0,0,0.1)'"
        />
      </div>
      <button class="btn-primary" onclick="handleSetAlert()" style="padding:9px 16px;">
        Set alert
      </button>
    </div>

    ${hasAlert ? `
    <button
      onclick="handleDisableAlert()"
      style="margin-top:10px;width:100%;padding:8px;background:transparent;border:none;font-size:12px;color:#aaa;cursor:pointer;font-family:'Inter',sans-serif;">
      Disable alert
    </button>` : ""}`;
}


// ── Data status footer ──────────────────────────────────────────

function renderDataStatus(product) {
  const el = document.getElementById("data-status");
  if (!el) return;

  const isStale = product.scrape_status !== "success";

  el.innerHTML = isStale
    ? `<div style="background:#FCEBEB;border:1px solid #F7C1C1;border-radius:8px;padding:10px 14px;font-size:13px;color:#A32D2D;display:flex;align-items:center;gap:8px;">
        ⚠️ Last fetch failed — <strong>${scrapeStatusText(product.scrape_status)}</strong>.
        Price data may be stale. <button onclick="handleRefresh()" style="background:none;border:none;color:#A32D2D;text-decoration:underline;cursor:pointer;font-size:13px;font-family:'Inter',sans-serif;">Retry now</button>
       </div>`
    : `<div style="font-size:12px;color:#aaa;text-align:center;">
        Prices fetched automatically every 8 hours · Last updated ${product.last_fetched || "—"}
       </div>`;
}


// ── Action handlers ─────────────────────────────────────────────

async function handleRefresh() {
  const id = getProductId();
  if (!id) return;

  showToast("Refreshing price...", "info");
  try {
    await refreshProduct(id);
    showToast("Price updated!", "success");
    await loadProduct();
  } catch (err) {
    showToast("Could not refresh: " + err.message, "error");
  }
}


async function handleDelete() {
  const id = getProductId();
  if (!id) return;
  if (!confirm("Stop tracking this product and delete all its price history?")) return;

  try {
    await deleteProduct(id);
    showToast("Product removed", "info");
    setTimeout(() => (window.location.href = "dashboard.html"), 800);
  } catch (err) {
    showToast("Could not delete: " + err.message, "error");
  }
}


async function handleSetAlert() {
  const id = getProductId();
  const input = document.getElementById("alert-input");
  if (!id || !input) return;

  const price = parseFloat(input.value);
  if (!price || price <= 0) {
    showToast("Please enter a valid price", "error");
    return;
  }

  try {
    await setAlert(parseInt(id), price, true);
    showToast(`Alert set for ${formatPrice(price)}`, "success");
    await loadProduct();
  } catch (err) {
    showToast("Could not set alert: " + err.message, "error");
  }
}


async function handleDisableAlert() {
  const id = getProductId();
  if (!id || !currentProduct) return;

  try {
    await setAlert(parseInt(id), currentProduct.alert_price, false);
    showToast("Alert disabled", "info");
    await loadProduct();
  } catch (err) {
    showToast("Could not disable alert: " + err.message, "error");
  }
}


// ── Helpers ─────────────────────────────────────────────────────

function volatilityLabel(v) {
  if (v == null) return "—";
  if (v < 5) return "Low";
  if (v < 15) return "Medium";
  return "High";
}

function platformEmoji(platform) {
  const map = { amazon: "📦", 
    flipkart: "🛒", 
    myntra: "👗", 
    croma: "💻",
    reliancedigital: "📱",
    meesho: "🛍️",
    tatacliq: "🏷️",
    snapdeal: "⚡", };
  return map[platform] || "🏷️";
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}


// ── Init ────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", loadProduct);