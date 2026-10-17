
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getRestaurantById,
  updateRestaurant,
} from "../../api/restaurants";
import { getMenu } from "../../api/menu";
import RestaurantForm from "../../components/RestaurantForm/RestaurantForm";
import "./OwnerRestaurantDetails.css";

const DEMO_OWNER_ID = "development_owner";

function OwnerRestaurantDetails() {
  const { id } = useParams();

  const [restaurant, setRestaurant] = useState(null);
  const [menu, setMenu] = useState([]);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [menuError, setMenuError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function loadRestaurant() {
      try {
        setLoading(true);
        setError("");
        setMenuError("");

        const data = await getRestaurantById(id);

        if (data.owner_id !== DEMO_OWNER_ID) {
          throw new Error(
            "This restaurant does not belong to the demo owner."
          );
        }

        if (!active) return;
        setRestaurant(data);

        try {
          const menuData = await getMenu(id);
          if (active) setMenu(menuData);
        } catch (err) {
          if (active) setMenuError(err.message);
        }
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadRestaurant();

    return () => {
      active = false;
    };
  }, [id]);

  async function handleUpdate(data) {
    const updated = await updateRestaurant(id, data);
    setRestaurant(updated);
    setEditing(false);
    setSuccess("Restaurant updated successfully.");
  }

  if (loading) {
    return <main className="owner-detail">Loading restaurant...</main>;
  }

  if (error) {
    return (
      <main className="owner-detail">
        <p role="alert">{error}</p>
        <Link to="/owner/restaurants">← My Restaurants</Link>
      </main>
    );
  }

  if (!restaurant) return null;

  return (
    <main className="owner-detail">
      <Link to="/owner/restaurants">← My Restaurants</Link>

      <header className="owner-detail-header">
        <div>
          <h1>{restaurant.name}</h1>
          <p>Restaurant Management</p>
        </div>

        <button
          type="button"
          onClick={() => {
            setEditing(!editing);
            setSuccess("");
          }}
        >
          {editing ? "Cancel Editing" : "Edit Restaurant"}
        </button>
      </header>

    <section className="owner-detail-section">
        <h2>Restaurant Information</h2>

        {success && <p role="status">{success}</p>}

        {editing ? (
        <RestaurantForm
        key={restaurant.id}
        initialValues={restaurant}
        onSubmit={handleUpdate}
        submitLabel="Save Changes"
        />
        ) : (
        <div className="owner-info">
        <p><strong>Name:</strong> {restaurant.name}</p>
        <p><strong>Cuisine:</strong> {restaurant.cuisine}</p>
        <p><strong>Address:</strong> {restaurant.address}</p>
        <p><strong>Rating:</strong> {restaurant.rating}</p>
        </div>
        )}
    </section>


    <section className="owner-detail-section">
    <h2>Menu Management</h2>

    <p>
        Add new dishes, update prices, and manage availability
        from your restaurant's menu editor.
    </p>

    <Link
        to={`/owner/restaurants/${id}/menu/edit`}
        className="owner-menu-manage-button"
    >
        Edit Menu Items →
    </Link>
    </section>

    </main>
  );
}

export default OwnerRestaurantDetails;
