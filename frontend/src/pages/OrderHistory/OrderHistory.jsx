
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getOrderHistory } from "../../api/orders";

import "./OrderHistory.css";

function formatPrice(amount) {
    return `$${Number(amount).toFixed(2)}`;
}

function OrderHistory() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        async function loadOrders() {
            try {
                const data = await getOrderHistory();

                if (active) {
                    setOrders(data);
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

        loadOrders();

        return () => {
            active = false;
        };
    }, []);

    if (loading) {
        return (
            <main className="order-history-page">
                <p>Loading order history...</p>
            </main>
        );
    }

    return (
        <main className="order-history-page">
            <Link
                to="/restaurants"
                className="order-history-back"
            >
                ← Back to Restaurants
            </Link>

            <h1>My Orders</h1>

            <p className="order-history-subtitle">
                View your previous orders and their details.
            </p>

            {error && (
                <p className="order-history-error" role="alert">
                    {error}
                </p>
            )}

            {!error && orders.length === 0 && (
                <section className="order-history-empty">
                    <h2>No orders yet</h2>

                    <p>
                        Once you place an order, it will
                        appear here.
                    </p>

                    <Link
                        to="/restaurants"
                        className="order-history-primary"
                    >
                        Browse Restaurants
                    </Link>
                </section>
            )}

            {!error && orders.length > 0 && (
                <div className="order-history-list">
                    {orders.map((order) => {
                        const itemCount = order.items.reduce(
                            (count, item) =>
                                count + item.quantity,
                            0
                        );

                        return (
                            <article
                                key={order.id}
                                className="order-history-card"
                            >
                                <div className="order-history-header">
                                    <div>
                                        <h2>Order</h2>

                                        <p className="order-history-id">
                                            {order.id}
                                        </p>
                                    </div>

                                    <strong className="order-history-total">
                                        {formatPrice(order.total)}
                                    </strong>
                                </div>

                                <div className="order-history-information">
                                    <p>
                                        <strong>Restaurant ID:</strong>{" "}
                                        {order.restaurant_id}
                                    </p>

                                    <p>
                                        <strong>Items:</strong>{" "}
                                        {itemCount}
                                    </p>
                                </div>

                                <ul className="order-history-items">
                                    {order.items.map((item) => (
                                        <li key={item.item_id}>
                                            {item.quantity} × {item.name}
                                        </li>
                                    ))}
                                </ul>

                                <Link
                                    to={`/orders/${encodeURIComponent(order.id)}`}
                                    className="order-history-details"
                                >
                                    View Order Details
                                </Link>
                            </article>
                        );
                    })}
                </div>
            )}
        </main>
    );
}

export default OrderHistory;
