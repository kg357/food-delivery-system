
import { beforeEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";
import { getSession } from "../auth/session";

// Mock session retrieval so each test can simulate a
// different authenticated user without calling the backend.
vi.mock("../auth/session", () => ({
    getSession: vi.fn(),
}));

// Render a simplified version of the application's
// role-protected routing structure.
function renderProtectedRoutes(initialPath) {
    return render(
        <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
                {/* Public login page */}
                <Route
                    path="/"
                    element={<h1>Login Page</h1>}
                />

                {/* Customer-only routes */}
                <Route
                    element={
                        <ProtectedRoute
                            allowedRoles={["customer"]}
                        />
                    }
                >
                    <Route
                        path="/restaurants"
                        element={<h1>Customer Restaurants</h1>}
                    />

                    <Route
                        path="/cart"
                        element={<h1>Customer Cart</h1>}
                    />
                </Route>

                {/* Restaurant owner routes */}
                <Route
                    element={
                        <ProtectedRoute
                            allowedRoles={["restaurant_owner"]}
                        />
                    }
                >
                    <Route
                        path="/owner/restaurants"
                        element={<h1>Owner Dashboard</h1>}
                    />
                </Route>

                {/* Administrator routes */}
                <Route
                    element={
                        <ProtectedRoute
                            allowedRoles={["admin"]}
                        />
                    }
                >
                    <Route
                        path="/admin"
                        element={<h1>Admin Dashboard</h1>}
                    />
                </Route>
            </Routes>
        </MemoryRouter>
    );
}

function mockSession(role, id = "test-user") {
    vi.mocked(getSession).mockReturnValue({
        id,
        role,
        token: "test-token",
    });
}

describe("ProtectedRoute", () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    test("redirects unauthenticated customers to login", () => {
        vi.mocked(getSession).mockReturnValue(null);

        renderProtectedRoutes("/cart");

        expect(
            screen.getByRole("heading", {
                name: "Login Page",
            })
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Customer Cart")
        ).not.toBeInTheDocument();
    });

    test("redirects unauthenticated owners to login", () => {
        vi.mocked(getSession).mockReturnValue(null);

        renderProtectedRoutes("/owner/restaurants");

        expect(
            screen.getByText("Login Page")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Owner Dashboard")
        ).not.toBeInTheDocument();
    });

    test("allows customers to access customer routes", () => {
        mockSession("customer");

        renderProtectedRoutes("/cart");

        expect(
            screen.getByText("Customer Cart")
        ).toBeInTheDocument();
    });

    test("allows restaurant owners to access owner routes", () => {
        mockSession("restaurant_owner", "owner1");

        renderProtectedRoutes("/owner/restaurants");

        expect(
            screen.getByText("Owner Dashboard")
        ).toBeInTheDocument();
    });

    test("allows administrators to access admin routes", () => {
        mockSession("admin", "admin1");

        renderProtectedRoutes("/admin");

        expect(
            screen.getByText("Admin Dashboard")
        ).toBeInTheDocument();
    });

    test("redirects customers away from owner routes", () => {
        mockSession("customer");

        renderProtectedRoutes("/owner/restaurants");

        // Customers should be redirected to their own homepage.
        expect(
            screen.getByText("Customer Restaurants")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Owner Dashboard")
        ).not.toBeInTheDocument();
    });

    test("redirects owners away from customer routes", () => {
        mockSession("restaurant_owner", "owner1");

        renderProtectedRoutes("/cart");

        expect(
            screen.getByText("Owner Dashboard")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Customer Cart")
        ).not.toBeInTheDocument();
    });

    test("redirects administrators away from customer routes", () => {
        mockSession("admin", "admin1");

        renderProtectedRoutes("/cart");

        expect(
            screen.getByText("Admin Dashboard")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Customer Cart")
        ).not.toBeInTheDocument();
    });

    test("redirects customers away from admin routes", () => {
        mockSession("customer");

        renderProtectedRoutes("/admin");

        expect(
            screen.getByText("Customer Restaurants")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Admin Dashboard")
        ).not.toBeInTheDocument();
    });
});
