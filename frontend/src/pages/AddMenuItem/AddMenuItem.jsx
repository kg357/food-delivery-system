import AddMenuItemForm from "../../components/AddMenuItemForm/AddMenuItemForm";
import { useState } from "react";
import { addMenuItem } from "../../api/menu";
import { useParams, Link } from "react-router-dom";
import "./AddMenuItem.css";

function AddMenuItem() {
    const { id } = useParams();
    const isOwnerMode = id !== undefined;
    const [manualRestaurantId, setManualRestaurantId] = useState("1");
    const restaurantId = isOwnerMode ? id : manualRestaurantId;
    const setRestaurantId = setManualRestaurantId;
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
    <main className="add-menu-page">
        {isOwnerMode && (
            <Link
            to={`/owner/restaurants/${restaurantId}`}
            className="add-menu-back"
            >
            ← Back to Restaurant
            </Link>
        )}

        <section className="add-menu-card">
        <h1>Add Menu Item</h1>

        <p className="add-menu-description">
            Enter the details of the new item you want to
            add to your restaurant's menu.
        </p>

        <AddMenuItemForm
            isOwnerMode={isOwnerMode}
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

        {error && (
            <p className="add-menu-error" role="alert">
            {error}
            </p>
        )}

        {createdItem && (
        <div className="add-menu-success" role="status">
            <strong>Menu item added successfully!</strong>
            <h2>{createdItem.name}</h2>
            <p>{createdItem.description}</p>
            <p>${Number(createdItem.price).toFixed(2)}</p>
        </div>
        )}
        </section>
    </main>
    );

}

export default AddMenuItem;