const API_BASE = "http://127.0.0.1:8000";

// ── Helper ──────────────────────────────────────────────────────

async function request(method, path, body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, options);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Something went wrong");
  }
  return data;
}

// ── Products ────────────────────────────────────────────────────

async function trackProduct(url) {
  return request("POST", "/track", { url });
}

async function getAllProducts() {
  return request("GET", "/products");
}

async function getProduct(id) {
  return request("GET", `/products/${id}`);
}

async function refreshProduct(id) {
  return request("POST", `/products/${id}/refresh`);
}

async function deleteProduct(id) {
  return request("DELETE", `/products/${id}`);
}

// ── Alerts ──────────────────────────────────────────────────────

async function setAlert(productId, alertPrice, enabled = true) {
  return request("POST", "/alerts", {
    product_id: productId,
    alert_price: alertPrice,
    enabled,
  });
}

// ── Toast notifications ─────────────────────────────────────────

function showToast(message, type = "info") {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.className = `toast ${type}`;

  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ── Formatting helpers ──────────────────────────────────────────

function formatPrice(price) {
  if (price === null || price === undefined) return "—";
  return "₹" + Number(price).toLocaleString("en-IN", {
    maximumFractionDigits: 0,
  });
}

function formatPlatform(platform) {
  const map = {
    amazon: "Amazon",
    flipkart: "Flipkart",
    myntra: "Myntra",
    croma: "Croma",
    reliancedigital: "Reliance Digital",
    meesho: "Meesho",
    tatacliq: "Tata CLiQ",
    snapdeal: "Snapdeal",
  };
  return map[platform] || platform;
}

function platformColor(platform) {
  const map = {
    amazon: "pill-amber",
    flipkart: "pill-blue",
    myntra: "pill-red",
    croma: "pill-green",
    reliancedigital: "pill-blue",
    meesho: "pill-red",
    tatacliq: "pill-amber",
    snapdeal: "pill-green",
  };
  return map[platform] || "pill-gray";
}

function verdictLabel(verdict) {
  const map = {
    buy: "Buy now",
    wait: "Wait",
    watching: "Watching",
  };
  return map[verdict] || "—";
}

function verdictPill(verdict) {
  const map = {
    buy: "pill-green",
    wait: "pill-amber",
    watching: "pill-gray",
  };
  return map[verdict] || "pill-gray";
}

function verdictEmoji(verdict) {
  const map = {
    buy: "✅",
    wait: "⏳",
    watching: "👀",
  };
  return map[verdict] || "—";
}

function confidencePill(confidence) {
  const map = {
    high: "pill-green",
    medium: "pill-blue",
    low: "pill-amber",
  };
  return map[confidence] || "pill-gray";
}

function scrapeStatusText(status) {
  if (status === "success") return "Live";
  if (status === "pending") return "Pending";
  if (status === "price_not_found") return "Price not found";
  if (status && status.startsWith("error")) return "Fetch error";
  return status || "Unknown";
}

function scrapeStatusPill(status) {
  if (status === "success") return "pill-green";
  if (status === "pending") return "pill-blue";
  return "pill-red";
}