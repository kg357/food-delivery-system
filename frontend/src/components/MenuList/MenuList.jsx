import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMenu } from "../../api/menu";
import Loading from "../Loading/Loading";
import "./MenuList.css";

function MenuList({ restaurantId }) {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        setLoading(true);
        setError("");

        getMenu(restaurantId)
            .then((data) => {
                if (active) {
                    setItems(data);
                    setLoading(false);
                }
            })
            .catch((error) => {
                if (active) {
                    setError(error.message || "Failed to load menu");
                    setLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, [restaurantId]);

    if (loading) {
        return <Loading />;
    }

    if (error) {
        return <p className="error">{error}</p>;
    }

    if (items.length === 0) {
        return <p className="empty">This restaurant has no menu items yet.</p>;
    }

    return (
        <div className="menu-list">
            {items.map((item) => (
                <Link
                    key={item.id}
                    to={`/restaurants/${restaurantId}/menu/${item.id}`}
                    className="menu-list-link"
                >
                    <div className="menu-list-card">
                        <div className="menu-list-header">
                            <h3>{item.name}</h3>
                            <span className="menu-list-price">
                                ${item.price.toFixed(2)}
                            </span>
                        </div>

                        <p className="menu-list-description">
                            {item.description}
                        </p>

                        {!item.available && (
                            <span className="unavailable-badge">Unavailable</span>
                        )}
                    </div>
                </Link>
            ))}
        </div>
    );
}

export default MenuList;
