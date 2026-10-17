
import { useState } from "react";
import "./RestaurantForm.css";

function RestaurantForm({
  initialValues = {},
  onSubmit,
  submitLabel = "Save Restaurant",
}) {
  const [name, setName] = useState(initialValues.name ?? "");
  const [cuisine, setCuisine] = useState(initialValues.cuisine ?? "");
  const [address, setAddress] = useState(initialValues.address ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const data = {
      name: name.trim(),
      cuisine: cuisine.trim(),
      address: address.trim(),
    };

    if (!data.name || !data.cuisine || !data.address) {
      setError("All fields are required.");
      return;
    }

    try {
      setSaving(true);
      await onSubmit(data);
    } catch (err) {
      setError(err.message || "Unable to save restaurant.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="restaurant-form" onSubmit={handleSubmit}>
      <label htmlFor="restaurant-name">Restaurant Name</label>
      <input
        id="restaurant-name"
        value={name}
        onChange={(event) => setName(event.target.value)}
        maxLength={100}
        required
        placeholder="e.g. The Golden Fork"
      />

      <label htmlFor="restaurant-cuisine">Cuisine</label>
      <input
        id="restaurant-cuisine"
        value={cuisine}
        onChange={(event) => setCuisine(event.target.value)}
        maxLength={100}
        required
        placeholder="e.g. Italian"
      />

      <label htmlFor="restaurant-address">Address</label>
      <input
        id="restaurant-address"
        value={address}
        onChange={(event) => setAddress(event.target.value)}
        maxLength={200}
        required
        placeholder="e.g. 123 Main Street"
      />

      {error && <p className="form-error" role="alert">{error}</p>}

      <button type="submit" disabled={saving}>
        {saving ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}

export default RestaurantForm;
