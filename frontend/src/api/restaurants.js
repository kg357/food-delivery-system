const API_BASE = "http://localhost:8000";

export async function getRestaurants() {
    const response = await fetch(
        `${API_BASE}/restaurants`
    );

    if (!response.ok) {
        throw new Error("Failed to load restaurants");
    }

    return response.json();
}

export async function getRestaurantById(id) {
    const response = await fetch(
        `${API_BASE}/restaurants/${id}`
    );

    if (!response.ok) {
        throw new Error("Restaurant not found");
    }

    return response.json();
}