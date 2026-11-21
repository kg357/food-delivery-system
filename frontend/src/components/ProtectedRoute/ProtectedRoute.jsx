
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { getSession } from "../../auth/session";

function ProtectedRoute({ allowedRoles }) {
    const location = useLocation();
    const session = getSession();

    // Redirect unauthenticated users to login.
    if (!session) {
        return (
            <Navigate
                to="/"
                replace
                state={{ from: location.pathname }}
            />
        );
    }

    // Redirect users who have the wrong role.
    if (!allowedRoles.includes(session.role)) {
        const destinations = {
            customer: "/restaurants",
            restaurant_owner: "/owner/restaurants",
            admin: "/admin",
        };

        return (
            <Navigate
                to={destinations[session.role] || "/"}
                replace
            />
        );
    }

    // Render the protected child route.
    return <Outlet />;
}

export default ProtectedRoute;
