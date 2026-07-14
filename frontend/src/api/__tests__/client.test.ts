import { beforeEach, describe, expect, it } from "vitest";
import { tokenStorage } from "../client";

describe("tokenStorage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns null when no tokens are stored", () => {
    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });

  it("stores and retrieves the access and refresh tokens", () => {
    tokenStorage.set("access-123", "refresh-456");
    expect(tokenStorage.getAccess()).toBe("access-123");
    expect(tokenStorage.getRefresh()).toBe("refresh-456");
  });

  it("overwrites previously stored tokens", () => {
    tokenStorage.set("old-access", "old-refresh");
    tokenStorage.set("new-access", "new-refresh");
    expect(tokenStorage.getAccess()).toBe("new-access");
    expect(tokenStorage.getRefresh()).toBe("new-refresh");
  });

  it("clears both tokens", () => {
    tokenStorage.set("access-123", "refresh-456");
    tokenStorage.clear();
    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });
});
