import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Upload,
  Compass,
  MessageSquare,
  History,
  FileText,
  User as UserIcon,
  Settings as SettingsIcon,
  LogOut,
  Moon,
  Sun,
  SearchCode,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Upload", icon: Upload },
  { to: "/explorer", label: "API Explorer", icon: Compass },
  { to: "/chat", label: "AI Chat", icon: MessageSquare },
  { to: "/history", label: "History", icon: History },
  { to: "/reports", label: "Reports", icon: FileText },
];

export function AppShell() {
  const { user, logout } = useAuth();
  const { isDark, toggle } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-ink-900">
      <aside className="flex w-64 flex-shrink-0 flex-col border-r border-ink-700 bg-ink-950">
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/20 text-accent">
            <SearchCode className="h-5 w-5" />
          </div>
          <span className="font-semibold tracking-tight text-slate-100">API Investigator</span>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-accent/15 text-accent-light"
                    : "text-slate-400 hover:bg-ink-800 hover:text-slate-100"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-ink-700 px-3 py-3 space-y-1">
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive ? "bg-accent/15 text-accent-light" : "text-slate-400 hover:bg-ink-800 hover:text-slate-100"
              }`
            }
          >
            <UserIcon className="h-4 w-4" />
            Profile
          </NavLink>
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive ? "bg-accent/15 text-accent-light" : "text-slate-400 hover:bg-ink-800 hover:text-slate-100"
              }`
            }
          >
            <SettingsIcon className="h-4 w-4" />
            Settings
          </NavLink>
          <button
            onClick={toggle}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition hover:bg-ink-800 hover:text-slate-100"
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            {isDark ? "Light mode" : "Dark mode"}
          </button>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>

        {user && (
          <div className="flex items-center gap-2 border-t border-ink-700 px-4 py-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-xs font-semibold text-accent-light">
              {user.full_name.slice(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-slate-200">{user.full_name}</p>
              <p className="truncate text-xs text-slate-500">{user.email}</p>
            </div>
          </div>
        )}
      </aside>

      <main className="flex-1 overflow-y-auto h-screen">
        <Outlet />
      </main>
    </div>
  );
}
