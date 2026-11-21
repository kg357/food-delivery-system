
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
    within,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import Cart from "../pages/Cart/Cart";

import {
    getCart,
    updateCartItem,
    removeCartItem,
    clearCart,
} from "../api/cart";

// Mock the backend API functions.
vi.mock("../api/cart", () => ({
    getCart: vi.fn(),
    updateCartItem: vi.fn(),
    removeCartItem: vi.fn(),
    clearCart: vi.fn(),
}));

vi.mock("../api/orders", () => ({
    checkout: vi.fn(),
}));

// Example cart containing one menu item.
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

// Example empty cart.
const emptyCart = {
    ...populatedCart,
    restaurant_id: null,
    items: [],
    subtotal: "0.00",
    total: "0.00",
};

function renderCart() {
    return render(
        <MemoryRouter>
            <Cart />
        </MemoryRouter>
    );
}

describe("Shopping Cart", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        // Default: the backend returns a populated cart.
        getCart.mockResolvedValue(populatedCart);
    });

    test("displays a loading message", () => {
        getCart.mockReturnValue(
            new Promise(() => {})
        );

        renderCart();

        expect(
            screen.getByText("Loading your cart...")
        ).toBeInTheDocument();
    });

    test("displays an empty cart", async () => {
        getCart.mockResolvedValue(emptyCart);

        renderCart();

        expect(
            await screen.findByText("Your cart is empty")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("link", {
                name: "Browse Restaurants",
            })
        ).toHaveAttribute("href", "/restaurants");
    });

    test("displays items and backend totals", async () => {
        renderCart();

        expect(
            await screen.findByText("Margherita Pizza")
        ).toBeInTheDocument();

        expect(
            screen.getByText("$16.99", {
                exact: false,
            })
        ).toBeInTheDocument();

        // The backend-provided total appears in
        // the item row, subtotal, and total.
        expect(
            screen.getAllByText("$33.98")
        ).toHaveLength(3);

        expect(getCart).toHaveBeenCalledOnce();
    });

    test("increases an item's quantity", async () => {
        const user = userEvent.setup();

        const updatedCart = {
            ...populatedCart,
            items: [
                {
                    ...populatedCart.items[0],
                    quantity: 3,
                    total_price: "50.97",
                },
            ],
            subtotal: "50.97",
            total: "50.97",
        };

        updateCartItem.mockResolvedValue(updatedCart);

        renderCart();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Increase Margherita Pizza quantity",
            })
        );

        await waitFor(() => {
            expect(updateCartItem).toHaveBeenCalledWith(
                "item-1",
                3
            );
        });

        await waitFor(() => {
            expect(
                within(
                    screen.getByRole("article")
                ).getByText("$50.97")
            ).toBeInTheDocument();
        });
    });

    test("decreases an item's quantity", async () => {
        const user = userEvent.setup();

        const updatedCart = {
            ...populatedCart,
            items: [
                {
                    ...populatedCart.items[0],
                    quantity: 1,
                    total_price: "16.99",
                },
            ],
            subtotal: "16.99",
            total: "16.99",
        };

        updateCartItem.mockResolvedValue(updatedCart);

        renderCart();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Decrease Margherita Pizza quantity",
            })
        );

        await waitFor(() => {
            expect(updateCartItem).toHaveBeenCalledWith(
                "item-1",
                1
            );
        });
    });

    test("removes an item from the cart", async () => {
        const user = userEvent.setup();

        removeCartItem.mockResolvedValue(emptyCart);

        renderCart();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Remove",
            })
        );

        await waitFor(() => {
            expect(removeCartItem).toHaveBeenCalledWith(
                "item-1"
            );
        });

        expect(
            await screen.findByText("Your cart is empty")
        ).toBeInTheDocument();
    });

    test("clears the entire cart", async () => {
        const user = userEvent.setup();

        clearCart.mockResolvedValue(emptyCart);

        renderCart();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Clear Cart",
            })
        );

        await waitFor(() => {
            expect(clearCart).toHaveBeenCalledOnce();
        });

        expect(
            await screen.findByText("Your cart is empty")
        ).toBeInTheDocument();
    });

    test("displays errors when cart retrieval fails", async () => {
        getCart.mockRejectedValue(
            new Error("Failed to load cart")
        );

        renderCart();

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent("Failed to load cart");
    });

    test("preserves cart contents when an update fails", async () => {
        const user = userEvent.setup();

        updateCartItem.mockRejectedValue(
            new Error("Unable to update quantity")
        );

        renderCart();

        await screen.findByText("Margherita Pizza");

        await user.click(
            screen.getByRole("button", {
                name: "Increase Margherita Pizza quantity",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Unable to update quantity"
        );

        // The previous cart should remain visible.
        expect(
            screen.getByText("Margherita Pizza")
        ).toBeInTheDocument();

        expect(
            within(
                screen.getByRole("article")
            ).getByText("$33.98")
        ).toBeInTheDocument();
    });
});
