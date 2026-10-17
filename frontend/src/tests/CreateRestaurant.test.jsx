
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import CreateRestaurant from "../pages/CreateRestaurant/CreateRestaurant";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("owner can create a restaurant", async () => {
  const user = userEvent.setup();

  const mockRestaurant = {
    id: 4,
    owner_id: "development_owner",
    name: "The Golden Fork",
    cuisine: "Italian",
    address: "123 Main Street",
    rating: 0,
  };

  const mockFetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 201,
    json: async () => mockRestaurant,
  });

  vi.stubGlobal("fetch", mockFetch);

  render(
    <MemoryRouter initialEntries={["/owner/restaurants/new"]}>
      <Routes>
        <Route
          path="/owner/restaurants/new"
          element={<CreateRestaurant />}
        />
        <Route
          path="/owner/restaurants/:id"
          element={<h1>Restaurant Created Successfully</h1>}
        />
      </Routes>
    </MemoryRouter>
  );

  await user.type(
    screen.getByLabelText("Restaurant Name"),
    "The Golden Fork"
  );

  await user.type(
    screen.getByLabelText("Cuisine"),
    "Italian"
  );

  await user.type(
    screen.getByLabelText("Address"),
    "123 Main Street"
  );

  await user.click(
    screen.getByRole("button", { name: "Create Restaurant" })
  );

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/restaurants",
      expect.objectContaining({
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "The Golden Fork",
          cuisine: "Italian",
          address: "123 Main Street",
        }),
      })
    );
  });

  expect(
    await screen.findByText("Restaurant Created Successfully")
  ).toBeInTheDocument();
});
