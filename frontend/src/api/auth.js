// Authentication and customer-account API calls.
//
// The login token is kept in sessionStorage, so it is forgotten when the
// browser tab closes. The backend decides what a token allows; the role
// stored here is only used to pick which page to show.

const API_BASE = "http://localhost:8000";
const SESSION_KEY = "session";

// ---------------------------------------------------------------
// Session (token + who is signed in)
// ---------------------------------------------------------------

export function getSession() {
  try {
    return JSON.parse(sessionStorage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}

export function getToken() {
  return getSession()?.token ?? null;
}

// Returns { id, role } for the signed-in user, or null.
export function getCurrentUser() {
  return getSession()?.user ?? null;
}

export function logout() {
  sessionStorage.removeItem(SESSION_KEY);
}

// Header to add to any request that needs a signed-in user.
export function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Where each role lands after signing in.
export function homePathForRole(role) {
  if (role === "restaurant_owner") return "/owner/restaurants";
  if (role === "admin") return "/admin";
  return "/restaurants";
}

// A token is three base64url parts: header.payload.signature.
// We only read the payload to learn the user's id and role. We cannot
// verify the signature here, which is fine: the backend verifies it on
// every request, so a faked token would only change what this page shows.
function readTokenPayload(token) {
  const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(part));
}

// ---------------------------------------------------------------
// Errors
// ---------------------------------------------------------------

async function errorMessage(response, fallback) {
  const data = await response.json().catch(() => null);

  // 400, 401, 403 and 404 send a plain text "detail".
  if (typeof data?.detail === "string") {
    return data.detail;
  }

  // 422 sends a list of problems. Show a friendly summary.
  if (response.status === 422) {
    return "Please check the form: some fields are missing or invalid.";
  }

  return fallback;
}

// ---------------------------------------------------------------
// Login
// ---------------------------------------------------------------

export async function login(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(await errorMessage(response, "Unable to sign in."));
  }

  const { access_token: token } = await response.json();
  const payload = readTokenPayload(token);
  const user = { id: payload.sub, role: payload.role };

  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ token, user }));

  return user;
}

// ---------------------------------------------------------------
// Customer accounts
// ---------------------------------------------------------------

export async function registerCustomer(data) {
  const response = await fetch(`${API_BASE}/customers/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(
      await errorMessage(response, "Unable to create the account.")
    );
  }

  return response.json();
}

export async function getCustomer(id) {
  const response = await fetch(`${API_BASE}/customers/${id}`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(
      await errorMessage(response, "Unable to load your account.")
    );
  }

  return response.json();
}

export async function updateCustomer(id, data) {
  const response = await fetch(`${API_BASE}/customers/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(
      await errorMessage(response, "Unable to save your changes.")
    );
  }

  return response.json();
}

export async function deactivateCustomer(id) {
  const response = await fetch(`${API_BASE}/customers/${id}/deactivate`, {
    method: "POST",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(
      await errorMessage(response, "Unable to deactivate the account.")
    );
  }

  return response.json();
}
