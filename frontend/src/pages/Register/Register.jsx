
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { homePathForRole, login, registerCustomer } from "../../api/auth";
import "../Login/Login.css";

function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [address, setAddress] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const data = {
      name: name.trim(),
      email: email.trim(),
      password,
    };

    // The delivery address is optional. Leave it out when empty.
    if (address.trim()) {
      data.address = address.trim();
    }

    try {
      setSaving(true);
      await registerCustomer(data);

      // Sign in right away so the new customer does not have to type
      // the same details again.
      const user = await login(data.email, password);
      navigate(homePathForRole(user.role));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">Food Delivery System</div>

        <h1>Create your account</h1>
        <p>Order food under your own name.</p>

        <form onSubmit={handleSubmit} className="login-form">
          <label htmlFor="register-name">Name</label>
          <input
            id="register-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={100}
            autoComplete="name"
            required
          />

          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />

          <label htmlFor="register-password">
            Password (at least 8 characters)
          </label>
          <input
            id="register-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            maxLength={72}
            autoComplete="new-password"
            required
          />

          <label htmlFor="register-address">
            Delivery address (optional)
          </label>
          <input
            id="register-address"
            value={address}
            onChange={(event) => setAddress(event.target.value)}
            maxLength={200}
            autoComplete="street-address"
          />

          <button
            type="submit"
            className="login-submit"
            disabled={saving}
          >
            {saving ? "Creating account..." : "Create Account"}
          </button>

          {error && <p role="alert">{error}</p>}
        </form>

        <p className="login-register">
          Already have an account? <Link to="/">Sign in</Link>
        </p>
      </section>
    </main>
  );
}

export default Register;
