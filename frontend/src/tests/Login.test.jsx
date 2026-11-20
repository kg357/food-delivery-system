import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import Login from "../pages/Login/Login";
import {
  errorResponse,
  fakeToken,
  okResponse,
} from "./authTestHelpers";

afterEach(() => {
  vi.unstubAllGlobals();
  sessionStorage.clear();
});

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/restaurants" element={<h1>Customer home</h1>} />
        <Route path="/owner/restaurants" element={<h1>Owner home</h1>} />
        <Route path="/register" element={<h1>Register page</h1>} />
      </Routes>
    </MemoryRouter>
  );
}

test("signing in sends the email and password in the request body", async () => {
  const user = userEvent.setup();
  const mockFetch = vi.fn().mockResolvedValue(
    okResponse({
      access_token: fakeToken("c1", "customer"),
      token_type: "bearer",
    })
  );
  vi.stubGlobal("fetch", mockFetch);

  renderLogin();

  await user.type(screen.getByLabelText("Email"), "ana@example.com");
  await user.type(screen.getByLabelText("Password"), "Password123");
  await user.click(screen.getByRole("button", { name: "Sign In" }));

  expect(await screen.findByText("Customer home")).toBeInTheDocument();

  const [url, options] = mockFetch.mock.calls[0];
  expect(url).toBe("http://localhost:8000/auth/login");
  expect(options.method).toBe("POST");
  expect(JSON.parse(options.body)).toEqual({
    email: "ana@example.com",
    password: "Password123",
  });
});

test("a signed-in session is saved with the user's id and role", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      okResponse({ access_token: fakeToken("c1", "customer") })
    )
  );

  renderLogin();

  await user.type(screen.getByLabelText("Email"), "ana@example.com");
  await user.type(screen.getByLabelText("Password"), "Password123");
  await user.click(screen.getByRole("button", { name: "Sign In" }));

  await screen.findByText("Customer home");

  const session = JSON.parse(sessionStorage.getItem("session"));
  expect(session.user).toEqual({ id: "c1", role: "customer" });
  expect(session.token).toBe(fakeToken("c1", "customer"));
});

test("an owner is sent to the owner dashboard", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      okResponse({ access_token: fakeToken("owner1", "restaurant_owner") })
    )
  );

  renderLogin();

  await user.type(screen.getByLabelText("Email"), "owner@example.com");
  await user.type(screen.getByLabelText("Password"), "OwnerDemo123");
  await user.click(screen.getByRole("button", { name: "Sign In" }));

  expect(await screen.findByText("Owner home")).toBeInTheDocument();
});

test("a wrong password shows the backend message and stays on the page", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      errorResponse(401, "Invalid email or password.")
    )
  );

  renderLogin();

  await user.type(screen.getByLabelText("Email"), "ana@example.com");
  await user.type(screen.getByLabelText("Password"), "wrong-password");
  await user.click(screen.getByRole("button", { name: "Sign In" }));

  expect(
    await screen.findByText("Invalid email or password.")
  ).toBeInTheDocument();
  expect(sessionStorage.getItem("session")).toBeNull();
});

test("a deactivated account shows the deactivated message", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      errorResponse(403, "This account has been deactivated.")
    )
  );

  renderLogin();

  await user.type(screen.getByLabelText("Email"), "ana@example.com");
  await user.type(screen.getByLabelText("Password"), "Password123");
  await user.click(screen.getByRole("button", { name: "Sign In" }));

  expect(
    await screen.findByText("This account has been deactivated.")
  ).toBeInTheDocument();
});

test("the example owner button signs in with the demo owner account", async () => {
  const user = userEvent.setup();
  const mockFetch = vi.fn().mockResolvedValue(
    okResponse({ access_token: fakeToken("owner1", "restaurant_owner") })
  );
  vi.stubGlobal("fetch", mockFetch);

  renderLogin();

  await user.click(screen.getByRole("button", { name: /Example Owner/ }));

  expect(await screen.findByText("Owner home")).toBeInTheDocument();
  expect(JSON.parse(mockFetch.mock.calls[0][1].body).email).toBe(
    "owner@example.com"
  );
});

test("there is a link to create an account", async () => {
  const user = userEvent.setup();

  renderLogin();

  await user.click(screen.getByRole("link", { name: "Create an account" }));

  await waitFor(() => {
    expect(screen.getByText("Register page")).toBeInTheDocument();
  });
});
