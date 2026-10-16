import "./RestaurantCard.css"
import { Link } from "react-router-dom";

function RestaurantCard({ restaurant }) {
    return (
        <Link
            to={`/restaurants/${restaurant.id}`}
            className='restaurant_details'
        >
            <div className="restaurant-card"
            >
                <div className="restaurant-banner">
                    <div className="cuisine-badge">
                        {restaurant.cuisine}
                    </div>
                    <h2>{restaurant.name}</h2>
                </div>

                <div className="restaurant-info">
                    <div className="restaurant-info-header">
                        <h3 className="restaurant-name">
                            {restaurant.name}
                        </h3>

                        <div className="rating">
                            <span>★</span>
                            {restaurant.rating}
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}

export default RestaurantCard