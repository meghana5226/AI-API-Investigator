import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { CardSkeleton, ListSkeleton, Skeleton, TableRowSkeleton } from "../Skeletons";

describe("Skeleton", () => {
  it("renders a pulsing placeholder element", () => {
    const { container } = render(<Skeleton className="h-4 w-1/2" />);
    const el = container.firstChild as HTMLElement;
    expect(el).toHaveClass("animate-pulse", "h-4", "w-1/2");
  });
});

describe("CardSkeleton", () => {
  it("renders three placeholder lines inside a card", () => {
    const { container } = render(<CardSkeleton />);
    const pulses = container.querySelectorAll(".animate-pulse");
    expect(pulses.length).toBe(3);
  });
});

describe("ListSkeleton", () => {
  it("renders the default number of skeleton rows", () => {
    const { container } = render(<ListSkeleton />);
    const rows = container.querySelectorAll(".animate-pulse");
    // 3 skeleton bars per TableRowSkeleton row, 5 rows by default
    expect(rows.length).toBe(15);
  });

  it("renders a custom number of rows when specified", () => {
    const { container } = render(<ListSkeleton rows={2} />);
    const rows = container.querySelectorAll(".animate-pulse");
    expect(rows.length).toBe(6);
  });
});

describe("TableRowSkeleton", () => {
  it("renders three placeholder segments per row", () => {
    const { container } = render(<TableRowSkeleton />);
    expect(container.querySelectorAll(".animate-pulse").length).toBe(3);
  });
});
