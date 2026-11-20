
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { homePathForRole, login } from "../../api/auth";
import "./Login.css";

// Demonstration accounts. These exist in backend/data/customers.json and
// are signed in through the same login request as any other account.
const DEMO_ACCOUNTS = {
  owner: { email: "owner@example.com", password: "OwnerDemo123" },
  customer: { email: "customer@example.com", password: "CustomerDemo123" },
  administrator: { email: "admin@example.com", password: "AdminDemo123" },
};

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [signingIn, setSigningIn] = useState(false);

  async function signIn(emailAddress, passwordText) {
    setMessage("");

    try {
      setSigningIn(true);
      const user = await login(emailAddress, passwordText);
      navigate(homePathForRole(user.role));
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSigningIn(false);
    }
  }

  function handleLogin(event) {
    event.preventDefault();
    signIn(email.trim(), password);
  }

  function enterDemo(name) {
    const account = DEMO_ACCOUNTS[name];
    signIn(account.email, account.password);
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">Food Delivery System</div>

        <h1>Welcome back</h1>
        <p>Sign in to your account or explore a demo.</p>

        <form onSubmit={handleLogin} className="login-form">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Enter email"
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter password"
            required
          />

          <button
            type="submit"
            className="login-submit"
            disabled={signingIn}
          >
            {signingIn ? "Signing in..." : "Sign In"}
          </button>

          {message && <p role="alert">{message}</p>}
        </form>

        <p className="login-register">
          New here? <Link to="/register">Create an account</Link>
        </p>

        <div className="login-divider"> 
        </div>

        <div className="demo-options">
          <button onClick={() => enterDemo("owner")} disabled={signingIn}>
            <strong>Example Owner</strong>
            <span>Manage restaurants and menus</span>
          </button>

          <button onClick={() => enterDemo("customer")} disabled={signingIn}>
            <strong>Example Customer</strong>
            <span>Browse restaurants and food</span>
          </button>

          <button
            onClick={() => enterDemo("administrator")}
            disabled={signingIn}
          >
            <strong>Example Administrator</strong>
            <span>Explore the administration area</span>
          </button>
        </div>

        <p className="demo-note">
          Demonstration accounts use the demo passwords from the README.
        </p>
      </section>
    </main>
  );
}

export default Login;
