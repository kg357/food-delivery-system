
import { getSession } from "../auth/session";

const API_BASE = "http://localhost:8000";

// Make an authenticated request to an order endpoint.
async function orderRequest(path, options = {}) {
    const session = getSession();

    if (!session || session.role !== "customer") {
        throw new Error(
            "You must be signed in as a customer."
        );
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            Authorization: `Bearer ${session.token}`,
            ...options.headers,
        },
        cache: "no-store",
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = data?.detail;

        const message =
            typeof detail === "string"
                ? detail
                : Array.isArray(detail)
                    ? detail.map((error) => error.msg).join(", ")
                    : `Order request failed (${response.status})`;

        throw new Error(message);
    }

    return data;
}

// Convert the active shopping cart into an order.
export async function checkout() {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    return orderRequest(
        `/customers/${encodeURIComponent(session.id)}/checkout`,
        {
            method: "POST",
        }
    );
}

// Retrieve an individual order.
export async function getOrder(orderId) {
    return orderRequest(
        `/orders/${encodeURIComponent(orderId)}`
    );
}

// Retrieve the signed-in customer's order history.
export async function getOrderHistory() {
    const session = getSession();

    if (!session) {
        throw new Error("You must be signed in.");
    }

    return orderRequest(
        `/customers/${encodeURIComponent(session.id)}/orders`
    );
}
