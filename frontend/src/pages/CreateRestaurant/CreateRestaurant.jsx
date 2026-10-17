
import { Link, useNavigate } from "react-router-dom";
import RestaurantForm from "../../components/RestaurantForm/RestaurantForm";
import { createRestaurant } from "../../api/restaurants";
import "./CreateRestaurant.css";

function CreateRestaurant() {
  const navigate = useNavigate();

  async function handleCreate(data) {
    const restaurant = await createRestaurant(data);
    navigate(`/owner/restaurants/${restaurant.id}`);
  }

  return (
    <main className="create-restaurant-page">
      <Link to="/owner/restaurants" className="create-back-link">
        ← Back to My Restaurants
      </Link>

      <section className="create-restaurant-card">
        <h1>Create a Restaurant</h1>
        <p>
          Enter your restaurant's information to add it to
          the food delivery system.
        </p>

        <RestaurantForm
          onSubmit={handleCreate}
          submitLabel="Create Restaurant"
        />
      </section>
    </main>
  );
}

export default CreateRestaurant;
