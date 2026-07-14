import { Loader2 } from "lucide-react";

export function FullPageSpinner() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-ink-900">
      <Loader2 className="h-8 w-8 animate-spin text-accent" />
    </div>
  );
}
