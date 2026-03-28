// ── Token storage ───────────────────────────────────────────────

function getToken() {
  return localStorage.getItem("ps_token");
}

function setToken(token) {
  localStorage.setItem("ps_token", token);
}

function removeToken() {
  localStorage.removeItem("ps_token");
  localStorage.removeItem("ps_user");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("ps_user"));
  } catch {
    return null;
  }
}

function setUser(user) {
  localStorage.setItem("ps_user", JSON.stringify(user));
}

function isLoggedIn() {
  return !!getToken();
}


// ── Auth API calls ──────────────────────────────────────────────

async function apiSignup(name, email, password) {
  const res  = await fetch(`${API_BASE}/auth/signup`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ name, email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  setToken(data.token);
  setUser(data.user);
  return data;
}

async function apiLogin(email, password) {
  const res  = await fetch(`${API_BASE}/auth/login`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  setToken(data.token);
  setUser(data.user);
  return data;
}

function logout() {
  removeToken();
  window.location.href = "login.html";
}


// ── Inject auth header into existing api.js request() ──────────
// Override the request function from api.js to include Bearer token

const _originalRequest = window.request;

async function request(method, path, body = null) {
  const token   = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res  = await fetch(`${API_BASE}${path}`, options);
  const data = await res.json();

  if (res.status === 401) {
    removeToken();
    window.location.href = "login.html";
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) throw new Error(data.detail || "Something went wrong");
  return data;
}


// ── Route protection ────────────────────────────────────────────

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.href = "dashboard.html";
  }
}


// ── Render user info in navbar ──────────────────────────────────

function renderNavUser() {
  const user      = getUser();
  const navUser   = document.getElementById("nav-user");
  const navLogin  = document.getElementById("nav-login");
  const navName   = document.getElementById("nav-user-name");
  const navLogout = document.getElementById("nav-logout");

  if (!navUser && !navLogin) return;

  if (isLoggedIn() && user) {
    if (navUser)   navUser.classList.remove("hidden");
    if (navLogin)  navLogin.classList.add("hidden");
    if (navName)   navName.textContent = user.name;
    if (navLogout) navLogout.addEventListener("click", logout);
  } else {
    if (navUser)   navUser.classList.add("hidden");
    if (navLogin)  navLogin.classList.remove("hidden");
  }
}


// ── Demo products ───────────────────────────────────────────────

async function getDemoProducts() {
  const res  = await fetch(`${API_BASE}/demo`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load demo products");
  return data;
}


// ── Auto-run on every page ──────────────────────────────────────

document.addEventListener("DOMContentLoaded", renderNavUser);