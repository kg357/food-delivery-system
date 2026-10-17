
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  function enterDemo(role) {
    sessionStorage.setItem("demoRole", role);

    if (role === "customer") {
      navigate("/restaurants");
    } else if (role === "owner") {
      navigate("/owner/restaurants");
    } else if (role === "administrator") {
      navigate("/admin");
    }
  }

  function handleLogin(event) {
    event.preventDefault();
    setMessage(
      "Username/password authentication is not implemented yet. Please select a demo account."
    );
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">Food Delivery System</div>

        <h1>Welcome back</h1>
        <p>Sign in to your account or explore a demo.</p>

        <form onSubmit={handleLogin} className="login-form">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Enter username"
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

          <button type="submit" className="login-submit">
            Sign In
          </button>

          {message && <p role="status">{message}</p>}
        </form>

        <div className="login-divider"> 
        </div>

        <div className="demo-options">
          <button onClick={() => enterDemo("owner")}>
            <strong>Example Owner</strong>
            <span>Manage restaurants and menus</span>
          </button>

          <button onClick={() => enterDemo("customer")}>
            <strong>Example Customer</strong>
            <span>Browse restaurants and food</span>
          </button>

          <button onClick={() => enterDemo("administrator")}>
            <strong>Example Administrator</strong>
            <span>Explore the administration area</span>
          </button>
        </div>

        <p className="demo-note">
          Demonstration mode — no password required.
        </p>
      </section>
    </main>
  );
}

export default Login;
