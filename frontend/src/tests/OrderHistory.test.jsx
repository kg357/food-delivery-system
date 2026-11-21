
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

import {
    MemoryRouter,
    Route,
    Routes,
} from "react-router-dom";

import OrderHistory from "../pages/OrderHistory/OrderHistory";
import OrderConfirmation from "../pages/OrderConfirmation/OrderConfirmation";

import {
    getOrderHistory,
    getOrder,
} from "../api/orders";

// Mock the order API so no backend is required.
vi.mock("../api/orders", () => ({
    getOrderHistory: vi.fn(),
    getOrder: vi.fn(),
    checkout: vi.fn(),
}));

const orders = [
    {
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
            {
                item_id: "item-2",
                name: "Garlic Bread",
                description: "Toasted garlic bread",
                quantity: 1,
                unit_price: 5.00,
                total_price: 5.00,
            },
        ],
        subtotal: 38.98,
        total: 38.98,
    },
    {
        id: "order-456",
        customer_id: "customer1",
        restaurant_id: 3,
        items: [
            {
                item_id: "item-3",
                name: "Chicken Curry",
                description: "Spiced chicken curry",
                quantity: 1,
                unit_price: 18.50,
                total_price: 18.50,
            },
        ],
        subtotal: 18.50,
        total: 18.50,
    },
];

function renderOrderHistory() {
    return render(
        <MemoryRouter initialEntries={["/orders"]}>
            <Routes>
                <Route
                    path="/orders"
                    element={<OrderHistory />}
                />

                <Route
                    path="/orders/:orderId"
                    element={<OrderConfirmation />}
                />

                <Route
                    path="/restaurants"
                    element={<h1>Restaurant Browsing</h1>}
                />
            </Routes>
        </MemoryRouter>
    );
}

describe("Order History", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        getOrderHistory.mockResolvedValue(orders);
        getOrder.mockResolvedValue(orders[0]);
    });

    test("displays a loading message", () => {
        getOrderHistory.mockReturnValue(
            new Promise(() => {})
        );

        renderOrderHistory();

        expect(
            screen.getByText("Loading order history...")
        ).toBeInTheDocument();
    });

    test("displays an empty state when no orders exist", async () => {
        getOrderHistory.mockResolvedValue([]);

        renderOrderHistory();

        expect(
            await screen.findByText("No orders yet")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("link", {
                name: "Browse Restaurants",
            })
        ).toHaveAttribute("href", "/restaurants");
    });

    test("displays all previous orders", async () => {
        renderOrderHistory();

        expect(
            await screen.findByText("order-123")
        ).toBeInTheDocument();

        expect(
            screen.getByText("order-456")
        ).toBeInTheDocument();

        expect(
            screen.getAllByRole("article")
        ).toHaveLength(2);

        expect(getOrderHistory).toHaveBeenCalledOnce();
    });

    test("displays order items, quantities, and totals", async () => {
        renderOrderHistory();

        await screen.findByText("order-123");

        const cards = screen.getAllByRole("article");

        expect(
            within(cards[0]).getByText(
                "2 × Margherita Pizza"
            )
        ).toBeInTheDocument();

        expect(
            within(cards[0]).getByText(
                "1 × Garlic Bread"
            )
        ).toBeInTheDocument();

        expect(
            within(cards[0]).getByText("$38.98")
        ).toBeInTheDocument();

        expect(
            within(cards[1]).getByText(
                "1 × Chicken Curry"
            )
        ).toBeInTheDocument();

        expect(
            within(cards[1]).getByText("$18.50")
        ).toBeInTheDocument();
    });

    test("opens the correct order details", async () => {
        const user = userEvent.setup();

        renderOrderHistory();

        await screen.findByText("order-123");

        const firstCard = screen.getAllByRole("article")[0];

        await user.click(
            within(firstCard).getByRole("link", {
                name: "View Order Details",
            })
        );

        await waitFor(() => {
            expect(getOrder).toHaveBeenCalledWith(
                "order-123"
            );
        });

        expect(
            await screen.findByRole("heading", {
                name: "Order Details",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByText("Order ID: order-123")
        ).toBeInTheDocument();

        // An old order should not appear
        // as a newly placed order.
        expect(
            screen.queryByText(
                "Order Placed Successfully!"
            )
        ).not.toBeInTheDocument();
    });

    test("displays an error when order history fails to load", async () => {
        getOrderHistory.mockRejectedValue(
            new Error("Unable to retrieve orders")
        );

        renderOrderHistory();

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent(
            "Unable to retrieve orders"
        );

        expect(
            screen.queryByText("No orders yet")
        ).not.toBeInTheDocument();
    });

    test("handles an individual order retrieval failure", async () => {
        const user = userEvent.setup();

        getOrder.mockRejectedValue(
            new Error("Order not found")
        );

        renderOrderHistory();

        await screen.findByText("order-123");

        const firstCard = screen.getAllByRole("article")[0];

        await user.click(
            within(firstCard).getByRole("link", {
                name: "View Order Details",
            })
        );

        expect(
            await screen.findByRole("alert")
        ).toHaveTextContent("Order not found");
    });
});
