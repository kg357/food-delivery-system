
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getMenuItem } from "../../api/menu";
import { getCart, addCartItem } from "../../api/cart";

import Loading from "../../components/Loading/Loading";

import "./MenuItemDetails.css";

function MenuItemDetails() {
    const { id, itemId } = useParams();

    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Shopping cart state
    const [adding, setAdding] = useState(false);
    const [cartError, setCartError] = useState("");
    const [cartSuccess, setCartSuccess] = useState("");

    // Retrieve the menu item.
    useEffect(() => {
        let active = true;

        setLoading(true);
        setError("");
        setCartError("");
        setCartSuccess("");

        getMenuItem(id, itemId)
            .then((data) => {
                if (active) {
                    setItem(data);
                    setLoading(false);
                }
            })
            .catch((err) => {
                if (active) {
                    setError(
                        err.message || "Failed to load menu item"
                    );
                    setLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, [id, itemId]);

    // Add the selected item to the customer's cart.
    async function handleAddToCart() {
        if (!item || !item.available || adding) {
            return;
        }

        setAdding(true);
        setCartError("");
        setCartSuccess("");

        try {
            // Ensure an active cart exists.
            await getCart();

            // Add one unit using the backend API.
            await addCartItem(
                Number(id),
                item.id,
                1
            );

            setCartSuccess(
                `${item.name} added to your cart!`
            );
        } catch (err) {
            setCartError(
                err.message || "Failed to add item to cart."
            );
        } finally {
            setAdding(false);
        }
    }

    if (loading) {
        return <Loading />;
    }

    return (
        <main className="menu-item-details">
            <Link
                to={`/restaurants/${id}`}
                className="menu-item-back-link"
            >
                <span aria-hidden="true">←</span>
                {" "}Back to restaurant
            </Link>

            {error && (
                <p className="error" role="alert">
                    {error}
                </p>
            )}

            {item && (
                <div className="menu-item-card">
                    <h1>{item.name}</h1>

                    <p className="menu-item-description">
                        {item.description}
                    </p>

                    <p className="menu-item-price">
                        ${Number(item.price).toFixed(2)}
                    </p>

                    <p
                        className={
                            item.available
                                ? "menu-item-status available"
                                : "menu-item-status unavailable"
                        }
                    >
                        {item.available
                            ? "Available"
                            : "Currently unavailable"}
                    </p>

                    {/* Add to Cart */}
                    <div className="menu-item-cart-actions">
                        <button
                            type="button"
                            className="add-to-cart-button"
                            onClick={handleAddToCart}
                            disabled={!item.available || adding}
                        >
                            {adding
                                ? "Adding..."
                                : item.available
                                    ? "Add to Cart"
                                    : "Unavailable"}
                        </button>

                        {cartSuccess && (
                            <div
                                className="cart-add-success"
                                role="status"
                            >
                                <p>{cartSuccess}</p>

                                <Link to="/cart">
                                    View Cart →
                                </Link>
                            </div>
                        )}

                        {cartError && (
                            <p
                                className="cart-add-error"
                                role="alert"
                            >
                                {cartError}
                            </p>
                        )}
                    </div>
                </div>
            )}
        </main>
    );
}

export default MenuItemDetails;
