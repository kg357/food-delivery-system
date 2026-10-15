import "./RestaurantCard.css"

function RestaurantCard({ restaurant }) {
    return (
        <div className="restaurant-card"
        >
            <h2 className="restaurant-name">{restaurant.name}</h2>

            <p className="restaurant-cuisine">
                Cuisine: {restaurant.cuisine}
            </p>

            <p className="restaurant-rating">
                Rating: {restaurant.rating}
            </p>

            <p>
                Address: {restaurant.address}
            </p>
        </div>
    );
}

export default RestaurantCard