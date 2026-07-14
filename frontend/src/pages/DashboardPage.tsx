import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, FolderOpen, Layers } from "lucide-react";
import { projectsApi } from "../api/projects";
import { PageHeader, EmptyState } from "../components/Shared";
import { ListSkeleton } from "../components/Skeletons";
import { StatusBadge } from "../components/Badges";

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["projects", { page: 1 }],
    queryFn: () => projectsApi.list({ page: 1, page_size: 50 }),
  });

  const projects = data?.data.items ?? [];

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title="Dashboard"
        description="All the APIs you've uploaded and investigated."
        action={
          <Link to="/upload" className="btn-primary">
            <Plus className="h-4 w-4" /> New investigation
          </Link>
        }
      />

      {isLoading ? (
        <ListSkeleton rows={4} />
      ) : projects.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title="No projects yet"
          description="Upload an OpenAPI spec, Postman collection, or documentation file to get started."
          action={
            <Link to="/upload" className="btn-primary">
              <Plus className="h-4 w-4" /> Upload your first API
            </Link>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/explorer/${project.id}`}
              className="card group flex flex-col gap-3 p-5 transition hover:border-accent/50"
            >
              <div className="flex items-start justify-between">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <Layers className="h-5 w-5" />
                </div>
                <StatusBadge status={project.status} />
              </div>
              <div>
                <h3 className="truncate font-semibold text-slate-100 group-hover:text-accent-light">
                  {project.name}
                </h3>
                <p className="mono mt-0.5 text-xs uppercase tracking-wide text-slate-500">
                  {project.source_type}
                </p>
              </div>
              <div className="mt-auto flex items-center justify-between text-xs text-slate-500">
                <span>{project.endpoint_count} endpoint{project.endpoint_count === 1 ? "" : "s"}</span>
                <span>{new Date(project.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
