import { useEffect, useState } from "react"

import RestaurantCard from "../../components/RestaurantCard/RestaurantCard"
import Loading from "../../components/Loading/Loading"
import { getRestaurants } from "../../api/restaurants"
import "./RestaurantList.css"

function RestaurantList() {
    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        getRestaurants().then((data) => {
            setRestaurants(data);
            setLoading(false);
        })
            .catch((error) => {
                setError(error.message);
                setLoading(false);
            })
    }, []);

    if (loading) {
        return <Loading />
    }

    if (error) {
        return <p className="error">{error}</p>
    }

    if (restaurants.length == 0) {
        return <p className="empty">No restaurants found.</p>;
    }

    return (
        <div className="restaurant-list-container">
            <h1>Restaurants</h1>

            <div className="restaurant-grid">
                {restaurants.map((restaurant) => (
                    <RestaurantCard key={restaurant.id} restaurant={restaurant} />
                ))}
            </div>
        </div>
    )
}

export default RestaurantList;