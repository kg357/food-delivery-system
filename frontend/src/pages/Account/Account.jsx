
import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import {
  deactivateCustomer,
  getCurrentUser,
  getCustomer,
  homePathForRole,
  logout,
  updateCustomer,
} from "../../api/auth";
import "./Account.css";

function Account() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const [customer, setCustomer] = useState(null);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmingDeactivate, setConfirmingDeactivate] = useState(false);

  useEffect(() => {
    if (!user) return;

    let active = true;

    getCustomer(user.id)
      .then((data) => {
        if (!active) return;
        setCustomer(data);
        setName(data.name);
        setAddress(data.address ?? "");
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
    // The signed-in user's id does not change while this page is open.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Nobody is signed in, so there is no account to show.
  if (!user) {
    return <Navigate to="/" replace />;
  }

  async function handleSave(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const changes = { name: name.trim() };

    // The backend does not accept an empty address, so only send one
    // when there is something to save.
    if (address.trim()) {
      changes.address = address.trim();
    }

    try {
      setSaving(true);
      const updated = await updateCustomer(user.id, changes);
      setCustomer(updated);
      setSuccess("Your account was updated.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDeactivate() {
    setError("");

    try {
      await deactivateCustomer(user.id);
      logout();
      navigate("/");
    } catch (err) {
      setError(err.message);
      setConfirmingDeactivate(false);
    }
  }

  if (loading) {
    return <p className="account-status">Loading your account...</p>;
  }

  return (
    <main className="account-page">
      <Link to={homePathForRole(user.role)} className="account-back">
        ← Back
      </Link>

      <section className="account-card">
        <h1>My Account</h1>

        {customer && (
          <p className="account-email">
            Signed in as <strong>{customer.email}</strong>
          </p>
        )}

        {error && <p role="alert" className="account-error">{error}</p>}
        {success && <p role="status" className="account-success">{success}</p>}

        {customer && (
          <form onSubmit={handleSave} className="account-form">
            <label htmlFor="account-name">Name</label>
            <input
              id="account-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              maxLength={100}
              required
            />

            <label htmlFor="account-address">Delivery address</label>
            <input
              id="account-address"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
              maxLength={200}
            />

            <button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </form>
        )}

        {customer && (
          <div className="account-danger">
            <h2>Deactivate account</h2>
            <p>
              You will be signed out and will not be able to sign in or
              order again. Your order history is kept.
            </p>

            {confirmingDeactivate ? (
              <div className="account-confirm">
                <p>Are you sure you want to deactivate your account?</p>
                <button type="button" onClick={handleDeactivate}>
                  Yes, deactivate my account
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmingDeactivate(false)}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setConfirmingDeactivate(true)}
              >
                Deactivate my account
              </button>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

export default Account;
