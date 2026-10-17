
function AddMenuItemForm({
    restaurantId,
    setRestaurantId,
    name,
    setName,
    description,
    setDescription,
    price,
    setPrice,
    available,
    setAvailable,
    handleSubmit,
    isOwnerMode = false
}) {
    return (
        <form onSubmit={handleSubmit} noValidate>
            {!isOwnerMode && (
            <>
                <label htmlFor="restaurantId">Restaurant ID</label>
                <input
                id="restaurantId"
                type="number"
                min="1"
                value={restaurantId}
                onChange={(event) => setRestaurantId(event.target.value)}
                required
                />
            </>
            )}

            <label htmlFor="name">Name</label>
            <input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
            />

            <label htmlFor="description">Description</label>
            <input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            />

            <label htmlFor="price">Price</label>
            <input
                id="price"
                type="number"
                min="0"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
            />

            <label htmlFor="available">Availability</label>
            <select
                id="available"
                value={String(available)}
                onChange={(e) => setAvailable(e.target.value === "true")}
            >
                <option value="true">Available</option>
                <option value="false">Unavailable</option>
            </select>

            <button type="submit">Add Menu Item</button>
        </form>
    );
}

export default AddMenuItemForm;
