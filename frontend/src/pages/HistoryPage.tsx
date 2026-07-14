import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { History, Search } from "lucide-react";
import { historyApi } from "../api/history";
import { PageHeader, EmptyState } from "../components/Shared";
import { ListSkeleton } from "../components/Skeletons";

const ACTION_COLORS: Record<string, string> = {
  upload: "text-sky-400",
  analysis: "text-accent-light",
  chat: "text-violet-400",
  export: "text-emerald-400",
  comparison: "text-amber-400",
};

export function HistoryPage() {
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["history", search],
    queryFn: () => historyApi.list({ search: search || undefined, page_size: 50 }),
  });

  const items = data?.data.items ?? [];

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <PageHeader title="History" description="Everything you've done in AI API Investigator." />

      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          className="input-field pl-9"
          placeholder="Search history…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <ListSkeleton rows={6} />
      ) : items.length === 0 ? (
        <EmptyState icon={History} title="No activity yet" description="Your uploads, analyses, and chats will show up here." />
      ) : (
        <div className="card divide-y divide-ink-700">
          {items.map((entry) => (
            <div key={entry.id} className="flex items-start justify-between gap-4 px-4 py-3">
              <div>
                <span className={`mono text-xs font-semibold uppercase ${ACTION_COLORS[entry.action] ?? "text-slate-400"}`}>
                  {entry.action}
                </span>
                <p className="mt-0.5 text-sm text-slate-300">{entry.description}</p>
              </div>
              <span className="flex-shrink-0 text-xs text-slate-500">
                {new Date(entry.created_at).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
