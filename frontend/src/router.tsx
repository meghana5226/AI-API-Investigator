import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { UploadPage } from "./pages/UploadPage";
import { ApiExplorerPage } from "./pages/ApiExplorerPage";
import { EndpointDetailsPage } from "./pages/EndpointDetailsPage";
import { AiChatPage } from "./pages/AiChatPage";
import { HistoryPage } from "./pages/HistoryPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SettingsPage } from "./pages/SettingsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/dashboard", element: <DashboardPage /> },
          { path: "/upload", element: <UploadPage /> },
          { path: "/explorer", element: <ApiExplorerPage /> },
          { path: "/explorer/:projectId", element: <ApiExplorerPage /> },
          { path: "/explorer/:projectId/endpoints/:endpointId", element: <EndpointDetailsPage /> },
          { path: "/chat", element: <AiChatPage /> },
          { path: "/history", element: <HistoryPage /> },
          { path: "/reports", element: <ReportsPage /> },
          { path: "/profile", element: <ProfilePage /> },
          { path: "/settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);
