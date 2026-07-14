import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { FileText, Download, FileJson } from "lucide-react";
import { projectsApi } from "../api/projects";
import { PageHeader, EmptyState } from "../components/Shared";
import { ListSkeleton } from "../components/Skeletons";
import { StatusBadge } from "../components/Badges";

export function ReportsPage() {
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["projects", { page: 1 }],
    queryFn: () => projectsApi.list({ page: 1, page_size: 100 }),
  });

  const projects = data?.data.items ?? [];

  const handleExport = async (id: string, name: string, format: "json" | "markdown") => {
    setDownloadingId(`${id}-${format}`);
    try {
      const response = await projectsApi.exportReport(id, format);
      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${name}-report.${format === "markdown" ? "md" : "json"}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Report downloaded");
    } catch {
      toast.error("Export failed");
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <PageHeader title="Reports" description="Export a full investigation report for any project." />

      {isLoading ? (
        <ListSkeleton rows={4} />
      ) : projects.length === 0 ? (
        <EmptyState icon={FileText} title="Nothing to export yet" description="Upload and analyze an API to generate a report." />
      ) : (
        <div className="card divide-y divide-ink-700">
          {projects.map((p) => (
            <div key={p.id} className="flex items-center justify-between gap-4 px-4 py-3.5">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <FileText className="h-4 w-4" />
                </div>
                <div>
                  <p className="font-medium text-slate-200">{p.name}</p>
                  <p className="text-xs text-slate-500">{p.endpoint_count} endpoints</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={p.status} />
                <button
                  onClick={() => handleExport(p.id, p.name, "markdown")}
                  disabled={downloadingId === `${p.id}-markdown`}
                  className="btn-secondary text-xs"
                >
                  <Download className="h-3.5 w-3.5" /> Markdown
                </button>
                <button
                  onClick={() => handleExport(p.id, p.name, "json")}
                  disabled={downloadingId === `${p.id}-json`}
                  className="btn-secondary text-xs"
                >
                  <FileJson className="h-3.5 w-3.5" /> JSON
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
