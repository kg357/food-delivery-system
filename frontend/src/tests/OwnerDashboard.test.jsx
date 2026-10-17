
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import OwnerDashboard from "../pages/OwnerDashboard/OwnerDashboard";

const restaurants = [
  {
    id: 1,
    owner_id: "owner1",
    name: "Wasabi Ramen",
    cuisine: "Japanese",
    address: "123 Main St",
    rating: 4.5,
  },
  {
    id: 2,
    owner_id: "development_owner",
    name: "The Golden Fork",
    cuisine: "Italian",
    address: "456 Main St",
    rating: 0,
  },
  {
    id: 3,
    owner_id: "development_owner",
    name: "Sunrise Cafe",
    cuisine: "Cafe",
    address: "789 Main St",
    rating: 0,
  },
];

function renderDashboard() {
  return render(
    <MemoryRouter>
      <OwnerDashboard />
    </MemoryRouter>
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("displays only restaurants owned by the demo owner", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => restaurants,
    })
  );

  renderDashboard();

  expect(await screen.findByText("The Golden Fork"))
    .toBeInTheDocument();

  expect(screen.getByText("Sunrise Cafe"))
    .toBeInTheDocument();

  expect(screen.queryByText("Wasabi Ramen"))
    .not.toBeInTheDocument();

  expect(
    screen.getAllByText("Manage Restaurant →")
  ).toHaveLength(2);
});

test("displays an empty state when owner has no restaurants", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => restaurants.slice(0, 1),
    })
  );

  renderDashboard();

  expect(
    await screen.findByText("No restaurants yet")
  ).toBeInTheDocument();

  expect(
    screen.getByText("Create your first restaurant to get started.")
  ).toBeInTheDocument();
});

test("displays an error when restaurants cannot be loaded", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new Error("Network unavailable"))
  );

  renderDashboard();

  expect(
    await screen.findByRole("alert")
  ).toHaveTextContent("Network unavailable");
});
