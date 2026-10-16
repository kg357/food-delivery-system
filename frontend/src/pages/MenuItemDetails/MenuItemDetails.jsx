import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMenuItem } from "../../api/menu";
import Loading from "../../components/Loading/Loading";
import "./MenuItemDetails.css";

function MenuItemDetails() {
    const { id, itemId } = useParams();

    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        setLoading(true);
        setError("");

        getMenuItem(id, itemId)
            .then((data) => {
                if (active) {
                    setItem(data);
                    setLoading(false);
                }
            })
            .catch((error) => {
                if (active) {
                    setError(error.message || "Failed to load menu item");
                    setLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, [id, itemId]);

    if (loading) {
        return <Loading />;
    }

    return (
        <main className="menu-item-details">
            <Link to={`/restaurants/${id}`} className="menu-item-back-link">
                <span aria-hidden="true">←</span> Back to restaurant
            </Link>

            {error && <p className="error">{error}</p>}

            {item && (
                <div className="menu-item-card">
                    <h1>{item.name}</h1>

                    <p className="menu-item-description">{item.description}</p>

                    <p className="menu-item-price">${item.price.toFixed(2)}</p>

                    <p
                        className={
                            item.available
                                ? "menu-item-status available"
                                : "menu-item-status unavailable"
                        }
                    >
                        {item.available ? "Available" : "Currently unavailable"}
                    </p>
                </div>
            )}
        </main>
    );
}

export default MenuItemDetails;
