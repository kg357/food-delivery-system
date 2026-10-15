import { useEffect, useState } from "react";
import "./App.css";


function App() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [editingItem, setEditingItem] = useState(null);

  const restaurantId = 1; // Temporary until owner login is implemented

useEffect(() => {
  async function loadMenu() {
    try {
      const response = await fetch(
        `/restaurants/${restaurantId}/menu`
      );

      if (!response.ok) {
        throw new Error("Failed to load menu");
      }

      const data = await response.json();
      setItems(data);
    } catch (error) {
      setError(error.message);
    }
  }

  loadMenu();
}, []);

  async function handleSave(event) {
  event.preventDefault();

  try {
    const response = await fetch(
      `/restaurants/${editingItem.restaurant_id}/menu/${editingItem.id}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: editingItem.name,
          description: editingItem.description,
          price: Number(editingItem.price),
          available: editingItem.available,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to update menu item");
    }

    const updatedItem = await response.json();

    setItems((previousItems) =>
      previousItems.map((item) =>
        item.id === updatedItem.id ? updatedItem : item
      )
    );

    setEditingItem(null);
    alert("Menu item updated successfully!");
  } catch (error) {
    alert(error.message);
  }
}

  return (
    <div>
      <h1>Restaurant Menu</h1>
      {error && <p role="alert">{error}</p>}

      {items.map((item) => (
        <div key={item.id}>
          <h3>{item.name}</h3>
          <p>{item.description}</p>
          <p>${item.price.toFixed(2)}</p>

          <button onClick={() => setEditingItem({ ...item })}>
            Edit
          </button>
        </div>
      ))}

      {editingItem && (
        <form onSubmit={handleSave}>
          <h2>Edit Menu Item</h2>

          <label htmlFor="name">Name</label>
          <input
            id="name"
            value={editingItem.name}
            onChange={(e) =>
              setEditingItem({ ...editingItem, name: e.target.value })
            }
            required
          />

          <label htmlFor="description">Description</label>
          <input
            id="description"
            value={editingItem.description}
            onChange={(e) =>
              setEditingItem({
                ...editingItem,
                description: e.target.value,
              })
            }
          />

          <label htmlFor="price">Price</label>
          <input
            id="price"
            type="number"
            min="0"
            step="0.01"
            value={editingItem.price}
            onChange={(e) =>
              setEditingItem({
                ...editingItem,
                price: e.target.value,
              })
            }
            required
          />

          <label htmlFor="available">Availability</label>
          <select
            id="available"
            value={String(editingItem.available)}
            onChange={(e) =>
              setEditingItem({
                ...editingItem,
                available: e.target.value === "true",
              })
            }
          >
            <option value="true">Available</option>
            <option value="false">Unavailable</option>
          </select>

          <button type="submit">Save Changes</button>
          <button type="button" onClick={() => setEditingItem(null)}>
            Cancel
          </button>
        </form>
      )}
    </div>
  );
}

export default App;