import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, test, vi } from "vitest";
import MenuItemDetails from "../pages/MenuItemDetails/MenuItemDetails";
import { getMenuItem } from "../api/menu";

vi.mock("../api/menu");

const availableItem = {
    id: "item-1",
    restaurant_id: 1,
    name: "Tonkotsu Ramen",
    description: "Pork broth with noodles",
    price: 14.5,
    available: true,
};

function renderDetails() {
    return render(
        <MemoryRouter initialEntries={["/restaurants/1/menu/item-1"]}>
            <Routes>
                <Route
                    path="/restaurants/:id/menu/:itemId"
                    element={<MenuItemDetails />}
                />
            </Routes>
        </MemoryRouter>
    );
}

describe("MenuItemDetails", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    test("shows a loading message while the item is loading", () => {
        getMenuItem.mockReturnValue(new Promise(() => {}));

        renderDetails();

        expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    test("requests the item using the ids from the URL", async () => {
        getMenuItem.mockResolvedValue(availableItem);

        renderDetails();

        await screen.findByText("Tonkotsu Ramen");

        expect(getMenuItem).toHaveBeenCalledWith("1", "item-1");
    });

    test("shows the name, description, price and availability", async () => {
        getMenuItem.mockResolvedValue(availableItem);

        renderDetails();

        expect(await screen.findByText("Tonkotsu Ramen")).toBeInTheDocument();
        expect(screen.getByText("Pork broth with noodles")).toBeInTheDocument();
        expect(screen.getByText("$14.50")).toBeInTheDocument();
        expect(screen.getByText("Available")).toBeInTheDocument();
    });

    test("shows that an unavailable item is currently unavailable", async () => {
        getMenuItem.mockResolvedValue({ ...availableItem, available: false });

        renderDetails();

        expect(
            await screen.findByText("Currently unavailable")
        ).toBeInTheDocument();
    });

    test("shows an error when the item is not found", async () => {
        getMenuItem.mockRejectedValue(new Error("Menu item not found"));

        renderDetails();

        expect(await screen.findByText("Menu item not found")).toBeInTheDocument();
        expect(screen.queryByText("Tonkotsu Ramen")).not.toBeInTheDocument();
    });

    test("has a link back to the restaurant page", async () => {
        getMenuItem.mockResolvedValue(availableItem);

        renderDetails();

        const backLink = await screen.findByRole("link", {
            name: /back to restaurant/i,
        });
        expect(backLink).toHaveAttribute("href", "/restaurants/1");
    });
});
