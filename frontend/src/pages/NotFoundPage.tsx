import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-ink-900 px-4 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-accent">
        <Compass className="h-7 w-7" />
      </div>
      <h1 className="mono text-5xl font-bold text-slate-100">404</h1>
      <p className="mt-2 text-sm text-slate-500">This route doesn't exist in the API surface.</p>
      <Link to="/dashboard" className="btn-primary mt-6">
        Back to dashboard
      </Link>
    </div>
  );
}
