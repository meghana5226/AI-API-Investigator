const STATUS_STYLES: Record<string, string> = {
  ready: "bg-emerald-500/15 text-emerald-400",
  processing: "bg-amber-500/15 text-amber-400",
  pending: "bg-slate-500/15 text-slate-400",
  failed: "bg-red-500/15 text-red-400",
  high: "bg-red-500/15 text-red-400",
  medium: "bg-amber-500/15 text-amber-400",
  low: "bg-sky-500/15 text-sky-400",
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status.toLowerCase()] ?? "bg-slate-500/15 text-slate-400";
  return <span className={`badge ${style}`}>{status}</span>;
}

const METHOD_STYLES: Record<string, string> = {
  GET: "bg-emerald-500/15 text-emerald-400",
  POST: "bg-sky-500/15 text-sky-400",
  PUT: "bg-amber-500/15 text-amber-400",
  PATCH: "bg-amber-500/15 text-amber-400",
  DELETE: "bg-red-500/15 text-red-400",
  DOC: "bg-violet-500/15 text-violet-400",
};

export function MethodBadge({ method }: { method: string }) {
  const style = METHOD_STYLES[method.toUpperCase()] ?? "bg-slate-500/15 text-slate-400";
  return <span className={`badge font-mono ${style}`}>{method}</span>;
}
