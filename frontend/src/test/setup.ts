import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// React Testing Library doesn't auto-cleanup between tests under Vitest the
// way it does under Jest, so we do it explicitly to avoid state leaking
// across test cases (duplicate DOM nodes, stale event listeners, etc.).
afterEach(() => {
  cleanup();
});

// jsdom doesn't implement matchMedia, but our ThemeContext calls it on
// mount to detect the user's OS-level dark-mode preference.
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});
