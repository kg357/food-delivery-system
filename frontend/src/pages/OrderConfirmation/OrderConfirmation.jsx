
import { useEffect, useState } from "react";
import {
    Link,
    useLocation,
    useParams,
} from "react-router-dom";

import { getOrder } from "../../api/orders";

import "./OrderConfirmation.css";

function formatPrice(amount) {
    return `$${Number(amount).toFixed(2)}`;
}

function OrderConfirmation() {
    const { orderId } = useParams();
    const location = useLocation();

    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const justPlaced =
        location.state?.checkoutSuccess === true;

    useEffect(() => {
        let active = true;

        async function loadOrder() {
            setLoading(true);
            setError("");

            try {
                const data = await getOrder(orderId);

                if (active) {
                    setOrder(data);
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

        loadOrder();

        return () => {
            active = false;
        };
    }, [orderId]);

    if (loading) {
        return (
            <main className="order-confirmation">
                <p>Loading order details...</p>
            </main>
        );
    }

    if (!order) {
        return (
            <main className="order-confirmation">
                <h1>Order Details</h1>

                <p role="alert" className="order-error">
                    {error || "Unable to retrieve this order."}
                </p>

                <Link to="/restaurants">
                    Back to Restaurants
                </Link>
            </main>
        );
    }

    return (
        <main className="order-confirmation">
            <div className="confirmation-header">
                <h1>
                    {justPlaced
                        ? "Order Placed Successfully!"
                        : "Order Details"}
                </h1>

                {justPlaced && (
                    <p role="status">
                        Your order has been saved successfully.
                    </p>
                )}

                <p className="confirmation-order-id">
                    Order ID: {order.id}
                </p>
            </div>

            <section className="confirmation-card">
                <h2>Order Information</h2>

                <div className="confirmation-row">
                    <span>Restaurant ID</span>
                    <span>{order.restaurant_id}</span>
                </div>
            </section>

            <section className="confirmation-card">
                <h2>Items Ordered</h2>

                {order.items.map((item) => (
                    <article
                        className="confirmation-item"
                        key={item.item_id}
                    >
                        <div>
                            <h3>{item.name}</h3>

                            <p>{item.description}</p>

                            <p>
                                {item.quantity} ×{" "}
                                {formatPrice(item.unit_price)}
                            </p>
                        </div>

                        <strong>
                            {formatPrice(item.total_price)}
                        </strong>
                    </article>
                ))}
            </section>

            <section className="confirmation-card">
                <h2>Order Summary</h2>

                <div className="confirmation-row">
                    <span>Subtotal</span>
                    <span>
                        {formatPrice(order.subtotal)}
                    </span>
                </div>

                <div className="confirmation-row confirmation-total">
                    <strong>Total</strong>
                    <strong>
                        {formatPrice(order.total)}
                    </strong>
                </div>
            </section>

            <div className="confirmation-actions">
                <Link
                    to="/restaurants"
                    className="confirmation-primary"
                >
                    Browse Restaurants
                </Link>

                <Link
                    to="/cart"
                    className="confirmation-secondary"
                >
                    View Cart
                </Link>

                <Link
                    to="/orders"
                    className="confirmation-secondary"
                >
                    View Order History
                </Link>
            </div>
        </main>
    );
}

export default OrderConfirmation;
