import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FolderOpen } from "lucide-react";
import { EmptyState, PageHeader } from "../Shared";

describe("EmptyState", () => {
  it("renders the title and description", () => {
    render(<EmptyState icon={FolderOpen} title="No projects yet" description="Upload your first API to get started." />);
    expect(screen.getByText("No projects yet")).toBeInTheDocument();
    expect(screen.getByText("Upload your first API to get started.")).toBeInTheDocument();
  });

  it("renders the optional action and responds to clicks", async () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        icon={FolderOpen}
        title="No projects yet"
        description="Upload your first API to get started."
        action={<button onClick={onClick}>Upload</button>}
      />
    );

    const button = screen.getByRole("button", { name: "Upload" });
    await userEvent.click(button);
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("does not render an action when none is provided", () => {
    render(<EmptyState icon={FolderOpen} title="No projects yet" description="Nothing here." />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});

describe("PageHeader", () => {
  it("renders the title", () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
  });

  it("renders an optional description", () => {
    render(<PageHeader title="Dashboard" description="All your API investigations." />);
    expect(screen.getByText("All your API investigations.")).toBeInTheDocument();
  });

  it("omits the description paragraph when none is given", () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.queryByText(/investigations/)).not.toBeInTheDocument();
  });

  it("renders an optional action element", () => {
    render(<PageHeader title="Dashboard" action={<button>New</button>} />);
    expect(screen.getByRole("button", { name: "New" })).toBeInTheDocument();
  });
});
