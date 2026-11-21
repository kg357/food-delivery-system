
import { useNavigate } from "react-router-dom";
import { clearSession } from "../../auth/session";

function LogoutButton() {
    const navigate = useNavigate();

    function handleLogout() {
        // Remove the authentication token.
        clearSession();

        // Remove any leftover demonstration session.
        sessionStorage.removeItem("demoRole");

        // Return to login.
        navigate("/", { replace: true });
    }

    return (
        <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
        >
            Sign Out
        </button>
    );
}

export default LogoutButton;
