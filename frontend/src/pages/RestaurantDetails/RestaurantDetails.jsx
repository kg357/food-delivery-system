import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getRestaurantById } from "../../api/restaurants";
import Loading from "../../components/Loading/Loading";
import MenuList from "../../components/MenuList/MenuList";
import "./RestaurantDetails.css";

function RestaurantDetails() {
    const { id } = useParams();

    const [restaurant, setRestaurant] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        setLoading(true);
        setError("");

        getRestaurantById(id).then((data) => {
            if (active) {
                setRestaurant(data);
                setLoading(false);
            }
        }).catch((error) => {
            if (active) {
                setError(error.message || "Unable to load restaurant details");
                setLoading(false);
            }
        });

        return () => {
            active = false;
        }

    }, [id]);

    if (loading) {
        return <Loading />
    }

    if (error) {
        return (
            <p className="error">
                {error}
            </p>
        )
    }

    if (!restaurant) {
        return <p className="empty">Restaurant not found.</p>
    }

    return (
        <main className="restaurant-details">
            <Link to="/restaurants"
                className="back-link"
            ><span aria-hidden="true">←</span>All restaurants</Link>

            <div className="hero-banner">
                <div className="hero-overlay">
                    <div className="hero-cuisine">
                        {restaurant.cuisine}
                    </div>

                    <h1>{restaurant.name}</h1>
                </div>
            </div>

            <div className="restaurant-meta">
                <div className="meta-item">
                    ⭐ {restaurant.rating}
                </div>
                <div className="meta-item">
                    🍜 {restaurant.cuisine}
                </div>

                <div className="meta-item">
                    📍 {restaurant.address}
                </div>
            </div>
            <section className="menu-section">
                <h2 className="menu-title">Menu</h2>

                <MenuList restaurantId={id} />
            </section>
        </main>
    )
}

export default RestaurantDetails;