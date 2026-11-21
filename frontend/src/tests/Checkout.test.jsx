
import {
    beforeEach,
    describe,
    expect,
    test,
    vi,
} from "vitest";

import {
    act,
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

import Cart from "../pages/Cart/Cart";
import OrderConfirmation from "../pages/OrderConfirmation/OrderConfirmation";

import {
    getCart,
    updateCartItem,
    removeCartItem,
    clearCart,
} from "../api/cart";

import { checkout, getOrder } from "../api/orders";

// Mock API calls without contacting FastAPI.
vi.mock("../api/cart", () => ({
    getCart: vi.fn(),
    updateCartItem: vi.fn(),
    removeCartItem: vi.fn(),
    clearCart: vi.fn(),
}));

vi.mock("../api/orders", () => ({
    checkout: vi.fn(),
    getOrder: vi.fn(),
    getOrderHistory: vi.fn(),
}));

const populatedCart = {
    id: "cart-1",
    customer_id: "customer1",
    restaurant_id: 7,
    items: [
        {
            item_id: "item-1",
            name: "Margherita Pizza",
            unit_price: "16.99",
            quantity: 2,
            total_price: "33.98",
        },
    ],
    subtotal: "33.98",
    total: "33.98",
};

const emptyCart = {
    ...populatedCart,
    restaurant_id: null,
    items: [],
    subtotal: "0.00",
    total: "0.00",
};

const createdOrder = {
    id: "order-123",
    customer_id: "customer1",
    restaurant_id: 7,
    items: [
        {
            item_id: "item-1",
            name: "Margherita Pizza",
            description: "Tomato and mozzarella",
            quantity: 2,
            unit_price: 16.99,
            total_price: 33.98,
        },
    ],
    subtotal: 33.98,
    total: 33.98,
};

// Render the actual cart and confirmation pages,
// with routing between them.
function renderCheckout() {
    return render(
        <MemoryRouter initialEntries={["/cart"]}>
            <Routes>
                <Route
                    path="/cart"
                    element={<Cart />}
                />

                <Route
                    path="/orders/:orderId"
                    element={<OrderConfirmation />}
                />
            </Routes>
        </MemoryRouter>
    );
}

describe("Checkout", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        getCart.mockResolvedValue(populatedCart);
        getOrder.mockResolvedValue(createdOrder);
    });

    test("successfully creates an order and navigates to confirmation", async () => {
        const user = userEvent.setup();

        checkout.mockResolvedValue(createdOrder);

        renderCheckout();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Place Order",
            })
        );

        expect(
            await screen.findByRole("heading", {
                name: "Order Placed Successfully!",
            })
        ).toBeInTheDocument();

        expect(checkout).toHaveBeenCalledOnce();

        expect(getOrder).toHaveBeenCalledWith(
            "order-123"
        );

        expect(
            screen.getByText("Order ID: order-123")
        ).toBeInTheDocument();

        expect(
            screen.getAllByText("$33.98")
        ).toHaveLength(3);
    });

    test("disables checkout and cart changes while placing an order", async () => {
        const user = userEvent.setup();

        let resolveCheckout;

        checkout.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveCheckout = resolve;
                })
        );

        renderCheckout();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Place Order",
            })
        );

        const placingButton = screen.getByRole(
            "button",
            { name: "Placing Order..." }
        );

        expect(placingButton).toBeDisabled();

        expect(
            screen.getByRole("button", {
                name: "Clear Cart",
            })
        ).toBeDisabled();

        expect(
            screen.getByRole("button", {
                name: "Increase Margherita Pizza quantity",
            })
        ).toBeDisabled();

        // A disabled button cannot submit another order.
        await user.click(placingButton);

        expect(checkout).toHaveBeenCalledOnce();

        // Finish the pending request.
        await act(async () => {
            resolveCheckout(createdOrder);
        });

        expect(
            await screen.findByRole("heading", {
                name: "Order Placed Successfully!",
            })
        ).toBeInTheDocument();
    });

    test("displays an error when checkout fails", async () => {
        const user = userEvent.setup();

        checkout.mockRejectedValue(
            new Error("Margherita Pizza is unavailable")
        );

        renderCheckout();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Place Order",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Margherita Pizza is unavailable"
        );

        // The existing cart remains visible.
        expect(
            screen.getByText("Margherita Pizza")
        ).toBeInTheDocument();

        // No automatic retry occurs.
        expect(checkout).toHaveBeenCalledOnce();

        expect(
            screen.getByRole("button", {
                name: "Place Order",
            })
        ).toBeEnabled();
    });

    test("does not assume checkout failed when the response has no order ID", async () => {
        const user = userEvent.setup();

        checkout.mockResolvedValue({});

        renderCheckout();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Place Order",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Checkout returned no order ID."
        );

        expect(
            screen.getByRole("alert")
        ).toHaveTextContent(
            "Check your order history before trying again."
        );

        expect(checkout).toHaveBeenCalledOnce();

        expect(getOrder).not.toHaveBeenCalled();
    });

    test("does not allow checkout with an empty cart", async () => {
        getCart.mockResolvedValue(emptyCart);

        renderCheckout();

        expect(
            await screen.findByText("Your cart is empty")
        ).toBeInTheDocument();

        expect(
            screen.queryByRole("button", {
                name: "Place Order",
            })
        ).not.toBeInTheDocument();

        expect(checkout).not.toHaveBeenCalled();
    });

    test("does not allow checkout during a cart update", async () => {
        const user = userEvent.setup();

        let resolveUpdate;

        updateCartItem.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveUpdate = resolve;
                })
        );

        renderCheckout();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Increase Margherita Pizza quantity",
            })
        );

        expect(
            screen.getByRole("button", {
                name: "Place Order",
            })
        ).toBeDisabled();

        expect(checkout).not.toHaveBeenCalled();

        // Complete the cart update.
        await act(async () => {
            resolveUpdate(populatedCart);
        });

        await waitFor(() => {
            expect(
                screen.getByRole("button", {
                    name: "Place Order",
                })
            ).toBeEnabled();
        });
    });
});
