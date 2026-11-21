
const API_BASE = "http://localhost:8000";

// Handle API responses and extract useful error messages.
async function handleResponse(response) {
    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = data?.detail;

        const message =
            typeof detail === "string"
                ? detail
                : Array.isArray(detail)
                    ? detail.map((error) => error.msg).join(", ")
                    : `Request failed (${response.status})`;

        throw new Error(message);
    }

    return data;
}

// Authenticate an existing user.
export async function loginCustomer(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email,
            password,
        }),
    });

    return handleResponse(response);
}

// Register a new customer account.
export async function registerCustomer(customerData) {
    const response = await fetch(
        `${API_BASE}/customers/register`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(customerData),
        }
    );

    return handleResponse(response);
}