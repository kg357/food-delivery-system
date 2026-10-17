import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, afterEach, expect, test, vi } from "vitest";
import App from "./App";

const menuItem = {
  id: "item-123",
  restaurant_id: 1,
  name: "Cheeseburger",
  description: "Beef burger",
  price: 12.99,
  available: true,
};

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [menuItem],
  }));

  vi.stubGlobal("alert", vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("displays menu items from the backend", async () => {
  window.history.pushState({}, "", "/menu/edit");
  render(<App />);

  expect(await screen.findByText("Cheeseburger")).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith("http://localhost:8000/restaurants/1/menu");
});

test("saves an edited menu item using PATCH", async () => {
  const user = userEvent.setup();

  fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => [menuItem],
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ...menuItem, price: 14.99 }),
    });

  window.history.pushState({}, "", "/menu/edit");
  render(<App />);

  await screen.findByText("Cheeseburger");

  await user.click(screen.getByRole("button", { name: "Edit" }));

  await user.clear(screen.getByLabelText("Price"));
  await user.type(screen.getByLabelText("Price"), "14.99");

  await user.click(screen.getByRole("button", { name: "Save Changes" }));

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/restaurants/1/menu/item-123",
      expect.objectContaining({
        method: "PATCH",
        body: expect.stringContaining('"price":14.99'),
      })
    );
  });

  expect(await screen.findByText("$14.99")).toBeInTheDocument();
});