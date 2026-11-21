
import {
    afterEach,
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
    useLocation,
} from "react-router-dom";

import CustomerProfile from "../pages/CustomerProfile/CustomerProfile";

import {
    getCustomerProfile,
    updateCustomerProfile,
    deactivateCustomerAccount,
} from "../api/customers";

import { clearSession } from "../auth/session";

// Mock backend customer API functions.
vi.mock("../api/customers", () => ({
    getCustomerProfile: vi.fn(),
    updateCustomerProfile: vi.fn(),
    deactivateCustomerAccount: vi.fn(),
}));

// Mock session clearing.
vi.mock("../auth/session", () => ({
    clearSession: vi.fn(),
}));

const customer = {
    id: "customer1",
    name: "Test Customer",
    email: "customer@example.com",
    address: "123 Main Street",
    role: "customer",
    active: true,
};

// Simulate the login destination after deactivation.
function LoginDestination() {
    const location = useLocation();

    return (
        <h1>
            {location.state?.accountDeactivated
                ? "Account deactivated"
                : "Login"}
        </h1>
    );
}

function renderProfile() {
    return render(
        <MemoryRouter initialEntries={["/account"]}>
            <Routes>
                <Route
                    path="/account"
                    element={<CustomerProfile />}
                />

                <Route
                    path="/"
                    element={<LoginDestination />}
                />
            </Routes>
        </MemoryRouter>
    );
}

describe("Customer Profile", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        getCustomerProfile.mockResolvedValue(customer);

        // Prevent native confirmation dialogs during tests.
        vi.stubGlobal("confirm", vi.fn());
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    test("displays a loading message", () => {
        getCustomerProfile.mockReturnValue(
            new Promise(() => {})
        );

        renderProfile();

        expect(
            screen.getByText("Loading profile...")
        ).toBeInTheDocument();
    });

    test("displays customer information", async () => {
        renderProfile();

        expect(
            await screen.findByRole("heading", {
                name: "My Account",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByLabelText("Full Name")
        ).toHaveValue("Test Customer");

        expect(
            screen.getByLabelText("Address")
        ).toHaveValue("123 Main Street");

        expect(
            screen.getByLabelText("Email Address")
        ).toHaveValue("customer@example.com");

        // Email cannot be edited through this interface.
        expect(
            screen.getByLabelText("Email Address")
        ).toBeDisabled();

        expect(getCustomerProfile).toHaveBeenCalledOnce();
    });

    test("displays an error when profile retrieval fails", async () => {
        getCustomerProfile.mockRejectedValue(
            new Error("Unable to load customer profile")
        );

        renderProfile();

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Unable to load customer profile"
        );

        expect(
            screen.queryByRole("button", {
                name: "Save Changes",
            })
        ).not.toBeInTheDocument();
    });

    test("updates the customer's name and address", async () => {
        const user = userEvent.setup();

        const updatedCustomer = {
            ...customer,
            name: "Updated Customer",
            address: "456 New Street",
        };

        updateCustomerProfile.mockResolvedValue(
            updatedCustomer
        );

        renderProfile();

        const nameInput =
            await screen.findByLabelText("Full Name");

        const addressInput =
            screen.getByLabelText("Address");

        await user.clear(nameInput);
        await user.type(nameInput, " Updated Customer ");

        await user.clear(addressInput);
        await user.type(addressInput, " 456 New Street ");

        await user.click(
            screen.getByRole("button", {
                name: "Save Changes",
            })
        );

        await waitFor(() => {
            expect(updateCustomerProfile)
                .toHaveBeenCalledWith({
                    name: "Updated Customer",
                    address: "456 New Street",
                });
        });

        expect(
            await screen.findByRole("status")
        ).toHaveTextContent(
            "Profile updated successfully."
        );

        expect(nameInput).toHaveValue(
            "Updated Customer"
        );

        expect(addressInput).toHaveValue(
            "456 New Street"
        );
    });

    test("rejects a name containing only whitespace", async () => {
        const user = userEvent.setup();

        renderProfile();

        const nameInput =
            await screen.findByLabelText("Full Name");

        await user.clear(nameInput);
        await user.type(nameInput, "   ");

        await user.click(
            screen.getByRole("button", {
                name: "Save Changes",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Name cannot be empty."
        );

        expect(updateCustomerProfile)
            .not.toHaveBeenCalled();
    });

    test("prevents clearing an existing address", async () => {
        const user = userEvent.setup();

        renderProfile();

        const addressInput =
            await screen.findByLabelText("Address");

        await user.clear(addressInput);

        await user.click(
            screen.getByRole("button", {
                name: "Save Changes",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "An existing delivery address cannot be cleared."
        );

        expect(updateCustomerProfile)
            .not.toHaveBeenCalled();
    });

    test("displays an error when updating fails", async () => {
        const user = userEvent.setup();

        updateCustomerProfile.mockRejectedValue(
            new Error("Failed to update profile")
        );

        renderProfile();

        const nameInput =
            await screen.findByLabelText("Full Name");

        await user.clear(nameInput);
        await user.type(nameInput, "New Name");

        await user.click(
            screen.getByRole("button", {
                name: "Save Changes",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Failed to update profile"
        );

        expect(
            screen.queryByText(
                "Profile updated successfully."
            )
        ).not.toBeInTheDocument();
    });

    test("does not deactivate when confirmation is cancelled", async () => {
        const user = userEvent.setup();

        window.confirm.mockReturnValue(false);

        renderProfile();

        await screen.findByText("My Account");

        await user.click(
            screen.getByRole("button", {
                name: "Deactivate Account",
            })
        );

        expect(window.confirm).toHaveBeenCalledOnce();

        expect(deactivateCustomerAccount)
            .not.toHaveBeenCalled();

        expect(clearSession).not.toHaveBeenCalled();
    });

    test("deactivates the account and signs out", async () => {
        const user = userEvent.setup();

        window.confirm.mockReturnValue(true);

        deactivateCustomerAccount.mockResolvedValue({
            ...customer,
            active: false,
        });

        renderProfile();

        await screen.findByText("My Account");

        await user.click(
            screen.getByRole("button", {
                name: "Deactivate Account",
            })
        );

        await waitFor(() => {
            expect(deactivateCustomerAccount)
                .toHaveBeenCalledOnce();
        });

        expect(clearSession).toHaveBeenCalledOnce();

        expect(
            await screen.findByRole("heading", {
                name: "Account deactivated",
            })
        ).toBeInTheDocument();
    });

    test("preserves the session if deactivation fails", async () => {
        const user = userEvent.setup();

        window.confirm.mockReturnValue(true);

        deactivateCustomerAccount.mockRejectedValue(
            new Error("Failed to deactivate account")
        );

        renderProfile();

        await screen.findByText("My Account");

        await user.click(
            screen.getByRole("button", {
                name: "Deactivate Account",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Failed to deactivate account"
        );

        expect(clearSession).not.toHaveBeenCalled();

        expect(
            screen.getByRole("heading", {
                name: "My Account",
            })
        ).toBeInTheDocument();
    });
});
