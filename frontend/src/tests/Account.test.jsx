import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import Account from "../pages/Account/Account";
import {
  errorResponse,
  okResponse,
  signInAs,
} from "./authTestHelpers";

const customer = {
  id: "c1",
  name: "Ana",
  email: "ana@example.com",
  address: "1 Main St",
  role: "customer",
  active: true,
};

afterEach(() => {
  vi.unstubAllGlobals();
  sessionStorage.clear();
});

function renderAccount() {
  return render(
    <MemoryRouter initialEntries={["/account"]}>
      <Routes>
        <Route path="/account" element={<Account />} />
        <Route path="/" element={<h1>Login page</h1>} />
        <Route path="/restaurants" element={<h1>Customer home</h1>} />
      </Routes>
    </MemoryRouter>
  );
}

test("someone who is not signed in is sent to the login page", async () => {
  vi.stubGlobal("fetch", vi.fn());

  renderAccount();

  expect(await screen.findByText("Login page")).toBeInTheDocument();
  expect(fetch).not.toHaveBeenCalled();
});

test("the account page loads the signed-in customer with their token", async () => {
  signInAs("c1");
  const mockFetch = vi.fn().mockResolvedValue(okResponse(customer));
  vi.stubGlobal("fetch", mockFetch);

  renderAccount();

  expect(await screen.findByDisplayValue("Ana")).toBeInTheDocument();
  expect(screen.getByDisplayValue("1 Main St")).toBeInTheDocument();
  expect(screen.getByText("ana@example.com")).toBeInTheDocument();

  const [url, options] = mockFetch.mock.calls[0];
  expect(url).toBe("http://localhost:8000/customers/c1");
  expect(options.headers.Authorization).toMatch(/^Bearer /);
});

test("saving sends only the name and address", async () => {
  const user = userEvent.setup();
  signInAs("c1");
  const mockFetch = vi
    .fn()
    .mockResolvedValueOnce(okResponse(customer))
    .mockResolvedValueOnce(okResponse({ ...customer, name: "Ana B" }));
  vi.stubGlobal("fetch", mockFetch);

  renderAccount();

  const nameInput = await screen.findByLabelText("Name");
  await user.clear(nameInput);
  await user.type(nameInput, "Ana B");
  await user.click(screen.getByRole("button", { name: "Save Changes" }));

  expect(
    await screen.findByText("Your account was updated.")
  ).toBeInTheDocument();

  const [url, options] = mockFetch.mock.calls[1];
  expect(url).toBe("http://localhost:8000/customers/c1");
  expect(options.method).toBe("PATCH");
  expect(JSON.parse(options.body)).toEqual({
    name: "Ana B",
    address: "1 Main St",
  });
});

test("a failed save shows the error", async () => {
  const user = userEvent.setup();
  signInAs("c1");
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(okResponse(customer))
      .mockResolvedValueOnce(errorResponse(403, "Not allowed."))
  );

  renderAccount();

  await user.click(await screen.findByRole("button", { name: "Save Changes" }));

  expect(await screen.findByText("Not allowed.")).toBeInTheDocument();
});

test("deactivating asks for confirmation, then signs the customer out", async () => {
  const user = userEvent.setup();
  signInAs("c1");
  const mockFetch = vi
    .fn()
    .mockResolvedValueOnce(okResponse(customer))
    .mockResolvedValueOnce(okResponse({ ...customer, active: false }));
  vi.stubGlobal("fetch", mockFetch);

  renderAccount();

  await user.click(
    await screen.findByRole("button", { name: "Deactivate my account" })
  );

  // Nothing is sent until the customer confirms.
  expect(mockFetch).toHaveBeenCalledTimes(1);

  await user.click(
    screen.getByRole("button", { name: "Yes, deactivate my account" })
  );

  expect(await screen.findByText("Login page")).toBeInTheDocument();

  const [url, options] = mockFetch.mock.calls[1];
  expect(url).toBe("http://localhost:8000/customers/c1/deactivate");
  expect(options.method).toBe("POST");
  expect(sessionStorage.getItem("session")).toBeNull();
});

test("cancelling the confirmation does not deactivate", async () => {
  const user = userEvent.setup();
  signInAs("c1");
  const mockFetch = vi.fn().mockResolvedValue(okResponse(customer));
  vi.stubGlobal("fetch", mockFetch);

  renderAccount();

  await user.click(
    await screen.findByRole("button", { name: "Deactivate my account" })
  );
  await user.click(screen.getByRole("button", { name: "Cancel" }));

  await waitFor(() => {
    expect(
      screen.getByRole("button", { name: "Deactivate my account" })
    ).toBeInTheDocument();
  });
  expect(mockFetch).toHaveBeenCalledTimes(1);
});
