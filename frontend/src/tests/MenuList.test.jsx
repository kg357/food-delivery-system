import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, test, vi } from "vitest";
import MenuList from "../components/MenuList/MenuList";
import { getMenu } from "../api/menu";

vi.mock("../api/menu");

const menuItems = [
    {
        id: "item-1",
        restaurant_id: 1,
        name: "Tonkotsu Ramen",
        description: "Pork broth with noodles",
        price: 14.5,
        available: true,
    },
    {
        id: "item-2",
        restaurant_id: 1,
        name: "Matcha Ice Cream",
        description: "Green tea ice cream",
        price: 5,
        available: false,
    },
];

function renderMenuList(restaurantId = "1") {
    return render(
        <MemoryRouter>
            <MenuList restaurantId={restaurantId} />
        </MemoryRouter>
    );
}

describe("MenuList", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    test("shows a loading message while the menu is loading", () => {
        getMenu.mockReturnValue(new Promise(() => {}));

        renderMenuList();

        expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    test("renders every menu item with name, price and description", async () => {
        getMenu.mockResolvedValue(menuItems);

        renderMenuList();

        expect(await screen.findByText("Tonkotsu Ramen")).toBeInTheDocument();
        expect(screen.getByText("Matcha Ice Cream")).toBeInTheDocument();
        expect(screen.getByText("$14.50")).toBeInTheDocument();
        expect(screen.getByText("$5.00")).toBeInTheDocument();
        expect(screen.getByText("Pork broth with noodles")).toBeInTheDocument();
    });

    test("marks only unavailable items with an Unavailable badge", async () => {
        getMenu.mockResolvedValue(menuItems);

        renderMenuList();

        await screen.findByText("Tonkotsu Ramen");

        expect(screen.getAllByText("Unavailable")).toHaveLength(1);
    });

    test("each item links to its details page", async () => {
        getMenu.mockResolvedValue(menuItems);

        renderMenuList();

        await screen.findByText("Tonkotsu Ramen");

        const links = screen.getAllByRole("link");
        expect(links[0]).toHaveAttribute("href", "/restaurants/1/menu/item-1");
        expect(links[1]).toHaveAttribute("href", "/restaurants/1/menu/item-2");
    });

    test("requests the menu for the given restaurant id", async () => {
        getMenu.mockResolvedValue(menuItems);

        renderMenuList("3");

        await screen.findByText("Tonkotsu Ramen");

        expect(getMenu).toHaveBeenCalledWith("3");
    });

    test("shows an empty message when the restaurant has no items", async () => {
        getMenu.mockResolvedValue([]);

        renderMenuList();

        expect(
            await screen.findByText("This restaurant has no menu items yet.")
        ).toBeInTheDocument();
    });

    test("shows an error message when the menu fails to load", async () => {
        getMenu.mockRejectedValue(new Error("Failed to load menu"));

        renderMenuList();

        expect(await screen.findByText("Failed to load menu")).toBeInTheDocument();
        expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
    });
});
