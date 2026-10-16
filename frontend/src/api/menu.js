export async function updateMenuItem(
    restaurantId,
    itemId,
    menuItem
) {
    const response = await fetch(
        `http://localhost:8000/restaurants/${restaurantId}/menu/${itemId}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
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
            headers: {
                "Content-Type": "application/json"
            },
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
