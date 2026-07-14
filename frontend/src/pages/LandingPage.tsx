import { Link } from "react-router-dom";
import { SearchCode, Sparkles, ShieldCheck, MessageSquare, FileCode2, ArrowRight } from "lucide-react";

const FEATURES = [
  {
    icon: Sparkles,
    title: "Instant AI summaries",
    body: "Upload any OpenAPI, Swagger, or Postman file and get a plain-English breakdown of what the API actually does.",
  },
  {
    icon: ShieldCheck,
    title: "Automated risk detection",
    body: "Catches unauthenticated mutating endpoints, missing documentation, and exposed identifiers before they ship.",
  },
  {
    icon: MessageSquare,
    title: "Chat with your API",
    body: "Ask natural-language questions and get answers grounded in the actual spec, powered by a local RAG pipeline.",
  },
  {
    icon: FileCode2,
    title: "One-click code samples",
    body: "Generate curl, Python, and JavaScript snippets for any endpoint — no more hand-writing boilerplate requests.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ink-900 text-slate-100">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/20 text-accent">
            <SearchCode className="h-5 w-5" />
          </div>
          <span className="font-semibold tracking-tight">API Investigator</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white">
            Sign in
          </Link>
          <Link to="/register" className="btn-primary">
            Get started
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-4xl px-6 pb-20 pt-16 text-center">
        <div className="mono mb-4 inline-flex items-center gap-2 rounded-full border border-ink-600 bg-ink-800 px-3 py-1 text-xs text-slate-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          RAG pipeline · local LLM · zero external API calls
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Understand any API<br />
          <span className="bg-gradient-to-r from-accent to-cyan bg-clip-text text-transparent">
            in minutes, not days
          </span>
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-slate-400">
          Upload an OpenAPI spec, Postman collection, or PDF doc. AI API Investigator parses it,
          indexes every endpoint, and lets you explore, question, and audit it instantly.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link to="/register" className="btn-primary px-6 py-3 text-base">
            Start investigating <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/login" className="btn-secondary px-6 py-3 text-base">
            I have an account
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="card p-5">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-ink-800 py-8 text-center text-xs text-slate-600">
        Built as a demonstration project — AI API Investigator.
      </footer>
    </div>
  );
}
