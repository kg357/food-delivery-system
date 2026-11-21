
import {
    beforeEach,
    describe,
    expect,
    test,
    vi,
} from "vitest";

import {
    render,
    screen,
    waitFor,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import {
    MemoryRouter,
    Route,
    Routes,
} from "react-router-dom";

import Login from "../pages/Login/Login";
import Register from "../pages/Register/Register";
import LogoutButton from "../components/LogoutButton/LogoutButton";

import {
    loginCustomer,
    registerCustomer,
} from "../api/auth";

import {
    saveSession,
    clearSession,
} from "../auth/session";

// Mock API requests.
vi.mock("../api/auth", () => ({
    loginCustomer: vi.fn(),
    registerCustomer: vi.fn(),
}));

// Mock session functions.
vi.mock("../auth/session", () => ({
    saveSession: vi.fn(),
    clearSession: vi.fn(),
}));

// Render the authentication pages with destination routes.
function renderAuth(initialPath = "/") {
    return render(
        <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
                <Route path="/" element={<Login />} />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/restaurants"
                    element={<h1>Customer Homepage</h1>}
                />

                <Route
                    path="/owner/restaurants"
                    element={<h1>Owner Dashboard</h1>}
                />

                <Route
                    path="/admin"
                    element={<h1>Admin Dashboard</h1>}
                />

                <Route
                    path="/cart"
                    element={
                        <>
                            <h1>Shopping Cart</h1>
                            <LogoutButton />
                        </>
                    }
                />
            </Routes>
        </MemoryRouter>
    );
}

async function fillLogin(user) {
    await user.type(
        screen.getByLabelText("Email"),
        "customer@example.com"
    );

    await user.type(
        screen.getByLabelText("Password"),
        "password123"
    );
}

async function fillRegistration(user, address = "") {
    await user.type(
        screen.getByLabelText("Full Name"),
        "Test Customer"
    );

    await user.type(
        screen.getByLabelText("Email"),
        "customer@example.com"
    );

    if (address) {
        await user.type(
            screen.getByLabelText(
                "Delivery Address (Optional)"
            ),
            address
        );
    }

    await user.type(
        screen.getByLabelText("Password", {
            exact: true,
        }),
        "password123"
    );

    await user.type(
        screen.getByLabelText("Confirm Password"),
        "password123"
    );
}

describe("Authentication", () => {
    beforeEach(() => {
        vi.resetAllMocks();
        sessionStorage.clear();
    });

    test.each([
        ["customer", "Customer Homepage"],
        ["restaurant_owner", "Owner Dashboard"],
        ["admin", "Admin Dashboard"],
    ])(
        "redirects a %s to the correct homepage",
        async (role, destination) => {
            const user = userEvent.setup();

            loginCustomer.mockResolvedValue({
                access_token: "test-token",
                token_type: "bearer",
            });

            saveSession.mockReturnValue({
                id: "user-1",
                role,
            });

            renderAuth();

            await fillLogin(user);

            await user.click(
                screen.getByRole("button", {
                    name: "Sign In",
                })
            );

            expect(
                await screen.findByRole("heading", {
                    name: destination,
                })
            ).toBeInTheDocument();

            expect(loginCustomer).toHaveBeenCalledWith(
                "customer@example.com",
                "password123"
            );

            expect(saveSession).toHaveBeenCalledWith(
                "test-token"
            );
        }
    );

    test("displays invalid login credentials", async () => {
        const user = userEvent.setup();

        loginCustomer.mockRejectedValue(
            new Error("Invalid email or password.")
        );

        renderAuth();

        await fillLogin(user);

        await user.click(
            screen.getByRole("button", {
                name: "Sign In",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Invalid email or password."
        );

        expect(saveSession).not.toHaveBeenCalled();

        expect(
            screen.getByRole("heading", {
                name: "Welcome back",
            })
        ).toBeInTheDocument();
    });

    test("registers a customer and redirects to login", async () => {
        const user = userEvent.setup();

        registerCustomer.mockResolvedValue({
            id: "customer-1",
            name: "Test Customer",
            email: "customer@example.com",
        });

        renderAuth("/register");

        await fillRegistration(
            user,
            "123 Main Street"
        );

        await user.click(
            screen.getByRole("button", {
                name: "Create Account",
            })
        );

        await waitFor(() => {
            expect(registerCustomer).toHaveBeenCalledWith({
                name: "Test Customer",
                email: "customer@example.com",
                password: "password123",
                address: "123 Main Street",
            });
        });

        expect(
            await screen.findByText(
                "Account created successfully. Please sign in."
            )
        ).toBeInTheDocument();

        // Registration does not automatically sign in.
        expect(saveSession).not.toHaveBeenCalled();
    });

    test("allows registration without an address", async () => {
        const user = userEvent.setup();

        registerCustomer.mockResolvedValue({
            id: "customer-1",
        });

        renderAuth("/register");

        await fillRegistration(user);

        await user.click(
            screen.getByRole("button", {
                name: "Create Account",
            })
        );

        await waitFor(() => {
            expect(registerCustomer).toHaveBeenCalledWith({
                name: "Test Customer",
                email: "customer@example.com",
                password: "password123",
            });
        });
    });

    test("rejects mismatched passwords", async () => {
        const user = userEvent.setup();

        renderAuth("/register");

        await fillRegistration(user);

        await user.clear(
            screen.getByLabelText("Confirm Password")
        );

        await user.type(
            screen.getByLabelText("Confirm Password"),
            "different123"
        );

        await user.click(
            screen.getByRole("button", {
                name: "Create Account",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent("Passwords do not match.");

        expect(registerCustomer).not.toHaveBeenCalled();
    });

    test("displays registration errors", async () => {
        const user = userEvent.setup();

        registerCustomer.mockRejectedValue(
            new Error(
                "An account with this email already exists."
            )
        );

        renderAuth("/register");

        await fillRegistration(user);

        await user.click(
            screen.getByRole("button", {
                name: "Create Account",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "An account with this email already exists."
        );
    });

    test("signs out and returns to login", async () => {
        const user = userEvent.setup();

        sessionStorage.setItem(
            "demoRole",
            "customer"
        );

        renderAuth("/cart");

        expect(
            screen.getByText("Shopping Cart")
        ).toBeInTheDocument();

        await user.click(
            screen.getByRole("button", {
                name: "Sign Out",
            })
        );

        expect(clearSession).toHaveBeenCalledOnce();

        expect(
            await screen.findByRole("heading", {
                name: "Welcome back",
            })
        ).toBeInTheDocument();

        expect(
            sessionStorage.getItem("demoRole")
        ).toBeNull();
    });
});
