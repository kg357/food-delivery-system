
import { getSession } from "../auth/session";

const API_BASE = "http://localhost:8000";

// Send an authenticated request to a customer endpoint.
async function customerRequest(path, options = {}) {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.token}`,
            ...options.headers,
        },
    });

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

// Retrieve the signed-in customer's profile.
export async function getCustomerProfile() {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    return customerRequest(`/customers/${session.id}`);
}

// Update the customer's name or delivery address.
export async function updateCustomerProfile(updates) {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    return customerRequest(`/customers/${session.id}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
    });
}

// Deactivate the customer's account.
export async function deactivateCustomerAccount() {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    return customerRequest(
        `/customers/${session.id}/deactivate`,
        {
            method: "POST",
        }
    );
}
