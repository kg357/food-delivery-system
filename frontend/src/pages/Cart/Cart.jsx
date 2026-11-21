
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { checkout } from "../../api/orders";

import {
    getCart,
    updateCartItem,
    removeCartItem,
    clearCart,
} from "../../api/cart";

import "./Cart.css";

// Format backend-provided monetary values.
function formatPrice(amount) {
    return `$${Number(amount).toFixed(2)}`;
}

function Cart() {
    const navigate = useNavigate();
    const [checkoutBusy, setCheckoutBusy] = useState(false);
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");

    // Retrieve or create the customer's active cart.
    useEffect(() => {
        let active = true;

        async function loadCart() {
            try {
                const data = await getCart();

                if (active) {
                    setCart(data);
                }
            } catch (err) {
                if (active) {
                    setError(err.message);
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        loadCart();

        return () => {
            active = false;
        };
    }, []);

    // Execute a cart modification and use the updated
    // cart returned by the backend.
    async function performCartAction(action) {
        if (busy || checkoutBusy) return;

        setBusy(true);
        setError("");

        try {
            const updatedCart = await action();
            setCart(updatedCart);
        } catch (err) {
            setError(err.message);
        } finally {
            setBusy(false);
        }
    }

    // Change an item's quantity.
    function handleQuantityChange(itemId, quantity) {
        if (!Number.isInteger(quantity) || quantity < 1) {
            return;
        }

        performCartAction(() =>
            updateCartItem(itemId, quantity)
        );
    }

    // Remove a single item.
    function handleRemove(itemId) {
        performCartAction(() =>
            removeCartItem(itemId)
        );
    }

    // Clear the entire cart.
    function handleClear() {
        performCartAction(() => clearCart());
    }

    async function handleCheckout() {
        if (busy || checkoutBusy || !cart?.items.length) {
            return;
        }

        setCheckoutBusy(true);
        setError("");

        try {
            const order = await checkout();

            if (!order?.id) {
                throw new Error(
                    "Checkout returned no order ID. " +
                    "Check your order history before trying again."
                );
            }

            navigate(
                `/orders/${encodeURIComponent(order.id)}`,
                {
                    replace: true,
                    state: { checkoutSuccess: true },
                }
            );
        } catch (err) {
            setError(
                `${err.message} If you're unsure whether the order ` +
                "was created, verify your order history before " +
                "attempting checkout again."
            );
        } finally {
            setCheckoutBusy(false);
        }
    }


    if (loading) {
        return (
            <main className="cart-page">
                <p>Loading your cart...</p>
            </main>
        );
    }

    if (!cart) {
        return (
            <main className="cart-page">
                <h1>Shopping Cart</h1>

                <p role="alert">
                    {error || "Unable to load your cart."}
                </p>

                <Link to="/restaurants">
                    Back to Restaurants
                </Link>
            </main>
        );
    }

    const isEmpty = cart.items.length === 0;

    return (
        <main className="cart-page">
            <Link
                to="/restaurants"
                className="cart-back"
            >
                ← Continue Shopping
            </Link>

            <h1>Shopping Cart</h1>

            <p className="cart-subtitle">
                Review your items before checkout.
            </p>

            {error && (
                <p role="alert" className="cart-error">
                    {error}
                </p>
            )}

            {isEmpty ? (
                <section className="cart-empty">
                    <h2>Your cart is empty</h2>

                    <p>
                        Browse restaurants and add
                        something to your cart.
                    </p>

                    <Link
                        to="/restaurants"
                        className="cart-primary-link"
                    >
                        Browse Restaurants
                    </Link>
                </section>
            ) : (
                <>
                    <section className="cart-items">
                        <h2>Your Items</h2>

                        {cart.items.map((item) => (
                            <article
                                key={item.item_id}
                                className="cart-item"
                            >
                                <div className="cart-item-info">
                                    <h3>{item.name}</h3>

                                    <p>
                                        {formatPrice(item.unit_price)}
                                        {" "}each
                                    </p>

                                    <button
                                        type="button"
                                        className="cart-remove"
                                        disabled={busy || checkoutBusy}
                                        onClick={() =>
                                            handleRemove(item.item_id)
                                        }
                                    >
                                        Remove
                                    </button>
                                </div>

                                <div className="cart-item-actions">
                                    <div className="quantity-controls">
                                        <button
                                            type="button"
                                            aria-label={`Decrease ${item.name} quantity`}
                                            disabled={
                                                busy || checkoutBusy || item.quantity <= 1
                                            }
                                            onClick={() =>
                                                handleQuantityChange(
                                                    item.item_id,
                                                    item.quantity - 1
                                                )
                                            }
                                        >
                                            −
                                        </button>

                                        <span>
                                            {item.quantity}
                                        </span>

                                        <button
                                            type="button"
                                            aria-label={`Increase ${item.name} quantity`}
                                            disabled={busy || checkoutBusy}
                                            onClick={() =>
                                                handleQuantityChange(
                                                    item.item_id,
                                                    item.quantity + 1
                                                )
                                            }
                                        >
                                            +
                                        </button>
                                    </div>

                                    <strong>
                                        {formatPrice(item.total_price)}
                                    </strong>
                                </div>
                            </article>
                        ))}
                    </section>

                    <section className="cart-summary">
                        <h2>Order Summary</h2>

                        <div className="cart-summary-row">
                            <span>Subtotal</span>
                            <span>
                                {formatPrice(cart.subtotal)}
                            </span>
                        </div>

                        <div className="cart-summary-row cart-total">
                            <strong>Total</strong>
                            <strong>
                                {formatPrice(cart.total)}
                            </strong>
                        </div>

                        <button
                            type="button"
                            className="cart-checkout-button"
                            onClick={handleCheckout}
                            disabled={busy || checkoutBusy}
                        >
                            {checkoutBusy
                                ? "Placing Order..."
                                : "Place Order"}
                        </button>

                        <button
                            type="button"
                            className="cart-clear"
                            onClick={handleClear}
                            disabled={busy || checkoutBusy}
                        >
                            Clear Cart
                        </button>

                    </section>
                </>
            )}
        </main>
    );
}

export default Cart;
