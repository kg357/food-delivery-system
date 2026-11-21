
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
    getCustomerProfile,
    updateCustomerProfile,
    deactivateCustomerAccount,
} from "../../api/customers";

import { clearSession } from "../../auth/session";

import "./CustomerProfile.css";

function CustomerProfile() {
    const navigate = useNavigate();

    const [profile, setProfile] = useState(null);
    const [name, setName] = useState("");
    const [address, setAddress] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [deactivating, setDeactivating] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Retrieve the customer's information.
    useEffect(() => {
        let active = true;

        async function loadProfile() {
            try {
                const customer = await getCustomerProfile();

                if (!active) return;

                setProfile(customer);
                setName(customer.name);
                setAddress(customer.address || "");
            } catch (err) {
                if (active) {
                    setError(err.message);
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        loadProfile();

        return () => {
            active = false;
        };
    }, []);

    // Save updates to the backend.
    async function handleSave(event) {
        event.preventDefault();

        setError("");
        setSuccess("");

        const trimmedName = name.trim();
        const trimmedAddress = address.trim();

        if (!trimmedName) {
            setError("Name cannot be empty.");
            return;
        }

        // The current backend does not support
        // clearing an existing address.
        if (profile.address && !trimmedAddress) {
            setError(
                "An existing delivery address cannot be cleared."
            );
            return;
        }

        const updates = {
            name: trimmedName,
        };

        if (trimmedAddress) {
            updates.address = trimmedAddress;
        }

        setSaving(true);

        try {
            const updated = await updateCustomerProfile(
                updates
            );

            setProfile(updated);
            setName(updated.name);
            setAddress(updated.address || "");

            setSuccess("Profile updated successfully.");
        } catch (err) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    }

    // Deactivate the customer account.
    async function handleDeactivate() {
        const confirmed = window.confirm(
            "Are you sure you want to deactivate your account? " +
            "You will no longer be able to sign in."
        );

        if (!confirmed) return;

        setError("");
        setSuccess("");
        setDeactivating(true);

        try {
            await deactivateCustomerAccount();

            clearSession();

            navigate("/", {
                replace: true,
                state: { accountDeactivated: true },
            });
        } catch (err) {
            setError(err.message);
            setDeactivating(false);
        }
    }

    if (loading) {
        return (
            <main className="customer-profile">
                <p>Loading profile...</p>
            </main>
        );
    }

    if (!profile) {
        return (
            <main className="customer-profile">
                <p role="alert">
                    {error || "Unable to load profile."}
                </p>

                <Link to="/restaurants">
                    Back to Restaurants
                </Link>
            </main>
        );
    }

    return (
        <main className="customer-profile">
            <Link
                to="/restaurants"
                className="profile-back"
            >
                ← Back to Restaurants
            </Link>

            <h1>My Account</h1>
            <p className="profile-subtitle">
                Manage your personal information
                and delivery address.
            </p>

            {error && (
                <p role="alert" className="profile-error">
                    {error}
                </p>
            )}

            {success && (
                <p role="status" className="profile-success">
                    {success}
                </p>
            )}

            <section className="profile-card">
                <h2>Personal Information</h2>

                <form onSubmit={handleSave}>
                    <label htmlFor="profile-name">
                        Full Name
                    </label>

                    <input
                        id="profile-name"
                        type="text"
                        value={name}
                        onChange={(event) =>
                            setName(event.target.value)
                        }
                        maxLength={100}
                        required
                    />

                    <label htmlFor="profile-email">
                        Email Address
                    </label>

                    <input
                        id="profile-email"
                        type="email"
                        value={profile.email}
                        disabled
                    />

                    <p className="profile-note">
                        Email addresses cannot currently
                        be changed.
                    </p>

                    <h2>Delivery Address</h2>

                    <label htmlFor="profile-address">
                        Address
                    </label>

                    <input
                        id="profile-address"
                        type="text"
                        value={address}
                        onChange={(event) =>
                            setAddress(event.target.value)
                        }
                        placeholder="Enter your delivery address"
                        maxLength={200}
                    />

                    <button
                        type="submit"
                        className="profile-save"
                        disabled={saving || deactivating}
                    >
                        {saving
                            ? "Saving..."
                            : "Save Changes"}
                    </button>
                </form>
            </section>

            <section className="profile-card danger-section">
                <h2>Account Deactivation</h2>

                <p>
                    Deactivating your account will prevent
                    you from signing in or placing orders.
                </p>

                <button
                    type="button"
                    className="deactivate-button"
                    onClick={handleDeactivate}
                    disabled={saving || deactivating}
                >
                    {deactivating
                        ? "Deactivating..."
                        : "Deactivate Account"}
                </button>
            </section>
        </main>
    );
}

export default CustomerProfile;
