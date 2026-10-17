
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRestaurants } from "../../api/restaurants";
import "./OwnerDashboard.css";

const DEMO_OWNER_ID = "development_owner";

function OwnerDashboard() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

getRestaurants()
  .then((data) => {

    if (active) {
      const ownedRestaurants = data.filter(
        (restaurant) =>
          restaurant.owner_id === DEMO_OWNER_ID
      );

      setRestaurants(ownedRestaurants);
    }
  })
      .catch((err) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="owner-page">
      <header className="owner-header">
        <div>
          <Link to="/">← Back to Login</Link>
          <h1>My Restaurants</h1>
          <p>Manage your restaurants and their menus.</p>
        </div>

        <Link
          to="/owner/restaurants/new"
          className="owner-primary-button"
        >
          + Create Restaurant
        </Link>
      </header>

      {loading && <p>Loading restaurants...</p>}

      {error && <p role="alert">{error}</p>}

      {!loading && !error && restaurants.length === 0 && (
        <section className="owner-empty">
          <h2>No restaurants yet</h2>
          <p>Create your first restaurant to get started.</p>
        </section>
      )}

      <div className="owner-grid">
        {restaurants.map((restaurant) => (
          <article className="owner-card" key={restaurant.id}>
            <h2>{restaurant.name}</h2>
            <p>{restaurant.cuisine}</p>
            <p>{restaurant.address}</p>
            <p>Rating: {restaurant.rating}</p>

            <Link to={`/owner/restaurants/${restaurant.id}`}>
              Manage Restaurant →
            </Link>
          </article>
        ))}
      </div>
    </main>
  );
}

export default OwnerDashboard;
