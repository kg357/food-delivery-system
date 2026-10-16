import AddMenuItemForm from "../../components/AddMenuItemForm/AddMenuItemForm";
import { useState } from "react";
import { addMenuItem } from "../../api/menu";

function AddMenuItem() {
    const [restaurantId, setRestaurantId] = useState("1");
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [price, setPrice] = useState("");
    const [available, setAvailable] = useState(true);
    const [createdItem, setCreatedItem] = useState(null);
    const [error, setError] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");
        setCreatedItem(null);

        if (!restaurantId || Number(restaurantId) <= 0 ||
            !Number.isInteger(Number(restaurantId))) {
            setError("Enter a valid restaurant ID.");
            return;
        }

        if (!name.trim() || price.trim() === "" ||
            !Number.isFinite(Number(price)) || Number(price) < 0) {
            setError("Enter a valid name and price.");
            return;
        }

        try {
            const item = await addMenuItem(Number(restaurantId), {
                name: name.trim(),
                description,
                price: Number(price),
                available
            });

            setCreatedItem(item);
            setName("");
            setDescription("");
            setPrice("");
            setAvailable(true);
        } catch (error) {
            setError(error.message);
        }
    }

    return (
        <div>
            <h1>Add Menu Item</h1>

            <AddMenuItemForm
                restaurantId={restaurantId}
                setRestaurantId={setRestaurantId}
                name={name}
                setName={setName}
                description={description}
                setDescription={setDescription}
                price={price}
                setPrice={setPrice}
                available={available}
                setAvailable={setAvailable}
                handleSubmit={handleSubmit}
            />

            {error && <p role="alert">{error}</p>}

            {createdItem && (
                <div>
                    <p role="status">Menu item added successfully!</p>
                    <h2>{createdItem.name}</h2>
                    <p>{createdItem.description}</p>
                    <p>${Number(createdItem.price).toFixed(2)}</p>
                </div>
            )}
        </div>
    );
}

export default AddMenuItem;