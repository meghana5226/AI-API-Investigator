import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Sparkles, ShieldAlert, Search, ChevronDown, Loader2, FolderOpen } from "lucide-react";
import { projectsApi } from "../api/projects";
import { PageHeader, EmptyState } from "../components/Shared";
import { ListSkeleton, CardSkeleton } from "../components/Skeletons";
import { MethodBadge, StatusBadge } from "../components/Badges";

export function ApiExplorerPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const { data: projectsList } = useQuery({
    queryKey: ["projects", { page: 1 }],
    queryFn: () => projectsApi.list({ page: 1, page_size: 100 }),
  });

  if (!projectId) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-8">
        <PageHeader title="API Explorer" description="Pick a project to explore its endpoints." />
        <div className="grid gap-3 sm:grid-cols-2">
          {(projectsList?.data.items ?? []).map((p) => (
            <button
              key={p.id}
              onClick={() => navigate(`/explorer/${p.id}`)}
              className="card flex items-center justify-between p-4 text-left transition hover:border-accent/50"
            >
              <div>
                <p className="font-medium text-slate-100">{p.name}</p>
                <p className="mono text-xs text-slate-500">{p.endpoint_count} endpoints</p>
              </div>
              <StatusBadge status={p.status} />
            </button>
          ))}
          {projectsList && projectsList.data.items.length === 0 && (
            <EmptyState icon={FolderOpen} title="No projects yet" description="Upload an API to start exploring." />
          )}
        </div>
      </div>
    );
  }

  return <ProjectExplorer projectId={projectId} />;
}

function ProjectExplorer({ projectId }: { projectId: string }) {
  const [search, setSearch] = useState("");
  const [method, setMethod] = useState("");
  const queryClient = useQueryClient();

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectsApi.get(projectId),
  });

  const { data: endpoints, isLoading: endpointsLoading } = useQuery({
    queryKey: ["endpoints", projectId, search, method],
    queryFn: () => projectsApi.listEndpoints(projectId, { search: search || undefined, method: method || undefined, page_size: 100 }),
  });

  const analyzeMutation = useMutation({
    mutationFn: () => projectsApi.analyze(projectId),
    onSuccess: () => {
      toast.success("AI analysis complete");
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    },
    onError: () => toast.error("Analysis failed — is the AI service running?"),
  });

  if (projectLoading) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-8">
        <CardSkeleton />
      </div>
    );
  }

  const p = project?.data;
  if (!p) return null;

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title={p.name}
        description={p.description || `${p.source_type.toUpperCase()} · ${p.endpoint_count} endpoints`}
        action={
          <button onClick={() => analyzeMutation.mutate()} disabled={analyzeMutation.isPending} className="btn-primary">
            {analyzeMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Run AI analysis
          </button>
        }
      />

      {p.ai_summary && (
        <div className="card mb-4 p-5">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-accent-light">
            <Sparkles className="h-4 w-4" /> AI Summary
          </div>
          <p className="text-sm leading-relaxed text-slate-300">{p.ai_summary}</p>
        </div>
      )}

      {p.risk_report && (
        <div className="card mb-6 p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-amber-400">
            <ShieldAlert className="h-4 w-4" /> Risk Report
          </div>
          <div className="mb-3 flex gap-4 text-sm">
            <span className="text-red-400">{p.risk_report.high} high</span>
            <span className="text-amber-400">{p.risk_report.medium} medium</span>
            <span className="text-sky-400">{p.risk_report.low} low</span>
          </div>
          <ul className="space-y-1.5">
            {p.risk_report.issues.slice(0, 6).map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                <StatusBadge status={issue.severity} />
                <span>
                  <code className="mono text-slate-300">{issue.endpoint}</code> — {issue.issue}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="input-field pl-9"
            placeholder="Search endpoints by path or summary…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="relative">
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="input-field appearance-none pr-8"
          >
            <option value="">All methods</option>
            {["GET", "POST", "PUT", "PATCH", "DELETE", "DOC"].map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        </div>
      </div>

      {endpointsLoading ? (
        <ListSkeleton rows={6} />
      ) : (
        <div className="card divide-y divide-ink-700 overflow-hidden">
          {(endpoints?.data.items ?? []).map((ep) => (
            <Link
              key={ep.id}
              to={`/explorer/${projectId}/endpoints/${ep.id}`}
              className="flex items-center gap-4 px-4 py-3 transition hover:bg-ink-700/50"
            >
              <MethodBadge method={ep.method} />
              <code className="mono flex-1 truncate text-sm text-slate-200">{ep.path}</code>
              <span className="hidden truncate text-xs text-slate-500 sm:block sm:max-w-xs">{ep.summary}</span>
            </Link>
          ))}
          {endpoints && endpoints.data.items.length === 0 && (
            <p className="px-4 py-8 text-center text-sm text-slate-500">No endpoints match your filters.</p>
          )}
        </div>
      )}
    </div>
  );
}
