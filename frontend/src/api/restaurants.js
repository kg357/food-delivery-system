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

export async function createRestaurant(restaurantData) {
  const response = await fetch(
    "http://localhost:8000/restaurants",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
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

export async function updateRestaurant(id, restaurantData) {
  const response = await fetch(
    `http://localhost:8000/restaurants/${id}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(restaurantData),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      typeof errorData?.detail === "string"
        ? errorData.detail
        : `Failed to update restaurant (${response.status}).`
    );
  }

  return response.json();
}