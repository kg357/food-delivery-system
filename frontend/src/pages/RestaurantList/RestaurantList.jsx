
import { useEffect, useState } from "react"
import { Link } from "react-router-dom";
import RestaurantCard from "../../components/RestaurantCard/RestaurantCard"
import Loading from "../../components/Loading/Loading"
import { getRestaurants } from "../../api/restaurants"
import "./RestaurantList.css"

function RestaurantList() {
    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Search and filter state
    const [search, setSearch] = useState("");
    const [selectedCuisine, setSelectedCuisine] = useState("all");
    const [minimumRating, setMinimumRating] = useState("0");

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

    // Generate cuisine choices from the restaurant data
    const cuisines = [...new Set(
        restaurants.map((restaurant) => restaurant.cuisine)
    )]
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b));

    // Filter restaurants using all three conditions
    const filteredRestaurants = restaurants.filter((restaurant) => {
        const matchesSearch = restaurant.name
            .toLowerCase()
            .includes(search.trim().toLowerCase());

        const matchesCuisine =
            selectedCuisine === "all" ||
            restaurant.cuisine === selectedCuisine;

        const matchesRating =
            restaurant.rating >= Number(minimumRating);

        return matchesSearch && matchesCuisine && matchesRating;
    });

    function clearFilters() {
        setSearch("");
        setSelectedCuisine("all");
        setMinimumRating("0");
    }

    if (loading) {
        return <Loading />
    }

    if (error) {
        return <p className="error">{error}</p>
    }

    return (
        <div className="restaurant-list-container">
            <Link
                to="/"
                className="back-to-login"
                onClick={() => sessionStorage.removeItem("demoRole")}
            >
                ← Back to Login
            </Link>

            <h1>Restaurants</h1>

            {/* Search and filter controls */}
            <section
                className="restaurant-filters"
                aria-label="Restaurant search and filters"
            >
                <div className="filter-search">
                    <label htmlFor="restaurant-search">
                        Search Restaurants
                    </label>
                    <input
                        id="restaurant-search"
                        type="search"
                        placeholder="Search by restaurant name..."
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />
                </div>

                <div className="filter-row">
                    <div className="filter-field">
                        <label htmlFor="cuisine-filter">
                            Cuisine
                        </label>
                        <select
                            id="cuisine-filter"
                            value={selectedCuisine}
                            onChange={(event) =>
                                setSelectedCuisine(event.target.value)
                            }
                        >
                            <option value="all">
                                All Cuisines
                            </option>

                            {cuisines.map((cuisine) => (
                                <option
                                    key={cuisine}
                                    value={cuisine}
                                >
                                    {cuisine}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-field">
                        <label htmlFor="rating-filter">
                            Minimum Rating
                        </label>
                        <select
                            id="rating-filter"
                            value={minimumRating}
                            onChange={(event) =>
                                setMinimumRating(event.target.value)
                            }
                        >
                            <option value="0">Any Rating</option>
                            <option value="3">3+ Stars</option>
                            <option value="4">4+ Stars</option>
                            <option value="4.5">4.5+ Stars</option>
                        </select>
                    </div>
                </div>

                <div className="filter-actions">
                    <button
                        type="button"
                        className="clear-filters-button"
                        onClick={clearFilters}
                    >
                        Clear Filters
                    </button>
                </div>
            </section>

            {/* Results count */}
            <p
                className="restaurant-results-count"
                role="status"
            >
                {filteredRestaurants.length}{" "}
                {filteredRestaurants.length === 1
                    ? "restaurant"
                    : "restaurants"}{" "}
                found
            </p>

            {/* Restaurant cards or empty state */}
            {filteredRestaurants.length === 0 ? (
                <div className="restaurant-no-results">
                    <h2>No restaurants found</h2>
                    <p>
                        Try a different search or adjust your filters.
                    </p>
                    <button
                        type="button"
                        onClick={clearFilters}
                    >
                        Clear Filters
                    </button>
                </div>
            ) : (
                <div className="restaurant-grid">
                    {filteredRestaurants.map((restaurant) => (
                        <RestaurantCard
                            key={restaurant.id}
                            restaurant={restaurant}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export default RestaurantList;
