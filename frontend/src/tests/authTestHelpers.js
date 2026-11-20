// Helpers shared by the login, registration and account tests.

// Build a token shaped like the backend's: header.payload.signature.
// The frontend only reads the payload, so the signature can be anything.
export function fakeToken(id, role) {
  const payload = btoa(JSON.stringify({ sub: id, role }));
  return `header.${payload}.signature`;
}

// Pretend someone is already signed in.
export function signInAs(id, role = "customer") {
  sessionStorage.setItem(
    "session",
    JSON.stringify({ token: fakeToken(id, role), user: { id, role } })
  );
}

// A fetch response that succeeded.
export function okResponse(data) {
  return { ok: true, status: 200, json: async () => data };
}

// A fetch response that failed with a message from the backend.
export function errorResponse(status, detail) {
  return { ok: false, status, json: async () => ({ detail }) };
}
