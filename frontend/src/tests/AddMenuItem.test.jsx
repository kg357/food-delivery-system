import { it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import AddMenuItem from "../pages/AddMenuItem/AddMenuItem";

it("adds a menu item", async () => {
    global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
            id: "123",
            name: "Burger",
            price: 10
        })
    });

    render(<AddMenuItem />);

    fireEvent.change(screen.getByLabelText("Name"), {
        target: { value: "Burger" }
    });

    fireEvent.change(screen.getByLabelText("Price"), {
        target: { value: "10" }
    });

    fireEvent.click(screen.getByRole("button", { name: "Add Menu Item" }));

    expect(await screen.findByText("Menu item added successfully!"))
        .toBeTruthy();

    expect(screen.getByText("Burger")).toBeTruthy();

    expect(global.fetch).toHaveBeenCalledWith(
    "http://localhost:8000/restaurants/1/menu",
    expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
            name: "Burger",
            description: "",
            price: 10,
            available: true
        })
    })
);
});



it("shows an error for invalid input", async () => {
    const mockFetch = vi.fn();
    global.fetch = mockFetch;

    render(<AddMenuItem />);

    fireEvent.click(screen.getByRole("button", {
        name: "Add Menu Item"
    }));

    expect(screen.getByRole("alert").textContent)
        .toBe("Enter a valid name and price.");

    expect(mockFetch).not.toHaveBeenCalled();
});


it("shows an error when the API fails", async () => {
    global.fetch = vi.fn().mockResolvedValue({
        ok: false
    });

    render(<AddMenuItem />);

    fireEvent.change(screen.getByLabelText("Name"), {
        target: { value: "Burger" }
    });

    fireEvent.change(screen.getByLabelText("Price"), {
        target: { value: "10" }
    });

    fireEvent.click(screen.getByRole("button", {
        name: "Add Menu Item"
    }));

    expect(await screen.findByRole("alert"))
        .toHaveProperty("textContent", "Failed to add menu item");
});
