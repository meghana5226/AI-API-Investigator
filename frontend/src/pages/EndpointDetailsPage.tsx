import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ArrowLeft, Sparkles, Copy, Check, Loader2 } from "lucide-react";
import { projectsApi } from "../api/projects";
import { MethodBadge } from "../components/Badges";
import { CardSkeleton } from "../components/Skeletons";

type Tab = "curl" | "python" | "javascript";

export function EndpointDetailsPage() {
  const { projectId, endpointId } = useParams();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>("curl");
  const [copied, setCopied] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["endpoint", projectId, endpointId],
    queryFn: () => projectsApi.getEndpoint(projectId!, endpointId!),
    enabled: !!projectId && !!endpointId,
  });

  const explainMutation = useMutation({
    mutationFn: () => projectsApi.explainEndpoint(projectId!, endpointId!),
    onSuccess: () => {
      toast.success("AI explanation generated");
      queryClient.invalidateQueries({ queryKey: ["endpoint", projectId, endpointId] });
    },
    onError: () => toast.error("Explanation failed — is the AI service running?"),
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-8">
        <CardSkeleton />
      </div>
    );
  }

  const ep = data?.data;
  if (!ep) return null;

  const samples: Record<Tab, string | null> = {
    curl: ep.sample_curl,
    python: ep.sample_python,
    javascript: ep.sample_javascript,
  };

  const copyCode = () => {
    const code = samples[activeTab];
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <Link to={`/explorer/${projectId}`} className="mb-4 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300">
        <ArrowLeft className="h-4 w-4" /> Back to explorer
      </Link>

      <div className="mb-6 flex items-center gap-3">
        <MethodBadge method={ep.method} />
        <code className="mono text-lg text-slate-100">{ep.path}</code>
      </div>

      {ep.summary && <p className="mb-1 text-sm font-medium text-slate-300">{ep.summary}</p>}
      {ep.description && <p className="mb-6 text-sm text-slate-500">{ep.description}</p>}

      <div className="card mb-6 p-5">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-accent-light">
            <Sparkles className="h-4 w-4" /> AI Explanation
          </div>
          <button onClick={() => explainMutation.mutate()} disabled={explainMutation.isPending} className="btn-secondary text-xs">
            {explainMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
            {ep.ai_explanation ? "Regenerate" : "Explain this endpoint"}
          </button>
        </div>
        {ep.ai_explanation ? (
          <p className="text-sm leading-relaxed text-slate-300">{ep.ai_explanation}</p>
        ) : (
          <p className="text-sm text-slate-500">No explanation generated yet. Click above to ask the AI.</p>
        )}
      </div>

      <div className="card p-5">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex gap-1">
            {(["curl", "python", "javascript"] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  activeTab === tab ? "bg-accent text-white" : "text-slate-400 hover:bg-ink-700"
                }`}
              >
                {tab === "curl" ? "cURL" : tab === "python" ? "Python" : "JavaScript"}
              </button>
            ))}
          </div>
          {samples[activeTab] && (
            <button onClick={copyCode} className="btn-secondary text-xs">
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          )}
        </div>
        <pre className="mono overflow-x-auto rounded-lg bg-ink-950 p-4 text-xs leading-relaxed text-slate-300">
          {samples[activeTab] || "Generate an AI explanation first to get code samples for this endpoint."}
        </pre>
      </div>
    </div>
  );
}
