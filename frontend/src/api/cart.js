
import { getSession } from "../auth/session";

const API_BASE = "http://localhost:8000";

// Send an authenticated cart request.
async function cartRequest(path, options = {}) {
    const session = getSession();

    if (!session || session.role !== "customer") {
        throw new Error("You must be signed in as a customer.");
    }

    const response = await fetch(
        `${API_BASE}/customers/${encodeURIComponent(session.id)}/cart${path}`,
        {
            ...options,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.token}`,
                ...options.headers,
            },
            cache: "no-store",
        }
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = data?.detail;

        const message =
            typeof detail === "string"
                ? detail
                : Array.isArray(detail)
                    ? detail.map((error) => error.msg).join(", ")
                    : `Cart request failed (${response.status})`;

        throw new Error(message);
    }

    return data;
}

// Retrieve the active cart, creating one if necessary.
export async function getCart() {
    return cartRequest("");
}

// Add a menu item to the active cart.
export async function addCartItem(
    restaurantId,
    itemId,
    quantity = 1
) {
    return cartRequest("/items", {
        method: "POST",
        body: JSON.stringify({
            restaurant_id: Number(restaurantId),
            item_id: itemId,
            quantity,
        }),
    });
}

// Set the quantity of an existing cart item.
export async function updateCartItem(itemId, quantity) {
    return cartRequest(
        `/items/${encodeURIComponent(itemId)}`,
        {
            method: "PATCH",
            body: JSON.stringify({ quantity }),
        }
    );
}

// Remove one menu item.
export async function removeCartItem(itemId) {
    return cartRequest(
        `/items/${encodeURIComponent(itemId)}`,
        {
            method: "DELETE",
        }
    );
}

// Remove every item from the cart.
export async function clearCart() {
    return cartRequest("/items", {
        method: "DELETE",
    });
}
