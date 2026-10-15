export async function updateMenuItem(
    restaurantId,
    itemId,
    menuItem
) {
    const response = await fetch(
        `/restaurants/${restaurantId}/menu/${itemId}`,
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