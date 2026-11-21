
import { getSession } from "../auth/session";

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


export async function updateMenuItem(
    restaurantId,
    itemId,
    menuItem
) {
    const response = await fetch(
        `http://localhost:8000/restaurants/${restaurantId}/menu/${itemId}`,
        {
            method: "PATCH",
            headers: getOwnerHeaders(),
            body: JSON.stringify(menuItem)
        }
    );

    if (!response.ok) {
        throw new Error("Failed to update menu item");
    }

    return response.json();
}

export async function addMenuItem(restaurantId, menuItem) {
    const response = await fetch(
        `http://localhost:8000/restaurants/${restaurantId}/menu`,
        {
            method: "POST",
            headers: getOwnerHeaders(),
            body: JSON.stringify(menuItem)
        }
    );

    if (!response.ok) {
        throw new Error("Failed to add menu item");
    }

    return response.json();
}

export async function getMenu(restaurantId) {
    const response = await fetch(
        `http://localhost:8000/restaurants/${restaurantId}/menu`
    );

    if (!response.ok) {
        throw new Error("Failed to load menu");
    }

    return response.json();
}

export async function getMenuItem(restaurantId, itemId) {
    const response = await fetch(
        `http://localhost:8000/restaurants/${restaurantId}/menu/${itemId}`
    );

    if (response.status === 404) {
        throw new Error("Menu item not found");
    }

    if (!response.ok) {
        throw new Error("Failed to load menu item");
    }

    return response.json();
}
