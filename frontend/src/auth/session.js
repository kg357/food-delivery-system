
const TOKEN_KEY = "foodDeliveryAccessToken";

// Read the user information contained in a JWT.
function decodeToken(token) {
    const parts = token.split(".");

    if (parts.length !== 3) {
        throw new Error("Invalid authentication token.");
    }

    const base64 = parts[1]
        .replace(/-/g, "+")
        .replace(/_/g, "/");

    const padded = base64.padEnd(
        Math.ceil(base64.length / 4) * 4,
        "="
    );

    const payload = JSON.parse(atob(padded));

    if (
        typeof payload.sub !== "string" ||
        !["customer", "restaurant_owner", "admin"]
            .includes(payload.role) ||
        typeof payload.exp !== "number"
    ) {
        throw new Error("Invalid authentication token.");
    }

    if (payload.exp * 1000 <= Date.now()) {
        throw new Error("Authentication token has expired.");
    }

    return {
        id: payload.sub,
        role: payload.role,
    };
}

// Save a successful login.
export function saveSession(token) {
    const user = decodeToken(token);

    sessionStorage.setItem(TOKEN_KEY, token);

    return user;
}

// Retrieve the current session.
export function getSession() {
    const token = sessionStorage.getItem(TOKEN_KEY);

    if (!token) {
        return null;
    }

    try {
        const user = decodeToken(token);

        return {
            ...user,
            token,
        };
    } catch {
        clearSession();
        return null;
    }
}

// Sign out.
export function clearSession() {
    sessionStorage.removeItem(TOKEN_KEY);
}
