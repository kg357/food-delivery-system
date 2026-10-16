import { useEffect, useState } from "react";
import { updateMenuItem } from "../../api/menu";
import MenuItemForm from "../../components/MenuItemForm/MenuItemForm";
import "./EditMenuItem.css"


function EditMenuItem() {
    const [items, setItems] = useState([]);

useEffect(() => {
  async function loadMenu() {
    try {
      const response = await fetch(
    "http://localhost:8000/restaurants/1/menu"
);

      if (!response.ok) {
        throw new Error("Failed to load menu");
      }

      const data = await response.json();
      setItems(data);
    } catch (error) {
      console.error("Failed to load menu:", error);
    }
  }

  loadMenu();
}, []);
    const [editingItem, setEditingItem] =
        useState(null);

    async function handleSave(event) {
        event.preventDefault();

        try {
            const updatedItem = await updateMenuItem(
                editingItem.restaurant_id,
                editingItem.id,
                {
                    name: editingItem.name,
                    description: editingItem.description,
                    price: Number(editingItem.price),
                    available: editingItem.available
                }
            )

            setItems((previousItems) =>
                previousItems.map((item) =>
                    item.id === updatedItem.id
                        ? updatedItem
                        : item
                )
            );

            setEditingItem(null);
            alert("Menu item updated successfully!")
        } catch (error) {
            alert(error.message);
        }
    }

    return (
        <div className="menu-page">
            <h1 className="page-title">Restaurant Menu</h1>

            <div className="menu-grid">
                {items.map((item) => (
                    <div key={item.id} className="menu-card">
                        <h3>{item.name}</h3>
                        <p className="menu-description">{item.description}</p>
                        <p className="menu-price">${item.price.toFixed(2)}</p>

                        <button className="edit-btn" onClick={() => setEditingItem({
                            ...item
                        })
                        }
                        >
                            Edit
                        </button>
                    </div>
                ))}
            </div>

            {editingItem && (
                <MenuItemForm
                    editingItem={editingItem}
                    setEditingItem={
                        setEditingItem
                    }
                    handleSave={handleSave}
                    handleCancel={() =>
                        setEditingItem(null)
                    }
                />

            )}

        </div>
    );
}

export default EditMenuItem;