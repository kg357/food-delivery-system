import { afterEach, test, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AddMenuItem from "../pages/AddMenuItem/AddMenuItem";
import { MemoryRouter, Routes, Route } from "react-router-dom";

it("adds a menu item", async () => {
    global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
            id: "123",
            name: "Burger",
            price: 10
        })
    });

    render(
        <MemoryRouter initialEntries={["/menu/add"]}>
            <AddMenuItem />
        </MemoryRouter>
    );

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

    render(
        <MemoryRouter initialEntries={["/menu/add"]}>
            <AddMenuItem />
        </MemoryRouter>
    );

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

    render(
        <MemoryRouter initialEntries={["/menu/add"]}>
            <AddMenuItem />
        </MemoryRouter>
    );

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


test("owner adds a menu item to the selected restaurant", async () => {
  const user = userEvent.setup();

  const mockFetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      id: "new-item",
      restaurant_id: 7,
      name: "Margherita Pizza",
      description: "Tomato and mozzarella",
      price: 16.99,
      available: true,
    }),
  });

  vi.stubGlobal("fetch", mockFetch);

  render(
    <MemoryRouter
      initialEntries={["/owner/restaurants/7/menu/add"]}
    >
      <Routes>
        <Route
          path="/owner/restaurants/:id/menu/add"
          element={<AddMenuItem />}
        />
      </Routes>
    </MemoryRouter>
  );

  expect(
    screen.queryByLabelText("Restaurant ID")
  ).not.toBeInTheDocument();

  await user.type(
    screen.getByLabelText("Name"),
    "Margherita Pizza"
  );

  await user.type(
    screen.getByLabelText("Description"),
    "Tomato and mozzarella"
  );

  await user.type(
    screen.getByLabelText("Price"),
    "16.99"
  );

  await user.click(
    screen.getByRole("button", { name: /add menu item/i })
  );

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/restaurants/7/menu",
      expect.objectContaining({
        method: "POST",
      })
    );
  });

  expect(
    await screen.findByText("Menu item added successfully!")
  ).toBeInTheDocument();
});
