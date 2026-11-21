
import { getSession } from "../auth/session";

const API_BASE = "http://localhost:8000";

// Get authorization headers for the signed-in owner.
function getOwnerHeaders() {
    const session = getSession();

    if (!session || session.role !== "restaurant_owner") {
        throw new Error(
            "You must be signed in as a restaurant owner."
        );
    }

    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.token}`,
    };
}

// Public: retrieve all restaurants.
export async function getRestaurants() {
    const response = await fetch(
        `${API_BASE}/restaurants`
    );

    if (!response.ok) {
        throw new Error("Failed to load restaurants");
    }

    return response.json();
}

// Public: retrieve restaurant details.
export async function getRestaurantById(id) {
    const response = await fetch(
        `${API_BASE}/restaurants/${id}`
    );

    if (!response.ok) {
        throw new Error("Restaurant not found");
    }

    return response.json();
}

// Owner only: create a restaurant.
export async function createRestaurant(restaurantData) {
    const response = await fetch(
        `${API_BASE}/restaurants`,
        {
            method: "POST",
            headers: getOwnerHeaders(),
            body: JSON.stringify(restaurantData),
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        const message =
            typeof errorData?.detail === "string"
                ? errorData.detail
                : "Failed to create restaurant.";

        throw new Error(message);
    }

    return response.json();
}

// Owner only: update an existing restaurant.
export async function updateRestaurant(id, restaurantData) {
    const response = await fetch(
        `${API_BASE}/restaurants/${id}`,
        {
            method: "PATCH",
            headers: getOwnerHeaders(),
            body: JSON.stringify(restaurantData),
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        const message =
            typeof errorData?.detail === "string"
                ? errorData.detail
                : `Failed to update restaurant (${response.status}).`;

        throw new Error(message);
    }

    return response.json();
}
