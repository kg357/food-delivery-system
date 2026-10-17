
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import OwnerRestaurantDetails from "../pages/OwnerRestaurantDetails/OwnerRestaurantDetails";

const restaurant = {
  id: 4,
  owner_id: "development_owner",
  name: "The Golden Fork",
  cuisine: "Italian",
  address: "123 Main Street",
  rating: 0,
};

afterEach(() => {
  vi.unstubAllGlobals();
});

test("owner can edit restaurant information", async () => {
  const user = userEvent.setup();

  const mockFetch = vi.fn(async (url, options) => {
    if (url === "http://localhost:8000/restaurants/4" &&
        options?.method === "PATCH") {
      return {
        ok: true,
        json: async () => ({
          ...restaurant,
          name: "The Golden Fork Bistro",
        }),
      };
    }

    if (url === "http://localhost:8000/restaurants/4") {
      return {
        ok: true,
        json: async () => restaurant,
      };
    }

    if (url === "http://localhost:8000/restaurants/4/menu") {
      return {
        ok: true,
        json: async () => [],
      };
    }

    throw new Error(`Unexpected request: ${url}`);
  });

  vi.stubGlobal("fetch", mockFetch);

  render(
    <MemoryRouter initialEntries={["/owner/restaurants/4"]}>
      <Routes>
        <Route
          path="/owner/restaurants/:id"
          element={<OwnerRestaurantDetails />}
        />
      </Routes>
    </MemoryRouter>
  );

  expect(
    await screen.findByRole("heading", {
      name: "The Golden Fork",
    })
  ).toBeInTheDocument();

  await user.click(
    screen.getByRole("button", { name: "Edit Restaurant" })
  );

  const nameInput = screen.getByLabelText("Restaurant Name");

  await user.clear(nameInput);
  await user.type(nameInput, "The Golden Fork Bistro");

  await user.click(
    screen.getByRole("button", { name: "Save Changes" })
  );

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/restaurants/4",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          name: "The Golden Fork Bistro",
          cuisine: "Italian",
          address: "123 Main Street",
        }),
      })
    );
  });

  expect(
    await screen.findByText("Restaurant updated successfully.")
  ).toBeInTheDocument();
});

test("owner cannot edit a restaurant belonging to another owner", async () => {
  const otherRestaurant = {
    ...restaurant,
    owner_id: "owner2",
  };

  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => otherRestaurant,
    })
  );

  render(
    <MemoryRouter initialEntries={["/owner/restaurants/4"]}>
      <Routes>
        <Route
          path="/owner/restaurants/:id"
          element={<OwnerRestaurantDetails />}
        />
      </Routes>
    </MemoryRouter>
  );

  expect(
    await screen.findByRole("alert")
  ).toHaveTextContent(
    "This restaurant does not belong to the demo owner."
  );

  expect(
    screen.queryByRole("button", {
      name: "Edit Restaurant",
    })
  ).not.toBeInTheDocument();
});
