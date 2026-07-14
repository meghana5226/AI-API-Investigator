import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MethodBadge, StatusBadge } from "../Badges";

describe("StatusBadge", () => {
  it("renders the status text", () => {
    render(<StatusBadge status="ready" />);
    expect(screen.getByText("ready")).toBeInTheDocument();
  });

  it("applies the emerald/success styling for 'ready'", () => {
    render(<StatusBadge status="ready" />);
    expect(screen.getByText("ready")).toHaveClass("bg-emerald-500/15", "text-emerald-400");
  });

  it("applies the red/danger styling for 'failed'", () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText("failed")).toHaveClass("bg-red-500/15", "text-red-400");
  });

  it("applies the amber styling for 'high' risk severity", () => {
    render(<StatusBadge status="high" />);
    expect(screen.getByText("high")).toHaveClass("bg-red-500/15", "text-red-400");
  });

  it("falls back to a neutral style for an unrecognized status", () => {
    render(<StatusBadge status="some-unknown-status" />);
    expect(screen.getByText("some-unknown-status")).toHaveClass("bg-slate-500/15", "text-slate-400");
  });

  it("is case-insensitive when matching known statuses", () => {
    render(<StatusBadge status="READY" />);
    expect(screen.getByText("READY")).toHaveClass("bg-emerald-500/15");
  });
});

describe("MethodBadge", () => {
  it("renders the HTTP method text", () => {
    render(<MethodBadge method="GET" />);
    expect(screen.getByText("GET")).toBeInTheDocument();
  });

  it("applies distinct styling for GET vs DELETE", () => {
    const { rerender } = render(<MethodBadge method="GET" />);
    const getBadge = screen.getByText("GET");
    expect(getBadge).toHaveClass("bg-emerald-500/15");

    rerender(<MethodBadge method="DELETE" />);
    const deleteBadge = screen.getByText("DELETE");
    expect(deleteBadge).toHaveClass("bg-red-500/15");
  });

  it("normalizes lowercase method input to uppercase display", () => {
    render(<MethodBadge method="post" />);
    expect(screen.getByText("post")).toHaveClass("bg-sky-500/15", "text-sky-400");
  });

  it("uses the mono font class for methods", () => {
    render(<MethodBadge method="GET" />);
    expect(screen.getByText("GET")).toHaveClass("font-mono");
  });
});
