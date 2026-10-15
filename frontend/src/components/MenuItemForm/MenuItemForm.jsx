import "./MenuItemForm.css"

function MenuItemForm({
    editingItem,
    setEditingItem,
    handleSave,
    handleCancel
}) {
    return (
        <form className="menu-form" onSubmit={handleSave}>
            <h2>Edit Menu Item</h2>

            <label htmlFor="name">Name</label>
            <input
                id="name"
                value={editingItem.name}
                onChange={(e) =>
                    setEditingItem({
                        ...editingItem,
                        name: e.target.value
                    })
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
                        description: e.target.value
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
            <div className="button-row">
                <button type="submit" className="save-btn">
                    Save Changes
                </button>

                <button
                    type="button"
                    className="cancel-btn"
                    onClick={handleCancel}
                >
                    Cancel
                </button>
            </div>
        </form >
    );
}

export default MenuItemForm;