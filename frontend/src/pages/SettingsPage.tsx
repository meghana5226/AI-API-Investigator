import { Moon, Sun, Bell, Shield } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { PageHeader } from "../components/Shared";

export function SettingsPage() {
  const { isDark, toggle } = useTheme();

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <PageHeader title="Settings" description="Customize how AI API Investigator looks and behaves." />

      <div className="card divide-y divide-ink-700">
        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            {isDark ? <Moon className="h-5 w-5 text-accent" /> : <Sun className="h-5 w-5 text-accent" />}
            <div>
              <p className="text-sm font-medium text-slate-200">Dark mode</p>
              <p className="text-xs text-slate-500">Switch between light and dark themes.</p>
            </div>
          </div>
          <button
            onClick={toggle}
            className={`relative h-6 w-11 rounded-full transition ${isDark ? "bg-accent" : "bg-ink-600"}`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                isDark ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <Bell className="h-5 w-5 text-accent" />
            <div>
              <p className="text-sm font-medium text-slate-200">Analysis notifications</p>
              <p className="text-xs text-slate-500">Get notified in-app when AI analysis completes.</p>
            </div>
          </div>
          <span className="badge bg-emerald-500/15 text-emerald-400">Enabled</span>
        </div>

        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <Shield className="h-5 w-5 text-accent" />
            <div>
              <p className="text-sm font-medium text-slate-200">Data stays local</p>
              <p className="text-xs text-slate-500">Uploaded specs and AI processing run entirely on this deployment.</p>
            </div>
          </div>
          <span className="badge bg-sky-500/15 text-sky-400">Private</span>
        </div>
      </div>
    </div>
  );
}
