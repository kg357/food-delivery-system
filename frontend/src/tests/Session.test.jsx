
import {
    afterEach,
    describe,
    expect,
    test,
} from "vitest";

import {
    saveSession,
    getSession,
    clearSession,
} from "../auth/session";

// Create a synthetic JWT for testing client-side parsing.
// These tokens are not cryptographically signed.
function createTestToken(overrides = {}) {
    const payload = {
        sub: "customer123",
        role: "customer",
        exp: Math.floor(Date.now() / 1000) + 3600,
        ...overrides,
    };

    return [
        "test-header",
        btoa(JSON.stringify(payload)),
        "test-signature",
    ].join(".");
}

afterEach(() => {
    sessionStorage.clear();
});

describe("Authentication Session", () => {
    test("saves a valid session", () => {
        const token = createTestToken();

        const user = saveSession(token);

        expect(user).toEqual({
            id: "customer123",
            role: "customer",
        });

        expect(
            sessionStorage.getItem(
                "foodDeliveryAccessToken"
            )
        ).toBe(token);
    });

    test("retrieves a saved session", () => {
        const token = createTestToken();

        saveSession(token);

        expect(getSession()).toEqual({
            id: "customer123",
            role: "customer",
            token,
        });
    });

    test("returns null when no session exists", () => {
        expect(getSession()).toBeNull();
    });

    test("rejects expired tokens", () => {
        const expiredToken = createTestToken({
            exp: Math.floor(Date.now() / 1000) - 60,
        });

        expect(() => {
            saveSession(expiredToken);
        }).toThrow("Authentication token has expired.");

        expect(getSession()).toBeNull();
    });

    test("clears an expired stored session", () => {
        const expiredToken = createTestToken({
            exp: Math.floor(Date.now() / 1000) - 60,
        });

        sessionStorage.setItem(
            "foodDeliveryAccessToken",
            expiredToken
        );

        expect(getSession()).toBeNull();

        expect(
            sessionStorage.getItem(
                "foodDeliveryAccessToken"
            )
        ).toBeNull();
    });

    test("rejects invalid user roles", () => {
        const token = createTestToken({
            role: "unknown_role",
        });

        expect(() => saveSession(token)).toThrow(
            "Invalid authentication token."
        );
    });

    test("rejects malformed tokens", () => {
        expect(() =>
            saveSession("invalid-token")
        ).toThrow("Invalid authentication token.");
    });

    test("clears the session during logout", () => {
        const token = createTestToken();

        saveSession(token);
        clearSession();

        expect(getSession()).toBeNull();
    });

    test("supports restaurant owner sessions", () => {
        const token = createTestToken({
            sub: "owner1",
            role: "restaurant_owner",
        });

        saveSession(token);

        expect(getSession()).toEqual({
            id: "owner1",
            role: "restaurant_owner",
            token,
        });
    });
});
