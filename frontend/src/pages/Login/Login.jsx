import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

import { loginCustomer } from "../../api/auth";
import { saveSession } from "../../auth/session";

import "./Login.css";

function Login() {
    const navigate = useNavigate();
    const location = useLocation();


    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleLogin(event) {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            // Authenticate through the backend.
            const response = await loginCustomer(
                email,
                password
            );

            // Store the token and retrieve user claims.
            const user = saveSession(response.access_token);

            // Remove any old demonstration role.
            sessionStorage.removeItem("demoRole");

            // Navigate based on the authenticated role.
            switch (user.role) {
                case "customer":
                    navigate("/restaurants", { replace: true });
                    break;

                case "restaurant_owner":
                    navigate("/owner/restaurants", {
                        replace: true
                    });
                    break;

                case "admin":
                    navigate("/admin", { replace: true });
                    break;

                default:
                    throw new Error("Unsupported account role.");
            }
        } catch (err) {
            setError(
                err.message || "Unable to sign in."
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

                <h1>Welcome back</h1>

                <p>Sign in to your account.</p>

                {location.state?.registrationSuccess && (
                    <p className="auth-success" role="status">
                        Account created successfully. Please sign in.
                    </p>
                )}

                {location.state?.accountDeactivated && (
                    <p className="auth-success" role="status">
                        Your account has been deactivated.
                    </p>
                )}

                <form
                    onSubmit={handleLogin}
                    className="login-form"
                >
                    <label htmlFor="email">
                        Email
                    </label>

                    <input
                        id="email"
                        type="email"
                        autoComplete="email"
                        value={email}
                        onChange={(event) =>
                            setEmail(event.target.value)
                        }
                        placeholder="Enter your email"
                        required
                    />

                    <label htmlFor="password">
                        Password
                    </label>

                    <input
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(event) =>
                            setPassword(event.target.value)
                        }
                        placeholder="Enter your password"
                        required
                    />

                    <button
                        type="submit"
                        className="login-submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Signing in..."
                            : "Sign In"}
                    </button>

                    {error && (
                        <p role="alert" className="error">
                            {error}
                        </p>
                    )}
                </form>

                <p className="auth-switch">
                    Don't have an account?{" "}
                    <Link to="/register">Create an Account</Link>
                </p>

            </section>
        </main>
    );
}

export default Login;
