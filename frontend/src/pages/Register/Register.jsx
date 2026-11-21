
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { registerCustomer } from "../../api/auth";

import "../Login/Login.css";

function Register() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        name: "",
        email: "",
        address: "",
        password: "",
        confirmPassword: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    function handleChange(event) {
        const { name, value } = event.target;

        setForm((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");

        // Check that both password fields match.
        if (form.password !== form.confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);

        try {
            // Only send fields accepted by the backend.
            const customerData = {
                name: form.name.trim(),
                email: form.email.trim(),
                password: form.password,
            };

            // Address is optional in the backend schema.
            if (form.address.trim()) {
                customerData.address = form.address.trim();
            }

            await registerCustomer(customerData);

            // Registration does not return an access token.
            // Redirect the new customer to the login page.
            navigate("/", {
                replace: true,
                state: { registrationSuccess: true },
            });
        } catch (err) {
            setError(
                err.message || "Registration failed."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="login-page">
            <section className="login-card">
                <div className="login-brand">
                    Food Delivery System
                </div>

                <h1>Create an account</h1>
                <p>Register to start ordering food.</p>

                <form
                    className="login-form"
                    onSubmit={handleSubmit}
                >
                    <label htmlFor="name">
                        Full Name
                    </label>
                    <input
                        id="name"
                        name="name"
                        type="text"
                        autoComplete="name"
                        value={form.name}
                        onChange={handleChange}
                        placeholder="Enter your full name"
                        required
                    />

                    <label htmlFor="email">
                        Email
                    </label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        autoComplete="email"
                        value={form.email}
                        onChange={handleChange}
                        placeholder="Enter your email"
                        required
                    />

                    <label htmlFor="address">
                        Delivery Address (Optional)
                    </label>
                    <input
                        id="address"
                        name="address"
                        type="text"
                        autoComplete="street-address"
                        value={form.address}
                        onChange={handleChange}
                        placeholder="Enter your delivery address"
                    />

                    <label htmlFor="password">
                        Password
                    </label>
                    <input
                        id="password"
                        name="password"
                        type="password"
                        autoComplete="new-password"
                        value={form.password}
                        onChange={handleChange}
                        minLength={8}
                        required
                    />

                    <label htmlFor="confirmPassword">
                        Confirm Password
                    </label>
                    <input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        autoComplete="new-password"
                        value={form.confirmPassword}
                        onChange={handleChange}
                        minLength={8}
                        required
                    />

                    <button
                        className="login-submit"
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Creating account..."
                            : "Create Account"}
                    </button>

                    {error && (
                        <p className="error" role="alert">
                            {error}
                        </p>
                    )}
                </form>

                <p className="auth-switch">
                    Already have an account?{" "}
                    <Link to="/">Sign In</Link>
                </p>
            </section>
        </main>
    );
}

export default Register;
