import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import Register from "../pages/Register/Register";
import {
  errorResponse,
  fakeToken,
  okResponse,
} from "./authTestHelpers";

afterEach(() => {
  vi.unstubAllGlobals();
  sessionStorage.clear();
});

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={["/register"]}>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/restaurants" element={<h1>Customer home</h1>} />
      </Routes>
    </MemoryRouter>
  );
}

async function fillForm(user, { address = "" } = {}) {
  await user.type(screen.getByLabelText("Name"), "Ana");
  await user.type(screen.getByLabelText("Email"), "ana@example.com");
  await user.type(
    screen.getByLabelText(/Password \(at least 8 characters\)/),
    "Password123"
  );

  if (address) {
    await user.type(screen.getByLabelText(/Delivery address/), address);
  }

  await user.click(screen.getByRole("button", { name: "Create Account" }));
}

test("registering creates the account and then signs in", async () => {
  const user = userEvent.setup();
  const mockFetch = vi
    .fn()
    .mockResolvedValueOnce(
      okResponse({ id: "c1", name: "Ana", email: "ana@example.com" })
    )
    .mockResolvedValueOnce(
      okResponse({ access_token: fakeToken("c1", "customer") })
    );
  vi.stubGlobal("fetch", mockFetch);

  renderRegister();
  await fillForm(user, { address: "1 Main St" });

  expect(await screen.findByText("Customer home")).toBeInTheDocument();

  const [registerUrl, registerOptions] = mockFetch.mock.calls[0];
  expect(registerUrl).toBe("http://localhost:8000/customers/register");
  expect(JSON.parse(registerOptions.body)).toEqual({
    name: "Ana",
    email: "ana@example.com",
    password: "Password123",
    address: "1 Main St",
  });

  expect(mockFetch.mock.calls[1][0]).toBe(
    "http://localhost:8000/auth/login"
  );
});

test("an empty address is left out of the request", async () => {
  const user = userEvent.setup();
  const mockFetch = vi
    .fn()
    .mockResolvedValueOnce(okResponse({ id: "c1" }))
    .mockResolvedValueOnce(
      okResponse({ access_token: fakeToken("c1", "customer") })
    );
  vi.stubGlobal("fetch", mockFetch);

  renderRegister();
  await fillForm(user);

  await screen.findByText("Customer home");

  expect(JSON.parse(mockFetch.mock.calls[0][1].body)).not.toHaveProperty(
    "address"
  );
});

test("a duplicate email shows the backend message", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      errorResponse(400, "An account with this email already exists.")
    )
  );

  renderRegister();
  await fillForm(user);

  expect(
    await screen.findByText("An account with this email already exists.")
  ).toBeInTheDocument();
  expect(sessionStorage.getItem("session")).toBeNull();
});
